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

    if len(new_height.shape) != 1:
        raise ValueError(
            f"Target height bins must be 1D but has {len(new_height.shape)} dimensions (shape={new_height.shape})"
        )

    M, _ = values.shape
    H = len(new_height)
    rebinned_values = np.full((M, H), np.nan)

    height = ensure_vertical_2d(height, M)
    for i in range(M):
        valid = np.isfinite(values[i])
        if np.sum(valid) > 1:
            try:
                if method == "interpolate":
                    interp = interp1d(
                        height[i, valid],
                        values[i, valid],
                        kind="linear",
                        bounds_error=False,
                        fill_value=np.nan,
                        assume_sorted=True,
                    )
                    rebinned_values[i] = interp(new_height)
                else:
                    bin_edges = _convert_height_centers_to_bins(new_height)
                    start_idxs = np.searchsorted(height[i], bin_edges[:-1], side="left")
                    end_idxs = np.searchsorted(height[i], bin_edges[1:], side="left")
                    rebinned_values[i] = np.array(
                        [
                            nan_mean(values[i, start:end]) if start < end else np.nan
                            for start, end in zip(start_idxs, end_idxs)
                        ]
                    )

            except Exception:
                continue

    return rebinned_values


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

    ref_time = time[0].astype("datetime64[ns]")
    # print("ref_time", ref_time)
    time_f = (time - ref_time).astype("timedelta64[ns]").astype(np.float64)
    # print("time_f", time_f)
    new_time_f = (new_time - ref_time).astype("timedelta64[ns]").astype(np.float64)
    # print("new_time_f", new_time_f)

    T, N = len(new_time), values.shape[1]
    if is_geo:
        rebinned = np.full((T, 2), np.nan)
    else:
        rebinned = np.full((T, N), np.nan)

    for i in range(N):
        valid = np.isfinite(values[:, i])
        if np.sum(valid) < 2:
            continue

        if is_geo:
            # interpolate each dimension separately (lat and lon)
            for j, t_new in enumerate(new_time_f):
                # Find surrounding time points
                mask = time_f[valid] <= t_new
                if np.all(~mask) or np.all(mask):
                    continue
                idx_before = np.max(np.where(mask)[0])
                idx_after = np.min(np.where(~mask)[0])
                # print(time_f)
                t0, t1 = time_f[valid][[idx_before, idx_after]]
                # print(idx_before, idx_after)
                # print(t0, t1, values.shape)
                v0, v1 = values[valid][[idx_before, idx_after]]
                # print(v0, v1)
                f = (t_new - t0) / (t1 - t0)

                lon0, lat0 = v0
                lon1, lat1 = v1
                lon, lat = interpgeo(lon0, lat0, lon1, lat1, f)
                rebinned[j] = np.array(
                    [
                        lon,
                        lat,
                    ]
                )
        else:
            try:
                if method == "interpolate":
                    interp = interp1d(
                        time_f[valid],
                        values[valid, i],
                        kind="linear",
                        bounds_error=False,
                        fill_value=np.nan,
                    )
                    rebinned[:, i] = interp(new_time_f)
                else:
                    bin_edges = _convert_height_centers_to_bins(new_time_f)
                    start_idxs = np.searchsorted(
                        time_f[valid], bin_edges[:-1], side="left"
                    )
                    end_idxs = np.searchsorted(
                        time_f[valid], bin_edges[1:], side="left"
                    )
                    rebinned[:, i] = np.array(
                        [
                            nan_mean(values[start:end, i]) if start < end else np.nan
                            for start, end in zip(start_idxs, end_idxs)
                        ]
                    )

            except Exception:
                continue

    return rebinned


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
