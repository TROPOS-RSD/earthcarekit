from ....product.file_info.type import FileType
from .. import ProductDefaults, register

register(
    file_type=FileType.CPR_CLP_2A.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        height_var="height",
        elevation_var="surface_elevation",
        land_flag_var="land_flag",
        temperature_var="GRID_temperature_1km",
        pressure_var="GRID_pressure_1km",
        generators={},
        optional_generators={},
        transforms={},
        height_vars={"height", "surface_elevation"},
    ),
)
