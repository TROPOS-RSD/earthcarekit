from typing import Iterable, Sequence

import numpy as np
import pandas as pd
import xarray as xr
from numpy.typing import NDArray

from ..constants import ALONG_TRACK_DIM, TIME_VAR, TRACK_LAT_VAR
from ..np_array_utils import pad_true_sequence
from ..time import TimeRangeLike, TimestampLike, to_timestamp
from ..typing import NumericPairNoneLike, validate_numeric_pair


def _get_pole_crossing_masks(
    ds: xr.Dataset,
    lat_var: str = TRACK_LAT_VAR,
) -> tuple[bool, bool, NDArray[np.bool_], NDArray[np.bool_]]:
    lats: NDArray = ds[lat_var].values
    lats_diff: NDArray = np.diff(lats)

    satellite_crosses_pole: bool = (lats_diff[0] > 0) != (lats_diff[-1] > 0)

    is_first_increase: bool = lats_diff[0] > 0

    mask_before_pole: NDArray[np.bool_]
    mask_after_pole: NDArray[np.bool_]
    if is_first_increase:
        mask_before_pole = np.append(lats_diff[0], lats_diff) > 0
        mask_after_pole = np.logical_not(mask_before_pole)
    else:
        mask_before_pole = np.append(lats_diff[0], lats_diff) <= 0
        mask_after_pole = np.logical_not(mask_before_pole)

    return satellite_crosses_pole, is_first_increase, mask_before_pole, mask_after_pole


def filter_latitude(
    ds: xr.Dataset,
    lat_range: NumericPairNoneLike,
    start_before_pole: bool = True,
    end_before_pole: bool = True,
    only_center: bool = False,
    lat_var: str = TRACK_LAT_VAR,
    along_track_dim: str = ALONG_TRACK_DIM,
    pad_idxs: int = 0,
) -> xr.Dataset:
    """
    Filters a dataset to include only points within a specified latitude range.

    Args:
        ds (xr.Dataset): Input dataset with geolocation data.
        lat_range (NumericPairNoneLike): A pair of latitude values (min_lat, max_lat) defining the selection range.
        start_before_pole (bool, optional): If True, selection starts before the pole when the track crosses one. Defaults to True.
        end_before_pole (bool, optional): If True, selection ends before the pole when the track crosses one. Defaults to True.
        only_center (bool, optional): If True, only the sample at the center index of selection is returned. Defaults to False.
        lat_var (str, optional): Name of the latitude variable. Defaults to TRACK_LAT_VAR.
        along_track_dim (str, optional): Dimension along which to apply filtering. Defaults to ALONG_TRACK_DIM.
        pad_idxs (int, optional): Number of additional samples added at both sides of the selection. Defaults to 0.

    Raises:
        ValueError: If selection is empty.

    Returns:
        xr.Dataset: Filtered dataset containing only points within the specified latitude range.
    """
    lats = ds[lat_var].values

    satellite_crosses_pole, is_first_increase, mask_before_pole, mask_after_pole = (
        _get_pole_crossing_masks(ds, lat_var=lat_var)
    )

    lat_range = validate_numeric_pair(lat_range, fallback=(lats[0], lats[-1]))

    lats_mask: NDArray[np.bool_] = (lats >= np.min(lat_range)) & (
        lats <= np.max(lat_range)
    )

    if satellite_crosses_pole and start_before_pole and not end_before_pole:
        if is_first_increase:
            mask_from_start = lats >= lat_range[0]
            mask_from_end = lats >= lat_range[1]
        else:
            mask_from_start = lats <= lat_range[0]
            mask_from_end = lats <= lat_range[1]

        mask_from_start_before_pole = np.logical_and(mask_before_pole, mask_from_start)
        mask_from_end_after_pole = np.logical_and(mask_after_pole, mask_from_end)

        mask = np.logical_or(mask_from_start_before_pole, mask_from_end_after_pole)
    elif satellite_crosses_pole and start_before_pole and end_before_pole:
        mask = np.logical_and(lats_mask, mask_before_pole)
    elif satellite_crosses_pole and not start_before_pole:
        mask = np.logical_and(lats_mask, mask_after_pole)
    else:
        mask = lats_mask

    if only_center:
        mask_true_idxs = np.where(mask)[0]
        if len(mask_true_idxs) > 0:
            idx_center = mask_true_idxs[len(mask_true_idxs) // 2]
            mask[:] = False
            mask[idx_center] = True

    mask = pad_true_sequence(mask, pad_idxs)

    if np.sum(mask) == 0:
        msg = f"No data falls into the given latitude range!\nIn the dataset latitude falls between {np.min(lats)} and {np.max(lats)}.\n"
        if satellite_crosses_pole:
            msg += "Note that the satellite crosses a pole (set `start_before_pole` and `end_before_pole`\nto clarify how the start and end of the range should be interpreted)."
        else:
            msg += "The satellite is not crossing a pole."
        raise ValueError(msg)

    da_mask: xr.DataArray = xr.DataArray(mask, dims=[along_track_dim], name=lat_var)

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
