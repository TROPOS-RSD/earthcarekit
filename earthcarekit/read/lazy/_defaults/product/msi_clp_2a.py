from ....info.type import FileType
from .. import ProductDefaults, register
from ._msi import MSI_GENERATORS, MSI_TRANSFORMS

register(
    file_type=FileType.MSI_CLP_2A.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        land_flag_var="land_water_flag",
        sensor_zenith_angle_var="satellite_zenith_angle",
        generators={**MSI_GENERATORS},
        transforms={**MSI_TRANSFORMS},
    ),
)
