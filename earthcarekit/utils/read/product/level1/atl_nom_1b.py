import warnings
from typing import Literal

import numpy as np
import xarray as xr
from scipy.interpolate import griddata  # type: ignore

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
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
from ..science_group import read_science_data


def get_depol_profile(
    ds: xr.Dataset,
    cpol_cleaned_var: str = "cpol_cleaned_for_depol_calculation",
    xpol_cleaned_var: str = "xpol_cleaned_for_depol_calculation",
):
    cpol = ds[cpol_cleaned_var].data
    xpol = ds[xpol_cleaned_var].data
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        mean_xpol_bsc = np.nanmean(xpol, axis=0)
        mean_mie_bsc = np.nanmean(cpol, axis=0)
    return mean_xpol_bsc / mean_mie_bsc


def add_scattering_ratio(
    ds_anom: xr.Dataset,
    formula: Literal["x/c", "(c+x)/r", "(c+x+r)/r"],
    rolling_w: int = 20,
    near_zero_tolerance: float = 2e-7,
    smooth: bool = True,
    skip_height_above_elevation: int = 300,
    cpol_var: str = "mie_attenuated_backscatter",
    xpol_var: str = "crosspolar_attenuated_backscatter",
    ray_var: str = "rayleigh_attenuated_backscatter",
    elevation_var: str = ELEVATION_VAR,
    height_var: str = HEIGHT_VAR,
    height_dim: str = VERTICAL_DIM,
) -> xr.Dataset:
    """
    Compute scattering ratio from attenuated backscatter signals given a formula: "x/c", "(c+x)/r", or "(c+x+r)/r".

    This function derives the scattering ratio from cross-polarized (`XPOL`), co-polarized (`CPOL`) and rayleigh (`RAY`) attenuated backscatter signals.
    Signals below the surface are masked, by default with a vertical margin on 300 meters above elevation to remove potential surface return.
    Also, signals are smoothed (or "cleaned") with a rolling mean, and near-zero divisions are suppressed and set to NaN instead.
    In the resulting dataset, the ratio curtain and a ratio profile calculated from mean profiles of the full dataset (e.g., mean(`XPOL`)/mean(`CPOL`)).

    Args:
        ds_anom (xr.Dataset): ATL_NOM_1B dataset containing the attenuated backscatter signals.
        formula (Literal["x/c", "(c+x)/r", "(c+x+r)/r"]): Formula used to calculate the scattering ratio.
        rolling_w (int, optional): Window size for rolling mean smoothing. Defaults to 20.
        near_zero_tolerance (float, optional): Tolerance for masking near-zero denominators. Defaults to 2e-7.
        smooth (bool, optional): Whether to apply rolling mean smoothing. Defaults to True.
        skip_height_above_elevation (int, optional): Vertical margin above surface elevation to mask in meters. Defaults to 300.
        cpol_var (str, optional): Input co-polar variable name. Defaults to "mie_attenuated_backscatter".
        xpol_var (str, optional): Input cross-polar variable name. Defaults to "crosspolar_attenuated_backscatter".
        ray_var (str, optional): Input rayleigh variable name. Defaults to "rayleigh_attenuated_backscatter".
        elevation_var (str, optional): Elevation variable name. Defaults to ELEVATION_VAR.
        height_var (str, optional): Height variable name. Defaults to HEIGHT_VAR.
        height_dim (str, optional): Height dimension name. Defaults to VERTICAL_DIM.

    Returns:
        xr.Dataset: xr.Dataset: Dataset with added ratio curtain and ratio profile from mean profiles.
    """

    if formula.lower() not in ["x/c", "(c+x)/r", "(c+x+r)/r"]:
        raise ValueError(
            f"invalid formula '{formula}', expected 'x/c', '(c+x)/r' or '(c+x+r)/r'"
        )

    # cpol_cleaned_var: str = "cpol_cleaned_for_ratio_calculation"
    # xpol_cleaned_var: str = "xpol_cleaned_for_ratio_calculation"
    # ray_cleaned_var: str = "ray_cleaned_for_ratio_calculation"

    cpol_da = ds_anom[cpol_var].copy()
    xpol_da = ds_anom[xpol_var].copy()
    if formula == "x/c":
        ray_da = xpol_da
    else:
        ray_da = ds_anom[ray_var].copy()

    def _calc(c, x, r):
        if formula == "x/c":
            return x / c
        elif formula == "(c+x)/r":
            return (c + x) / r
        elif formula == "(c+x+r)/r":
            return (c + x + r) / r

    def _get_near_zero_mask(c, x, r):
        if formula == "x/c":
            return np.isclose(c, 0, atol=near_zero_tolerance)
        elif formula == "(c+x)/r":
            return np.isclose(r, 0, atol=near_zero_tolerance)
        elif formula == "(c+x+r)/r":
            return np.isclose(r, 0, atol=near_zero_tolerance)

    def _get_long_name():
        if formula == "x/c":
            return "Depol. ratio from cross- and co-polar atten. part. bsc."
        elif formula == "(c+x)/r":
            return "Total part. to ray. atten. bsc. ratio"
        elif formula == "(c+x+r)/r":
            return "Total to ray. atten. bsc. ratio"

    def _get_ratio_var():
        if formula == "x/c":
            return "depol_ratio"
        elif formula == "(c+x)/r":
            return "cpol_xpol_to_ray_ratio"
        elif formula == "(c+x+r)/r":
            return "cpol_xpol_ray_to_ray_ratio"

    ratio_var = _get_ratio_var()
    ratio_from_means_var = f"{ratio_var}_from_means"

    ds_anom[ratio_var] = _calc(cpol_da, xpol_da, ray_da)
    rename_var_info(
        ds_anom,
        ratio_var,
        name=ratio_var,
        long_name=_get_long_name(),
        units="",
    )

    elevation = (
        ds_anom[elevation_var].data.copy()[:, np.newaxis] + skip_height_above_elevation
    )
    mask_surface = ds_anom[height_var].data[0].copy() < elevation

    cpol = ds_anom[cpol_var].data
    xpol = ds_anom[xpol_var].data
    if formula == "x/c":
        ray = xpol
    else:
        ray = ds_anom[ray_var].data

    cpol[mask_surface] = np.nan
    xpol[mask_surface] = np.nan
    ray[mask_surface] = np.nan

    if smooth:
        cpol = rolling_mean_2d(cpol, rolling_w, axis=0)
        xpol = rolling_mean_2d(xpol, rolling_w, axis=0)
        ray = rolling_mean_2d(ray, rolling_w, axis=0)

    ds_anom[ratio_var].data = _calc(cpol, xpol, ray)

    if smooth:
        near_zero_mask = _get_near_zero_mask(cpol, xpol, ray)
        ds_anom[ratio_var].data[near_zero_mask] = np.nan
        cpol[near_zero_mask] = np.nan
        xpol[near_zero_mask] = np.nan
        ray[near_zero_mask] = np.nan

    # ds_anom[xpol_cleaned_var] = ds_anom[xpol_var].copy()
    # ds_anom[xpol_cleaned_var].data = xpol

    # ds_anom[cpol_cleaned_var] = ds_anom[cpol_var].copy()
    # ds_anom[cpol_cleaned_var].data = cpol

    # if formula == "x/c":
    #     ds_anom[ray_cleaned_var] = ds_anom[ray_var].copy()
    #     ds_anom[ray_cleaned_var].data = ray

    ratio_mean = _calc(
        nan_mean(cpol, axis=0),
        nan_mean(xpol, axis=0),
        nan_mean(ray, axis=0),
    )

    ds_anom[ratio_from_means_var] = xr.DataArray(
        data=ratio_mean,
        dims=[height_dim],
        attrs=dict(
            long_name=_get_long_name(),
            units="",
        ),
    )

    return ds_anom


