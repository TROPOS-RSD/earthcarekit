from ....constants import (
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
    TEMP_KELVIN_VAR,
    TIME_VAR,
    TRACK_LAT_VAR,
    TRACK_LON_VAR,
    TROPOPAUSE_VAR,
)
from .._typing import _LazyDataset, _LazyVariable
from .registry.common import register_common_var_transformer


@register_common_var_transformer(TEMP_KELVIN_VAR)
@register_common_var_transformer(TEMP_CELSIUS_VAR)
def _init_temperature(common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable") -> None:
    lvar.varname = TEMP_KELVIN_VAR
    lvar.attrs["long_name"] = "Temperature"
    lvar.attrs["units"] = "K"
    lds._add_var(TEMP_KELVIN_VAR, lvar)

    lvar_celsius = lvar.copy()
    lvar_celsius.values = lvar_celsius.values - 273.15
    lvar_celsius.varname = TEMP_CELSIUS_VAR
    lvar_celsius.attrs["units"] = r"$^{\circ}$C"
    lds._add_var(TEMP_CELSIUS_VAR, lvar_celsius)


@register_common_var_transformer(HEIGHT_VAR)
def _init_height(common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable") -> None:
    lvar.varname = HEIGHT_VAR
    lvar.attrs["long_name"] = "Height"
    lvar.attrs["units"] = "m"
    lds._add_var(common_var, lvar)


@register_common_var_transformer(TIME_VAR)
def _init_time(common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable") -> None:
    lvar.varname = TIME_VAR
    lvar.attrs["long_name"] = "Time"
    lvar.attrs["units"] = ""
    lvar.attrs["time_standard"] = "UTC"
    lds._add_var(common_var, lvar)


@register_common_var_transformer(TRACK_LAT_VAR)
def _init_lat(common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable") -> None:
    lvar.varname = TRACK_LAT_VAR
    lvar.attrs["long_name"] = "Latitude"
    lvar.attrs["units"] = r"$^{\circ}$N"
    lds._add_var(common_var, lvar)


@register_common_var_transformer(TRACK_LON_VAR)
def _init_lon(common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable") -> None:
    lvar.varname = TRACK_LON_VAR
    lvar.attrs["long_name"] = "Longitude"
    lvar.attrs["units"] = r"$^{\circ}$E"
    lds._add_var(common_var, lvar)


@register_common_var_transformer(SWATH_LAT_VAR)
def _init_swath_lat(common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable") -> None:
    lvar.varname = SWATH_LAT_VAR
    lvar.attrs["long_name"] = "Latitude"
    lvar.attrs["units"] = r"$^{\circ}$N"
    lds._add_var(common_var, lvar)


@register_common_var_transformer(SWATH_LON_VAR)
def _init_swath_lon(common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable") -> None:
    lvar.varname = SWATH_LON_VAR
    lvar.attrs["long_name"] = "Longitude"
    lvar.attrs["units"] = r"$^{\circ}$E"
    lds._add_var(common_var, lvar)


@register_common_var_transformer(ELEVATION_VAR)
def _init_elevation(common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable") -> None:
    lvar.varname = ELEVATION_VAR
    lvar.attrs["long_name"] = "Surface elevation"
    lvar.attrs["units"] = "m"
    lds._add_var(common_var, lvar)


@register_common_var_transformer(LAND_FLAG_VAR)
def _init_land_flag(common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable") -> None:
    lvar.varname = LAND_FLAG_VAR
    lvar.attrs["long_name"] = "Land flag"
    lvar.attrs["units"] = ""
    lds._add_var(common_var, lvar)


@register_common_var_transformer(GEOID_OFFSET_VAR)
def _init_geoid_offset(common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable") -> None:
    lvar.varname = GEOID_OFFSET_VAR
    lvar.attrs["long_name"] = "Geoid offset"
    lvar.attrs["units"] = "m"
    lvar.attrs["comment"] = "Height of geoid EGM96 over the ellipsoid WGS84"
    lds._add_var(common_var, lvar)


@register_common_var_transformer(TROPOPAUSE_VAR)
def _init_tropopause(common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable") -> None:
    lvar.varname = TROPOPAUSE_VAR
    lvar.attrs["long_name"] = "Tropopause height"
    lvar.attrs["units"] = "m"
    lds._add_var(common_var, lvar)


@register_common_var_transformer(PRESSURE_VAR)
def _init_pressure(common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable") -> None:
    lvar.varname = PRESSURE_VAR
    lds._add_var(common_var, lvar)


@register_common_var_transformer(NADIR_INDEX_VAR)
def _init_nadir_index(common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable") -> None:
    lvar.varname = NADIR_INDEX_VAR
    lds._add_var(common_var, lvar)


@register_common_var_transformer(SOLAR_ELEVATION_ANGLE_VAR)
def _init_solar_elevation_angle(
    common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable"
) -> None:
    lvar.varname = SOLAR_ELEVATION_ANGLE_VAR
    lds._add_var(common_var, lvar)


@register_common_var_transformer(SENSOR_ELEVATION_ANGLE_VAR)
def _init_sensor_elevation_angle(
    common_var: str, lds: "_LazyDataset", lvar: "_LazyVariable"
) -> None:
    lvar.varname = SENSOR_ELEVATION_ANGLE_VAR
    lds._add_var(common_var, lvar)
