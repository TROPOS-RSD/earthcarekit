from functools import reduce
from typing import Callable, Final, TypeAlias, cast

import numpy as np
import xarray as xr

from .... import colormap as cm
from ....colormap import Cmap, get_cmap
from ....read import FileType

_CmapFn: TypeAlias = Callable[[], Cmap]
_CmapRegistry: TypeAlias = dict[str, _CmapFn]


def _get_cmap(name: str) -> _CmapFn:
    return lambda: get_cmap(name)


_BSC: _CmapFn = cm.calipso.get_cmap
_EXT: _CmapFn = cm.chiljet2.get_cmap
_LR: _CmapFn = cm.chiljet2.get_cmap
_DEPOL: _CmapFn = cm.ratio.get_cmap
_ATL_TC: _CmapFn = cm.atl_tc.get_cmap
_RADAR_REF: _CmapFn = cm.radar_reflectivity.get_cmap


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
    cmap = Cmap(cast(list, colors), name="quality_status_amcth").to_categorical(definitions)
    return cmap


def _mcm_qs() -> Cmap:
    cmap = get_cmap("roma_r")
    colors = cmap(np.linspace(0.1, 1, 4))
    definitions = {v: str(v) for v in [0, 1, 2, 3]}
    cmap = Cmap(cast(list, colors), name="quality_status_mcm").to_categorical(definitions)
    return cmap


def _maot_qs() -> Cmap:
    cmap = get_cmap("roma_r")
    colors = cmap(np.linspace(0.1, 1, 5))
    definitions = {v: str(v) for v in [0, 1, 2, 3, 4]}
    cmap = Cmap(cast(list, colors), name="quality_status_maot").to_categorical(definitions)
    return cmap


def _qs() -> Cmap:
    cmap = get_cmap("roma_r")
    colors = cmap(np.linspace(0.1, 1, 5))
    colors = np.append(np.array([[1, 1, 1, 1]]), colors, axis=0)
    definitions = {v: str(v) for v in [-1, 0, 1, 2, 3, 4]}
    cmap = Cmap(cast(list, colors), name="quality_status").to_categorical(definitions)
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
    "spectrum_width_uncorrected": cm.chiljet2.get_cmap,
    "spectrum_width_integrated": cm.chiljet2.get_cmap,
    "spectrum_width_integrated_error": cm.chiljet2.get_cmap,
}

CPR_CLD_2A: Final[_CmapRegistry] = {
    "water_content": cm.chiljet2.get_cmap,
    "characteristic_diameter": cm.chiljet2.get_cmap,
    "maximum_dimension_L": cm.chiljet2.get_cmap,
    "liquid_water_content": cm.chiljet2.get_cmap,
    "liquid_effective_radius": cm.chiljet2.get_cmap,
}

AC__TC__2B: Final[_CmapRegistry] = {
    "synergetic_target_classification": cm.synergetic_tc.get_cmap,
    "synergetic_target_classification_medium_resolution": cm.synergetic_tc.get_cmap,
    "synergetic_target_classification_low_resolution": cm.synergetic_tc.get_cmap,
    "ATLID_target_classification": cm.atl_tc.get_cmap,
    "ATLID_target_classification_low_resolution": cm.atl_tc.get_cmap,
    "ATLID_target_classification_medium_resolution": cm.atl_tc.get_cmap,
    "CPR_target_classification": cm.cpr_hydrometeor_cls.get_cmap,
    "ATLID_detection_status": cm.atl_status_mie.get_cmap,
    "CPR_detection_status": cm.cpr_status_detection.get_cmap,
    "CPR_ATLID_status": cm.synergetic_status.get_cmap,
    "CPR_ATLID_low_resolution_status": cm.synergetic_status.get_cmap,
    "CPR_ATLID_medium_resolution_status": cm.synergetic_status.get_cmap,
    "quality_status": cm.synergetic_quality.get_cmap,
    "quality_low_resolution_status": cm.synergetic_quality.get_cmap,
    "quality_medium_resolution_status": cm.synergetic_quality.get_cmap,
    "insect_detection_status": cm.synergetic_insect.get_cmap,
}

ACM_CAP_2B: Final[_CmapRegistry] = {
    "ice_water_content": cm.chiljet2.get_cmap,
    "ice_effective_radius": cm.chiljet2.get_cmap,
    "rain_water_content": cm.chiljet2.get_cmap,
    "rain_median_volume_diameter": cm.chiljet2.get_cmap,
    "liquid_water_content": cm.chiljet2.get_cmap,
    "liquid_effective_radius": cm.chiljet2.get_cmap,
    "aerosol_extinction": cm.chiljet2.get_cmap,
    "aerosol_classification": cm.acmcap_aer_cls.get_cmap,
    "ATLID_bscat_extinction_ratio": _LR,
    "ATLID_backscatter_rayleight": cm.ray.get_cmap,
}


MSI_CM__2A: Final[_CmapRegistry] = {
    "plot_cloud_mask_quality_status": _mcm_qs_fn,
    "plot_cloud_type_quality_status": _mcm_qs_fn,
    "plot_cloud_phase_quality_status": _mcm_qs_fn,
    "cloud_mask": cm.msi_cloud_mask.get_cmap,
    "cloud_phase": cm.msi_cloud_phase.get_cmap,
    "plot_surface_classification": cm.msi_surface_cls.get_cmap,
    "quality_status": _mcm_qs,
}

