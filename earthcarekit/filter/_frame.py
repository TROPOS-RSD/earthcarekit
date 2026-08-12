import warnings

import numpy as np
from numpy.typing import ArrayLike, NDArray
from xarray import Dataset

from ..constants import ALONG_TRACK_DIM, EC_LATITUDE_FRAME_BOUNDS, TRACK_LAT_VAR
from ..utils import get_file_info_from_str
from ..utils.xarray import insert_var


def get_frame_id(ds: Dataset) -> str:
    """Identifies EarthCARE frame of a `xarray.Dataset`.

    Args:
        ds (Dataset): EarthCARE dataset. Defaults to None.

    Raises:
        ValueError: When not able to retrieve frame ID from either the dataset encoding (i.e., `ds.encoding["source"]`) or a variable (i.e., `"frame_id"` or `"frameID"`).

    Returns:
        str: EarthCARE frame ID letter (A-H)
    """
    frame_id: str | None = None
    source = ds.encoding.get("source")
    if isinstance(source, str):
        frame_id = get_file_info_from_str(source).get("frame_id")

    if frame_id in EC_LATITUDE_FRAME_BOUNDS:
        return frame_id

    for var in ("frame_id", "frameID"):
        if var in ds:
            if len(ds[var].values) > 1:
                warnings.warn("Dataset contains multiple frame IDs; only the first will be used.")
            return str(ds[var].values[0])

    raise ValueError(
        """dataset missing info on 'frame_id', expected to find info in `ds.encoding["source"]` or in variables named `"frame_id"` or `"frameID"`."""
    )


def argwhere_frame(latitude: ArrayLike, start: float, stop: float) -> NDArray[np.intp]:
    latitude = np.asarray(latitude)
    if start == stop:
        if start > 0:
            idxs = np.argwhere(latitude >= start)
        else:
            idxs = np.argwhere(latitude <= start)
    elif start < stop:
        idxs = np.argwhere(np.logical_and(latitude >= start, latitude <= stop))
    else:
        idxs = np.argwhere(np.logical_and(latitude <= start, latitude >= stop))
    return idxs


def get_frame_slice_tuple(
    latitude: ArrayLike,
    frame_id: str,
) -> tuple[int, int]:
    """Return start and end index of an EarthCARE frame for a along-track latitude sequence.

    This method assumes input latitudes from a continous sequence of satellite track coordinates
    spanning at most a single EarthCARE frame. The coordinates may extend slightly beyond the
    frame's limits (e.g., due to margins), but they must not span multiple frames or full orbits.

    Args:
        latitude (Dataset): EarthCARE dataset.
        frame_id (str): EarthCARE frame ID letter (A-H).

    Raises:
        ValueError: When not able to retrieve frame ID from either the dataset encoding (i.e., `ds.encoding["source"]`) or a variable (i.e., `"frame_id"` or `"frameID"`).

    Returns:
        str: Slice tuple matching the data within the EarthCARE frame.
    """
    start, stop = EC_LATITUDE_FRAME_BOUNDS[frame_id]
    idxs = argwhere_frame(latitude, start, stop)
    slice_tuple = int(idxs[0][0]), int(idxs[-1][0]) + 1
    return slice_tuple


def argwhere_frame_check_gaps(latitude: ArrayLike, start: float, stop: float) -> NDArray[np.intp]:
    idxs = argwhere_frame(latitude, start, stop)
    diffs = np.argwhere(np.diff(idxs[:, 0]) > 1)
    if len(diffs) > 0:
        return idxs[: diffs[0, 0] + 1]
    return idxs


def get_frame_slice_tuple_check_gaps(latitude: ArrayLike, frame_id: str) -> tuple[int, int]:
    start, stop = EC_LATITUDE_FRAME_BOUNDS[frame_id]
    idxs = argwhere_frame_check_gaps(latitude, start, stop)
    slice_tuple = int(idxs[0][0]), int(idxs[-1][0]) + 1
    return slice_tuple


