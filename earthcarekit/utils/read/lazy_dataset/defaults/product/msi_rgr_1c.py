from typing import Final

import numpy as np
from numpy.typing import NDArray

from .....constants import UNITLESS, UNITS_KELVIN, UNITS_MSI_RADIANCE, UNITS_SPECTRAL_IRRADIANCE
from ....product.file_info.type import FileType
from ..._lazy_variable import LazyVariable
from ..._typing import _LazyDataset, _VarGenerator
from .. import ProductDefaults, register
from ._msi import (
    _generate_across_track_distance,
    _generate_from_track_distance,
    _tranform_swath_latitude,
    _tranform_swath_longitude,
)

_PIXEL_QUALITY_DEFINITION: Final[str] = (
    "0:PIXEL_OK, 1:PIXEL_DEAD, 2:PIXEL_SATURATED, 3:UNUSED, 4:PIXEL_OTHER_ERROR"
)

_PIXEL_QUALITY_ATTRS: Final[dict[str, str]] = {
    "units": UNITLESS,
    "definition": _PIXEL_QUALITY_DEFINITION,
}

_ATTRS_REGISTRY: Final[dict[str, dict[str, str]]] = {
    "vis": {"long_name": "Radiance at 670 nm", "units": UNITS_MSI_RADIANCE},
    "vis_uncertainty": {"long_name": "Radiance uncertainty at 670 nm", "units": UNITS_MSI_RADIANCE},
    "nir": {"long_name": "Radiance at 865 nm", "units": UNITS_MSI_RADIANCE},
    "nir_uncertainty": {"long_name": "Radiance uncertainty at 865 nm", "units": UNITS_MSI_RADIANCE},
    "swir1": {"long_name": "Radiance at 1650 nm", "units": UNITS_MSI_RADIANCE},
    "swir1_uncertainty": {
        "long_name": "Radiance uncertainty at 1650 nm",
        "units": UNITS_MSI_RADIANCE,
    },
    "swir2": {"long_name": "Radiance at 2210 nm", "units": UNITS_MSI_RADIANCE},
    "swir2_uncertainty": {
        "long_name": "Radiance uncertainty at 2210 nm",
        "units": UNITS_MSI_RADIANCE,
    },
    "tir1": {"long_name": "BT at 8.8 µm", "units": UNITS_KELVIN},
    "tir1_uncertainty": {"long_name": "BT uncertainty at 8.8 µm", "units": UNITS_KELVIN},
    "tir2": {"long_name": "BT at 10.8 µm", "units": UNITS_KELVIN},
    "tir2_uncertainty": {"long_name": "BT uncertainty at 10.8 µm", "units": UNITS_KELVIN},
    "tir3": {"long_name": "BT at 12.0 µm", "units": UNITS_KELVIN},
    "tir3_uncertainty": {"long_name": "BT uncertainty at 12.0 µm", "units": UNITS_KELVIN},
    "vis_line_quality_status": {"long_name": "Line quality (VIS)", "units": UNITLESS},
    "nir_line_quality_status": {"long_name": "Line quality (NIR)", "units": UNITLESS},
    "swir1_line_quality_status": {"long_name": "Line quality (SWIR-1)", "units": UNITLESS},
    "swir2_line_quality_status": {"long_name": "Line quality (SWIR-2)", "units": UNITLESS},
    "tir1_line_quality_status": {"long_name": "Line quality (TIR-1)", "units": UNITLESS},
    "tir2_line_quality_status": {"long_name": "Line quality (TIR-2)", "units": UNITLESS},
    "tir3_line_quality_status": {"long_name": "Line quality (TIR-3)", "units": UNITLESS},
    "vis_pixel_quality_status": {"long_name": "Pixel quality (VIS)", **_PIXEL_QUALITY_ATTRS},
    "nir_pixel_quality_status": {"long_name": "Pixel quality (NIR)", **_PIXEL_QUALITY_ATTRS},
    "swir1_pixel_quality_status": {"long_name": "Pixel quality (SWIR-1)", **_PIXEL_QUALITY_ATTRS},
    "swir2_pixel_quality_status": {"long_name": "Pixel quality (SWIR-2)", **_PIXEL_QUALITY_ATTRS},
    "tir1_pixel_quality_status": {"long_name": "Pixel quality (TIR-1)", **_PIXEL_QUALITY_ATTRS},
    "tir2_pixel_quality_status": {"long_name": "Pixel quality (TIR-2)", **_PIXEL_QUALITY_ATTRS},
    "tir3_pixel_quality_status": {"long_name": "Pixel quality (TIR-3)", **_PIXEL_QUALITY_ATTRS},
    "vis_solar_spectral_irradiance": {
        "long_name": "Spectral irradiance (VIS)",
        "units": UNITS_SPECTRAL_IRRADIANCE,
    },
    "nir_solar_spectral_irradiance": {
        "long_name": "Spectral irradiance (NIR)",
        "units": UNITS_SPECTRAL_IRRADIANCE,
    },
    "swir1_solar_spectral_irradiance": {
        "long_name": "Spectral irradiance (SWIR-1)",
        "units": UNITS_SPECTRAL_IRRADIANCE,
    },
    "swir2_solar_spectral_irradiance": {
        "long_name": "Spectral irradiance (SWIR-2)",
        "units": UNITS_SPECTRAL_IRRADIANCE,
    },
}


