from xarray import Dataset

from ...constants import *


def _rename(
    ds: Dataset,
    name: str | None,
    new_name: str,
) -> Dataset:
    if isinstance(name, str):
        ds = ds.rename({name: new_name})
    return ds


def rename_and_create_temperature_vars(
    ds: Dataset,
    temperature_var: str | None = None,
    is_kelvin: bool = True,
    var_name_kelvin: str = TEMP_KELVIN_VAR,
    var_name_celsius: str = TEMP_CELSIUS_VAR,
) -> Dataset:
    if isinstance(temperature_var, str):
        if is_kelvin:
            name1 = var_name_kelvin
            units1 = "K"
            name2 = var_name_celsius
            units2 = r"$^{\circ}$C"
            conversion = -273.15
        else:
            name1 = var_name_celsius
            units1 = r"$^{\circ}$C"
            name2 = var_name_kelvin
            units2 = "K"
            conversion = 273.15
        ds = _rename(ds, temperature_var, name1)
        ds = rename_var_info(ds, name1, "Temperature", "Temperature", units1)
        ds[name2] = ds[name1].copy() + conversion
        ds = rename_var_info(ds, name2, "Temperature", "Temperature", units2)
    return ds


def rename_common_dims_and_vars(
    ds: Dataset,
    along_track_dim: str | None = None,
    across_track_dim: str | None = None,
    vertical_dim: str | None = None,
    time_var: str | None = None,
    height_var: str | None = None,
    track_lat_var: str | None = None,
    track_lon_var: str | None = None,
    swath_lat_var: str | None = None,
    swath_lon_var: str | None = None,
    elevation_var: str | None = None,
    tropopause_var: str | None = None,
    temperature_var: str | None = None,
) -> Dataset:
    """Renames standard dimensions and variables to create consistency across EarthCARE products."""
    ds = _rename(ds, along_track_dim, ALONG_TRACK_DIM)
    ds = _rename(ds, across_track_dim, ACROSS_TRACK_DIM)
    ds = _rename(ds, vertical_dim, VERTICAL_DIM)
    ds = _rename(ds, time_var, TIME_VAR)
    ds = _rename(ds, height_var, HEIGHT_VAR)
    ds = _rename(ds, track_lat_var, TRACK_LAT_VAR)
    ds = _rename(ds, track_lon_var, TRACK_LON_VAR)
    ds = _rename(ds, swath_lat_var, SWATH_LAT_VAR)
    ds = _rename(ds, swath_lon_var, SWATH_LON_VAR)
    ds = _rename(ds, elevation_var, ELEVATION_VAR)
    ds = _rename(ds, tropopause_var, TROPOPAUSE_VAR)
    ds = rename_and_create_temperature_vars(ds, temperature_var, is_kelvin=True)
    return ds


def rename_var_info(
    ds: Dataset,
    var: str,
    name: str | None = None,
    long_name: str | None = None,
    units: str | None = None,
) -> Dataset:
    if name is not None:
        ds[var] = ds[var].assign_attrs(name=name)
    if long_name is not None:
        ds[var] = ds[var].assign_attrs(long_name=long_name)
    if units is not None:
        ds[var] = ds[var].assign_attrs(units=units)
    return ds
