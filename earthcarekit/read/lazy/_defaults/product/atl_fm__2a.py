from ....info.type import FileType
from .. import ProductDefaults, register
from ._edit_attrs import _edit_attrs

register(
    file_type=FileType.ATL_FM__2A.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        height_var="height",
        elevation_var="surface_elevation",
        tropopause_var="tropopause_height",
        land_flag_var="land_flag",
        geoid_offset_var="geoid_offset",
        generators={},
        optional_generators={},
        transforms={"featuremask": _edit_attrs({"long_name": "Featuremask", "units": ""})},
        height_vars={
            "height",
            "surface_elevation",
            "tropopause_height",
        },
    ),
)