def _get_generator(varname: str, var: str, band: int) -> _VarGenerator:

    def generator(lds: _LazyDataset[LazyVariable]) -> tuple[LazyVariable]:
        values = lds[var].values[band]

        dims: tuple[str, ...]
        if var in ("pixel_values", "pixel_values_uncertainty", "pixel_quality_status"):
            dims = ("along_track", "across_track")
        elif var == "line_quality_status":
            dims = ("along_track",)
        else:
            dims = ("across_track",)

        return (
            LazyVariable(
                varname=varname,
                dims=dims,
                attrs=_ATTRS_REGISTRY.get(varname, {}),
                values=values,
                _dataset=lds,
            ),
        )

    return generator


_BAND_SEPARATION_GENERATORS: Final[dict[str, _VarGenerator]] = {
    "vis": _get_generator("vis", "pixel_values", 0),
    "nir": _get_generator("nir", "pixel_values", 1),
    "swir1": _get_generator("swir1", "pixel_values", 2),
    "swir2": _get_generator("swir2", "pixel_values", 3),
    "tir1": _get_generator("tir1", "pixel_values", 4),
    "tir2": _get_generator("tir2", "pixel_values", 5),
    "tir3": _get_generator("tir3", "pixel_values", 6),
    "vis_uncertainty": _get_generator("vis_uncertainty", "pixel_values_uncertainty", 0),
    "nir_uncertainty": _get_generator("nir_uncertainty", "pixel_values_uncertainty", 1),
    "swir1_uncertainty": _get_generator("swir1_uncertainty", "pixel_values_uncertainty", 2),
    "swir2_uncertainty": _get_generator("swir2_uncertainty", "pixel_values_uncertainty", 3),
    "tir1_uncertainty": _get_generator("tir1_uncertainty", "pixel_values_uncertainty", 4),
    "tir2_uncertainty": _get_generator("tir2_uncertainty", "pixel_values_uncertainty", 5),
    "tir3_uncertainty": _get_generator("tir3_uncertainty", "pixel_values_uncertainty", 6),
    "vis_line_quality_status": _get_generator("vis_line_quality_status", "line_quality_status", 0),
    "nir_line_quality_status": _get_generator("nir_line_quality_status", "line_quality_status", 1),
    "swir1_line_quality_status": _get_generator(
        "swir1_line_quality_status", "line_quality_status", 2
    ),
    "swir2_line_quality_status": _get_generator(
        "swir2_line_quality_status", "line_quality_status", 3
    ),
    "tir1_line_quality_status": _get_generator(
        "tir1_line_quality_status", "line_quality_status", 4
    ),
    "tir2_line_quality_status": _get_generator(
        "tir2_line_quality_status", "line_quality_status", 5
    ),
    "tir3_line_quality_status": _get_generator(
        "tir3_line_quality_status", "line_quality_status", 6
    ),
    "vis_pixel_quality_status": _get_generator(
        "vis_pixel_quality_status", "pixel_quality_status", 0
    ),
    "nir_pixel_quality_status": _get_generator(
        "nir_pixel_quality_status", "pixel_quality_status", 1
    ),
    "swir1_pixel_quality_status": _get_generator(
        "swir1_pixel_quality_status", "pixel_quality_status", 2
    ),
    "swir2_pixel_quality_status": _get_generator(
        "swir2_pixel_quality_status", "pixel_quality_status", 3
    ),
    "tir1_pixel_quality_status": _get_generator(
        "tir1_pixel_quality_status", "pixel_quality_status", 4
    ),
    "tir2_pixel_quality_status": _get_generator(
        "tir2_pixel_quality_status", "pixel_quality_status", 5
    ),
    "tir3_pixel_quality_status": _get_generator(
        "tir3_pixel_quality_status", "pixel_quality_status", 6
    ),
    "vis_solar_spectral_irradiance": _get_generator(
        "vis_solar_spectral_irradiance", "solar_spectral_irradiance", 0
    ),
    "nir_solar_spectral_irradiance": _get_generator(
        "nir_solar_spectral_irradiance", "solar_spectral_irradiance", 1
    ),
    "swir1_solar_spectral_irradiance": _get_generator(
        "swir1_solar_spectral_irradiance", "solar_spectral_irradiance", 2
    ),
    "swir2_solar_spectral_irradiance": _get_generator(
        "swir2_solar_spectral_irradiance", "solar_spectral_irradiance", 3
    ),
}


