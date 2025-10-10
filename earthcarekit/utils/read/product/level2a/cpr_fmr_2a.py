import xarray as xr

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
)
from ....xarray_utils import merge_datasets
from .._rename_dataset_content import (
    ELEVATION_VAR,
    TROPOPAUSE_VAR,
    rename_common_dims_and_vars,
    rename_var_info,
)
from ..file_info import FileAgency
from ..header_group import add_header_and_meta_data
from ..science_group import read_science_data


def read_product_cfmr(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
) -> xr.Dataset:
    """Opens CPR_FMR_2A file as a `xarray.Dataset`."""
    ds = read_science_data(filepath, agency=FileAgency.ESA)

    if not modify:
        return ds

    ds = rename_common_dims_and_vars(
        ds,
        along_track_dim="along_track",
        vertical_dim="CPR_height",
        track_lat_var="latitude",
        track_lon_var="longitude",
        height_var="height",
        time_var="time",
        elevation_var="surface_elevation",
    )

    ds = rename_var_info(
        ds,
        "reflectivity_no_attenuation_correction",
        long_name="Atten. reflectivity factor",
    )
    ds = rename_var_info(
        ds,
        "reflectivity_masked",
        long_name="Reflectivity masked",
    )
    ds = rename_var_info(
        ds,
        "reflectivity_corrected",
        long_name="Reflectivity corrected",
        units="dBz",
    )
    ds = rename_var_info(
        ds,
        "path_integrated_attenuation",
        long_name="PIA",
    )
    ds = rename_var_info(
        ds,
        "brightness_temperature",
        long_name="BT at 94 GHz",
    )
    ds = rename_var_info(
        ds,
        "detection_status",
        long_name="Detection status",
    )

    ds = add_header_and_meta_data(filepath=filepath, ds=ds, header=header, meta=meta)

    return ds
