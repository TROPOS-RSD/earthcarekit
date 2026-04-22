from ....product.file_info.type import FileType
from ..._lazy_variable import LazyVariable
from ..._typing import NonEmptyTuple, _LazyDataset, _VarGenerator
from .. import ProductDefaults, register
from ._msi import (
    _generate_across_track_distance,
    _generate_from_track_distance,
    _get_dominant_classes,
    _tranform_swath_latitude,
    _tranform_swath_longitude,
)


def _generate_plot_surface_classification(
    lds: _LazyDataset[LazyVariable],
) -> NonEmptyTuple[LazyVariable]:
    n = 8
    new_lvar = lds["surface_classification"].copy()
    new_lvar.varname = "plot_surface_classification"
    new_lvar.values = _get_dominant_classes(new_lvar.values, n)
    new_lvar.attrs["long_name"] = "Surface classification"
    new_lvar.attrs["definition"] = (
        "0: Undefined, 1: Water, 2: Land, 3: Desert, 4: Vegetation NDVI, 5: Snow XMET, 6: Snow NDSI, 7: Sea ice XMET, 8: Sunglint"
    )
    new_lvar.attrs["units"] = ""
    new_lvar.attrs["earthcarekit"] = "Added by earthcarekit: class integers converted from bitwise"

    return (new_lvar,)


def _get_quality_status_generator(var: str) -> _VarGenerator:
    def generator(
        lds: _LazyDataset[LazyVariable],
    ) -> NonEmptyTuple[LazyVariable]:
        n = 4
        new_lvar = lds[var].copy()
        new_lvar.varname = f"plot_{var}"
        new_lvar.values = _get_dominant_classes(new_lvar.values, n)
        new_lvar.attrs["definition"] = "0: Undefined, 1: Poor, 2: Low, 3: Medium, 4: High"
        new_lvar.attrs["units"] = ""
        new_lvar.attrs["earthcarekit"] = (
            "Added by earthcarekit: class integers converted from bitwise"
        )

        return (new_lvar,)

    return generator


register(
    file_type=FileType.MSI_CM__2A.value,
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
            "plot_surface_classification": _generate_plot_surface_classification,
            "plot_cloud_mask_quality_status": _get_quality_status_generator(
                "cloud_mask_quality_status"
            ),
            "plot_cloud_type_quality_status": _get_quality_status_generator(
                "cloud_type_quality_status"
            ),
            "plot_cloud_phase_quality_status": _get_quality_status_generator(
                "cloud_phase_quality_status"
            ),
        },
        optional_generators={},
        transforms={
            "latitude": _tranform_swath_latitude,
            "longitude": _tranform_swath_longitude,
        },
        height_vars={"surface_elevation"},
    ),
)
