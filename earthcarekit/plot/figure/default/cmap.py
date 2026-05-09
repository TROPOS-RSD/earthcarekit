from functools import reduce
from typing import Callable, Final, TypeAlias

import numpy as np
import xarray as xr

from ....colormap import Cmap, get_cmap
from ....read import FileType

_CmapFn: TypeAlias = Callable[[], Cmap]
_CmapRegistry: TypeAlias = dict[str, _CmapFn]


def _get_cmap(name: str) -> _CmapFn:
    return lambda: get_cmap(name)


def _mcm_qs_fn() -> Cmap:
    cmap = get_cmap("bam")
    colors = cmap(np.array([0.05, 0.3, 0.65, 0.9]))
    colors = np.append(np.array([[1, 1, 1, 1]]), colors, axis=0)
    definitions = {v: str(v) for v in [0, 1, 2, 3, 4]}
    cmap = Cmap(colors, name="quality_status_amcth").to_categorical(definitions)
    return cmap


def _ctc_qs() -> Cmap:
    cmap = get_cmap("roma_r")
    colors = cmap(np.linspace(0.1, 1, 5))
    colors = np.append(np.array([[1, 1, 1, 1]]), colors, axis=0)
    cmap = Cmap(["#000000", "#BDBDBD"], name="quality_status_ctc").to_categorical(
        {0: "good", 1: "bad"}
    )
    return cmap


def _amcth_qs() -> Cmap:
    cmap = get_cmap("roma_r")
    colors = cmap(np.linspace(0.1, 1, 5))
    colors = np.append(np.array([[1, 1, 1, 1]]), colors, axis=0)
    definitions = {v: str(v) for v in [-1, 0, 1, 2, 3, 4]}
    cmap = Cmap(colors, name="quality_status_amcth").to_categorical(definitions)
    return cmap


def _mcm_qs() -> Cmap:
    cmap = get_cmap("roma_r")
    colors = cmap(np.linspace(0.1, 1, 4))
    definitions = {v: str(v) for v in [0, 1, 2, 3]}
    cmap = Cmap(colors, name="quality_status_mcm").to_categorical(definitions)
    return cmap


def _maot_qs() -> Cmap:
    cmap = get_cmap("roma_r")
    colors = cmap(np.linspace(0.1, 1, 5))
    definitions = {v: str(v) for v in [0, 1, 2, 3, 4]}
    cmap = Cmap(colors, name="quality_status_maot").to_categorical(definitions)
    return cmap


def _qs() -> Cmap:
    cmap = get_cmap("roma_r")
    colors = cmap(np.linspace(0.1, 1, 5))
    colors = np.append(np.array([[1, 1, 1, 1]]), colors, axis=0)
    definitions = {v: str(v) for v in [-1, 0, 1, 2, 3, 4]}
    cmap = Cmap(colors, name="quality_status").to_categorical(definitions)
    return cmap


CPR_CD__2A: Final[_CmapRegistry] = {
    "doppler_velocity_uncorrected": _get_cmap("vik"),
    "doppler_velocity_corrected_for_mispointing": _get_cmap("vik"),
    "doppler_velocity_corrected_for_nubf": _get_cmap("vik"),
    "doppler_velocity_integrated": _get_cmap("vik"),
    "doppler_velocity_integrated_error": _get_cmap("vik"),
    "doppler_velocity_best_estimate": _get_cmap("vik"),
    "sedimentation_velocity_best_estimate": _get_cmap("vik"),
    "sedimentation_velocity_best_estimate_error": _get_cmap("vik"),
    "spectrum_width_uncorrected": _get_cmap("chiljet2"),
    "spectrum_width_integrated": _get_cmap("chiljet2"),
    "spectrum_width_integrated_error": _get_cmap("chiljet2"),
}

CPR_CLD_2A: Final[_CmapRegistry] = {
    "water_content": _get_cmap("chiljet2"),
    "characteristic_diameter": _get_cmap("chiljet2"),
    "maximum_dimension_L": _get_cmap("chiljet2"),
    "liquid_water_content": _get_cmap("chiljet2"),
    "liquid_effective_radius": _get_cmap("chiljet2"),
}

