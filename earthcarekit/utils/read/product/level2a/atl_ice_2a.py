import xarray as xr

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
)
from ....xarray_utils import merge_datasets
from .._rename_dataset_content import (
    BSC_LABEL,
    DEPOL_LABEL,
    ELEVATION_VAR,
    EXT_LABEL,
    LR_LABEL,
    TROPOPAUSE_VAR,
    rename_common_dims_and_vars,
    rename_var_info,
)
from ..file_info import FileAgency
from ..header_group import add_header_and_meta_data
from ..science_group import read_science_data


def read_product_aice(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
) -> xr.Dataset:
    """Opens ATL_ICE_2A file as a `xarray.Dataset`."""
    ds = read_science_data(filepath, agency=FileAgency.ESA)

    if not modify:
        return ds

    ds = rename_common_dims_and_vars(
        ds,
        along_track_dim="along_track",
        vertical_dim="JSG_height",
        track_lat_var="latitude",
        track_lon_var="longitude",
        time_var="time",
        tropopause_var="tropopause_height",
        elevation_var="elevation",
    )

    var = "ice_water_content"
    ds[var].values = ds[var].values * 1e-3
    ds = rename_var_info(
        ds=ds,
        var=var,
        name="IWC",
        long_name="Ice water content",
        units="g/m$^3$",
    )
    var = "ice_water_content_error"
    ds[var].values = ds[var].values * 1e-3
    ds = rename_var_info(
        ds=ds,
        var=var,
        name="IWC error",
        long_name="Ice water content error",
        units="g/m$^3$",
    )
    ds = rename_var_info(
        ds=ds,
        var="ice_effective_radius",
        name="Ice effective radius",
        long_name="Ice effective radius",
        units="$\mu$m",
    )
    ds = rename_var_info(
        ds=ds,
        var="ice_effective_radius_error",
        name="Ice effective radius error",
        long_name="Ice effective radius error",
        units="$\mu$m",
    )

    ds = add_header_and_meta_data(filepath=filepath, ds=ds, header=header, meta=meta)

    return ds
