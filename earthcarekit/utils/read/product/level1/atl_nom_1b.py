import warnings

import numpy as np
import xarray as xr
from scipy.interpolate import griddata  # type: ignore

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
    ELEVATION_VAR,
    HEIGHT_VAR,
)
from ....rolling_mean import rolling_mean_2d
from ....xarray_utils import filter_time, merge_datasets
from .._rename_dataset_content import rename_common_dims_and_vars, rename_var_info
from ..file_info import FileAgency
from ..header_group import add_header_and_meta_data
from ..science_group import read_science_data


def get_depol_profile(
    ds: xr.Dataset,
    cpol_cleaned_var: str = "cpol_cleaned_for_depol_calculation",
    xpol_cleaned_var: str = "xpol_cleaned_for_depol_calculation",
):
    cpol = ds[cpol_cleaned_var].values
    xpol = ds[xpol_cleaned_var].values
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        mean_xpol_bsc = np.nanmean(xpol, axis=0)
        mean_mie_bsc = np.nanmean(cpol, axis=0)
    return mean_xpol_bsc / mean_mie_bsc


def add_depol_ratio(
    ds: xr.Dataset,
    rolling_w: int = 20,
    near_zero_tolerance: float = 2e-7,
    smooth: bool = True,
    skip_height_above_elevation: int = 3,
    depol_ratio_var: str = "depol_ratio",
    cpol_cleaned_var: str = "cpol_cleaned_for_depol_calculation",
    xpol_cleaned_var: str = "xpol_cleaned_for_depol_calculation",
    cpol_var: str = "mie_attenuated_backscatter",
    xpol_var: str = "crosspolar_attenuated_backscatter",
    elevation_var: str = ELEVATION_VAR,
    height_var: str = HEIGHT_VAR,
) -> xr.Dataset:
    cpol_da = ds[cpol_var].copy()
    xpol_da = ds[xpol_var].copy()
    ds[depol_ratio_var] = xpol_da / cpol_da
    rename_var_info(
        ds,
        depol_ratio_var,
        name=depol_ratio_var,
        long_name="Depol. ratio from cross- and co-polar atten. part. bsc.",
        units="",
    )

    elevation = (
        ds[elevation_var].values.copy()[:, np.newaxis] + skip_height_above_elevation
    )
    mask_surface = ds[height_var].values[0].copy() < elevation

    xpol = ds[xpol_var].values
    cpol = ds[cpol_var].values
    xpol[mask_surface] = np.nan
    cpol[mask_surface] = np.nan
    if smooth:
        xpol = rolling_mean_2d(xpol, rolling_w, axis=0)
        cpol = rolling_mean_2d(cpol, rolling_w, axis=0)
        near_zero_mask = np.isclose(cpol, 0, atol=near_zero_tolerance)
        ds[depol_ratio_var].values = xpol / cpol
        ds[depol_ratio_var].values[near_zero_mask] = np.nan
    else:
        ds[depol_ratio_var].values = xpol / cpol

    ds[cpol_cleaned_var] = ds[cpol_var].copy()
    ds[cpol_cleaned_var].values = cpol

    ds[xpol_cleaned_var] = ds[xpol_var].copy()
    ds[xpol_cleaned_var].values = xpol

    return ds


def read_product_anom(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
) -> xr.Dataset:
    """Opens ATL_NOM_1B file as a `xarray.Dataset`."""
    ds = read_science_data(filepath, agency=FileAgency.ESA)

    if not modify:
        return ds

    # Since ATLID is angled backwards a time shift of nearly 3 seconds is created which is corrected here to
    ds["original_time"] = ds["time"].copy()
    ds["time"].values = ds["time"].values + np.timedelta64(-2989554432, "ns")

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

    ds = add_header_and_meta_data(filepath=filepath, ds=ds, header=header, meta=meta)

    return ds
