from ....product.file_info.type import FileType
from ..._typing import _VarTransformer
from .. import ProductDefaults, register
from ._edit_attrs import _edit_attrs


def _get_renamers() -> dict[str, _VarTransformer]:
    return {
        "reflectivity_no_attenuation_correction": _edit_attrs(
            {"long_name": "Atten. reflectivity factor"}
        ),
        "reflectivity_masked": _edit_attrs({"long_name": "Reflectivity masked"}),
        "reflectivity_corrected": _edit_attrs(
            {"long_name": "Reflectivity corrected", "units": "dBz"}
        ),
        "path_integrated_attenuation": _edit_attrs({"long_name": "PIA"}),
        "brightness_temperature": _edit_attrs({"long_name": "BT at 94 GHz"}),
        "detection_status": _edit_attrs({"long_name": "Detection status"}),
    }


register(
    file_type=FileType.CPR_FMR_2A.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        height_var="height",
        elevation_var="surface_elevation",
        generators={},
        optional_generators={},
        transforms=_get_renamers(),
        height_vars={"height", "surface_elevation"},
    ),
)
