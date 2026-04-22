from ....product.file_info.type import FileType
from ..._lazy_variable import LazyVariable
from ..._typing import NonEmptyTuple, _LazyDataset, _VarTransformer
from .. import ProductDefaults, register
from ._edit_attrs import _edit_attrs
from ._msi import (
    _generate_across_track_distance,
    _generate_from_track_distance,
    _get_dominant_classes,
    _tranform_swath_latitude,
    _tranform_swath_longitude,
)


def _generate_quality_mask_plot_var(
    lds: _LazyDataset[LazyVariable],
) -> NonEmptyTuple[LazyVariable]:
    n = 10
    new_lvar = lds["quality_mask"].copy()
    new_lvar.varname = "plot_quality_mask"
    new_lvar.values = _get_dominant_classes(new_lvar.values, n)
    new_lvar.attrs["long_name"] = "Quality mask"
    new_lvar.attrs["definition"] = (
        "0: Undefined, 1: suspicious_input_flag, 2: water_flag, 3: land_flag, 4: cloud_edge_flag, 5: cloud_flag, 6: algorithm_converged_flag, 7: homogeneity_flag, 8: suspicious_angstrom_flag, 9: missing_lines_before_flag, 10 :unexpectedly_bright_surface_flag"
    )
    new_lvar.attrs["units"] = ""
    new_lvar.attrs["earthcarekit"] = "Added by earthcarekit: class integers converted from bitwise"

    return (new_lvar,)


def _get_renamers() -> dict[str, _VarTransformer]:
    return {
        "aerosol_optical_thickness_670nm": _edit_attrs({"long_name": "AOT at 670nm", "units": ""}),
        "aerosol_optical_thickness_865nm": _edit_attrs({"long_name": "AOT at 865nm", "units": ""}),
        "aerosol_optical_thickness_670nm_error": _edit_attrs(
            {"long_name": "AOT error at 670nm", "units": ""}
        ),
        "aerosol_optical_thickness_865nm_error": _edit_attrs(
            {"long_name": "AOT error at 865nm", "units": ""}
        ),
        "angstrom_parameter_670nm_865nm": _edit_attrs(
            {"long_name": "$\\mathrm{\\AA}_{670/865}$", "units": ""}
        ),
        "angstrom_parameter_355nm_670nm": _edit_attrs(
            {"long_name": "$\\mathrm{\\AA}_{355/670}$", "units": ""}
        ),
    }


register(
    file_type=FileType.MSI_AOT_2A.value,
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
            "plot_quality_mask": _generate_quality_mask_plot_var,
        },
        optional_generators={},
        transforms={
            "latitude": _tranform_swath_latitude,
            "longitude": _tranform_swath_longitude,
            **_get_renamers(),
        },
        height_vars={"surface_elevation"},
    ),
)
