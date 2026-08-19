from typing import Iterable, Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ...geo import haversine, interpgeo
from ...utils.numpy import centers_to_bins
from ...utils.numpy._rebin._rebin_lerp import _get_lerp_params, _rebin_lerp_1d, _rebin_lerp_2d
from ...utils.numpy._rebin._rebin_mean import _rebin_mean_1d, _rebin_mean_2d
from ...utils.time import TimestampLike, num_to_time, time_to_num
from ._validate_dimensions import ensure_vertical_2d, validate_profile_data_dimensions


def _ensure_numical_time(t: NDArray) -> NDArray:
    if np.isdtype(t.dtype, np.datetime64):
        return t.astype("int64")
    return t


def _get_time_bins(t: NDArray, t_new: NDArray) -> NDArray:
    t = _ensure_numical_time(t)
    t_new = _ensure_numical_time(t_new)

    edges = centers_to_bins(t_new)
    bins = np.digitize(t, edges) - 1
    bins = np.clip(bins, 0, t_new.shape[0] - 1)
    return bins


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
        v_new = _rebin_mean_2d(v, v_new, bins)
    elif len(v.shape) == 1:
        v_new = np.full(t_new.shape, np.nan, dtype=v.dtype)
        v_new = _rebin_mean_1d(v, v_new, bins)
    else:
        raise ValueError(f"unsupported shape {v.shape} for v, expected 1D or 2D array")
    return v_new


def _get_time_lerp_params(
    t: NDArray,
    t_new: NDArray,
) -> tuple[NDArray, NDArray]:
    t = _ensure_numical_time(t)
    t_new = _ensure_numical_time(t_new)

    return _get_lerp_params(t, t_new)


def _rebin_time_lerp_2d(
    idx: NDArray,
    w: NDArray,
    v: NDArray,
    is_geo: bool = False,
) -> NDArray:
    if is_geo:
        v0 = v[idx - 1, :]
        v1 = v[idx, :]

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
        return rebinned
    else:
        return _rebin_lerp_2d(idx, w, v)


def _rebin_time_lerp(
    t: NDArray,
    t_new: NDArray,
    v: NDArray,
    is_geo: bool = False,
) -> NDArray:
    idx, w = _get_time_lerp_params(t, t_new)

    if len(v.shape) == 2:
        return _rebin_time_lerp_2d(idx, w, v, is_geo=is_geo)
    elif len(v.shape) == 1 and not is_geo:
        return _rebin_lerp_1d(idx, w, v)
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
        edges = centers_to_bins(h_new[i])
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
    """Rebins profile data to new height bins.

    Args:
        values: Profile values as a 2D array (time/height).
        height: Height values as a 2D (time/height) or 1D (vertical) array.
        new_height: Target height bin centers as a 1D (vertical) array.
        method: "interpolate" for linear interpolation to bin centers; "mean" for bin-averaging.

    Returns:
        A 2D array with values rebinned along the vertical dimension.
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
    """Rebins profile data to new time bins.

    Args:
        values: Profile values as a 2D array (time/height).
        time: Time values as a 1D array (datetime64).
        new_time: Target time bin centers as a 1D array (datetime64).
        is_geo: If True, perform geodesic interpolation for lon/lat data.
        method: "interpolate" for linear interpolation to bin centers; "mean" for bin-averaging.

    Returns:
        A 2D array with values rebinned along the temporal dimension.
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
    """Interpolates values along track coordinates onto a new track.

    Args:
        values: Values along the original track (1D or 2D).
        lat: Original latitude (1D).
        lon: Original longitude (1D).
        lat2: New latitude coordinates (1D).
        lon2: New longitude coordinates (1D).

    Returns:
        Interpolated values at new track coordinates (1D or 2D).
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
            [np.interp(cum_dists2, cum_dists, values[:, i]) for i in range(values.shape[1])]
        ).T
    else:
        raise ValueError("values must be 1D or 2D array")

    if is_time:
        result = num_to_time(result, input[0])

    return np.asarray(result)
