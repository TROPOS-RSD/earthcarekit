import numpy as np
import xarray as xr
from matplotlib.colors import Colormap, LogNorm, Normalize

from ...utils import FileType
from ..color.colormap import Cmap, get_cmap


def get_default_norm(
    var: str,
    file_type: str | xr.Dataset | FileType | None = None,
) -> Normalize:

    if file_type is not None and not isinstance(file_type, FileType):
        file_type = FileType.from_input(file_type)

    if file_type == FileType.CPR_FMR_2A:
        if var in [
            "reflectivity_no_attenuation_correction",
            "reflectivity_corrected",
        ]:
            return Normalize(vmin=-40, vmax=20)
        elif var in [
            "brightness_temperature",
        ]:
            return Normalize(vmin=240, vmax=300)
        elif var in [
            "path_integrated_attenuation",
        ]:
            return Normalize(vmin=0, vmax=10)
    elif file_type == FileType.CPR_CD__2A:
        if var in [
            "doppler_velocity_uncorrected",
            "doppler_velocity_corrected_for_mispointing",
            "doppler_velocity_corrected_for_nubf",
            "doppler_velocity_integrated",
            "doppler_velocity_integrated_error",
            "doppler_velocity_best_estimate",
            "sedimentation_velocity_best_estimate",
            "sedimentation_velocity_best_estimate_error",
        ]:
            return Normalize(vmin=-6, vmax=6)
        elif var in [
            "spectrum_width_uncorrected",
            "spectrum_width_integrated",
            "spectrum_width_integrated_error",
        ]:
            return Normalize(vmin=0, vmax=5)
    elif file_type == FileType.CPR_CLD_2A:
        if var in ["water_content"]:
            return LogNorm(1e-6, 1e-3)
        elif var in ["characteristic_diameter"]:
            return LogNorm(1e-5, 2e-3)
        elif var in ["maximum_dimension_L"]:
            return LogNorm(1e-4, 2e-3)
        elif var in ["liquid_water_content"]:
            return LogNorm(1e-4, 1e-2)
        elif var in ["liquid_effective_radius"]:
            return Normalize(1e-4, 2e-3)
    elif file_type == FileType.ACM_CAP_2B:
        if var in ["ice_water_content"]:
            return LogNorm(1e-7, 1e-2)
        elif var in ["ice_effective_radius"]:
            return Normalize(0e-6, 200e-6)
        elif var in ["rain_water_content"]:
            return LogNorm(1e-3, 1e1)
        elif var in ["rain_median_volume_diameter"]:
            return Normalize(1e-5, 2e-3)
        elif var in ["liquid_water_content"]:
            return LogNorm(1e-7, 2e-3)
        elif var in ["liquid_effective_radius"]:
            return Normalize(0e-6, 50e-6)
        elif var in ["aerosol_extinction"]:
            return LogNorm(1e-7, 1e-3)

    if var in [
        "mie_attenuated_backscatter",
        "rayleigh_attenuated_backscatter",
        "crosspolar_attenuated_backscatter",
    ]:
        return LogNorm(vmin=1e-8, vmax=1e-5)
    elif var in [
        "particle_backscatter_coefficient_355nm",
        "particle_backscatter_coefficient_355nm_medium_resolution",
        "particle_backscatter_coefficient_355nm_low_resolution",
        "mie_total_attenuated_backscatter_355nm",
    ]:
        return LogNorm(vmin=1e-7, vmax=1e-4)
    elif var in [
        "particle_extinction_coefficient_355nm",
        "particle_extinction_coefficient_355nm_medium_resolution",
        "particle_extinction_coefficient_355nm_low_resolution",
    ]:
        return LogNorm(vmin=1e-6, vmax=1e-3)
    elif var in [
        "lidar_ratio_355nm",
        "lidar_ratio_355nm_medium_resolution",
        "lidar_ratio_355nm_low_resolution",
    ]:
        return Normalize(vmin=0, vmax=100)
    elif var in [
        "particle_linear_depol_ratio_355nm",
        "particle_linear_depol_ratio_355nm_medium_resolution",
        "particle_linear_depol_ratio_355nm_low_resolution",
        "depol_ratio",
    ]:
        return Normalize(vmin=0, vmax=0.6)
    elif var in [
        "plot_radarReflectivityFactor",
    ]:
        return Normalize(vmin=-25, vmax=20)
    elif var in [
        "plot_dopplerVelocity",
    ]:
        return Normalize(vmin=-2, vmax=4)
    elif "cloud_top_height_MSI" in var:
        return Normalize(vmin=0)
    elif var == "plot_cloud_top_height_difference_ATLID_MSI" and isinstance(
        file_type, xr.Dataset
    ):
        return Normalize(
            vmin=0,
            vmax=np.nanmax(file_type["cloud_top_height_difference_ATLID_MSI"].values),
        )
    elif "cloud_top_height_difference_ATLID_MSI" in var:
        return Normalize(vmin=0)
    elif "quality_status" in var:
        return Normalize(vmin=-1.5, vmax=4.5)
    elif var in [
        "ice_water_content",
    ]:
        return LogNorm(vmin=1e-4, vmax=5e-1)
    elif var in [
        "ice_effective_radius",
    ]:
        return Normalize(vmin=0, vmax=150)
    elif var in ["tir1", "tir2", "tir3"]:
        return Normalize(vmin=210, vmax=330)
    return Normalize()


