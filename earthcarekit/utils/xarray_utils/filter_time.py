from typing import Iterable, Sequence

import numpy as np
import pandas as pd
import xarray as xr
from numpy.typing import NDArray

from ..constants import ALONG_TRACK_DIM, TIME_VAR
from ..np_array_utils import pad_true_sequence
from ..time import TimeRangeLike, TimestampLike, to_timestamp


def get_time_range(
    ds: xr.Dataset,
    time_range: TimeRangeLike | Iterable | None,
    time_var: str = TIME_VAR,
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """
    Ensures a complete time range by filling in missing start or end values using dataset boundaries.

    Args:
        ds (xr.Dataset): Dataset containing the time variable.
        time_var (str): Name of the time variable in the dataset.
        time_range (TimeRangeLike | Iterable | None): A two-element list, tuple or array containing start and end times,
            which may be strings, pandas Timestamps, or None.

    Returns:
        List[pd.Timestamp]: A complete [start, end] time range as pandas Timestamps.
    """
    if isinstance(time_range, (Sequence, np.ndarray)) and not isinstance(
        time_range, str
    ):
        if len(time_range) >= 2:
            time_range = [
                time_range[0],
                time_range[-1],
            ]
        else:
            raise ValueError(f"invalid time range '{time_range}'")
    elif time_range is None:
        time_range = [None, None]
    else:
        raise TypeError(
            f"Invalid type '{type(time_range).__name__}' for time_range. Expected a 2-element sequence (tuple or list)."
        )

    new_time_range: list[pd.Timestamp] = [pd.Timestamp(0), pd.Timestamp(0)]
    if time_range[0] is None:
        new_time_range[0] = to_timestamp(ds[time_var].values[0])
    else:
        new_time_range[0] = to_timestamp(time_range[0])

    if time_range[1] is None:
        new_time_range[1] = to_timestamp(ds[time_var].values[-1])
    else:
        new_time_range[1] = to_timestamp(time_range[1])

    return (new_time_range[0], new_time_range[1])


def get_filter_time_mask(
    ds: xr.Dataset,
    time_range: TimeRangeLike | Iterable | None = None,
    timestamp: TimestampLike | None = None,
    only_center: bool = False,
    time_var: str = TIME_VAR,
    along_track_dim: str = ALONG_TRACK_DIM,
    pad_idxs: int = 0,
) -> NDArray:
    times = ds[time_var].values
    mask: NDArray[np.bool_] = np.full(times.shape, False, dtype=bool)
    if timestamp is not None:
        timestamp = to_timestamp(timestamp)

        tmin = to_timestamp(times[0])
        tmax = to_timestamp(times[-1])

        if not tmin <= timestamp <= tmax:
            raise ValueError(
                f"Timestamp {timestamp} lies outside of the dataset's time range ({tmin} -> {tmax})"
            )

        idx = np.argmin(np.abs(times - timestamp.to_numpy()))
        mask[idx] = True
    else:
        time_range = get_time_range(ds, time_range=time_range, time_var=time_var)

        mask = (times >= np.min([time_range[0], time_range[1]])) & (
            times <= np.max([time_range[0], time_range[1]])
        )

    if only_center:
        mask_true_idxs = np.where(mask)[0]
        if len(mask_true_idxs) > 0:
            idx_center = mask_true_idxs[len(mask_true_idxs) // 2]
            mask[:] = False
            mask[idx_center] = True

    mask = pad_true_sequence(mask, pad_idxs)
    return mask


def filter_time(
    ds: xr.Dataset,
    time_range: TimeRangeLike | Iterable | None = None,
    timestamp: TimestampLike | None = None,
    only_center: bool = False,
    time_var: str = TIME_VAR,
    along_track_dim: str = ALONG_TRACK_DIM,
    pad_idxs: int = 0,
) -> xr.Dataset:
    """
    Filters an xarray Dataset to include only samples within a given time range.

    Args:
        ds (xr.Dataset): The input dataset containing a time coordinate.
        time_range (TimeRangeLike | Iterable | None):
            Start and end time of the range to filter, as strings or pandas timestamps. Defaults to None.
        timestamp (TimestampLike | None): A single timestamp for which the closest sample to return. Defaults to None.
        only_center (bool, optional): If True, only the sample at the center index of selection is returned. Defaults to False.
        time_var (str, optional): Name of the time variable in `ds`. Defaults to TIME_VAR.
        along_track_dim (str, optional): Dimension name along which time is defined. Defaults to ALONG_TRACK_DIM.
        pad_idxs (int, optional): Number of additional samples added at both sides of the selection. Defaults to 0.

    Returns:
        xr.Dataset: Subset of `ds` containing only samples within the specified time range.
    """
    if time_range is not None and timestamp is not None:
        raise ValueError(
            f"Can not use both arguments time_range and timestamp at the same time."
        )

    mask = get_filter_time_mask(
        ds=ds,
        time_range=time_range,
        timestamp=timestamp,
        only_center=only_center,
        time_var=time_var,
        along_track_dim=along_track_dim,
        pad_idxs=pad_idxs,
    )

    if np.sum(mask) == 0:
        times = ds[time_var].values
        msg = (
            f"No data falls into the given time range!\n"
            f"In the dataset time ranges from {times[0]} to {times[-1]}.\n"
        )
        raise ValueError(msg)

    da_mask: xr.DataArray = xr.DataArray(mask, dims=[along_track_dim], name=time_var)

    ds_new: xr.Dataset = xr.Dataset(
        {
            var: (
                ds[var].copy().where(da_mask, drop=True)
                if along_track_dim in ds[var].dims
                else ds[var].copy()
            )
            for var in ds.data_vars
        }
    )
    ds_new.attrs = ds.attrs.copy()
    ds_new.encoding = ds.encoding.copy()

    return ds_new
