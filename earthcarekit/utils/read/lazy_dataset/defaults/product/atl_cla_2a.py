from ....product.file_info.type import FileType
from ..._lazy_variable import LazyVariable
from ..._typing import NonEmptyTuple, _LazyDataset, _VarTransformer
from .. import ProductDefaults, register


def _get_depol_transformer(var: str) -> _VarTransformer:

    def tranformer(
        lds: _LazyDataset[LazyVariable], lvar: LazyVariable
    ) -> NonEmptyTuple[LazyVariable]:
        lvar.values *= 0.01
        lvar.attrs["units"] = ""
        lvar.attrs["valid_range"] = "[0, 1]"
        lvar.attrs["earthcarekit"] = (
            "Modified by earthcarekit: Converted from percantage to decimal"
        )
        return (lvar,)

    return tranformer


def _get_tranforms() -> dict[str, _VarTransformer]:
    vars = ("aerosol_depolarization_10km", "cloud_depolarization_1km", "cloud_depolarization_10km")
    return {v: _get_depol_transformer(v) for v in vars}


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
        transforms=_get_tranforms(),
        height_vars={
            "height",
            "surface_elevation",
        },
    ),
)
