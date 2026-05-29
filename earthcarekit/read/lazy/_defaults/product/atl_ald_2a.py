from ....info.type import FileType
from ..._typing import _LazyDataset, _VarTransformer
from ..._variable import LazyVariable
from .. import ProductDefaults, register


def _split_layers(
    lds: _LazyDataset[LazyVariable], lvar: LazyVariable
) -> tuple[LazyVariable, *tuple[LazyVariable, ...]]:
    out: list[LazyVariable] = []
    n_layers = lvar.values.shape[1]
    for i in range(n_layers):
        _lvar = lvar.copy()
        _lvar.varname = f"{lvar.varname}{i + 1}"
        _lvar.values = _lvar.values[:, i]
        _lvar.dims = ("along_track",)
        out.append(_lvar)

    return (lvar, *out)


def _get_split_layer_transforms() -> dict[str, _VarTransformer]:
    vars = [
        "aerosol_layer_top",
        "aerosol_layer_base",
        "aerosol_layer_confidence",
        "aerosol_layer_base_confidence",
        "aerosol_layer_top_confidence",
        "aerosol_layer_optical_thickness_355nm",
        "aerosol_layer_optical_thickness_355nm_error",
        "aerosol_layer_mean_extinction_355nm",
        "aerosol_layer_mean_extinction_355nm_error",
        "aerosol_layer_mean_backscatter_355nm",
        "aerosol_layer_mean_backscatter_355nm_error",
        "aerosol_layer_mean_lidar_ratio_355nm",
        "aerosol_layer_mean_lidar_ratio_355nm_error",
        "aerosol_layer_mean_depolarisation_355nm",
        "aerosol_layer_mean_depolarisation_355nm_error",
    ]

    return {v: _split_layers for v in vars}


register(
    file_type=FileType.ATL_ALD_2A.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        geoid_offset_var="geoid_offset",
        generators={},
        optional_generators={},
        transforms={**_get_split_layer_transforms()},
        height_vars={
            "aerosol_layer_top",
            "aerosol_layer_base",
            "tropopause_height_calipso",
            "tropopause_height_wmo",
        },
    ),
)
