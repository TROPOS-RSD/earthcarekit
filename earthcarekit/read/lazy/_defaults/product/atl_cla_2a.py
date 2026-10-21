from .....constants import BSC_LABEL, EXT_LABEL, LR_LABEL
from ....info.type import FileType
from ..._typing import _VarTransformer
from .. import ProductDefaults, register
from ._edit_attrs import _edit_attrs
from ._transform_depol import get_depol_tranformers


def _get_transforms() -> dict[str, _VarTransformer]:
    return {
        "aerosol_backscatter_10km": _edit_attrs(
            {
                "label": f"Aer. {BSC_LABEL.lower()} (10km)",
                "units": "m$^{-1}$ sr$^{-1}$",
            }
        ),
        "aerosol_extinction_10km": _edit_attrs(
            {
                "label": f"Aer. {EXT_LABEL.lower()} (10km)",
                "units": "m$^{-1}$",
            }
        ),
        "aerosol_lidar_ratio_10km": _edit_attrs(
            {
                "label": f"Aer. {LR_LABEL.lower()} (10km)",
                "units": "sr",
            }
        ),
        "attenuated_backscatter_10km": _edit_attrs(
            {
                "label": "Tot. atten. bsc. (10km)",
                "units": "m$^{-1}$ sr$^{-1}$",
            }
        ),
        "attenuated_backscatter_1km": _edit_attrs(
            {
                "label": "Tot. atten. bsc. (1km)",
                "units": "m$^{-1}$ sr$^{-1}$",
            }
        ),
        "cloud_backscatter_10km": _edit_attrs(
            {
                "label": f"Cloud {BSC_LABEL.lower()} (10km)",
                "units": "m$^{-1}$ sr$^{-1}$",
            }
        ),
        "cloud_backscatter_1km": _edit_attrs(
            {
                "label": f"Cloud {BSC_LABEL.lower()} (1km)",
                "units": "m$^{-1}$ sr$^{-1}$",
            }
        ),
        "cloud_extinction_10km": _edit_attrs(
            {
                "label": f"Cloud {EXT_LABEL.lower()} (10km)",
                "units": "m$^{-1}$",
            }
        ),
        "cloud_extinction_1km": _edit_attrs(
            {
                "label": f"Cloud {EXT_LABEL.lower()} (1km)",
                "units": "m$^{-1}$",
            }
        ),
        "cloud_lidar_ratio_10km": _edit_attrs(
            {
                "label": f"Cloud {LR_LABEL.lower()} (10km)",
                "units": "sr",
            }
        ),
        "cloud_lidar_ratio_1km": _edit_attrs(
            {
                "label": f"Cloud {LR_LABEL.lower()} (1km)",
                "units": "sr",
            }
        ),
        "crosspolar_attenuated_backscatter_10km": _edit_attrs(
            {
                "label": "Cross-polar atten. bsc. (10km)",
                "units": "m$^{-1}$ sr$^{-1}$",
            }
        ),
        "crosspolar_attenuated_backscatter_1km": _edit_attrs(
            {
                "label": "Cross-polar atten. bsc. (1km)",
                "units": "m$^{-1}$ sr$^{-1}$",
            }
        ),
    }


register(
    file_type=FileType.ATL_CLA_2A.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        height_var="height",
        elevation_var="surface_elevation",
        land_flag_var="land_water_flag",
        generators={},
        optional_generators={},
        transforms={
            **get_depol_tranformers(
                "aerosol_depolarization_10km",
                "cloud_depolarization_1km",
                "cloud_depolarization_10km",
                "volume_depolarization_ratio_10km",
                "volume_depolarization_ratio_1km",
            ),
            **_get_transforms(),
        },
        height_vars={
            "height",
            "surface_elevation",
            "PBL_height_10km",
        },
    ),
)
