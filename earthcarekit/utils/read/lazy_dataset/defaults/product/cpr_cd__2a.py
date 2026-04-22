from ....product.file_info.type import FileType
from ..._typing import _VarTransformer
from .. import ProductDefaults, register
from ._edit_attrs import _edit_attrs


def _get_renamers() -> dict[str, _VarTransformer]:
    return {
        "doppler_velocity_uncorrected": _edit_attrs({"long_name": "Uncorrected doppler velocity"}),
        "doppler_velocity_corrected_for_mispointing": _edit_attrs(
            {"long_name": "Doppler velocity corrected for mispointing"}
        ),
        "doppler_velocity_corrected_for_nubf": _edit_attrs(
            {"long_name": "Doppler velocity corrected for non-uniform beam filling"}
        ),
        "doppler_velocity_integrated": _edit_attrs({"long_name": "Integrated doppler velocity"}),
        "doppler_velocity_integrated_error": _edit_attrs(
            {"long_name": "Integrated doppler velocity error"}
        ),
        "doppler_velocity_best_estimate": _edit_attrs({"long_name": "Doppler velocity best est."}),
        "sedimentation_velocity_best_estimate": _edit_attrs(
            {"long_name": "Sedimentation velocity best est."}
        ),
        "sedimentation_velocity_best_estimate_error": _edit_attrs(
            {"long_name": "Sedimentation velocity best est. error"}
        ),
        "spectrum_width_integrated": _edit_attrs({"long_name": "Integrated spectrum width"}),
        "spectrum_width_uncorrected": _edit_attrs({"long_name": "Uncorrected spectrum width"}),
    }


register(
    file_type=FileType.CPR_CD__2A.value,
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
        height_vars={"height", "surface_elevation"},
    ),
)