def get_default_rolling_mean(
    var: str,
    file_type: str | xr.Dataset | FileType | None = None,
) -> int | None:

    if file_type is not None and not isinstance(file_type, FileType):
        file_type = FileType.from_input(file_type)

    if var in [
        "mie_attenuated_backscatter",
        "rayleigh_attenuated_backscatter",
        "crosspolar_attenuated_backscatter",
    ]:
        return 20
    if var in [
        "mie_total_attenuated_backscatter_355nm",
    ]:
        return 1
    return None


def get_default_cmap(
    var: str,
    file_type: str | xr.Dataset | FileType | None = None,
) -> Cmap:

    if file_type is not None and not isinstance(file_type, FileType):
        file_type = FileType.from_input(file_type)

    if file_type == FileType.CPR_CD__2A:
        if var in [
            "doppler_velocity_uncorrected",
            "doppler_velocity_corrected_for_mispointing",
            "doppler_velocity_corrected_for_nubf",
            "doppler_velocity_integrated",
            "doppler_velocity_integrated_error",
            "doppler_velocity_best_estimate",
            "sedimentation_velocity_best_estimate",
            "sedimentation_velocity_best_estimate_error",
        ]:
            return get_cmap("vik")
        elif var in [
            "spectrum_width_uncorrected",
            "spectrum_width_integrated",
            "spectrum_width_integrated_error",
        ]:
            return get_cmap("chiljet2")
    elif file_type == FileType.CPR_CLD_2A:
        if var in [
            "water_content",
            "characteristic_diameter",
            "maximum_dimension_L",
            "liquid_water_content",
            "liquid_effective_radius",
        ]:
            return get_cmap("chiljet2")
    elif file_type == FileType.AC__TC__2B:
        if var in [
            "synergetic_target_classification",
            "synergetic_target_classification_medium_resolution",
            "synergetic_target_classification_low_resolution",
        ]:
            return get_cmap("synergetic_tc")
    elif file_type == FileType.ACM_CAP_2B:
        if var in [
            "ice_water_content",
            "ice_effective_radius",
            "rain_water_content",
            "rain_median_volume_diameter",
            "liquid_water_content",
            "liquid_effective_radius",
            "aerosol_extinction",
        ]:
            return get_cmap("chiljet2")
    if var in [
        "mie_attenuated_backscatter",
        "crosspolar_attenuated_backscatter",
        "particle_backscatter_coefficient_355nm",
        "particle_backscatter_coefficient_355nm_medium_resolution",
        "particle_backscatter_coefficient_355nm_low_resolution",
        "mie_total_attenuated_backscatter_355nm",
    ]:
        return get_cmap("calipso")
    elif var in [
        "particle_extinction_coefficient_355nm",
        "particle_extinction_coefficient_355nm_medium_resolution",
        "particle_extinction_coefficient_355nm_low_resolution",
    ]:
        return get_cmap("chiljet2")
    elif var in [
        "lidar_ratio_355nm",
        "lidar_ratio_355nm_medium_resolution",
        "lidar_ratio_355nm_low_resolution",
    ]:
        return get_cmap("chiljet2")
    elif var in [
        "rayleigh_attenuated_backscatter",
    ]:
        return get_cmap("ray")
    elif var in [
        "particle_linear_depol_ratio_355nm",
        "particle_linear_depol_ratio_355nm_medium_resolution",
        "particle_linear_depol_ratio_355nm_low_resolution",
        "depol_ratio",
    ]:
        return get_cmap("ratio")
    elif var in [
        "simple_classification",
    ]:
        return get_cmap("atl_simple_classification")
    elif var in [
        "classification",
        "classification_medium_resolution",
        "classification_low_resolution",
    ]:
        return get_cmap("atl_tc")
    elif var in [
        "plot_radarReflectivityFactor",
        "reflectivity_no_attenuation_correction",
        "reflectivity_corrected",
    ]:
        return get_cmap("radar_reflectivity")
    elif var in [
        "plot_dopplerVelocity",
    ]:
        return get_cmap("doppler_velocity")
    elif "cloud_top_height_MSI" in var:
        return get_cmap(get_cmap("navia").with_extremes(bad="#ffffff00"))
    elif "cloud_top_height_difference_ATLID_MSI" in var:
        return get_cmap(get_cmap("navia").with_extremes(bad="#808080", over="white"))
    elif "quality_status" in var:
        if isinstance(file_type, FileType):
            if file_type == FileType.AM__CTH_2B:
                cmap = get_cmap("roma_r")
                colors = cmap(np.linspace(0.1, 1, 5))
                colors = np.append(np.array([[1, 1, 1, 1]]), colors, axis=0)
                definitions = {v: str(v) for v in [-1, 0, 1, 2, 3, 4]}
                cmap = Cmap(colors, name="quality_status_amcth").to_categorical(
                    definitions
                )
                return cmap
            elif file_type == FileType.CPR_TC__2A:
                cmap = get_cmap("roma_r")
                colors = cmap(np.linspace(0.1, 1, 5))
                colors = np.append(np.array([[1, 1, 1, 1]]), colors, axis=0)
                definitions = {v: str(v) for v in [-1, 0, 1, 2, 3, 4]}
                cmap = Cmap(
                    ["#000000", "#BDBDBD"], name="quality_status_ctc"
                ).to_categorical({0: "good", 1: "bad"})
                return cmap
        cmap = get_cmap("roma_r")
        colors = cmap(np.linspace(0.1, 1, 5))
        colors = np.append(np.array([[1, 1, 1, 1]]), colors, axis=0)
        definitions = {v: str(v) for v in [-1, 0, 1, 2, 3, 4]}
        cmap = Cmap(colors, name="quality_status_amcth").to_categorical(definitions)
        return cmap
    elif var in [
        "ice_water_content",
    ]:
        return get_cmap("chiljet2")
    elif var in [
        "ice_effective_radius",
    ]:
        return get_cmap("chiljet2")
    elif var in ["featuremask"]:
        return get_cmap("featuremask")
    elif file_type in [
        FileType.MSI_COP_2A,
        FileType.MSI_CM__2A,
    ] and var in [
        "cloud_type",
        "isccp_cloud_type",
    ]:
        return get_cmap("msi_cloud_type")
    elif var in ["hydrometeor_classification"]:
        return get_cmap("cpr_hydrometeor_classification")
    elif var in ["doppler_velocity_classification"]:
        return get_cmap("cpr_doppler_velocity_classification")
    elif var in ["simplified_convective_classification"]:
        return get_cmap("cpr_simplified_convective_classification")
    elif var in ["tir1", "tir2", "tir3"]:
        return get_cmap("Greys")
    return get_cmap("viridis")


