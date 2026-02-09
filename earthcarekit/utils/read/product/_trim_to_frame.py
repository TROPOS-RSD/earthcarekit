import numpy as np
from xarray import DataArray, Dataset

from ...constants import ALONG_TRACK_DIM, EC_LATITUDE_FRAME_BOUNDS, TRACK_LAT_VAR
from ...xarray_utils import insert_var
from .header_group import read_header_data


def get_frame_id(ds: Dataset) -> str:
    if "frameID" in ds:
        return str(ds.frameID.values)
    return str(read_header_data(ds).frameID.values.astype(str))


def get_frame_along_track(
    ds: Dataset,
    lat_var: str = TRACK_LAT_VAR,
    frame_id: str | None = None,
) -> tuple[int, int]:
    if not isinstance(frame_id, str):
        frame_id = get_frame_id(ds)
    lat_framestart, lat_framestop = EC_LATITUDE_FRAME_BOUNDS[frame_id]

    lat = ds[lat_var].data

    if lat_framestart == lat_framestop:
        if lat_framestart > 0:
            idxs = np.argwhere(lat >= lat_framestart)
        else:
            idxs = np.argwhere(lat <= lat_framestart)
    elif lat_framestart < lat_framestop:
        idxs = np.argwhere(np.logical_and(lat >= lat_framestart, lat <= lat_framestop))
    else:
        idxs = np.argwhere(np.logical_and(lat <= lat_framestart, lat >= lat_framestop))

    slice_tuple = int(idxs[0][0]), int(idxs[-1][0]) + 1

    return slice_tuple


def trim_to_latitude_frame_bounds(
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
    slice_tuple = get_frame_along_track(
        ds,
        lat_var=lat_var,
        frame_id=frame_id,
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