AC__TC__2B: Final[_CmapRegistry] = {
    "synergetic_target_classification": _get_cmap("synergetic_tc"),
    "synergetic_target_classification_medium_resolution": _get_cmap("synergetic_tc"),
    "synergetic_target_classification_low_resolution": _get_cmap("synergetic_tc"),
    "ATLID_target_classification": _get_cmap("atl_tc"),
    "ATLID_target_classification_low_resolution": _get_cmap("atl_tc"),
    "ATLID_target_classification_medium_resolution": _get_cmap("atl_tc"),
    "CPR_target_classification": _get_cmap("cpr_hydrometeor_classification"),
    "ATLID_detection_status": _get_cmap("atl_status_mie"),
    "CPR_detection_status": _get_cmap("cpr_status_detection"),
    "CPR_ATLID_status": _get_cmap("synergetic_status"),
    "CPR_ATLID_low_resolution_status": _get_cmap("synergetic_status"),
    "CPR_ATLID_medium_resolution_status": _get_cmap("synergetic_status"),
    "quality_status": _get_cmap("synergetic_quality"),
    "quality_low_resolution_status": _get_cmap("synergetic_quality"),
    "quality_medium_resolution_status": _get_cmap("synergetic_quality"),
    "insect_detection_status": _get_cmap("synergetic_insect"),
}

ACM_CAP_2B: Final[_CmapRegistry] = {
    "ice_water_content": _get_cmap("chiljet2"),
    "ice_effective_radius": _get_cmap("chiljet2"),
    "rain_water_content": _get_cmap("chiljet2"),
    "rain_median_volume_diameter": _get_cmap("chiljet2"),
    "liquid_water_content": _get_cmap("chiljet2"),
    "liquid_effective_radius": _get_cmap("chiljet2"),
    "aerosol_extinction": _get_cmap("chiljet2"),
}


MSI_CM__2A: Final[_CmapRegistry] = {
    "plot_cloud_mask_quality_status": _mcm_qs_fn,
    "plot_cloud_type_quality_status": _mcm_qs_fn,
    "plot_cloud_phase_quality_status": _mcm_qs_fn,
    "cloud_mask": _get_cmap("msi_cloud_mask"),
    "cloud_phase": _get_cmap("msi_cloud_phase"),
    "plot_surface_classification": _get_cmap("msi_surface_classification"),
    "quality_status": _mcm_qs,
}

MSI_AOT_2A: Final[_CmapRegistry] = {
    "aerosol_optical_thickness_670nm": _get_cmap("Oranges"),
    "aerosol_optical_thickness_865nm": _get_cmap("Oranges"),
    "plot_quality_mask": _get_cmap("maot_quality_mask"),
    "quality_status": _maot_qs,
}

CPR_TC__2A: Final[_CmapRegistry] = {
    "detection_status": _get_cmap("cpr_status_detection"),
    "multiple_scattering_status": _get_cmap("cpr_status_multi_scat"),
    "quality_status": _ctc_qs,
}

ATL_TC__2A: Final[_CmapRegistry] = {
    "extended_data_quality_status": _get_cmap("atl_status_extq"),
    "quality_status": _get_cmap("atl_status_q"),
}


AM__CTH_2B: Final[_CmapRegistry] = {
    "quality_status": _amcth_qs,
}

MSI_RGR_1C: Final[_CmapRegistry] = {
    "tir1": _get_cmap("Greys"),
    "tir2": _get_cmap("Greys"),
    "tir3": _get_cmap("Greys"),
}

_bsc: _CmapFn = _get_cmap("calipso")
_ext: _CmapFn = _get_cmap("chiljet2")
_lr: _CmapFn = _get_cmap("chiljet2")
_depol: _CmapFn = _get_cmap("ratio")
_atl_tc: _CmapFn = _get_cmap("atl_tc")
_radar_ref: _CmapFn = _get_cmap("radar_reflectivity")

