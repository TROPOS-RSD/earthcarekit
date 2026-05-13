from functools import reduce
from typing import Final, TypeAlias

import xarray as xr
from matplotlib.colors import LogNorm, Normalize

from ....read import FileType

_NormRegistry: TypeAlias = dict[str, Normalize]

CPR_FMR_2A: Final[_NormRegistry] = {
    "reflectivity_no_attenuation_correction": Normalize(-40, 20),
    "reflectivity_corrected": Normalize(-40, 20),
    "brightness_temperature": Normalize(180, 400),
    "path_integrated_attenuation": Normalize(0, 10),
}

CPR_CD__2A: Final[_NormRegistry] = {
    "doppler_velocity_uncorrected": Normalize(-6, 6),
    "doppler_velocity_corrected_for_mispointing": Normalize(-6, 6),
    "doppler_velocity_corrected_for_nubf": Normalize(-6, 6),
    "doppler_velocity_integrated": Normalize(-6, 6),
    "doppler_velocity_integrated_error": Normalize(-6, 6),
    "doppler_velocity_best_estimate": Normalize(-6, 6),
    "sedimentation_velocity_best_estimate": Normalize(-6, 6),
    "sedimentation_velocity_best_estimate_error": Normalize(-6, 6),
    "spectrum_width_uncorrected": Normalize(0, 5),
    "spectrum_width_integrated": Normalize(0, 5),
    "spectrum_width_integrated_error": Normalize(0, 5),
}

CPR_CLD_2A: Final[_NormRegistry] = {
    "water_content": LogNorm(1e-6, 1e-3),
    "characteristic_diameter": LogNorm(1e-5, 2e-3),
    "maximum_dimension_L": LogNorm(1e-4, 2e-3),
    "liquid_water_content": LogNorm(1e-4, 1e-2),
    "liquid_effective_radius": Normalize(1e-4, 2e-3),
}

ACM_CAP_2B: Final[_NormRegistry] = {
    "ice_water_content": LogNorm(1e-7, 1e-2),
    "ice_effective_radius": Normalize(0e-6, 200e-6),
    "rain_water_content": LogNorm(1e-3, 1e1),
    "rain_median_volume_diameter": Normalize(1e-5, 2e-3),
    "liquid_water_content": LogNorm(1e-7, 2e-3),
    "liquid_effective_radius": Normalize(0e-6, 50e-6),
    "aerosol_extinction": LogNorm(1e-7, 1e-3),
}

MSI_CM__2A: Final[_NormRegistry] = {
    "plot_cloud_mask_quality_status": LogNorm(-0.5, 4.5),
    "plot_cloud_type_quality_status": LogNorm(-0.5, 4.5),
    "plot_cloud_phase_quality_status": LogNorm(-0.5, 4.5),
    "quality_status": Normalize(-0.5, 3.5),
}

MSI_AOT_2A: Final[_NormRegistry] = {
    "aerosol_optical_thickness_670nm": Normalize(0.0, 0.15),
    "aerosol_optical_thickness_865nm": Normalize(0.0, 0.15),
}

ATL_NOM_1B: Final[_NormRegistry] = {
    "mie_attenuated_backscatter": LogNorm(1e-8, 1e-5),
    "rayleigh_attenuated_backscatter": LogNorm(1e-8, 1e-5),
    "crosspolar_attenuated_backscatter": LogNorm(1e-8, 1e-5),
}

ATL_EBD_2A: Final[_NormRegistry] = {
    "particle_backscatter_coefficient_355nm": LogNorm(1e-7, 1e-4),
    "particle_backscatter_coefficient_355nm_medium_resolution": LogNorm(1e-7, 1e-4),
    "particle_backscatter_coefficient_355nm_low_resolution": LogNorm(1e-7, 1e-4),
    "mie_total_attenuated_backscatter_355nm": LogNorm(1e-7, 1e-4),
    "particle_extinction_coefficient_355nm": LogNorm(1e-6, 1e-3),
    "particle_extinction_coefficient_355nm_medium_resolution": LogNorm(1e-6, 1e-3),
    "particle_extinction_coefficient_355nm_low_resolution": LogNorm(1e-6, 1e-3),
    "lidar_ratio_355nm": Normalize(0, 100),
    "lidar_ratio_355nm_medium_resolution": Normalize(0, 100),
    "lidar_ratio_355nm_low_resolution": Normalize(0, 100),
    "particle_linear_depol_ratio_355nm": Normalize(0, 0.6),
    "particle_linear_depol_ratio_355nm_medium_resolution": Normalize(0, 0.6),
    "particle_linear_depol_ratio_355nm_low_resolution": Normalize(0, 0.6),
}

