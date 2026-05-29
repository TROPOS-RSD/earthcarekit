import numpy as np
from numpy.typing import ArrayLike
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
            return str(ds[var].values)

    raise ValueError(
        """dataset missing info on 'frame_id', expected to find info in `ds.encoding["source"]` or in variables named `"frame_id"` or `"frameID"`."""
    )


def get_frame_slice_tuple(
    latitude: ArrayLike,
    frame_id: str,
) -> tuple[int, int]:
    """Returns start and end index of EC frame bounds for a along-track latitude sequence and frame ID.

    Args:
        latitude (Dataset): EarthCARE dataset. Defaults to None.

    Raises:
        ValueError: When not able to retrieve frame ID from either the dataset encoding (i.e., `ds.encoding["source"]`) or a variable (i.e., `"frame_id"` or `"frameID"`).

    Returns:
        str: EarthCARE frame ID letter (A-H)
    """
    latitude = np.asarray(latitude)

    lat_framestart, lat_framestop = EC_LATITUDE_FRAME_BOUNDS[frame_id]

    if lat_framestart == lat_framestop:
        if lat_framestart > 0:
            idxs = np.argwhere(latitude >= lat_framestart)
        else:
            idxs = np.argwhere(latitude <= lat_framestart)
    elif lat_framestart < lat_framestop:
        idxs = np.argwhere(np.logical_and(latitude >= lat_framestart, latitude <= lat_framestop))
    else:
        idxs = np.argwhere(np.logical_and(latitude <= lat_framestart, latitude >= lat_framestop))

    slice_tuple = int(idxs[0][0]), int(idxs[-1][0]) + 1

    return slice_tuple


def get_frame_index_range(
    latitude: ArrayLike | None = None,
    frame_id: str | None = None,
    ds: Dataset | None = None,
    lat_var: str = TRACK_LAT_VAR,
) -> tuple[int, int]:
    """
    Generates index range for trimming arrays or datasets to EarthCARE latitude frame bounds.

    Args:
        latitude (ArrayLike | None, optional): Sequence of along-track latitude values. Defaults to None.
        frame_id (str | None, optional): EarthCARE frame ID (single character between "A" and "H"). Defaults to None.
        ds (Dataset | None, optional): EarthCARE dataset containing along-track latitude values. Defaults to None.
        lat_var (str, optional): Name of the latitude dataset variable. Defaults to TRACK_LAT_VAR.

    Raises:
        ValueError: If inputs are missing (`latitude` or `ds` are required, also `frame_id` when `ds` is None).

    Returns:
        tuple[int, int]: EarthCARE frame index range (i.e., slice tuple)
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
    return get_frame_slice_tuple(lat, frame_id)


def filter_frame(
    ds: Dataset,
    along_track_dim: str = ALONG_TRACK_DIM,
    lat_var: str = TRACK_LAT_VAR,
    frame_id: str | None = None,
    add_trim_index_offset_var: bool = True,
    trim_index_offset_var: str = "trim_index_offset",
) -> Dataset:
    """
    Trims the dataset to the region within the latitude frame bounds.

    Args:
        ds (xarray.Dataset):
            Input dataset to be trimmed.
        along_track_dim (str, optional):
            Dimension along which to trim. Defaults to ALONG_TRACK_DIM.
        lat_var (str, optional):
            Name of the latitude variable. Defaults to TRACK_LAT_VAR.
        frame_id (str | None, optional):
            EarthCARE frame ID (single character between "A" and "H").
            If given, speeds up trimming. Defaults to None.
        add_trim_index_offset_var (bool, optional):
            Whether the index offset between the original and trimmed dataset is stored
            in the trimmed dataset (variable: "trim_index_offset"). Defaults to True.

    Returns:
        xarray.Dataset: Trimmed dataset.
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