def _calculate_rgb(
    swir1: NDArray,
    nir: NDArray,
    vis: NDArray,
) -> np.ndarray:
    def get_min_max(x: NDArray):
        return np.nanquantile(x, 0.01), np.nanquantile(x, 0.99)

    r_min, r_max = get_min_max(swir1)
    g_min, g_max = get_min_max(nir)
    b_min, b_max = get_min_max(vis)

    r_w, g_w, b_w = [1.0, 1.0, 1.0]
    r_s, g_s, b_s = [1.0, 1.0, 1.0]

    def get_v(x, _w, _s, _min, _max):
        return np.clip(_w * (x - _min) / (_s * (_max - _min)), a_min=0, a_max=1).T

    r_v = get_v(swir1, r_w, r_s, r_min, r_max)
    g_v = get_v(nir, g_w, g_s, g_min, g_max)
    b_v = get_v(vis, b_w, b_s, b_min, b_max)

    rgb = np.stack((r_v, g_v, b_v), axis=2)
    rgb[np.isnan(rgb)] = 0.0

    return rgb


def _generate_rgb(lds: _LazyDataset[LazyVariable]) -> tuple[LazyVariable]:
    return (
        LazyVariable(
            varname="rgb",
            dims=("across_track", "along_track", "rgb_channel"),
            attrs={"long_name": "False RGB", "units": ""},
            values=_calculate_rgb(
                swir1=lds["swir1"].values,
                nir=lds["nir"].values,
                vis=lds["vis"].values,
            ),
            _dataset=lds,
        ),
    )


register(
    file_type=FileType.MSI_RGR_1C.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        elevation_var="surface_elevation",
        sensor_elevation_angle_var="sensor_elevation_angle",
        land_flag_var="land_flag",
        geoid_offset_var="geoid_offset",
        generators={
            **_BAND_SEPARATION_GENERATORS,
            "rgb": _generate_rgb,
            "across_track_distance": _generate_across_track_distance,
            "from_track_distance": _generate_from_track_distance,
        },
        optional_generators={},
        transforms={"latitude": _tranform_swath_latitude, "longitude": _tranform_swath_longitude},
        height_vars={"surface_elevation"},
    ),
)
