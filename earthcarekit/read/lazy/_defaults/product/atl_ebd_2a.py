from ....info.type import FileType
from ..._typing import _LazyDataset, _VarTransformer
from ..._variable import LazyVariable
from .. import ProductDefaults, register
from . import _apro
from ._edit_attrs import _edit_attrs


def _get_transformer(var: str) -> _VarTransformer:
    return _edit_attrs({"long_name": _apro.LONG_NAMES_WITH_RESOLUTION[var]})


def _get_transforms_dict() -> dict[str, _VarTransformer]:
    resolutions: tuple[str, ...] = ("", "_medium_resolution", "_low_resolution")

    vars: list[str] = []
    for res in resolutions:
        vars.extend(
            [
                f"particle_backscatter_coefficient_355nm{res}",
                f"particle_extinction_coefficient_355nm{res}",
                f"lidar_ratio_355nm{res}",
                f"particle_linear_depol_ratio_355nm{res}",
            ]
        )

    return {v: _get_transformer(v) for v in vars}


def _rename_mie_tot_bsc_attrs(
    lds: _LazyDataset[LazyVariable], lvar: LazyVariable
) -> tuple[LazyVariable]:
    lvar.attrs["long_name"] = "Total atten. part. bsc."
    lvar.attrs["units"] = "m$^{-1}$ sr$^{-1}$"

    return (lvar,)


register(
    file_type=FileType.ATL_EBD_2A.value,
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
            **_get_transforms_dict(),
            "mie_total_attenuated_backscatter_355nm": _rename_mie_tot_bsc_attrs,
        },
        height_vars={
            "height",
            "elevation",
            "tropopause_height",
        },
    ),
)
