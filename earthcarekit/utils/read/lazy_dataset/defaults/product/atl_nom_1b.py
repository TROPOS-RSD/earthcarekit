from typing import Any, Literal, TypeAlias

import numpy as np
from numpy.typing import NDArray

from .....rolling_mean import rolling_mean_2d
from .....stats import nan_mean
from ....product.file_info.type import FileType
from ..._lazy_variable import LazyVariable
from ..._typing import _LazyDataset
from .. import ProductDefaults, register

Formula: TypeAlias = Literal["x/c", "(c+x)/r", "(c+x+r)/r"]


def _validate_formula(formula: Any) -> Formula:
    formula = formula.lower()
    if formula not in ["x/c", "(c+x)/r", "(c+x+r)/r"]:
        raise ValueError(f"invalid formula '{formula}', expected 'x/c', '(c+x)/r' or '(c+x+r)/r'")
    return formula


def _get_long_name(
    formula: Formula,
) -> str:
    formula = _validate_formula(formula)

    if formula == "x/c":
        return "Depol. ratio from cross- and co-polar atten. part. bsc."
    elif formula == "(c+x)/r":
        return "Total part. to ray. atten. bsc. ratio"
    return "Total to ray. atten. bsc. ratio"


def _get_ratio_var(
    formula: Formula,
) -> str:
    formula = _validate_formula(formula)

    if formula == "x/c":
        return "depol_ratio"
    elif formula == "(c+x)/r":
        return "particle_to_rayleigh_ratio"
    elif formula == "(c+x+r)/r":
        return "total_to_rayleigh_ratio"


def _calculate_scattering_ratio(
    cpol: NDArray,
    xpol: NDArray,
    ray: NDArray,
    elevation: NDArray,
    height: NDArray,
    formula: Formula,
    rolling_w: int = 20,
    near_zero_tolerance: float = 2e-7,
    smooth: bool = True,
    mask_near_zero: bool = True,
    skip_height_above_elevation: int = 300,
) -> tuple[NDArray, NDArray, NDArray, NDArray, NDArray]:
    formula = _validate_formula(formula)

    def _calc(c, x, r):
        if formula == "x/c":
            return x / np.where(c == 0, np.nan, c)
        elif formula == "(c+x)/r":
            return (c + x) / np.where(r == 0, np.nan, r)
        return (c + x + r) / np.where(r == 0, np.nan, r)

    def _get_near_zero_mask(c, x, r):
        if formula == "x/c":
            return np.isclose(c, 0, atol=near_zero_tolerance)
        elif formula == "(c+x)/r":
            return np.isclose(r, 0, atol=near_zero_tolerance)
        return np.isclose(r, 0, atol=near_zero_tolerance)

    elevation = elevation[:, np.newaxis] + skip_height_above_elevation
    mask_surface = height < elevation

    cpol[mask_surface] = np.nan
    xpol[mask_surface] = np.nan
    ray[mask_surface] = np.nan

    if smooth:
        cpol = rolling_mean_2d(cpol, rolling_w, axis=0)
        xpol = rolling_mean_2d(xpol, rolling_w, axis=0)
        ray = rolling_mean_2d(ray, rolling_w, axis=0)

    if mask_near_zero:
        near_zero_mask = _get_near_zero_mask(cpol, xpol, ray)
        cpol[near_zero_mask] = np.nan
        xpol[near_zero_mask] = np.nan
        ray[near_zero_mask] = np.nan

    ratio = _calc(cpol, xpol, ray)

    ratio_mean = _calc(nan_mean(cpol, axis=0), nan_mean(xpol, axis=0), nan_mean(ray, axis=0))

    return ratio, ratio_mean, cpol, xpol, ray


