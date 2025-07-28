import xarray as xr

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
)
from ....swath_data.across_track_distance import (
    add_across_track_distance,
    add_nadir_track,
    get_nadir_index,
)
from ....xarray_utils import merge_datasets
from .._rename_dataset_content import rename_common_dims_and_vars, rename_var_info
from ..file_info import FileAgency
from ..header_group import add_header_and_meta_data
from ..science_group import read_science_data


def read_product_amacd(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
) -> xr.Dataset:
    """Opens AM__ACD_2B file as a `xarray.Dataset`."""
    ds = read_science_data(filepath, agency=FileAgency.ESA)

    if not modify:
        return ds

    nadir_idx = get_nadir_index(ds, nadir_idx=150)

    ds = ds.rename({"latitude": "swath_latitude"})
    ds = ds.rename({"longitude": "swath_longitude"})
    ds = add_nadir_track(
        ds,
        nadir_idx,
        swath_lat_var="swath_latitude",
        swath_lon_var="swath_longitude",
        along_track_dim="along_track",
        across_track_dim="across_track",
        nadir_lat_var="latitude",
        nadir_lon_var="longitude",
    )
    ds = add_across_track_distance(
        ds, nadir_idx, swath_lat_var="swath_latitude", swath_lon_var="swath_longitude"
    )

    ds = rename_common_dims_and_vars(
        ds,
        along_track_dim="along_track",
        across_track_dim="across_track",
        track_lat_var="latitude",
        track_lon_var="longitude",
        swath_lat_var="swath_latitude",
        swath_lon_var="swath_longitude",
        time_var="time",
    )

    ds = ds.assign(
        aerosol_optical_thickness_spectral_355=ds[
            "aerosol_optical_thickness_spectral"
        ].isel({"aerosol_optical_thickness_dimension": 0}),
        aerosol_optical_thickness_spectral_670=ds[
            "aerosol_optical_thickness_spectral"
        ].isel({"aerosol_optical_thickness_dimension": 1}),
        aerosol_optical_thickness_spectral_865=ds[
            "aerosol_optical_thickness_spectral"
        ].isel({"aerosol_optical_thickness_dimension": 2}),
        aerosol_type_quality_1=ds["aerosol_type_quality"].isel(
            {"quality_indicator_dimension": 0}
        ),
        aerosol_type_quality_2=ds["aerosol_type_quality"].isel(
            {"quality_indicator_dimension": 1}
        ),
        aerosol_type_quality_3=ds["aerosol_type_quality"].isel(
            {"quality_indicator_dimension": 2}
        ),
        aerosol_angstrom_exponent_355_670=ds["aerosol_angstrom_exponent"].isel(
            {"angstrom_dimension": 0}
        ),
        aerosol_angstrom_exponent_670_865=ds["aerosol_angstrom_exponent"].isel(
            {"angstrom_dimension": 1}
        ),
    )

    ds = rename_var_info(
        ds,
        "aerosol_optical_thickness_spectral_355",
        long_name="AOT at 355 nm (AM-ACD)",
        units="",
    )
    ds = rename_var_info(
        ds,
        "aerosol_optical_thickness_spectral_670",
        long_name="AOT at 670 nm (M-AOT)",
        units="",
    )
    ds = rename_var_info(
        ds,
        "aerosol_optical_thickness_spectral_865",
        long_name="AOT at 865 nm (M-AOT)",
        units="",
    )
    ds = rename_var_info(
        ds,
        "quality_status",
        long_name="Quality status",
        units="",
    )
    ds = rename_var_info(
        ds,
        "aerosol_angstrom_exponent_355_670",
        long_name="Ångström exponent (355/670)",
        units="",
    )
    ds = rename_var_info(
        ds,
        "aerosol_angstrom_exponent_355_670",
        long_name="Ångström exponent (355/670)",
        units="",
    )

    ds = add_header_and_meta_data(filepath=filepath, ds=ds, header=header, meta=meta)

    return ds
