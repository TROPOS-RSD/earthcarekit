from ....info.type import FileType
from ..._typing import _VarTransformer
from .. import ProductDefaults, register
from . import _apro
from ._edit_attrs import _edit_attrs


def _get_transformer(var: str) -> _VarTransformer:
    return _edit_attrs({"long_name": _apro.LONG_NAMES_WITH_RESOLUTION[var], "units": ""})


def _get_transforms_dict() -> dict[str, _VarTransformer]:
    resolutions: tuple[str, ...] = ("", "_medium_resolution", "_low_resolution")

    vars: list[str] = [f"classification{res}" for res in resolutions]

    return {v: _get_transformer(v) for v in vars}


register(
    file_type=FileType.ATL_TC__2A.value,
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
        transforms={
            "simple_classification": _edit_attrs(
                {"long_name": "Simple classification", "units": ""}
            ),
            **_get_transforms_dict(),
        },
        height_vars={
            "height",
            "elevation",
            "tropopause_height",
        },
    ),
)
