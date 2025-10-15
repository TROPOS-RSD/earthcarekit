import xarray as xr

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
    EXT_LABEL,
)
from ....swath_data.across_track_distance import (
    add_across_track_distance,
    add_nadir_track,
    add_nadir_var,
    get_nadir_index,
)
from ....xarray_utils import merge_datasets
from .._rename_dataset_content import rename_common_dims_and_vars, rename_var_info
from ..file_info import FileAgency
from ..header_group import add_header_and_meta_data
from ..science_group import read_science_data


def read_product_acmcap(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
    **kwargs,
) -> xr.Dataset:
    """Opens ACM_CAP_2B file as a `xarray.Dataset`."""
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
        vertical_dim="JSG_height",
        track_lat_var="latitude",
        track_lon_var="longitude",
        height_var="height",
        time_var="time",
        elevation_var="elevation",
        tropopause_var="tropopause_height",
    )

    "ice_water_content",
    "ice_effective_radius",
    "rain_water_content",
    "rain_median_volume_diameter",
    "liquid_water_content",
    "liquid_effective_radius",
    "aerosol_extinction",

    ds = rename_var_info(
        ds=ds,
        var="ice_water_content",
        long_name="Ice water content",
        units="kg m$^{-3}$",
    )
    ds = rename_var_info(
        ds=ds,
        var="ice_effective_radius",
        long_name="Ice effective radius",
    )
    ds = rename_var_info(
        ds=ds,
        var="rain_water_content",
        long_name="Rain water content",
        units="kg m$^{-3}$",
    )
    ds = rename_var_info(
        ds=ds,
        var="rain_median_volume_diameter",
        long_name="Rain median volume diameter",
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
    )
    ds = rename_var_info(
        ds=ds,
        var="aerosol_extinction",
        long_name=EXT_LABEL,
        units="m$^{-1}$",
    )

    ds = add_header_and_meta_data(filepath=filepath, ds=ds, header=header, meta=meta)

    return ds
