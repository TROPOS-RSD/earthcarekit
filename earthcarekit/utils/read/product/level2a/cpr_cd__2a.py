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


def read_product_ccd(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
) -> xr.Dataset:
    """Opens CPR_CD__2A file as a `xarray.Dataset`."""
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
        land_flag_var="land_flag",
    )

    ds = rename_var_info(
        ds=ds,
        var="doppler_velocity_uncorrected",
        long_name="Uncorrected doppler velocity",
    )
    ds = rename_var_info(
        ds=ds,
        var="doppler_velocity_corrected_for_mispointing",
        long_name="Doppler velocity corrected for mispointing",
    )
    ds = rename_var_info(
        ds=ds,
        var="doppler_velocity_corrected_for_nubf",
        long_name="Doppler velocity corrected for non-uniform beam filling",
    )
    ds = rename_var_info(
        ds=ds,
        var="doppler_velocity_integrated",
        long_name="Integrated doppler velocity",
    )
    ds = rename_var_info(
        ds=ds,
        var="doppler_velocity_integrated_error",
        long_name="Integrated doppler velocity error",
    )
    ds = rename_var_info(
        ds=ds,
        var="doppler_velocity_best_estimate",
        long_name="Doppler velocity best est.",
    )

    ds = rename_var_info(
        ds=ds,
        var="sedimentation_velocity_best_estimate",
        long_name="Sedimentation velocity best est.",
    )
    ds = rename_var_info(
        ds=ds,
        var="sedimentation_velocity_best_estimate_error",
        long_name="Sedimentation velocity best est. error",
    )
    ds = rename_var_info(
        ds=ds,
        var="spectrum_width_integrated",
        long_name="Integrated spectrum width",
    )
    ds = rename_var_info(
        ds=ds,
        var="spectrum_width_uncorrected",
        long_name="Uncorrected spectrum width",
    )

    for v in ds.variables:
        if hasattr(ds[v], "units"):
            if ds[v].units == "m s-1":
                ds[v] = ds[v].assign_attrs(units="m/s")

    ds = add_header_and_meta_data(filepath=filepath, ds=ds, header=header, meta=meta)

    return ds
