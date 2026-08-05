from ....info.type import FileType
from .. import ProductDefaults, register

register(
    file_type=FileType.ATL_CTH_2A.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        geoid_offset_var="geoid_offset",
        generators={},
        optional_generators={},
        transforms={},
        height_vars={
            "ATLID_cloud_top_height",
            "tropopause_height_calipso",  # old: last used in BC
            "tropopause_height_wmo",  # old: last used in BC
            "tropopause_height",  # new: first used in BD
        },
    ),
)