def get_default_profile_range(
    var: str, ds: xr.Dataset | None = None
) -> tuple[float | None, float | None] | None:
    file_type: FileType | None = None
    if ds is not None and not isinstance(ds, FileType):
        file_type = FileType.from_input(ds)

    pad_frac = 0.00
    max_bsc = 8e-6  # [m-1 sr-1]
    max_ext = 6e-4  # [m-1]
    max_lr = 100.0  # [sr]
    max_depol = 0.5  # [-]

    _min: float
    _max: float
    if var in ["mie_attenuated_backscatter"]:
        _max = 0.8e-6
        return (-_max * pad_frac, _max)
    elif var in ["rayleigh_attenuated_backscatter"]:
        _max = 3e-6
        return (-_max * pad_frac, _max)
    elif var in ["crosspolar_attenuated_backscatter"]:
        _max = 0.2e-6
        return (-_max * pad_frac, _max)
    elif var in [
        "particle_backscatter_coefficient_355nm",
        "particle_backscatter_coefficient_355nm_medium_resolution",
        "particle_backscatter_coefficient_355nm_low_resolution",
    ]:
        _max = max_bsc
        return (-_max * pad_frac, _max)
    elif var in [
        "particle_extinction_coefficient_355nm",
        "particle_extinction_coefficient_355nm_medium_resolution",
        "particle_extinction_coefficient_355nm_low_resolution",
    ]:
        _max = max_ext
        return (-_max * pad_frac, _max)
    elif var in [
        "lidar_ratio_355nm",
        "lidar_ratio_355nm_medium_resolution",
        "lidar_ratio_355nm_low_resolution",
    ]:
        _max = max_lr
        return (-_max * pad_frac, _max)
    elif var in [
        "particle_linear_depol_ratio_355nm",
        "particle_linear_depol_ratio_355nm_medium_resolution",
        "particle_linear_depol_ratio_355nm_low_resolution",
        "depol_ratio",
    ]:
        _max = max_depol
        return (-_max * pad_frac, _max)
    elif var in [
        "plot_radarReflectivityFactor",
    ]:
        _min = -25
        _max = 20
        vrange = _max - _min
        pad = vrange * pad_frac
        return (_min - pad, _max + pad)
    elif var in [
        "plot_dopplerVelocity",
    ]:
        _min = -2
        _max = 4
        vrange = _max - _min
        pad = vrange * pad_frac
        return (_min - pad, _max + pad)
    elif var in [
        "reflectivity_no_attenuation_correction",
        "reflectivity_corrected",
    ]:
        _min = -40
        _max = 20
        vrange = _max - _min
        pad = vrange * pad_frac
        return (_min - pad, _max + pad)
    return (None, None)
