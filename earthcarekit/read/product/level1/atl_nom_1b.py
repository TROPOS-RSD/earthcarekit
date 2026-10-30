import numpy as np
import xarray as xr

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
)
from ....scatt_ratio import add_depol_ratio
from ...info import FileAgency
from ...science import read_science_data
from .._rename_dataset_content import rename_common_dims_and_vars, rename_var_info


def read_product_anom(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
    ensure_nans: bool = DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    **kwargs,
) -> xr.Dataset:
    """Opens ATL_NOM_1B file as a `xarray.Dataset`."""
    ds = read_science_data(
        filepath,
        agency=FileAgency.ESA,
        ensure_nans=ensure_nans,
        **kwargs,
    )

    if not modify:
        return ds

    ds["original_time"] = ds["time"].copy()
    ds["original_time"] = ds["original_time"].assign_attrs(
        {"earthcarekit": "Added by earthcarekit: A copy of the original time variable."}
    )
    ds["time"].data = ds["time"].data + np.timedelta64(-2989554432, "ns")
    ds["time"] = ds["time"].assign_attrs(
        {
            "earthcarekit": 'Modified by earthcarekit: Since ATLID is angled backwards a time shift of around 3 seconds (here deltatime=-2989554432 ns) is applied to facilitate plotting with L2 products. The original time is stored in the variable "original_time".'
        }
    )

    ds = rename_common_dims_and_vars(
        ds,
        along_track_dim="along_track",
        vertical_dim="height",
        track_lat_var="ellipsoid_latitude",
        track_lon_var="ellipsoid_longitude",
        height_var="sample_altitude",
        time_var="time",
        temperature_var="layer_temperature",
        elevation_var="surface_elevation",
        land_flag_var="land_flag",
    )
    ds = rename_var_info(
        ds,
        "mie_attenuated_backscatter",
        "Co-polar atten. part. bsc.",
        "Co-polar atten. part. bsc.",
        "m$^{-1}$ sr$^{-1}$",
    )
    ds = rename_var_info(
        ds,
        "rayleigh_attenuated_backscatter",
        "Ray. atten. bsc.",
        "Ray. atten. bsc.",
        "m$^{-1}$ sr$^{-1}$",
    )
    ds = rename_var_info(
        ds,
        "crosspolar_attenuated_backscatter",
        "Cross-polar atten. part. bsc.",
        "Cross-polar atten. part. bsc.",
        "m$^{-1}$ sr$^{-1}$",
    )
    ds = add_depol_ratio(ds)

    return ds
