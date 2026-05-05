from ....info.type import FileType
from ..._typing import _LazyDataset, _VarTransformer
from ..._variable import LazyVariable
from .. import ProductDefaults, register
from ._edit_attrs import _edit_attrs


def _transform_iwc(lds: _LazyDataset[LazyVariable], lvar: LazyVariable) -> tuple[LazyVariable]:
    lvar.values = lvar.values * 1e-3
    lvar.attrs["long_name"] = "Ice water content"
    lvar.attrs["short_name"] = "IWC"
    lvar.attrs["units"] = "g/m$^3$"

    return (lvar,)


def _transform_iwc_error(
    lds: _LazyDataset[LazyVariable], lvar: LazyVariable
) -> tuple[LazyVariable]:
    lvar.values = lvar.values * 1e-3
    lvar.attrs["long_name"] = "Ice water content error"
    lvar.attrs["short_name"] = "IWC error"
    lvar.attrs["units"] = "g/m$^3$"

    return (lvar,)


def _get_transforms_dict() -> dict[str, _VarTransformer]:
    return {
        "ice_water_content": _transform_iwc,
        "ice_water_content_error": _transform_iwc_error,
        "ice_effective_radius": _edit_attrs(
            {
                "long_name": "Ice effective radius",
                "units": "$\\mu$m",
            }
        ),
        "ice_effective_radius_error": _edit_attrs(
            {
                "long_name": "Ice effective radius error",
                "units": "$\\mu$m",
            }
        ),
    }


register(
    file_type=FileType.ATL_ICE_2A.value,
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
