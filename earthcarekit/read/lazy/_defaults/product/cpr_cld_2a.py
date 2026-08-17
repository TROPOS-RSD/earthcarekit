from ....info.type import FileType
from ..._typing import _VarTransformer
from .. import ProductDefaults, register
from ._edit_attrs import _edit_attrs


def _get_renamers() -> dict[str, _VarTransformer]:
    return {
        "water_content": _edit_attrs({"label": "Water content", "units": "kg m$^{-3}$"}),
        "characteristic_diameter": _edit_attrs({"label": "Characteristic diameter", "units": "m"}),
        "maximum_dimension_L": _edit_attrs(
            {"label": "Max. size of ice/snow particle", "units": "m"}
        ),
        "liquid_water_content": _edit_attrs(
            {"label": "Liquid water content", "units": "kg m$^{-3}$"}
        ),
        "liquid_effective_radius": _edit_attrs({"label": "Liquid effective radius", "units": "m"}),
        "ice_water_path": _edit_attrs({"label": "Ice water path", "units": "kg m$^{-2}$"}),
        "rain_water_path": _edit_attrs({"label": "Rain water path", "units": "kg m$^{-2}$"}),
        "liquid_water_path": _edit_attrs({"label": "Liquid water path", "units": "kg m$^{-2}$"}),
    }


register(
    file_type=FileType.CPR_CLD_2A.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        height_var="height",
        elevation_var="surface_elevation",
        land_flag_var="land_flag",
        generators={},
        optional_generators={},
        transforms={**_get_renamers()},
        height_vars={
            "height",
            "surface_elevation",
        },
    ),
)
