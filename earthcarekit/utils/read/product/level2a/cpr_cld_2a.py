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


def read_product_ccld(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
    **kwargs,
) -> xr.Dataset:
    """Opens CPR_CLD_2A file as a `xarray.Dataset`."""
    ds = read_science_data(
        filepath,
        agency=FileAgency.ESA,
        **kwargs,
    )

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
        ds=ds,
        var="water_content",
        long_name="Water content",
        units="kg m$^{-3}$",
    )
    ds = rename_var_info(
        ds=ds,
        var="characteristic_diameter",
        long_name="Characteristic diameter",
        units="m",
    )
    ds = rename_var_info(
        ds=ds,
        var="maximum_dimension_L",
        long_name="Max. size of ice/snow particle",
        units="m",
    )
    ds = rename_var_info(
        ds=ds,
        var="liquid_water_content",
        long_name="Liquid water content",
        units="kg m$^{-3}$",
    )
    ds = rename_var_info(
        ds=ds,
        var="liquid_effective_radius",
        long_name="Liquid effective radius",
        units="m",
    )

    ds = rename_var_info(
        ds=ds,
        var="ice_water_path",
        long_name="Ice water path",
        units="kg m$^{-2}$",
    )
    ds = rename_var_info(
        ds=ds,
        var="rain_water_path",
        long_name="Rain water path",
        units="kg m$^{-2}$",
    )
    ds = rename_var_info(
        ds=ds,
        var="liquid_water_path",
        long_name="Liquid water path",
        units="kg m$^{-2}$",
    )

    ds = add_header_and_meta_data(filepath=filepath, ds=ds, header=header, meta=meta)

    return ds
