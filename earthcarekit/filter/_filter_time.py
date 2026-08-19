from typing import Iterable, Sequence

import numpy as np
import pandas as pd
import xarray as xr
from numpy.typing import NDArray

from ..constants import ALONG_TRACK_DIM, TIME_VAR
from ..utils.time import TimedeltaLike, TimeRangeLike, TimestampLike, to_timestamp
from ._handle_trim_index_offset import update_trim_index_offset
from ._padding import _pad_mask


def get_time_range(
    ds: xr.Dataset,
    time_range: TimeRangeLike | Iterable | None,
    time_var: str = TIME_VAR,
) -> tuple[pd.Timestamp, pd.Timestamp]:
    """Ensures a complete time range by filling missing start/end values with dataset boundaries.

    Args:
        ds: Dataset containing the time variable.
        time_var: Name of the time variable.
        time_range: Time range (start, end); `None` entries filled from `ds`.

    Returns:
        A complete (start, end) time range as pandas Timestamps.
    """
    if isinstance(time_range, (Sequence, np.ndarray)) and not isinstance(time_range, str):
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
    pad_idxs: int = 0,
    shift_idxs: int = 0,
    pad_time: TimedeltaLike | tuple[TimedeltaLike, TimedeltaLike] | None = None,
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

    mask = _pad_mask(
        ds=ds,
        mask=mask,
        pad_idxs=pad_idxs,
        shift_idxs=shift_idxs,
        pad_time=pad_time,
        time_var=time_var,
    )

    return mask


def filter_time(
    ds: xr.Dataset,
    time_range: TimeRangeLike | Iterable | None = None,
    timestamp: TimestampLike | None = None,
    only_center: bool = False,
    time_var: str = TIME_VAR,
    along_track_dim: str = ALONG_TRACK_DIM,
    trim_index_offset_var: str = "trim_index_offset",
    pad_idxs: int = 0,
    shift_idxs: int = 0,
    pad_time: TimedeltaLike | tuple[TimedeltaLike, TimedeltaLike] | None = None,
) -> xr.Dataset:
    """Filters an xarray Dataset to include only samples within a given time range.

    Args:
        ds: Input dataset containing a time coordinate.
        time_range: Start and end time of the range to filter.
        timestamp: Single timestamp; returns closest sample if provided.
        only_center: If True, returns only the center sample of the selection.
        time_var: Name of the time variable in `ds`.
        along_track_dim: Dimension name along which time is defined.
        trim_index_offset_var: Variable tracking index offsets from trimming/filtering.
        pad_idxs: Number of additional samples added at both ends.
        shift_idxs: Offset to shift selected sample indices.
        pad_time: Additional time padding applied before index-based padding.

    Returns:
        Filtered dataset containing only samples within the specified time range.

    Examples:
        >>> import earthcarekit as eck
        >>> ds = eck.ecload("CPR_FMR_2A", "09167F", download=True)
        >>> print(ds.time.values[[0, -1]])
        ['2026-01-08T03:04:08.393852234' '2026-01-08T03:15:57.401298285']

        >>> ds_filtered = eck.filter_time(ds, time_range=("2026-01-08 03:10", "2026-01-08 03:12"))
        >>> print(ds_filtered.time.values[[0, -1]])
        ['2026-01-08T03:10:00.115605354' '2026-01-08T03:11:59.985651731']
    """
    if time_range is not None and timestamp is not None:
        raise ValueError("Can not use both arguments time_range and timestamp at the same time.")

    mask = get_filter_time_mask(
        ds=ds,
        time_range=time_range,
        timestamp=timestamp,
        only_center=only_center,
        time_var=time_var,
        pad_idxs=pad_idxs,
        shift_idxs=shift_idxs,
        pad_time=pad_time,
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

    ds_new = update_trim_index_offset(
        ds=ds_new,
        offset=int(np.argmax(mask)),
        var=trim_index_offset_var,
    )

    return ds_new
