from typing import Final

import numpy as np

from .....constants import ACROSS_TRACK_DIM, NADIR_INDEX_VAR
from ....info.type import FileType
from ..._typing import _LazyDataset, _VarGenerator
from ..._variable import LazyVariable
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


def _get_nadir_generator(varname: str, var: str) -> _VarGenerator:

    def generator(lds: _LazyDataset[LazyVariable]) -> tuple[LazyVariable]:
        lvar = lds[var]

        _slice: list[slice | int] = [slice(None)] * lvar.ndim
        i_across_track = lvar.dims.index(ACROSS_TRACK_DIM)
        _slice[i_across_track] = int(lds[NADIR_INDEX_VAR].values)

        values = lvar.values[*_slice]
        _dims = list(lvar.dims)
        _dims.pop(i_across_track)

        return (
            LazyVariable(
                varname=varname,
                dims=tuple(_dims),
                attrs=lvar.attrs,
                values=values,
                _dataset=lds,
            ),
        )

    return generator


def _generate_plot_cth_diff(lds: _LazyDataset[LazyVariable]) -> tuple[LazyVariable]:
    lvar_cth_diff = lds["cloud_top_height_difference_ATLID_MSI"]

    values = np.where(lds["quality_status"].values == 4, np.nan, lvar_cth_diff.values)

    return (
        LazyVariable(
            varname="plot_cloud_top_height_difference_ATLID_MSI",
            dims=lvar_cth_diff.dims,
            attrs=lvar_cth_diff.attrs,
            values=values,
            _dataset=lds,
        ),
    )


# TODO: this entire file
register(
    file_type=FileType.AM__CTH_2B.value,
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
            "plot_cloud_top_height_difference_ATLID_MSI": _generate_plot_cth_diff,
            "cloud_top_height_MSI_track": _get_nadir_generator(
                "cloud_top_height_MSI_track", "cloud_top_height_MSI"
            ),
            "cloud_top_height_difference_ATLID_MSI_track": _get_nadir_generator(
                "cloud_top_height_difference_ATLID_MSI_track",
                "cloud_top_height_difference_ATLID_MSI",
            ),
            "quality_status_track": _get_nadir_generator("quality_status_track", "quality_status"),
            "cloud_fraction_track": _get_nadir_generator("cloud_fraction_track", "cloud_fraction"),
        },
        optional_generators={},
        transforms={
            "latitude": _tranform_swath_latitude,
            "longitude": _tranform_swath_longitude,
            "quality_status": _edit_attrs({"long_name": "Quality status", "units": ""}),
            "cloud_top_height_MSI": _edit_attrs({"long_name": "CTH from M-COP", "units": "m"}),
            "cloud_top_height_difference_ATLID_MSI": _edit_attrs(
                {"long_name": "CTH difference (ATL $-$ MSI)", "units": "m"}
            ),
        },
        height_vars={"surface_elevation"},
    ),
)