def add_depol_ratio(
    ds_anom: xr.Dataset,
    rolling_w: int = 20,
    near_zero_tolerance: float = 2e-7,
    smooth: bool = True,
    skip_height_above_elevation: int = 300,
    cpol_var: str = "mie_attenuated_backscatter",
    xpol_var: str = "crosspolar_attenuated_backscatter",
    elevation_var: str = ELEVATION_VAR,
    height_var: str = HEIGHT_VAR,
    height_dim: str = VERTICAL_DIM,
) -> xr.Dataset:
    """
    Compute depolarization ratio (`DPOL` = `XPOL`/`CPOL`) from attenuated backscatter signals.

    This function derives the depol. ratio from cross-polarized (`XPOL`) and co-polarized (`CPOL`) attenuated backscatter signals.
    Signals below the surface are masked, by default with a vertical margin on 300 meters above elevation to remove potential surface return.
    Also, signals are smoothed (or "cleaned") with a rolling mean, and near-zero divisions are suppressed and set to NaN instead.
    In the resulting dataset, the ratio curtain and a ratio profile calculated from mean profiles of the full dataset (e.g., mean(`XPOL`)/mean(`CPOL`)).

    Args:
        ds_anom (xr.Dataset): ATL_NOM_1B dataset containing cross- and co-polar attenuated backscatter.
        rolling_w (int, optional): Window size for rolling mean smoothing. Defaults to 20.
        near_zero_tolerance (float, optional): Tolerance for masking near-zero `CPOL` (i.e., denominators). Defaults to 2e-7.
        smooth (bool, optional): Whether to apply rolling mean smoothing. Defaults to True.
        skip_height_above_elevation (int, optional): Vertical margin above surface elevation to mask in meters. Defaults to 300.
        cpol_var (str, optional): Input co-polar variable name. Defaults to "mie_attenuated_backscatter".
        xpol_var (str, optional): Input cross-polar variable name. Defaults to "crosspolar_attenuated_backscatter".
        elevation_var (str, optional): Elevation variable name. Defaults to ELEVATION_VAR.
        height_var (str, optional): Height variable name. Defaults to HEIGHT_VAR.
        height_dim (str, optional): Height dimension name. Defaults to VERTICAL_DIM.

    Returns:
        xr.Dataset: Dataset with added depol. ratio, cleaned signals, and depol. ratio profile from mean profiles.
    """
    return add_scattering_ratio(
        ds_anom=ds_anom,
        formula="x/c",
        rolling_w=rolling_w,
        near_zero_tolerance=near_zero_tolerance,
        smooth=smooth,
        skip_height_above_elevation=skip_height_above_elevation,
        cpol_var=cpol_var,
        xpol_var=xpol_var,
        elevation_var=elevation_var,
        height_var=height_var,
        height_dim=height_dim,
    )


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

    # Since ATLID is angled backwards a time shift of nearly 3 seconds is created which is corrected here to
    ds["original_time"] = ds["time"].copy()
    ds["time"].data = ds["time"].data + np.timedelta64(-2989554432, "ns")

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
