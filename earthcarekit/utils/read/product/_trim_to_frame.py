import numpy as np
from xarray import Dataset

from ...constants import ALONG_TRACK_DIM, EC_LATITUDE_FRAME_BOUNDS, TRACK_LAT_VAR
from .header_group import read_header_data


def get_frame_id(ds: Dataset) -> str:
    if "frameID" in ds:
        return str(ds.frameID.values)
    return str(read_header_data(ds).frameID.values.astype(str))


def get_frame_along_track(
    ds: Dataset, along_track_dim: str = ALONG_TRACK_DIM, lat_var: str = TRACK_LAT_VAR
) -> tuple[int, int]:
    frame_id = get_frame_id(ds)
    lat_framestart, lat_framestop = EC_LATITUDE_FRAME_BOUNDS[frame_id]

    i_halfway = len(ds[along_track_dim]) // 2
    i_framestart = np.argmin(np.abs(ds[lat_var].values[:i_halfway] - lat_framestart))
    i_framestop = i_halfway + np.argmin(
        np.abs(ds[lat_var].values[i_halfway:] - lat_framestop)
    )

    return int(i_framestart), int(i_framestop)


def trim_to_latitude_frame_bounds(
    ds: Dataset, along_track_dim: str = ALONG_TRACK_DIM, lat_var: str = TRACK_LAT_VAR
) -> Dataset:
    """
    Trims the dataset to the region within the latitude frame bounds.

    Args:
        ds (xarray.Dataset): Input dataset to be trimmed.
        along_track_dim (str, optional): Dimension along which to trim. Defaults to ALONG_TRACK_DIM.
        lat_var (str, optional): Name of the latitude variable. Defaults to TRACK_LAT_VAR.

    Returns:
        xarray.Dataset: Trimmed dataset.
    """
    return ds.isel(
        {
            along_track_dim: slice(
                *get_frame_along_track(
                    ds, along_track_dim=along_track_dim, lat_var=lat_var
                )
            )
        }
    )
