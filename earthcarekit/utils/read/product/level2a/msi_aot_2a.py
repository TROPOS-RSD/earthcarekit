import numpy as np
import xarray as xr

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
    SWATH_LAT_VAR,
    SWATH_LON_VAR,
    UNITS_KELVIN,
    UNITS_MSI_RADIANCE,
)
from ....swath_data.across_track_distance import (
    add_across_track_distance,
    add_nadir_track,
    drop_samples_with_missing_geo_data_along_track,
    get_nadir_index,
)
from ....xarray_utils import merge_datasets
from .._rename_dataset_content import rename_common_dims_and_vars, rename_var_info
from ..file_info import FileAgency
from ..science_group import read_science_data
from .msi_cm__2a import _get_bitmasks, _get_dominant_classes


def add_quality_mask_plot_var(
    ds: xr.Dataset,
    var: str = "quality_mask",
    n: int = 10,
):
    """Adds a plottable variable for the M-CM "quality_mask" to the given dataset, called "plot_quality_mask"."""
    new_values = _get_dominant_classes(ds, var=var, n=n)

    new_var = f"plot_{var}"
    ds[new_var] = ds[var].copy()
    ds[new_var].values = new_values
    ds[new_var] = ds[new_var].assign_attrs(
        {
            "long_name": "Quality mask",
            "definition": "0: Undefined, 1: suspicious_input_flag, 2: water_flag, 3: land_flag, 4: cloud_edge_flag, 5: cloud_flag, 6: algorithm_converged_flag, 7: homogeneity_flag, 8: suspicious_angstrom_flag, 9: missing_lines_before_flag, 10 :unexpectedly_bright_surface_flag",
            "units": "",
            "earthcarekit": "Added by earthcarekit: class integers converted from bitwise",
        }
    )

    return ds


def read_product_maot(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
    ensure_nans: bool = DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    **kwargs,
) -> xr.Dataset:
    """Opens MSI_AOT_2A file as a `xarray.Dataset`."""
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

    nadir_idx = get_nadir_index(ds, nadir_idx=266)
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
        ds,
        along_track_dim="along_track",
        across_track_dim="across_track",
        track_lat_var="latitude",
        track_lon_var="longitude",
        swath_lat_var=SWATH_LAT_VAR,
        swath_lon_var=SWATH_LON_VAR,
        time_var="time",
    )

    ds = rename_var_info(
        ds,
        "aerosol_optical_thickness_670nm",
        long_name="AOT at 670nm",
        units="",
    )
    ds = rename_var_info(
        ds,
        "aerosol_optical_thickness_865nm",
        long_name="AOT at 865nm",
        units="",
    )

    ds = rename_var_info(
        ds,
        "aerosol_optical_thickness_670nm_error",
        long_name="AOT error at 670nm",
        units="",
    )
    ds = rename_var_info(
        ds,
        "aerosol_optical_thickness_865nm_error",
        long_name="AOT error at 865nm",
        units="",
    )

    ds = rename_var_info(
        ds,
        "angstrom_parameter_670nm_865nm",
        long_name="$\mathrm{\AA}_{670/865}$",
        units="",
    )
    ds = rename_var_info(
        ds,
        "angstrom_parameter_355nm_670nm",
        long_name="$\mathrm{\AA}_{355/670}$",
        units="",
    )

    ds = add_quality_mask_plot_var(ds)

    return ds
