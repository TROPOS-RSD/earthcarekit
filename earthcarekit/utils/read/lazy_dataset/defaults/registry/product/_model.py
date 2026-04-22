from dataclasses import dataclass, field

from ......constants import (
    ELEVATION_VAR,
    GEOID_OFFSET_VAR,
    HEIGHT_VAR,
    LAND_FLAG_VAR,
    NADIR_INDEX_VAR,
    PRESSURE_VAR,
    SENSOR_ELEVATION_ANGLE_VAR,
    SOLAR_ELEVATION_ANGLE_VAR,
    SWATH_LAT_VAR,
    SWATH_LON_VAR,
    TEMP_CELSIUS_VAR,
    TIME_VAR,
    TRACK_LAT_VAR,
    TRACK_LON_VAR,
    TROPOPAUSE_VAR,
)
from ...._typing import _VarGenerator, _VarTransformer


@dataclass
class ProductDefaults:
    lat_var: str = TRACK_LAT_VAR
    lon_var: str = TRACK_LON_VAR
    time_var: str = TIME_VAR
    height_var: str = HEIGHT_VAR
    elevation_var: str = ELEVATION_VAR
    temperature_var: str = TEMP_CELSIUS_VAR
    tropopause_var: str = TROPOPAUSE_VAR
    land_flag_var: str = LAND_FLAG_VAR
    geoid_offset_var: str = GEOID_OFFSET_VAR
    swath_lat_var: str = SWATH_LAT_VAR
    swath_lon_var: str = SWATH_LON_VAR
    pressure_var: str = PRESSURE_VAR
    nadir_index_var: str = NADIR_INDEX_VAR
    sensor_elevation_angle_var: str = SENSOR_ELEVATION_ANGLE_VAR
    solar_elevation_angle_var: str = SOLAR_ELEVATION_ANGLE_VAR
    generators: dict[str, _VarGenerator] = field(default_factory=dict)
    optional_generators: dict[str, _VarGenerator] = field(default_factory=dict)
    transforms: dict[str, _VarTransformer] = field(default_factory=dict)
    height_vars: set[str] = field(default_factory=set)
    time_vars: set[str] = field(default_factory=set)

    def get_varname_map(self) -> dict[str, str]:
        return {
            TRACK_LAT_VAR: self.lat_var,
            TRACK_LON_VAR: self.lon_var,
            TIME_VAR: self.time_var,
            HEIGHT_VAR: self.height_var,
            ELEVATION_VAR: self.elevation_var,
            TEMP_CELSIUS_VAR: self.temperature_var,
            TROPOPAUSE_VAR: self.tropopause_var,
            LAND_FLAG_VAR: self.land_flag_var,
            GEOID_OFFSET_VAR: self.geoid_offset_var,
            SWATH_LAT_VAR: self.swath_lat_var,
            SWATH_LON_VAR: self.swath_lon_var,
            PRESSURE_VAR: self.pressure_var,
            NADIR_INDEX_VAR: self.nadir_index_var,
        }
