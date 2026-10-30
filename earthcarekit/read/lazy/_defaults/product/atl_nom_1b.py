import numpy as np

from .....scatt_ratio import RatioType, calc_scatt_ratio
from ....info.type import FileType
from ..._typing import _LazyDataset
from ..._variable import LazyVariable
from .. import ProductDefaults, register
from ._edit_attrs import _edit_attrs


def _gen_pdr_vars(
    lds: _LazyDataset[LazyVariable],
) -> tuple[LazyVariable, *tuple[LazyVariable, ...]]:
    rolling_w: int = 20
    near_zero_tolerance: float = 2e-7
    skip_height_above_elevation: int = 300
    cpol_lvar = lds["mie_attenuated_backscatter"]
    res = calc_scatt_ratio(
        ratio_type=RatioType.PDR,
        cpol=cpol_lvar.values,
        xpol=lds["crosspolar_attenuated_backscatter"].values,
        ray=lds["rayleigh_attenuated_backscatter"].values,
        elevation=lds["surface_elevation"].values,
        height=lds["sample_altitude"].values,
        rolling_w=rolling_w,
        tol=near_zero_tolerance,
        elevation_margin=skip_height_above_elevation,
    )
    ratio_type = res.ratio_type
    ratio = res.ratio
    ratio_mean = res.ratio_mean
    cpol = res.cleaned["cpol"]
    xpol = res.cleaned["xpol"]
    ray = res.cleaned["ray"]

    attr_cleaned_info = {
        "earthcarekit": f"Added by earthcarekit: Rolling mean applied (w={rolling_w}), near-zero values removed (tol={near_zero_tolerance}), and first {skip_height_above_elevation}m above elevation height set to NaN"
    }

    return (
        LazyVariable(
            varname=ratio_type.var_name,
            dims=cpol_lvar.dims,
            attrs=ratio_type.attrs,
            values=ratio,
            _dataset=lds,
        ),
        LazyVariable(
            varname=f"{ratio_type.var_name}_from_means",
            dims=("vertical",),
            attrs=ratio_type.attrs,
            values=ratio_mean,
            _dataset=lds,
        ),
        LazyVariable(
            varname="cpol_cleaned_for_ratio_calculation",
            dims=cpol_lvar.dims,
            attrs={
                "label": "Co-polar atten. part. bsc.",
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
                "label": "Cross-polar atten. part. bsc.",
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
                "label": "Ray. atten. bsc.",
                "units": "m$^{-1}$ sr$^{-1}$",
                **attr_cleaned_info,
            },
            values=ray,
            _dataset=lds,
        ),
    )


def _gen_bsr_m1_vars(
    lds: _LazyDataset[LazyVariable],
) -> tuple[LazyVariable, *tuple[LazyVariable, ...]]:
    rolling_w: int = 20
    near_zero_tolerance: float = 2e-7
    skip_height_above_elevation: int = 300
    cpol_lvar = lds["mie_attenuated_backscatter"]
    res = calc_scatt_ratio(
        ratio_type=RatioType.BSR_M1,
        cpol=cpol_lvar.values,
        xpol=lds["crosspolar_attenuated_backscatter"].values,
        ray=lds["rayleigh_attenuated_backscatter"].values,
        elevation=lds["surface_elevation"].values,
        height=lds["sample_altitude"].values,
        rolling_w=rolling_w,
        tol=near_zero_tolerance,
        elevation_margin=skip_height_above_elevation,
    )
    ratio_type = res.ratio_type
    ratio = res.ratio
    ratio_mean = res.ratio_mean
    cpol = res.cleaned["cpol"]
    xpol = res.cleaned["xpol"]
    ray = res.cleaned["ray"]

    attr_cleaned_info = {
        "earthcarekit": f"Added by earthcarekit: Rolling mean applied (w={rolling_w}), near-zero values removed (tol={near_zero_tolerance}), and first {skip_height_above_elevation}m above elevation height set to NaN"
    }

    return (
        LazyVariable(
            varname=ratio_type.var_name,
            dims=cpol_lvar.dims,
            attrs=ratio_type.attrs,
            values=ratio,
            _dataset=lds,
        ),
        LazyVariable(
            varname=f"{ratio_type.var_name}_from_means",
            dims=("vertical",),
            attrs=ratio_type.attrs,
            values=ratio_mean,
            _dataset=lds,
        ),
        LazyVariable(
            varname="cpol_cleaned_for_ratio_calculation",
            dims=cpol_lvar.dims,
            attrs={
                "label": "Co-polar atten. part. bsc.",
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
                "label": "Cross-polar atten. part. bsc.",
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
                "label": "Ray. atten. bsc.",
                "units": "m$^{-1}$ sr$^{-1}$",
                **attr_cleaned_info,
            },
            values=ray,
            _dataset=lds,
        ),
    )