def get_frame_index_range(
    latitude: ArrayLike | None = None,
    frame_id: str | None = None,
    ds: Dataset | None = None,
    lat_var: str = TRACK_LAT_VAR,
) -> tuple[int, int]:
    """Generate an index range for trimming arrays or datasets to EarthCARE latitude frame bounds.

    Args:
        latitude (ArrayLike | None, optional):
            Sequence of along-track latitude values. Defaults to None.
        frame_id (str | None, optional):
            EarthCARE frame ID (single character between "A" and "H"). Defaults to None.
        ds (Dataset | None, optional):
            EarthCARE dataset containing along-track latitude values. Defaults to None.
        lat_var (str, optional):
            Name of the latitude dataset variable. Defaults to TRACK_LAT_VAR.

    Raises:
        ValueError:
            If inputs are missing (requires `latitude` and `ds` or `frame_id`).

    Returns:
        tuple[int, int]: EarthCARE frame index range (i.e., slice tuple)

    Examples:
        >>> import earthcarekit as eck
        >>> ds = eck.ecload("CPR_FMR_2A", "09167F", download=True, trim_to_frame=False)
        >>> slice_tuple = eck.filter.get_frame_index_range(ds=ds, frame_id="F")
        >>> # Or: eck.filter.get_frame_index_range(latitude=ds.latitude.values, frame_id="F")
        >>> ds_sliced = ds.isel({"along_track": slice(*slice_tuple)})
        >>> print("non-trimmed:", ds.along_track.shape)
        >>> print("timming slice:", slice_tuple)
        >>> print("timmed:", ds_sliced.along_track.shape)
        non-trimmed: (4992,)
        timming slice: (14, 4978)
        timmed: (4964,)
    """
    if isinstance(ds, Dataset):
        lat = ds[lat_var].data
        if not isinstance(frame_id, str):
            frame_id = get_frame_id(ds)
    elif latitude is not None:
        lat = np.asarray(latitude)
    else:
        raise ValueError("Either ds or latitude array must be given")

    if not isinstance(frame_id, str):
        raise ValueError("Missing frame_id input")
    return get_frame_slice_tuple_check_gaps(lat, frame_id)


def filter_frame(
    ds: Dataset,
    frame_id: str | None = None,
    along_track_dim: str = ALONG_TRACK_DIM,
    lat_var: str = TRACK_LAT_VAR,
    add_trim_index_offset_var: bool = True,
    trim_index_offset_var: str = "trim_index_offset",
) -> Dataset:
    """
    Trims the dataset to the region within the latitude frame bounds.

    Args:
        ds (xarray.Dataset):
            Input dataset to be trimmed.
        frame_id (str | None, optional):
            EarthCARE frame ID (single character between "A" and "H").
            If given, speeds up trimming. Defaults to None.
        along_track_dim (str, optional):
            Dimension along which to trim. Defaults to ALONG_TRACK_DIM.
        lat_var (str, optional):
            Name of the latitude variable. Defaults to TRACK_LAT_VAR.
        add_trim_index_offset_var (bool, optional):
            Whether the index offset between the original and trimmed dataset is stored
            in the trimmed dataset (variable: "trim_index_offset"). Defaults to True.

    Returns:
        xarray.Dataset: Trimmed dataset.

    Examples:
        >>> import earthcarekit as eck
        >>> ds = eck.ecload("CPR_FMR_2A", "09167F", download=True, trim_to_frame=False)
        >>> ds_filtered = eck.filter_frame(ds)
        >>> print("non-trimmed:", ds.along_track.shape)
        >>> print("timmed:", ds_filtered.along_track.shape)
        non-trimmed: (4992,)
        timmed: (4964,)
    """
    slice_tuple = get_frame_index_range(
        frame_id=frame_id,
        ds=ds,
        lat_var=lat_var,
    )
    ds = ds.isel({along_track_dim: slice(*slice_tuple)})
    if add_trim_index_offset_var and slice_tuple[0] > 0:
        ds = insert_var(
            ds=ds,
            var=trim_index_offset_var,
            data=int(slice_tuple[0]),
            index=0,
            after_var="processing_start_time",
        )
        ds[trim_index_offset_var] = ds[trim_index_offset_var].assign_attrs(
            {
                "earthcarekit": "Added by earthcarekit: Used to calculate the index in the original, untrimmed dataset, i.e. by addition."
            }
        )
    return ds
