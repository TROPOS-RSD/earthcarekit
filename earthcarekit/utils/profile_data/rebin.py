from typing import Iterable, Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray
from scipy.interpolate import interp1d  # type: ignore

from ..geo import haversine, interpgeo
from ..statistics import nan_mean
from ..time import TimestampLike, num_to_time, time_to_num
from ._validate_dimensions import ensure_vertical_2d, validate_profile_data_dimensions


def _convert_height_centers_to_bins(height: ArrayLike) -> NDArray:
    height = np.asarray(height)

    if len(height.shape) != 1:
        raise ValueError(f"height is {len(height.shape)}D but exptected to be 1D.")

    hd1 = np.diff(height)
    hd2 = np.append(hd1[0], hd1)
    hd3 = np.append(hd1, hd1[-1])

    hnew1 = height - hd2 / 2
    hnew2 = height + hd3 / 2

    hnew = np.append(hnew1, hnew2[-1])
    return hnew


def _ensure_numical_time(t: NDArray) -> NDArray:
    if np.isdtype(t.dtype, np.datetime64):
        return t.astype("int64")
    return t


def _get_time_bins(t: NDArray, t_new: NDArray) -> NDArray:
    t = _ensure_numical_time(t)
    t_new = _ensure_numical_time(t_new)

    edges = _convert_height_centers_to_bins(t_new)
    bins = np.digitize(t, edges) - 1
    bins = np.clip(bins, 0, t_new.shape[0] - 1)
    return bins


def _rebin_time_mean_1d(v: NDArray, v_new: NDArray, bins: NDArray) -> NDArray:
    mask = np.isfinite(v)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.bincount(
            bins[mask], weights=v[mask], minlength=len(v_new)
        ) / np.bincount(bins[mask], minlength=len(v_new))


def _rebin_time_mean_2d(v: NDArray, v_new: NDArray, bins: NDArray) -> NDArray:
    for j in range(v.shape[1]):
        v_new[:, j] = _rebin_time_mean_1d(v[:, j], v_new[:, j], bins)
    return v_new


def _rebin_time_mean(
    t: NDArray,
    t_new: NDArray,
    v: NDArray,
    is_geo: bool = False,
) -> NDArray:
    if is_geo:
        return _rebin_time_lerp(t, t_new, v, is_geo=is_geo)

    bins = _get_time_bins(t, t_new)

    if len(v.shape) == 2:
        v_new = np.full((t_new.shape[0], v.shape[1]), np.nan, dtype=v.dtype)
        v_new = _rebin_time_mean_2d(v, v_new, bins)
    elif len(v.shape) == 1:
        v_new = np.full(t_new.shape, np.nan, dtype=v.dtype)
        v_new = _rebin_time_mean_1d(v, v_new, bins)
    else:
        raise ValueError(f"unsupported shape {v.shape} for v, expected 1D or 2D array")
    return v_new


def _get_time_lerp_params(
    t: NDArray,
    t_new: NDArray,
    v: NDArray,
) -> tuple[NDArray, NDArray]:
    t = _ensure_numical_time(t)
    t_new = _ensure_numical_time(t_new)

    idx = np.searchsorted(t, t_new, side="left")
    idx = np.clip(idx, 1, len(t) - 1)
    t0 = t[idx - 1]
    t1 = t[idx]
    dt = t1 - t0
    w = np.where(dt != 0.0, (t_new - t0) / dt, 0.5)

    return (idx, w)


def _rebin_time_lerp_1d(
    idx: NDArray,
    w: NDArray,
    v: NDArray,
) -> NDArray:
    v0 = v[idx - 1]
    v1 = v[idx]
    dv = v1 - v0
    return v0 + w * dv


def _rebin_time_lerp_2d(
    idx: NDArray,
    w: NDArray,
    v: NDArray,
    is_geo: bool = False,
) -> NDArray:
    v0 = v[idx - 1, :]
    v1 = v[idx, :]

    if is_geo:
        rebinned = np.full((w.shape[0], 2), np.nan)
        for i in range(w.shape[0]):
            lon0, lat0 = v0[i]
            lon1, lat1 = v1[i]
            lon, lat = interpgeo(lon0, lat0, lon1, lat1, w[i])
            rebinned[i] = np.array(
                [
                    lat,
                    lon,
                ]
            )
    else:
        dv = v1 - v0
        rebinned = v0 + w[:, np.newaxis] * dv
    return rebinned


def _rebin_time_lerp(
    t: NDArray,
    t_new: NDArray,
    v: NDArray,
    is_geo: bool = False,
) -> NDArray:
    idx, w = _get_time_lerp_params(t, t_new, v)

    if len(v.shape) == 2:
        return _rebin_time_lerp_2d(idx, w, v, is_geo=is_geo)
    elif len(v.shape) == 1 and not is_geo:
        return _rebin_time_lerp_1d(idx, w, v)
    else:
        raise ValueError(
            f"unsupported shape {v.shape} for v, expected 1D or 2D array; also if 'is_geo=True', v must be 2D (n_time, 2) i.e. lat/lon"
        )


def _rebin_height_lerp(h: NDArray, h_new: NDArray, v: NDArray) -> NDArray:
    n = h.shape[0]
    m = h.shape[1]

    idx = np.array([np.searchsorted(h[i], h_new[i], side="left") for i in range(n)])
    idx = np.clip(idx, 1, m - 1)

    h0 = np.take_along_axis(h, idx - 1, axis=1)
    h1 = np.take_along_axis(h, idx, axis=1)
    dh = h1 - h0

    v0 = np.take_along_axis(v, idx - 1, axis=1)
    v1 = np.take_along_axis(v, idx, axis=1)
    dv = v1 - v0

    w = np.where(dh != 0.0, (h_new - h0) / dh, 0.0)

    return v0 + w * dv


