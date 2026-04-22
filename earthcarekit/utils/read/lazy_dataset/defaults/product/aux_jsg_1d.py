import numpy as np
from numpy.typing import NDArray

from ....product.file_info.type import FileType
from ..._lazy_variable import LazyVariable
from ..._typing import _LazyDataset
from .. import ProductDefaults, register
from ._msi import (
    _generate_across_track_distance,
    _generate_from_track_distance,
    _tranform_swath_latitude,
    _tranform_swath_longitude,
)


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
    file_type=FileType.AUX_JSG_1D.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        height_var="altitude",
        land_flag_var="land_flag",
        elevation_var="surface_elevation",
        geoid_offset_var="geoid_offset",
        sensor_elevation_angle_var="sensor_elevation_angle",
        time_var="time",
        generators={
            "across_track_distance": _generate_across_track_distance,
            "from_track_distance": _generate_from_track_distance,
        },
        optional_generators={},
        transforms={
            "latitude": _tranform_swath_latitude,
            "longitude": _tranform_swath_longitude,
        },
        height_vars={
            "altitude",
            "surface_elevation",
            "sensor_altitude",
        },
        time_vars={
            "radar_profile_time",
            "lidar_profile_time",
        },
    ),
)
