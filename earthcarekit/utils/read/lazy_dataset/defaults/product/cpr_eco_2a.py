from ....product.file_info.type import FileType
from .. import ProductDefaults, register

register(
    file_type=FileType.CPR_ECO_2A.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        height_var="bin_height",
        elevation_var="surface_elevation",
        land_flag_var="land_water_flag",
        generators={},
        optional_generators={},
        transforms={},
        height_vars={"bin_height", "surface_elevation"},
    ),
)