def _calc_depol_ratio(
    lds: _LazyDataset[LazyVariable],
) -> tuple[LazyVariable, *tuple[LazyVariable, ...]]:
    rolling_w: int = 20
    near_zero_tolerance: float = 2e-7
    skip_height_above_elevation: int = 300
    cpol_lvar = lds["mie_attenuated_backscatter"]
    formula: Formula = "x/c"
    ratio, ratio_means, cpol, xpol, ray = _calculate_scattering_ratio(
        cpol=cpol_lvar.values,
        xpol=lds["crosspolar_attenuated_backscatter"].values,
        ray=lds["rayleigh_attenuated_backscatter"].values,
        elevation=lds["surface_elevation"].values,
        height=lds["sample_altitude"].values,
        formula=formula,
        rolling_w=rolling_w,
        near_zero_tolerance=near_zero_tolerance,
        skip_height_above_elevation=skip_height_above_elevation,
    )

    attr_cleaned_info = {
        "earthcarekit": f"Added by earthcarekit: Rolling mean applied (w={rolling_w}), near-zero values removed (tol={near_zero_tolerance}), and first {skip_height_above_elevation}m above elevation height set to NaN"
    }

    return (
        LazyVariable(
            varname="depol_ratio",
            dims=cpol_lvar.dims,
            attrs={
                "long_name": _get_long_name(formula),
                "units": "",
                "earthcarekit": "Calculated from cleaned co- and cross-polar attenuated backscatter signals",
            },
            values=ratio,
            _dataset=lds,
        ),
        LazyVariable(
            varname="depol_ratio_from_means",
            dims=("vertical",),
            attrs={
                "long_name": _get_long_name(formula),
                "units": "",
                "earthcarekit": "Added by earthcarekit: Scattering ratio profile calculated from the mean profiles",
            },
            values=ratio_means,
            _dataset=lds,
        ),
        LazyVariable(
            varname="cpol_cleaned_for_ratio_calculation",
            dims=cpol_lvar.dims,
            attrs={
                "long_name": "Co-polar atten. part. bsc.",
                "units": "m$^{-1}$ sr$^{-1}$",
                **attr_cleaned_info,
            },
            values=cpol,
            _dataset=lds,
        ),
        LazyVariable(
            varname="xpol_cleaned_for_ratio_calculation",
            dims=cpol_lvar.dims,
            attrs={
                "long_name": "Cross-polar atten. part. bsc.",
                "units": "m$^{-1}$ sr$^{-1}$",
                **attr_cleaned_info,
            },
            values=xpol,
            _dataset=lds,
        ),
        LazyVariable(
            varname="ray_cleaned_for_ratio_calculation",
            dims=cpol_lvar.dims,
            attrs={
                "long_name": "Ray. atten. bsc.",
                "units": "m$^{-1}$ sr$^{-1}$",
                **attr_cleaned_info,
            },
            values=ray,
            _dataset=lds,
        ),
    )


def _calc_particle_to_rayleigh_ratio(
    lds: _LazyDataset[LazyVariable],
) -> tuple[LazyVariable, *tuple[LazyVariable, ...]]:
    rolling_w: int = 20
    near_zero_tolerance: float = 2e-7
    skip_height_above_elevation: int = 300
    cpol_lvar = lds["mie_attenuated_backscatter"]
    formula: Formula = "(c+x)/r"
    ratio, ratio_means, cpol, xpol, ray = _calculate_scattering_ratio(
        cpol=cpol_lvar.values,
        xpol=lds["crosspolar_attenuated_backscatter"].values,
        ray=lds["rayleigh_attenuated_backscatter"].values,
        elevation=lds["surface_elevation"].values,
        height=lds["sample_altitude"].values,
        formula=formula,
        rolling_w=rolling_w,
        near_zero_tolerance=near_zero_tolerance,
        skip_height_above_elevation=skip_height_above_elevation,
    )

    attr_cleaned_info = {
        "earthcarekit": f"Added by earthcarekit: Rolling mean applied (w={rolling_w}), near-zero values removed (tol={near_zero_tolerance}), and first {skip_height_above_elevation}m above elevation height set to NaN"
    }

    return (
        LazyVariable(
            varname="particle_to_rayleigh_ratio",
            dims=cpol_lvar.dims,
            attrs={
                "long_name": _get_long_name(formula),
                "units": "",
                "earthcarekit": "Calculated from cleaned co- and cross-polar attenuated backscatter signals",
            },
            values=ratio,
            _dataset=lds,
        ),
        LazyVariable(
            varname="particle_to_rayleigh_ratio_from_means",
            dims=("vertical",),
            attrs={
                "long_name": _get_long_name(formula),
                "units": "",
                "earthcarekit": "Added by earthcarekit: Scattering ratio profile calculated from the mean profiles",
            },
            values=ratio_means,
            _dataset=lds,
        ),
        LazyVariable(
            varname="cpol_cleaned_for_particle_to_rayleigh_ratio",
            dims=cpol_lvar.dims,
            attrs={
                "long_name": "Co-polar atten. part. bsc.",
                "units": "m$^{-1}$ sr$^{-1}$",
                **attr_cleaned_info,
            },
            values=cpol,
            _dataset=lds,
        ),
        LazyVariable(
            varname="xpol_cleaned_for_particle_to_rayleigh_ratio",
            dims=cpol_lvar.dims,
            attrs={
                "long_name": "Cross-polar atten. part. bsc.",
                "units": "m$^{-1}$ sr$^{-1}$",
                **attr_cleaned_info,
            },
            values=xpol,
            _dataset=lds,
        ),
        LazyVariable(
            varname="ray_cleaned_for_particle_to_rayleigh_ratio",
            dims=cpol_lvar.dims,
            attrs={
                "long_name": "Ray. atten. bsc.",
                "units": "m$^{-1}$ sr$^{-1}$",
                **attr_cleaned_info,
            },
            values=ray,
            _dataset=lds,
        ),
    )