_OTHER: Final[_CmapRegistry] = {
    "mie_attenuated_backscatter": _bsc,
    "crosspolar_attenuated_backscatter": _bsc,
    "crosspolar_attenuated_backscatter_10km": _bsc,
    "crosspolar_attenuated_backscatter_1km": _bsc,
    "particle_backscatter_coefficient_355nm": _bsc,
    "particle_backscatter_coefficient_355nm_medium_resolution": _bsc,
    "particle_backscatter_coefficient_355nm_low_resolution": _bsc,
    "aerosol_backscatter_10km": _bsc,
    "cloud_backscatter_10km": _bsc,
    "cloud_backscatter_1km": _bsc,
    "mie_total_attenuated_backscatter_355nm": _bsc,
    "attenuated_backscatter_10km": _bsc,
    "attenuated_backscatter_1km": _bsc,
    "backscatter": _bsc,
    "bsc": _bsc,
    "bsc_n": _bsc,
    "bsc_nd": _bsc,
    "particle_extinction_coefficient_355nm": _ext,
    "particle_extinction_coefficient_355nm_medium_resolution": _ext,
    "particle_extinction_coefficient_355nm_low_resolution": _ext,
    "aerosol_extinction_10km": _ext,
    "cloud_extinction_10km": _ext,
    "cloud_extinction_1km": _ext,
    "extinction": _ext,
    "ext": _ext,
    "ext_n": _ext,
    "ext_nd": _ext,
    "lidar_ratio_355nm": _lr,
    "lidar_ratio_355nm_medium_resolution": _lr,
    "lidar_ratio_355nm_low_resolution": _lr,
    "aerosol_lidar_ratio_10km": _lr,
    "cloud_lidar_ratio_10km": _lr,
    "cloud_lidar_ratio_1km": _lr,
    "particle_linear_depol_ratio_355nm": _depol,
    "particle_linear_depol_ratio_355nm_medium_resolution": _depol,
    "particle_linear_depol_ratio_355nm_low_resolution": _depol,
    "aerosol_depolarization_10km": _depol,
    "cloud_depolarization_10km": _depol,
    "cloud_depolarization_1km": _depol,
    "volume_depolarization_ratio_10km": _depol,
    "volume_depolarization_ratio_1km": _depol,
    "depol_ratio": _depol,
    "rayleigh_attenuated_backscatter": _get_cmap("ray"),
    "simple_classification": _get_cmap("atl_simple_classification"),
    "classification": _atl_tc,
    "classification_medium_resolution": _atl_tc,
    "classification_low_resolution": _atl_tc,
    "plot_radarReflectivityFactor": _radar_ref,
    "reflectivity_no_attenuation_correction": _radar_ref,
    "reflectivity_corrected": _radar_ref,
    "plot_dopplerVelocity": _get_cmap("doppler_velocity"),
    "cloud_top_height_MSI": lambda: get_cmap(get_cmap("navia").with_extremes(bad="#ffffff00")),
    "cloud_top_height_difference_ATLID_MSI": lambda: get_cmap(
        get_cmap("navia").with_extremes(bad="#808080", over="white")
    ),
    "mie_detection_status": _get_cmap("atl_status_mie"),
    "rayleigh_detection_status": _get_cmap("atl_status_rayleigh"),
    "quality_status": _qs,
    "ice_water_content": _get_cmap("chiljet2"),
    "ice_effective_radius": _get_cmap("chiljet2"),
    "featuremask": _get_cmap("featuremask"),
    "cloud_type": _get_cmap("msi_cloud_type"),
    "isccp_cloud_type": _get_cmap("msi_cloud_type"),
    "hydrometeor_classification": _get_cmap("cpr_hydrometeor_classification"),
    "doppler_velocity_classification": _get_cmap("cpr_doppler_velocity_classification"),
    "simplified_convective_classification": _get_cmap("cpr_simplified_convective_classification"),
}

_FILE_TYPE_REGISTRY: Final[dict[FileType, _CmapRegistry]] = {
    FileType.CPR_CD__2A: CPR_CD__2A,
    FileType.CPR_CLD_2A: CPR_CLD_2A,
    FileType.ACM_CAP_2B: ACM_CAP_2B,
    FileType.MSI_CM__2A: MSI_CM__2A,
    FileType.MSI_AOT_2A: MSI_AOT_2A,
    FileType.AC__TC__2B: AC__TC__2B,
    FileType.CPR_TC__2A: CPR_TC__2A,
    FileType.ATL_TC__2A: ATL_TC__2A,
    FileType.AM__CTH_2B: AM__CTH_2B,
    FileType.MSI_RGR_1C: MSI_RGR_1C,
}


ALL: Final[_CmapRegistry] = reduce(lambda a, b: a | b, _FILE_TYPE_REGISTRY.values()) | _OTHER


def get_default_cmap(
    var: str,
    file_type: str | xr.Dataset | FileType | None = None,
) -> Cmap:

    if file_type is not None and not isinstance(file_type, FileType):
        try:
            file_type = FileType.from_input(file_type)
        except ValueError:
            pass

    if isinstance(file_type, FileType):
        fn = _FILE_TYPE_REGISTRY.get(file_type, ALL).get(var, _get_cmap("viridis"))
    else:
        fn = ALL.get(var, _get_cmap("viridis"))

    return fn()
