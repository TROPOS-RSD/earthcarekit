import numpy as np
from numpy.typing import NDArray

from ....info.type import FileType
from ..._typing import _LazyDataset
from ..._variable import LazyVariable
from .. import ProductDefaults, register


def _get_potential_temperature(t: NDArray, p: NDArray) -> NDArray:
    p0 = 100_000.0  # [Pa]
    rcp = 0.286
    return t * np.pow(p0 / p, rcp)


def _generate_pot_temp_k(
    lds: _LazyDataset[LazyVariable],
) -> tuple[LazyVariable, LazyVariable]:
    lvar_t = lds["temperature_kelvin"]
    p = lds["pressure"].values

    values = _get_potential_temperature(lvar_t.values, p)

    attrs_kelvin = {
        "long_name": "Potential temperature",
        "units": "K",
    }

    attrs_celsius = {
        "long_name": "Potential temperature",
        "units": r"$^{\circ}$C",
    }

    return (
        LazyVariable(
            varname="potential_temperature_kelvin",
            dims=lvar_t.dims,
            attrs=attrs_kelvin,
            values=values,
            _dataset=lds,
        ),
        LazyVariable(
            varname="potential_temperature_celsius",
            dims=lvar_t.dims,
            attrs=attrs_celsius,
            values=values - 273.15,
            _dataset=lds,
        ),
    )


def _generate_pot_temp_c(
    lds: _LazyDataset[LazyVariable],
) -> tuple[LazyVariable, LazyVariable]:
    lvar_k, lvar_c = _generate_pot_temp_c(lds)
    return (lvar_c, lvar_k)


register(
    file_type=FileType.AUX_MET_1D.value,
    defaults=ProductDefaults(
        tropopause_var="tropopause_height_calipso",
        temperature_var="temperature",
        generators={
            "potential_temperature_kelvin": _generate_pot_temp_k,
            "potential_temperature_celsius": _generate_pot_temp_c,
        },
        optional_generators={},
        transforms={},
        height_vars={
            "height",
            "elevation",
            "tropopause_height",
        },
    ),
)