def _calc_total_to_rayleigh_ratio(
    lds: _LazyDataset[LazyVariable],
) -> tuple[LazyVariable, *tuple[LazyVariable, ...]]:
    rolling_w: int = 20
    near_zero_tolerance: float = 2e-7
    skip_height_above_elevation: int = 300
    cpol_lvar = lds["mie_attenuated_backscatter"]
    formula: Formula = "(c+x+r)/r"
    ratio, ratio_means, cpol, xpol, ray = _calculate_scattering_ratio(
        cpol=cpol_lvar.values,
        xpol=lds["crosspolar_attenuated_backscatter"].values,
        ray=lds["rayleigh_attenuated_backscatter"].values,
        elevation=lds["surface_elevation"].values,
        height=lds["sample_altitude"].values,
        formula=formula,
        rolling_w=rolling_w,
        near_zero_tolerance=near_zero_tolerance,
        skip_height_above_elevation=skip_height_above_elevation,
    )

    attr_cleaned_info = {
        "earthcarekit": f"Added by earthcarekit: Rolling mean applied (w={rolling_w}), near-zero values removed (tol={near_zero_tolerance}), and first {skip_height_above_elevation}m above elevation height set to NaN"
    }

    return (
        LazyVariable(
            varname="total_to_rayleigh_ratio",
            dims=cpol_lvar.dims,
            attrs={
                "long_name": _get_long_name(formula),
                "units": "",
                "earthcarekit": "Calculated from cleaned co- and cross-polar attenuated backscatter signals",
            },
            values=ratio,
            _dataset=lds,
        ),
        LazyVariable(
            varname="total_to_rayleigh_ratio_from_means",
            dims=("vertical",),
            attrs={
                "long_name": _get_long_name(formula),
                "units": "",
                "earthcarekit": "Added by earthcarekit: Scattering ratio profile calculated from the mean profiles",
            },
            values=ratio_means,
            _dataset=lds,
        ),
        LazyVariable(
            varname="cpol_cleaned_for_total_to_rayleigh_ratio",
            dims=cpol_lvar.dims,
            attrs={
                "long_name": "Co-polar atten. part. bsc.",
                "units": "m$^{-1}$ sr$^{-1}$",
                **attr_cleaned_info,
            },
            values=cpol,
            _dataset=lds,
        ),
        LazyVariable(
            varname="xpol_cleaned_for_total_to_rayleigh_ratio",
            dims=cpol_lvar.dims,
            attrs={
                "long_name": "Cross-polar atten. part. bsc.",
                "units": "m$^{-1}$ sr$^{-1}$",
                **attr_cleaned_info,
            },
            values=xpol,
            _dataset=lds,
        ),
        LazyVariable(
            varname="ray_cleaned_for_total_to_rayleigh_ratio",
            dims=cpol_lvar.dims,
            attrs={
                "long_name": "Ray. atten. bsc.",
                "units": "m$^{-1}$ sr$^{-1}$",
                **attr_cleaned_info,
            },
            values=ray,
            _dataset=lds,
        ),
    )


def _shift_time(
    lds: _LazyDataset[LazyVariable], lvar: LazyVariable
) -> tuple[LazyVariable, *tuple[LazyVariable]]:
    lvar_original = lvar.copy()
    lvar_original.varname = "original_time"
    lvar_original.attrs["earthcarekit"] = (
        "Added by earthcarekit: A copy of the original time variable."
    )
    lvar.values = lvar.values + np.timedelta64(-2989554432, "ns")
    lvar.attrs["earthcarekit"] = (
        'Modified by earthcarekit: Since ATLID is angled backwards a time shift of around 3 seconds (here deltatime=-2989554432 ns) is applied to facilitate plotting with L2 products. The original time is stored in the variable "original_time".'
    )

    return (lvar, lvar_original)


register(
    file_type=FileType.ATL_NOM_1B.value,
    defaults=ProductDefaults(
        lat_var="ellipsoid_latitude",
        lon_var="ellipsoid_longitude",
        time_var="time",
        height_var="sample_altitude",
        elevation_var="surface_elevation",
        temperature_var="layer_temperature",
        land_flag_var="land_flag",
        geoid_offset_var="geoid_offset",
        generators={
            "depol_ratio": _calc_depol_ratio,
        },
        optional_generators={
            "particle_to_rayleigh_ratio": _calc_particle_to_rayleigh_ratio,
            "total_to_rayleigh_ratio": _calc_total_to_rayleigh_ratio,
        },
        transforms={"time": _shift_time},
        height_vars={
            "sample_altitude",
            "sensor_altitude",
            "surface_elevation",
        },
    ),
)
