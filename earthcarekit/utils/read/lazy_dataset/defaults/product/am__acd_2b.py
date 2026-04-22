from typing import Final

from ....product.file_info.type import FileType
from ..._lazy_variable import LazyVariable
from ..._typing import _LazyDataset, _VarGenerator
from .. import ProductDefaults, register
from ._edit_attrs import _edit_attrs
from ._msi import (
    _generate_across_track_distance,
    _generate_from_track_distance,
    _tranform_swath_latitude,
    _tranform_swath_longitude,
)

_ATTRS: Final[dict[str, dict[str, str]]] = {
    "aerosol_optical_thickness_spectral_355": {"long_name": "AOT at 355 nm (AM-ACD)", "units": ""},
    "aerosol_optical_thickness_spectral_670": {"long_name": "AOT at 670 nm (M-AOT)", "units": ""},
    "aerosol_optical_thickness_spectral_865": {"long_name": "AOT at 865 nm (M-AOT)", "units": ""},
    "aerosol_type_quality_1": {"long_name": "Aerosol type quality 1", "units": ""},
    "aerosol_type_quality_2": {"long_name": "Aerosol type quality 2", "units": ""},
    "aerosol_type_quality_3": {"long_name": "Aerosol type quality 3", "units": ""},
    "aerosol_angstrom_exponent_355_670": {"long_name": "Ångström exponent (355/670)", "units": ""},
    "aerosol_angstrom_exponent_670_865": {"long_name": "Ångström exponent (670/867)", "units": ""},
}


def _get_generator(varname: str, var: str, dim_idx: int) -> _VarGenerator:

    def generator(lds: _LazyDataset[LazyVariable]) -> tuple[LazyVariable]:
        values = lds[var].values[:, :, dim_idx]

        return (
            LazyVariable(
                varname=varname,
                dims=("along_track", "across_track"),
                attrs=_ATTRS.get(varname, {}),
                values=values,
                _dataset=lds,
            ),
        )

    return generator


def _get_generators() -> dict[str, _VarGenerator]:
    return {
        "aerosol_optical_thickness_spectral_355": _get_generator(
            "aerosol_optical_thickness_spectral_355", "aerosol_optical_thickness_spectral", 0
        ),
        "aerosol_optical_thickness_spectral_670": _get_generator(
            "aerosol_optical_thickness_spectral_670", "aerosol_optical_thickness_spectral", 1
        ),
        "aerosol_optical_thickness_spectral_865": _get_generator(
            "aerosol_optical_thickness_spectral_865", "aerosol_optical_thickness_spectral", 2
        ),
        "aerosol_type_quality_1": _get_generator(
            "aerosol_type_quality_1", "aerosol_type_quality", 0
        ),
        "aerosol_type_quality_2": _get_generator(
            "aerosol_type_quality_2", "aerosol_type_quality", 1
        ),
        "aerosol_type_quality_3": _get_generator(
            "aerosol_type_quality_3", "aerosol_type_quality", 2
        ),
        "aerosol_angstrom_exponent_355_670": _get_generator(
            "aerosol_angstrom_exponent_355_670", "aerosol_angstrom_exponent", 0
        ),
        "aerosol_angstrom_exponent_670_865": _get_generator(
            "aerosol_angstrom_exponent_670_865", "aerosol_angstrom_exponent", 1
        ),
    }


register(
    file_type=FileType.AM__ACD_2B.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        elevation_var="surface_elevation",
        land_flag_var="land_flag",
        geoid_offset_var="geoid_offset",
        generators={
            "across_track_distance": _generate_across_track_distance,
            "from_track_distance": _generate_from_track_distance,
            **_get_generators(),
        },
        optional_generators={},
        transforms={
            "latitude": _tranform_swath_latitude,
            "longitude": _tranform_swath_longitude,
            "quality_status": _edit_attrs({"long_name": "Quality_status", "units": ""}),
        },
        height_vars={"surface_elevation"},
    ),
)
