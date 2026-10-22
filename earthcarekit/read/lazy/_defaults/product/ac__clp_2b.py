import numpy as np

from ....info.type import FileType
from ..._typing import _LazyDataset, _VarTransformerDict
from ..._variable import LazyVariable
from .. import ProductDefaults, register
from ._combine import combine_dicts
from ._depol import get_depol_tranformers
from ._edit_attrs import _edit_attrs


def _fix_nans(lds: _LazyDataset[LazyVariable], lvar: LazyVariable) -> tuple[LazyVariable]:
    lvar.values = np.where(lvar.values < -9e3, np.nan, lvar.values)
    return (lvar,)


def _fix_long_name(lds: _LazyDataset[LazyVariable], lvar: LazyVariable) -> tuple[LazyVariable]:
    if long_name := lvar.attrs.get("longName"):
        lvar.attrs["long_name"] = long_name
    return (lvar,)


def _fix_all_long_name() -> _VarTransformerDict:
    vars = [
        "GRID_pressure_1km",
        "GRID_temperature_1km",
        "GRID_relativeHumidity_1km",
        "GRID_specificHumidity_1km",
    ]
    return {v: _fix_long_name for v in vars}


def _get_all_fix_nans() -> _VarTransformerDict:
    vars = [
        "GRID_pressure_1km",
        "GRID_temperature_1km",
        "GRID_relativeHumidity_1km",
        "GRID_specificHumidity_1km",
        "attenuated_backscatter_10km",
        "cloud_air_velocity_10km",
        "cloud_air_velocity_1km",
        "cloud_backscatter_10km",
        "cloud_backscatter_1km",
        "cloud_doppler_velocity_10km",
        "cloud_doppler_velocity_1km",
        "cloud_effective_radius1_10km",
        "cloud_effective_radius1_1km",
        "cloud_effective_radius2_10km",
        "cloud_effective_radius2_1km",
        "cloud_extinction_10km",
        "cloud_extinction_1km",
        "cloud_lidar_ratio_10km",
        "cloud_lidar_ratio_1km",
        "cloud_number_concentration1_10km",
        "cloud_number_concentration1_1km",
        "cloud_number_concentration2_10km",
        "cloud_number_concentration2_1km",
        "cloud_radar_reflectivity_10km",
        "cloud_radar_reflectivity_1km",
        "cloud_terminal_velocity1_10km",
        "cloud_terminal_velocity1_1km",
        "cloud_terminal_velocity2_10km",
        "cloud_terminal_velocity2_1km",
        "cloud_water_content1_10km",
        "cloud_water_content1_1km",
        "cloud_water_content2_10km",
        "cloud_water_content2_1km",
        "ice_effective_radius_10km",
        "ice_effective_radius_10km_uncertainty",
        "ice_effective_radius_1km",
        "ice_effective_radius_1km_uncertainty",
        "ice_water_content_10km",
        "ice_water_content_10km_uncertainty",
        "ice_water_content_1km",
        "ice_water_content_1km_uncertainty",
        "ice_water_path_10km",
        "ice_water_path_1km",
        "liquid_water_content_10km",
        "liquid_water_content_10km_uncertainty",
        "liquid_water_content_1km",
        "liquid_water_content_1km_uncertainty",
        "liquid_water_path_10km",
        "liquid_water_path_1km",
        "optical_thickness_10km",
        "optical_thickness_1km",
        "total_cloud_ice_number_concentration_10km",
        "total_cloud_ice_number_concentration_1km",
        "total_cloud_terminal_velocity_10km",
        "total_cloud_terminal_velocity_1km",
        "total_cloud_water_number_concentration_10km",
        "total_cloud_water_number_concentration_1km",
        "water_effective_radius_10km",
        "water_effective_radius_10km_uncertainty",
        "water_effective_radius_1km",
        "water_effective_radius_1km_uncertainty",
    ]
    return {v: _fix_nans for v in vars}


def _get_all_fix_units() -> _VarTransformerDict:
    transforms: _VarTransformerDict = {}
    # /m/sr
    for var in [
        "attenuated_backscatter_10km",
        "attenuated_backscatter_1km",
        "cloud_backscatter_10km",
        "cloud_backscatter_1km",
        "crosspolar_attenuated_backscatter_10km",
        "crosspolar_attenuated_backscatter_1km",
    ]:
        transforms[var] = _edit_attrs({"units": "m-1 sr-1"})
    # /m
    for var in [
        "cloud_extinction_10km",
        "cloud_extinction_1km",
    ]:
        transforms[var] = _edit_attrs({"units": "m-1"})

    # micro m
    for var in [
        "cloud_effective_radius1_10km",
        "cloud_effective_radius1_1km",
        "cloud_effective_radius2_10km",
        "cloud_effective_radius2_1km",
        "ice_effective_radius_10km",
        "ice_effective_radius_1km",
        "water_effective_radius_10km",
    ]:
        transforms[var] = _edit_attrs({"units": "um"})
    return transforms


def _get_transforms() -> _VarTransformerDict:
    transforms: _VarTransformerDict = {
        **get_depol_tranformers(
            "volume_depolarization_ratio_1km",
            "volume_depolarization_ratio_10km",
            "cloud_depolarization_1km",
            "cloud_depolarization_10km",
        ),
    }
    transforms = combine_dicts(_fix_all_long_name(), transforms)
    transforms = combine_dicts(_get_all_fix_nans(), transforms)
    transforms = combine_dicts(_get_all_fix_units(), transforms)
    return transforms


register(
    file_type=FileType.AC__CLP_2B.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        height_var="height",
        elevation_var="surface_elevation",
        land_flag_var="land_water_flag",
        pressure_var="GRID_pressure_1km",
        temperature_var="GRID_temperature_1km",
        generators={},
        optional_generators={},
        transforms=_get_transforms(),
        height_vars={
            "height",
            "surface_elevation",
        },
    ),
)
