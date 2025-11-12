import warnings

import numpy as np
import xarray as xr
from scipy.interpolate import interp1d  # type: ignore
from scipy.spatial import cKDTree  # type: ignore

from ....constants import (
    ALONG_TRACK_DIM,
    DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
    HEIGHT_VAR,
    SWATH_LAT_VAR,
    SWATH_LON_VAR,
    TIME_VAR,
    TRACK_LAT_VAR,
    TRACK_LON_VAR,
    VERTICAL_DIM,
)
from ....geo import sequence_geo_to_ecef
from ....swath_data.across_track_distance import (
    add_across_track_distance,
    add_nadir_track,
    drop_samples_with_missing_geo_data_along_track,
    get_nadir_index,
)
from ....xarray_utils import merge_datasets, remove_dims
from .._rename_dataset_content import (
    rename_and_create_temperature_vars,
    rename_common_dims_and_vars,
)
from ..file_info import FileAgency
from ..science_group import read_science_data


def read_product_xjsg(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
    ensure_nans: bool = DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    **kwargs,
) -> xr.Dataset:
    """Opens AUX_JSG_1D file as a `xarray.Dataset`."""
    ds = read_science_data(
        filepath,
        agency=FileAgency.ESA,
        ensure_nans=ensure_nans,
        **kwargs,
    )

    if not modify:
        return ds

    ds = drop_samples_with_missing_geo_data_along_track(
        ds=ds,
        swath_lat_var="latitude",
        along_track_dim="along_track",
        across_track_dim="across_track",
    )

    nadir_idx = get_nadir_index(ds)

    ds = ds.rename({"latitude": SWATH_LAT_VAR})
    ds = ds.rename({"longitude": SWATH_LON_VAR})
    ds = add_nadir_track(
        ds,
        nadir_idx,
        swath_lat_var=SWATH_LAT_VAR,
        swath_lon_var=SWATH_LON_VAR,
        along_track_dim="along_track",
        across_track_dim="across_track",
        nadir_lat_var="latitude",
        nadir_lon_var="longitude",
    )
    ds = add_across_track_distance(
        ds, nadir_idx, swath_lat_var=SWATH_LAT_VAR, swath_lon_var=SWATH_LON_VAR
    )

    ds = rename_common_dims_and_vars(
        ds=ds,
        track_lat_var="latitude",
        track_lon_var="longitude",
        height_var="altitude",
        land_flag_var="land_flag",
        elevation_var="surface_elevation",
        time_var="time",
        vertical_dim="height",
    )
    import pandas as pd

    ds[TIME_VAR].values = pd.to_datetime(
        ds[TIME_VAR].values, unit="s", origin="2000-01-01 00:00:00"
    ).to_numpy()

    ds = ds.drop_vars(["along_track", "across_track"])

    return ds
