from ....info.type import FileType
from ..._typing import _VarTransformer
from .. import ProductDefaults, register
from . import _apro
from ._edit_attrs import _edit_attrs


def _get_transformer(var: str) -> _VarTransformer:
    return _edit_attrs({"long_name": _apro.LONG_NAMES[var]})


def _get_transforms_dict() -> dict[str, _VarTransformer]:
    vars: list[str] = [
        "particle_backscatter_coefficient_355nm",
        "particle_extinction_coefficient_355nm",
        "lidar_ratio_355nm",
        "particle_linear_depol_ratio_355nm",
    ]

    return {v: _get_transformer(v) for v in vars}


register(
    file_type=FileType.ATL_AER_2A.value,
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
