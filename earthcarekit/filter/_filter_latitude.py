import warnings

import numpy as np
import xarray as xr
from numpy.typing import NDArray
from scipy.signal import find_peaks  # type: ignore

from ..constants import ALONG_TRACK_DIM, TIME_VAR, TRACK_LAT_VAR
from ..typing import NumberPairNoneLike, validate_numeric_pair
from ..utils.time import TimedeltaLike
from ._handle_trim_index_offset import update_trim_index_offset
from ._padding import _pad_mask


def cosses_pole(lats: NDArray) -> bool:
    maxima, _ = find_peaks(lats)
    minima, _ = find_peaks(-lats)
    peaks = np.sort(np.concat((maxima, minima)))
    n_corssings = len(peaks)
    if n_corssings > 1:
        warnings.warn(
            f"Latitude track crosses polar regions more than one time ({len(peaks)}); filtering by latitude might yield unexpected results."
        )
    return n_corssings > 0


def _get_pole_crossing_masks(
    lats: NDArray,
) -> tuple[bool, bool, NDArray[np.bool_], NDArray[np.bool_]]:
    lats_diff: NDArray = np.diff(lats)

    satellite_crosses_pole: bool = cosses_pole(lats)

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
    lat_range: NumberPairNoneLike,
    start_before_pole: bool = True,
    end_before_pole: bool = True,
    only_center: bool = False,
    lat_var: str = TRACK_LAT_VAR,
    along_track_dim: str = ALONG_TRACK_DIM,
    trim_index_offset_var: str = "trim_index_offset",
    pad_idxs: int = 0,
    shift_idxs: int = 0,
    pad_time: TimedeltaLike | tuple[TimedeltaLike, TimedeltaLike] | None = None,
    time_var: str = TIME_VAR,
) -> xr.Dataset:
    """
    Filters a dataset to include only points within a specified latitude range.

    Args:
        ds: Input dataset with geolocation data.
        lat_range: A pair of latitude values (min_lat, max_lat) defining the selection range.
        start_before_pole: If True, selection starts before the pole when the track crosses one.
        end_before_pole: If True, selection ends before the pole when the track crosses one.
        only_center: If True, only the sample at the center index of selection is returned.
        lat_var: Name of the latitude variable.
        along_track_dim: Dimension along which to apply filtering.
        trim_index_offset_var: Variable tracking index offsets from trimming/filtering.
        pad_idxs: Number of additional samples added at both ends.
        shift_idxs: Offset number to shift selection of samples.
        pad_time: Additional time padding; applied before index-based padding (`pad_idxs`, `shift_idxs`).
        time_var: Name of the time variable in `ds`.

    Raises:
        ValueError: If selection is empty.

    Returns:
        Filtered dataset containing only points within the specified latitude range.

    Examples:
        >>> import numpy as np
        >>> import earthcarekit as eck
        >>> np.set_printoptions(precision=3)
        >>> ds = eck.ecload("CPR_FMR_2A", "09167F", download=True)
        >>> print(ds.latitude.values)
        [-22.503 -22.512 -22.521 ... -67.482 -67.491 -67.499]

        >>> ds_filtered = eck.filter_latitude(ds, (-40, -30))
        >>> print(ds_filtered.latitude.values)
        [-30.004 -30.013 -30.021 ... -39.981 -39.99  -39.998]
    """
    lats = ds[lat_var].values
    satellite_crosses_pole, is_first_increase, mask_before_pole, mask_after_pole = (
        _get_pole_crossing_masks(lats)
    )
    lat_range = validate_numeric_pair(lat_range, fallback=(lats[0], lats[-1]))

    lats_mask: NDArray[np.bool_] = (lats >= np.min(lat_range)) & (lats <= np.max(lat_range))

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

    mask = _pad_mask(
        ds=ds,
        mask=mask,
        pad_idxs=pad_idxs,
        shift_idxs=shift_idxs,
        pad_time=pad_time,
        time_var=time_var,
    )

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

    ds_new = update_trim_index_offset(
        ds=ds_new,
        offset=int(np.argmax(mask)),
        var=trim_index_offset_var,
    )

    return ds_new
