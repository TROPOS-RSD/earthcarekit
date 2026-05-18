from ....info.type import FileType
from .. import ProductDefaults, register

register(
    file_type=FileType.CPR_TC__2A.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        height_var="height",
        elevation_var="surface_elevation",
        generators={},
        optional_generators={},
        transforms={},
        height_vars={"height", "surface_elevation"},
    ),
)
