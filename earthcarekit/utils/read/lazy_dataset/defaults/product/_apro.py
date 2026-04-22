from typing import Final

from .....constants import BSC_LABEL, DEPOL_LABEL, EXT_LABEL, LR_LABEL


def _get_long_name_registry() -> dict[str, str]:
    resolutions: tuple[str, ...] = ("", "_medium_resolution", "_low_resolution")
    long_names: dict[str, str] = {}

    for res in resolutions:
        long_names[f"particle_backscatter_coefficient_355nm{res}"] = BSC_LABEL
        long_names[f"particle_extinction_coefficient_355nm{res}"] = EXT_LABEL
        long_names[f"lidar_ratio_355nm{res}"] = LR_LABEL
        long_names[f"particle_linear_depol_ratio_355nm{res}"] = DEPOL_LABEL
        long_names[f"classification{res}"] = "Target classification"

    return long_names


def _get_long_name_with_resolution_registry() -> dict[str, str]:
    resolutions: tuple[str, ...] = ("", "_medium_resolution", "_low_resolution")
    labels: tuple[str, ...] = ("HiRes", "MedRes", "LowRes")

    long_names: dict[str, str] = {}
    for res, label in zip(resolutions, labels):
        long_names[f"particle_backscatter_coefficient_355nm{res}"] = f"{BSC_LABEL} {label}"
        long_names[f"particle_extinction_coefficient_355nm{res}"] = f"{EXT_LABEL} {label}"
        long_names[f"lidar_ratio_355nm{res}"] = f"{LR_LABEL} {label}"
        long_names[f"particle_linear_depol_ratio_355nm{res}"] = f"{DEPOL_LABEL} {label}"
        long_names[f"classification{res}"] = f"Target classification {label}"

    return long_names


def _get_short_name_with_resolution_registry() -> dict[str, str]:
    resolutions: tuple[str, ...] = ("", "_medium_resolution", "_low_resolution")
    labels: tuple[str, ...] = ("HiRes", "MedRes", "LowRes")

    long_names: dict[str, str] = {}
    for res, label in zip(resolutions, labels):
        long_names[f"particle_backscatter_coefficient_355nm{res}"] = f"{BSC_LABEL} {label}"
        long_names[f"particle_extinction_coefficient_355nm{res}"] = f"{EXT_LABEL} {label}"
        long_names[f"lidar_ratio_355nm{res}"] = f"{LR_LABEL} {label}"
        long_names[f"particle_linear_depol_ratio_355nm{res}"] = f"{DEPOL_LABEL} {label}"
        long_names[f"classification{res}"] = f"A-TC {label}"

    return long_names


LONG_NAMES: Final[dict[str, str]] = _get_long_name_registry()
LONG_NAMES_WITH_RESOLUTION: Final[dict[str, str]] = _get_long_name_with_resolution_registry()
SHORT_NAMES_WITH_RESOLUTION: Final[dict[str, str]] = _get_long_name_with_resolution_registry()