def _rebin_height_mean(h: NDArray, h_new: NDArray, v: NDArray) -> NDArray:
    n = h.shape[0]
    m_new = h_new.shape[1]

    v_new = np.full((n, m_new), np.nan)

    for i in range(n):
        edges = _convert_height_centers_to_bins(h_new[i])
        bins = np.digitize(h[i], edges) - 1
        bins = np.clip(bins, 0, m_new - 1)

        mask = np.isfinite(v[i])
        sums = np.bincount(bins[mask], weights=v[i, mask], minlength=m_new)
        counts = np.bincount(bins[mask], minlength=m_new)
        with np.errstate(divide="ignore", invalid="ignore"):
            v_new[i] = sums / counts

    return v_new


def rebin_height(
    values: Iterable[float] | NDArray,
    height: Iterable[float] | NDArray,
    new_height: Iterable[float] | NDArray,
    method: Literal["interpolate", "mean"] = "mean",
) -> NDArray:
    """
    Rebins profile data to new height bins.

    Parameters:
        values (np.ndarray):
            Profile values as a 2D array
            (shape represents temporal and vertical dimension).
        height (np.ndarray):
            Height values either as a 2D array (same dimensions as `values`)
            or as a 1D array (shape represents vertical dimension).
        new_height (np.ndarray):
            Target height bin centers as a 1D array (shape represents vertical dimension)

    Returns:
        rebinned_values (np.ndarray):
            2D array with values rebinned along the second (i.e. vertical) according to `new_height`.
    """
    values = np.asarray(values)
    height = np.asarray(height)
    new_height = np.asarray(new_height)

    validate_profile_data_dimensions(values, height=height)
    if len(new_height.shape) == 2 and new_height.shape[0] == 1:
        new_height = np.asarray(new_height[0])

    M, _ = values.shape

    if len(new_height.shape) == 1:
        new_height = ensure_vertical_2d(new_height, M)

    height = ensure_vertical_2d(height, M)

    if method == "interpolate":
        return _rebin_height_lerp(height, new_height, values)
    return _rebin_height_mean(height, new_height, values)


def rebin_time(
    values: ArrayLike,
    time: ArrayLike,
    new_time: ArrayLike,
    is_geo: bool = False,
    method: Literal["interpolate", "mean"] = "mean",
) -> NDArray:
    """
    Rebins profile data to new time bins. If `is_geographic` is True, performs geodesic interpolation
    appropriate for latitude and longitude data.

    Args:
        values (np.ndarray): 2D array of values, shape (T, N).
        time (np.ndarray): 1D array of times (datetime64).
        new_time (np.ndarray): 1D array of target times (datetime64).
        is_geographic (bool): If True, apply geodesic interpolation for lon/lat.

    Returns:
        np.ndarray: Rebinned values with shape (len(new_time), N).
    """
    values = np.asarray(values)
    time = np.asarray(time)
    new_time = np.asarray(new_time)

    validate_profile_data_dimensions(values, time=time)

    if method == "interpolate":
        return _rebin_time_lerp(time, new_time, values, is_geo=is_geo)
    return _rebin_time_mean(time, new_time, values, is_geo=is_geo)


def rebin_along_track(
    values: ArrayLike,
    lat: ArrayLike,
    lon: ArrayLike,
    lat2: ArrayLike,
    lon2: ArrayLike,
) -> NDArray:
    """
    Interpolates values along track coordinates defined by lat/lon
    onto a new track's coordinates defined by lat2/lon2.

    Args:
        values (ArrayLike of shape (n,) or (n, m)): Values along the original track.
        lat (ArrayLike of shape (n,)): Original latitude.
        lon (ArrayLike of shape (n,)): Original longitude.
        lat2 (ArrayLike of shape (k,)): New latitude to interpolate to.
        lon2 (ArrayLike of shape (k,)): New longitude to interpolate to.

    Returns
        NDArray of shape (k,) or (k, m): Interpolated values at new track coordniates.
    """
    input = np.asarray(values)
    lat = np.asarray(lat)
    lon = np.asarray(lon)
    lat2 = np.asarray(lat2)
    lon2 = np.asarray(lon2)

    is_time: bool = isinstance(input[0], TimestampLike)

    if is_time:
        values = time_to_num(input, input[0])
    else:
        values = input

    # Calculate cumulative distances along track 1
    dists = haversine(
        np.vstack((lat[:-1], lon[:-1])).T,
        np.vstack((lat[1:], lon[1:])).T,
    )
    cum_dists = np.insert(np.cumsum(dists), 0, 0)

    # Calculate cumulative distances along track 2
    dists2 = haversine(
        np.vstack((lat2[:-1], lon2[:-1])).T,
        np.vstack((lat2[1:], lon2[1:])).T,
    )
    cum_dists2 = np.insert(np.cumsum(dists2), 0, 0)

    # Interpolate at points of track 2
    result = None
    if values.ndim == 1:
        result = np.interp(cum_dists2, cum_dists, values)
    elif values.ndim == 2:
        result = np.vstack(
            [
                np.interp(cum_dists2, cum_dists, values[:, i])
                for i in range(values.shape[1])
            ]
        ).T
    else:
        raise ValueError("values must be 1D or 2D array")

    if is_time:
        result = num_to_time(result, input[0])

    return np.asarray(result)