def _gen_bsr_vars(
    lds: _LazyDataset[LazyVariable],
) -> tuple[LazyVariable, *tuple[LazyVariable, ...]]:
    rolling_w: int = 20
    near_zero_tolerance: float = 2e-7
    skip_height_above_elevation: int = 300
    cpol_lvar = lds["mie_attenuated_backscatter"]
    res = calc_scatt_ratio(
        ratio_type=RatioType.BSR,
        cpol=cpol_lvar.values,
        xpol=lds["crosspolar_attenuated_backscatter"].values,
        ray=lds["rayleigh_attenuated_backscatter"].values,
        elevation=lds["surface_elevation"].values,
        height=lds["sample_altitude"].values,
        rolling_w=rolling_w,
        tol=near_zero_tolerance,
        elevation_margin=skip_height_above_elevation,
    )
    ratio_type = res.ratio_type
    ratio = res.ratio
    ratio_mean = res.ratio_mean
    cpol = res.cleaned["cpol"]
    xpol = res.cleaned["xpol"]
    ray = res.cleaned["ray"]

    attr_cleaned_info = {
        "earthcarekit": f"Added by earthcarekit: Rolling mean applied (w={rolling_w}), near-zero values removed (tol={near_zero_tolerance}), and first {skip_height_above_elevation}m above elevation height set to NaN"
    }

    return (
        LazyVariable(
            varname=ratio_type.var_name,
            dims=cpol_lvar.dims,
            attrs=ratio_type.attrs,
            values=ratio,
            _dataset=lds,
        ),
        LazyVariable(
            varname=f"{ratio_type.var_name}_from_means",
            dims=("vertical",),
            attrs=ratio_type.attrs,
            values=ratio_mean,
            _dataset=lds,
        ),
        LazyVariable(
            varname="cpol_cleaned_for_ratio_calculation",
            dims=cpol_lvar.dims,
            attrs={
                "label": "Co-polar atten. part. bsc.",
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
                "label": "Cross-polar atten. part. bsc.",
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
                "label": "Ray. atten. bsc.",
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
            RatioType.PDR.var_name: _gen_pdr_vars,
        },
        optional_generators={
            RatioType.BSR_M1.var_name: _gen_bsr_m1_vars,
            RatioType.BSR.var_name: _gen_bsr_vars,
        },
        transforms={
            "time": _shift_time,
            "mie_attenuated_backscatter": _edit_attrs(
                {
                    "label": "Co-polar atten. part. bsc.",
                    "units": "m$^{-1}$ sr$^{-1}$",
                }
            ),
            "rayleigh_attenuated_backscatter": _edit_attrs(
                {
                    "label": "Ray. atten. bsc.",
                    "units": "m$^{-1}$ sr$^{-1}$",
                }
            ),
            "crosspolar_attenuated_backscatter": _edit_attrs(
                {
                    "label": "Cross-polar atten. part. bsc.",
                    "units": "m$^{-1}$ sr$^{-1}$",
                }
            ),
        },
        height_vars={
            "sample_altitude",
            "sensor_altitude",
            "surface_elevation",
        },
    ),
)