ATL_CLA_2A: Final[_NormRegistry] = {
    "crosspolar_attenuated_backscatter_10km": LogNorm(1e-8, 1e-5),
    "crosspolar_attenuated_backscatter_1km": LogNorm(1e-8, 1e-5),
    "aerosol_backscatter_10km": LogNorm(1e-7, 1e-4),
    "cloud_backscatter_10km": LogNorm(1e-7, 1e-4),
    "cloud_backscatter_1km": LogNorm(1e-7, 1e-4),
    "attenuated_backscatter_10km": LogNorm(1e-7, 1e-4),
    "attenuated_backscatter_1km": LogNorm(1e-7, 1e-4),
    "aerosol_extinction_10km": LogNorm(1e-6, 1e-3),
    "cloud_extinction_10km": LogNorm(1e-6, 1e-3),
    "cloud_extinction_1km": LogNorm(1e-6, 1e-3),
    "aerosol_lidar_ratio_10km": Normalize(0, 100),
    "cloud_lidar_ratio_10km": Normalize(0, 100),
    "cloud_lidar_ratio_1km": Normalize(0, 100),
    "aerosol_depolarization_10km": Normalize(0, 0.6),
    "cloud_depolarization_10km": Normalize(0, 0.6),
    "cloud_depolarization_1km": Normalize(0, 0.6),
    "volume_depolarization_ratio_10km": Normalize(0, 0.6),
    "volume_depolarization_ratio_1km": Normalize(0, 0.6),
}

CPR_NOM_1B: Final[_NormRegistry] = {
    "plot_radarReflectivityFactor": Normalize(-25, 20),
    "plot_dopplerVelocity": Normalize(-2, 4),
}

AM__CTH_2B: Final[_NormRegistry] = {  # FIXME: need to be updated
    "cloud_top_height_MSI": Normalize(0),
    "plot_cloud_top_height_difference_ATLID_MSI": Normalize(0),
    "cloud_top_height_difference_ATLID_MSI": Normalize(0),
}

MSI_RGR_1C: Final[_NormRegistry] = {
    "tir1": Normalize(180, 320),
    "tir2": Normalize(180, 320),
    "tir3": Normalize(180, 320),
}

_OTHER: Final[_NormRegistry] = {
    "backscatter": LogNorm(1e-7, 1e-4),
    "bsc": LogNorm(1e-7, 1e-4),
    "bsc_n": LogNorm(1e-7, 1e-4),
    "bsc_nd": LogNorm(1e-7, 1e-4),
    "extinction": LogNorm(1e-6, 1e-3),
    "ext": LogNorm(1e-6, 1e-3),
    "ext_n": LogNorm(1e-6, 1e-3),
    "ext_nd": LogNorm(1e-6, 1e-3),
    "depol_ratio": Normalize(0, 0.6),
    "quality_status": Normalize(-1.5, 4.5),  # FIXME: move to product specific registry
    "ice_water_content": LogNorm(1e-4, 5e-1),  # FIXME: move to product specific registry
    "ice_effective_radius": Normalize(0, 150),  # FIXME: move to product specific registry
}

_FILE_TYPE_REGISTRY: Final[dict[FileType, _NormRegistry]] = {
    FileType.CPR_FMR_2A: CPR_FMR_2A,
    FileType.CPR_CD__2A: CPR_CD__2A,
    FileType.CPR_CLD_2A: CPR_CLD_2A,
    FileType.ACM_CAP_2B: ACM_CAP_2B,
    FileType.MSI_CM__2A: MSI_CM__2A,
    FileType.MSI_AOT_2A: MSI_AOT_2A,
    FileType.ATL_NOM_1B: ATL_NOM_1B,
    FileType.ATL_EBD_2A: ATL_EBD_2A,
    FileType.ATL_CLA_2A: ATL_CLA_2A,
    FileType.CPR_NOM_1B: CPR_NOM_1B,
    FileType.AM__CTH_2B: AM__CTH_2B,
    FileType.MSI_RGR_1C: MSI_RGR_1C,
}


ALL: Final[_NormRegistry] = reduce(lambda a, b: a | b, _FILE_TYPE_REGISTRY.values()) | _OTHER


def get_default_norm(
    var: str,
    file_type: str | xr.Dataset | FileType | None = None,
) -> Normalize:
    if isinstance(file_type, (str, xr.Dataset)):
        file_type = FileType.from_input(file_type)

    if isinstance(file_type, FileType):
        return _FILE_TYPE_REGISTRY.get(file_type, ALL).get(var, Normalize())

    return ALL.get(var, Normalize())
