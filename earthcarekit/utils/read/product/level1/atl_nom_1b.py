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
    VERTICAL_DIM,
)
from ....rolling_mean import rolling_mean_2d
from ....statistics import nan_mean
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
    ds_anom: xr.Dataset,
    rolling_w: int = 20,
    near_zero_tolerance: float = 2e-7,
    smooth: bool = True,
    skip_height_above_elevation: int = 300,
    depol_ratio_var: str = "depol_ratio",
    cpol_cleaned_var: str = "cpol_cleaned_for_depol_calculation",
    xpol_cleaned_var: str = "xpol_cleaned_for_depol_calculation",
    depol_ratio_from_means_var: str = "depol_ratio_from_means",
    cpol_var: str = "mie_attenuated_backscatter",
    xpol_var: str = "crosspolar_attenuated_backscatter",
    elevation_var: str = ELEVATION_VAR,
    height_var: str = HEIGHT_VAR,
    height_dim: str = VERTICAL_DIM,
) -> xr.Dataset:
    """
    Compute depolarization ratio (`DPOL` = `XPOL`/`CPOL`) from attenuated backscatter signals.

    This function derives the depolarization ratio from cross-polarized (`XPOL`) and
    co-polarized (`CPOL`) attenuated backscatter signals. Signals below the surface
    are masked, by default with a vertical margin on 300 meters above elevation to remove
    potencial surface retrun. Also, signals are smoothed (or "cleaned") with a rolling mean,
    and near-zero divisions are suppressed. Cleaned `CPOL` and `XPOL` signals are stored alongside `DPOL`,
    and a secondary single depol. profile calculated from mean profiles is added (i.e., mean(`XPOL`)/mean(`CPOL`)).

    Args:
        ds_anom (xr.Dataset): ATL_NOM_1B dataset containing cross- and co-polar attenuated backscatter.
        rolling_w (int, optional): Window size for rolling mean smoothing. Defaults to 20.
        near_zero_tolerance (float, optional): Tolerance for masking near-zero `CPOL` (i.e., denominators). Defaults to 2e-7.
        smooth (bool, optional): Whether to apply rolling mean smoothing. Defaults to True.
        skip_height_above_elevation (int, optional): Vertical margin above surface elevation to mask in meters. Defaults to 300.
        depol_ratio_var (str, optional): Name for depol. ratio variable. Defaults to "depol_ratio".
        cpol_cleaned_var (str, optional): Name for cleaned co-polar variable. Defaults to "cpol_cleaned_for_depol_calculation".
        xpol_cleaned_var (str, optional): Name for cleaned cross-polar variable. Defaults to "xpol_cleaned_for_depol_calculation".
        depol_ratio_from_means_var (str, optional): Name for ratio from mean profiles. Defaults to "depol_ratio_from_means".
        cpol_var (str, optional): Input co-polar variable name. Defaults to "mie_attenuated_backscatter".
        xpol_var (str, optional): Input cross-polar variable name. Defaults to "crosspolar_attenuated_backscatter".
        elevation_var (str, optional): Elevation variable name. Defaults to ELEVATION_VAR.
        height_var (str, optional): Height variable name. Defaults to HEIGHT_VAR.
        height_dim (str, optional): Height dimension name. Defaults to VERTICAL_DIM.

    Returns:
        xr.Dataset: Dataset with added depol. ratio, cleaned `CPOL`/`XPOL` signals,
            and depol. ratio from mean profiles.
    """
    cpol_da = ds_anom[cpol_var].copy()
    xpol_da = ds_anom[xpol_var].copy()
    ds_anom[depol_ratio_var] = xpol_da / cpol_da
    rename_var_info(
        ds_anom,
        depol_ratio_var,
        name=depol_ratio_var,
        long_name="Depol. ratio from cross- and co-polar atten. part. bsc.",
        units="",
    )

    elevation = (
        ds_anom[elevation_var].values.copy()[:, np.newaxis]
        + skip_height_above_elevation
    )
    mask_surface = ds_anom[height_var].values[0].copy() < elevation

    xpol = ds_anom[xpol_var].values
    cpol = ds_anom[cpol_var].values
    xpol[mask_surface] = np.nan
    cpol[mask_surface] = np.nan
    if smooth:
        xpol = rolling_mean_2d(xpol, rolling_w, axis=0)
        cpol = rolling_mean_2d(cpol, rolling_w, axis=0)
        near_zero_mask = np.isclose(cpol, 0, atol=near_zero_tolerance)
        ds_anom[depol_ratio_var].values = xpol / cpol
        ds_anom[depol_ratio_var].values[near_zero_mask] = np.nan
    else:
        ds_anom[depol_ratio_var].values = xpol / cpol

    xpol[near_zero_mask] = np.nan
    cpol[near_zero_mask] = np.nan

    ds_anom[cpol_cleaned_var] = ds_anom[cpol_var].copy()
    ds_anom[cpol_cleaned_var].values = cpol

    ds_anom[xpol_cleaned_var] = ds_anom[xpol_var].copy()
    ds_anom[xpol_cleaned_var].values = xpol

    dpol_mean = nan_mean(xpol, axis=0) / nan_mean(cpol, axis=0)
    ds_anom[depol_ratio_from_means_var] = xr.DataArray(
        data=dpol_mean,
        dims=[height_dim],
        attrs=dict(
            long_name="Depol. ratio from cross- and co-polar atten. part. bsc.",
            units="",
        ),
    )

    return ds_anom


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