MSI_AOT_2A: Final[_CmapRegistry] = {
    "aerosol_optical_thickness_670nm": _get_cmap("Oranges"),
    "aerosol_optical_thickness_865nm": _get_cmap("Oranges"),
    "plot_quality_mask": cm.maot_quality_mask.get_cmap,
    "quality_status": _maot_qs,
}

CPR_TC__2A: Final[_CmapRegistry] = {
    "detection_status": cm.cpr_status_detection.get_cmap,
    "multiple_scattering_status": cm.cpr_status_multi_scat.get_cmap,
    "quality_status": _ctc_qs,
}

ATL_TC__2A: Final[_CmapRegistry] = {
    "extended_data_quality_status": cm.atl_quality_status_ext.get_cmap,
    "quality_status": cm.atl_quality_status.get_cmap,
}


AM__CTH_2B: Final[_CmapRegistry] = {
    "quality_status": _amcth_qs,
}

MSI_RGR_1C: Final[_CmapRegistry] = {
    "tir1": _get_cmap("Greys"),
    "tir2": _get_cmap("Greys"),
    "tir3": _get_cmap("Greys"),
}

_OTHER: Final[_CmapRegistry] = {
    "mie_attenuated_backscatter": _BSC,
    "crosspolar_attenuated_backscatter": _BSC,
    "crosspolar_attenuated_backscatter_10km": _BSC,
    "crosspolar_attenuated_backscatter_1km": _BSC,
    "particle_backscatter_coefficient_355nm": _BSC,
    "particle_backscatter_coefficient_355nm_medium_resolution": _BSC,
    "particle_backscatter_coefficient_355nm_low_resolution": _BSC,
    "aerosol_backscatter_10km": _BSC,
    "cloud_backscatter_10km": _BSC,
    "cloud_backscatter_1km": _BSC,
    "mie_total_attenuated_backscatter_355nm": _BSC,
    "attenuated_backscatter_10km": _BSC,
    "attenuated_backscatter_1km": _BSC,
    "backscatter": _BSC,
    "bsc": _BSC,
    "bsc_n": _BSC,
    "bsc_nd": _BSC,
    "particle_extinction_coefficient_355nm": _EXT,
    "particle_extinction_coefficient_355nm_medium_resolution": _EXT,
    "particle_extinction_coefficient_355nm_low_resolution": _EXT,
    "aerosol_extinction_10km": _EXT,
    "cloud_extinction_10km": _EXT,
    "cloud_extinction_1km": _EXT,
    "extinction": _EXT,
    "ext": _EXT,
    "ext_n": _EXT,
    "ext_nd": _EXT,
    "lidar_ratio_355nm": _LR,
    "lidar_ratio_355nm_medium_resolution": _LR,
    "lidar_ratio_355nm_low_resolution": _LR,
    "aerosol_lidar_ratio_10km": _LR,
    "cloud_lidar_ratio_10km": _LR,
    "cloud_lidar_ratio_1km": _LR,
    "particle_linear_depol_ratio_355nm": _DEPOL,
    "particle_linear_depol_ratio_355nm_medium_resolution": _DEPOL,
    "particle_linear_depol_ratio_355nm_low_resolution": _DEPOL,
    "aerosol_depolarization_10km": _DEPOL,
    "cloud_depolarization_10km": _DEPOL,
    "cloud_depolarization_1km": _DEPOL,
    "volume_depolarization_ratio_10km": _DEPOL,
    "volume_depolarization_ratio_1km": _DEPOL,
    "depol_ratio": _DEPOL,
    "rayleigh_attenuated_backscatter": cm.ray.get_cmap,
    "simple_classification": cm.atl_simple_cls.get_cmap,
    "classification": _ATL_TC,
    "classification_medium_resolution": _ATL_TC,
    "classification_low_resolution": _ATL_TC,
    "plot_radarReflectivityFactor": _RADAR_REF,
    "reflectivity_no_attenuation_correction": _RADAR_REF,
    "reflectivity_corrected": _RADAR_REF,
    "plot_dopplerVelocity": cm.doppler_velocity.get_cmap,
    "cloud_top_height_MSI": lambda: get_cmap(get_cmap("navia").with_extremes(bad="#ffffff00")),
    "cloud_top_height_difference_ATLID_MSI": lambda: get_cmap(
        get_cmap("navia").with_extremes(bad="#808080", over="white")
    ),
    "mie_detection_status": cm.atl_status_mie.get_cmap,
    "rayleigh_detection_status": cm.atl_status_ray.get_cmap,
    "quality_status": _qs,
    "ice_water_content": cm.chiljet2.get_cmap,
    "ice_effective_radius": cm.chiljet2.get_cmap,
    "featuremask": cm.featuremask.get_cmap,
    "cloud_type": cm.msi_cloud_type.get_cmap,
    "isccp_cloud_type": cm.msi_cloud_type.get_cmap,
    "hydrometeor_classification": cm.cpr_hydrometeor_cls.get_cmap,
    "doppler_velocity_classification": cm.cpr_doppler_velocity_cls.get_cmap,
    "simplified_convective_classification": cm.cpr_simplified_convective_cls.get_cmap,
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
        fn_file_type = _FILE_TYPE_REGISTRY.get(file_type, {}).get(var)
        fn = fn_file_type or ALL.get(var, _get_cmap("viridis"))
    else:
        fn = ALL.get(var, _get_cmap("viridis"))

    return fn()
