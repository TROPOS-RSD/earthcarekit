from .....constants import EXT_LABEL
from ....info.type import FileType
from ..._typing import _VarTransformer
from .. import ProductDefaults, register
from ._edit_attrs import _edit_attrs


def _get_transforms_dict() -> dict[str, _VarTransformer]:
    return {
        "ice_water_content": _edit_attrs(
            {"long_name": "Ice water content", "units": "kg m$^{-3}$"}
        ),
        "ice_effective_radius": _edit_attrs({"long_name": "Ice effective radius"}),
        "rain_water_content": _edit_attrs(
            {"long_name": "Rain water content", "units": "kg m$^{-3}$"}
        ),
        "rain_median_volume_diameter": _edit_attrs({"long_name": "Rain median volume diameter"}),
        "liquid_water_content": _edit_attrs(
            {"long_name": "Liquid water content", "units": "kg m$^{-3}$"}
        ),
        "liquid_effective_radius": _edit_attrs({"long_name": "Liquid effective radius"}),
        "aerosol_extinction": _edit_attrs({"long_name": EXT_LABEL, "units": "m$^{-1}$"}),
    }


register(
    file_type=FileType.ACM_CAP_2B.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        height_var="height",
        elevation_var="elevation",
        tropopause_var="tropopause_height",
        land_flag_var="land_flag",
        geoid_offset_var="geoid_offset",
        generators={},
        optional_generators={},
        transforms={**_get_transforms_dict()},
        height_vars={
            "height",
            "elevation",
            "tropopause_height",
        },
    ),
)
