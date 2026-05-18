from typing import Final

from ....info.type import FileType
from ..._typing import _VarTransformer
from .. import ProductDefaults, register
from ._edit_attrs import _edit_attrs

_NAMES: Final[dict[str, tuple[str, str]]] = {
    "synergetic_target_classification": (
        "Synergetic target classification (HiRes)",
        "AC-TC (HiRes)",
    ),
    "synergetic_target_classification_medium_resolution": (
        "Synergetic target classification (MedRes)",
        "AC-TC (MedRes)",
    ),
    "synergetic_target_classification_low_resolution": (
        "Synergetic target classification (LowRes)",
        "AC-TC (LowRes)",
    ),
    "ATLID_target_classification": ("ATLID target classification (HiRes)", "A-TC (HiRes)"),
    "ATLID_target_classification_low_resolution": (
        "ATLID target classification (MedRes)",
        "A-TC (MedRes)",
    ),
    "ATLID_target_classification_medium_resolution": (
        "ATLID target classification (LowRes)",
        "A-TC (LowRes)",
    ),
    "CPR_target_classification": (
        "CPR target classification",
        "C-TC",
    ),
}


def _get_transformer(var: str) -> _VarTransformer:
    names = _NAMES[var]
    return _edit_attrs({"long_name": names[0], "short_name": names[1]})


def _get_transforms_dict() -> dict[str, _VarTransformer]:
    return {v: _get_transformer(v) for v in _NAMES.keys()}


register(
    file_type=FileType.AC__TC__2B.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        height_var="height",
        elevation_var="elevation",
        tropopause_var="tropopause_height",
        land_flag_var="land_flag",
        geoid_offset_var="geoid_offset",
        temperature_var="temperature",
        pressure_var="pressure",
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
