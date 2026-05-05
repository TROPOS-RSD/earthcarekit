from .....constants import BSC_LABEL, DEPOL_LABEL, EXT_LABEL, LR_LABEL
from ....info.type import FileType
from ..._typing import NonEmptyTuple, _LazyDataset, _VarTransformer
from ..._variable import LazyVariable
from .. import ProductDefaults, register
from ._edit_attrs import _edit_attrs


def _get_depol_transformer(var: str) -> _VarTransformer:

    def tranformer(
        lds: _LazyDataset[LazyVariable], lvar: LazyVariable
    ) -> NonEmptyTuple[LazyVariable]:
        long_name = DEPOL_LABEL
        if lvar.varname.startswith("10km"):
            long_name = f"Aer. {long_name.lower()}"
        elif lvar.varname.startswith("cloud"):
            long_name = f"Cloud {long_name.lower()}"

        if lvar.varname.endswith("10km"):
            long_name = f"{long_name} (10km)"
        elif lvar.varname.endswith("1km"):
            long_name = f"{long_name} (1km)"

        lvar.values *= 0.01
        lvar.attrs["long_name"] = long_name
        lvar.attrs["units"] = ""
        lvar.attrs["valid_range"] = "[0, 1]"
        lvar.attrs["earthcarekit"] = (
            "Modified by earthcarekit: Converted from percantage to decimal"
        )
        return (lvar,)

    return tranformer


def _get_depol_tranforms() -> dict[str, _VarTransformer]:
    vars = (
        "aerosol_depolarization_10km",
        "cloud_depolarization_1km",
        "cloud_depolarization_10km",
        "volume_depolarization_ratio_10km",
        "volume_depolarization_ratio_1km",
    )
    return {v: _get_depol_transformer(v) for v in vars}


def _get_transforms() -> dict[str, _VarTransformer]:
    return {
        "aerosol_backscatter_10km": _edit_attrs(
            {
                "long_name": f"Aer. {BSC_LABEL.lower()} (10km)",
                "units": "m$^{-1}$ sr$^{-1}$",
            }
        ),
        "aerosol_extinction_10km": _edit_attrs(
            {
                "long_name": f"Aer. {EXT_LABEL.lower()} (10km)",
                "units": "m$^{-1}$",
            }
        ),
        "aerosol_lidar_ratio_10km": _edit_attrs(
            {
                "long_name": f"Aer. {LR_LABEL.lower()} (10km)",
                "units": "sr",
            }
        ),
        "attenuated_backscatter_10km": _edit_attrs(
            {
                "long_name": "Tot. atten. bsc. (10km)",
                "units": "m$^{-1}$ sr$^{-1}$",
            }
        ),
        "attenuated_backscatter_1km": _edit_attrs(
            {
                "long_name": "Tot. atten. bsc. (1km)",
                "units": "m$^{-1}$ sr$^{-1}$",
            }
        ),
        "cloud_backscatter_10km": _edit_attrs(
            {
                "long_name": f"Cloud {BSC_LABEL.lower()} (10km)",
                "units": "m$^{-1}$ sr$^{-1}$",
            }
        ),
        "cloud_backscatter_1km": _edit_attrs(
            {
                "long_name": f"Cloud {BSC_LABEL.lower()} (1km)",
                "units": "m$^{-1}$ sr$^{-1}$",
            }
        ),
        "cloud_extinction_10km": _edit_attrs(
            {
                "long_name": f"Cloud {EXT_LABEL.lower()} (10km)",
                "units": "m$^{-1}$",
            }
        ),
        "cloud_extinction_1km": _edit_attrs(
            {
                "long_name": f"Cloud {EXT_LABEL.lower()} (1km)",
                "units": "m$^{-1}$",
            }
        ),
        "cloud_lidar_ratio_10km": _edit_attrs(
            {
                "long_name": f"Cloud {LR_LABEL.lower()} (10km)",
                "units": "sr",
            }
        ),
        "cloud_lidar_ratio_1km": _edit_attrs(
            {
                "long_name": f"Cloud {LR_LABEL.lower()} (1km)",
                "units": "sr",
            }
        ),
        "crosspolar_attenuated_backscatter_10km": _edit_attrs(
            {
                "long_name": "Cross-polar atten. bsc. (10km)",
                "units": "m$^{-1}$ sr$^{-1}$",
            }
        ),
        "crosspolar_attenuated_backscatter_1km": _edit_attrs(
            {
                "long_name": "Cross-polar atten. bsc. (1km)",
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
            **_get_depol_tranforms(),
            **_get_transforms(),
        },
        height_vars={
            "height",
            "surface_elevation",
            "PBL_height_10km",
        },
    ),
)
