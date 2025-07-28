import numpy as np
import xarray as xr
from matplotlib.colors import Colormap, LogNorm, Normalize

from ...utils import FileType
from ..color.colormap import Cmap, get_cmap


def get_default_norm(var: str, ds: xr.Dataset | None = None) -> Normalize:
    file_type: FileType | None = None
    if ds is not None and not isinstance(ds, FileType):
        file_type = FileType.from_input(ds)

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
        ds, xr.Dataset
    ):
        return Normalize(
            vmin=0, vmax=np.nanmax(ds["cloud_top_height_difference_ATLID_MSI"].values)
        )
    elif "cloud_top_height_difference_ATLID_MSI" in var:
        return Normalize(vmin=0)
    elif "quality_status" in var:
        return Normalize(vmin=-1.5, vmax=4.5)
    return Normalize()


def get_default_rolling_mean(
    var: str, file_type: str | xr.Dataset | FileType | None = None
) -> int | None:

    if file_type is not None and not isinstance(file_type, FileType):
        file_type = FileType.from_input(file_type)

    if var in [
        "mie_attenuated_backscatter",
        "rayleigh_attenuated_backscatter",
        "crosspolar_attenuated_backscatter",
    ]:
        return 20
    return None


def get_default_cmap(
    var: str, file_type: str | xr.Dataset | FileType | None = None
) -> Cmap:

    if file_type is not None and not isinstance(file_type, FileType):
        file_type = FileType.from_input(file_type)

    if var in [
        "mie_attenuated_backscatter",
        "crosspolar_attenuated_backscatter",
        "particle_backscatter_coefficient_355nm",
        "particle_backscatter_coefficient_355nm_medium_resolution",
        "particle_backscatter_coefficient_355nm_low_resolution",
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
        return get_cmap("simple_classification")
    elif var in [
        "classification",
        "classification_medium_resolution",
        "classification_low_resolution",
    ]:
        return get_cmap("target_classification")
    elif var in [
        "plot_radarReflectivityFactor",
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
        cmap = get_cmap("roma_r")
        colors = cmap(np.linspace(0.1, 1, 5))
        colors = np.append(np.array([[1, 1, 1, 1]]), colors, axis=0)
        definitions = {v: str(v) for v in [-1, 0, 1, 2, 3, 4]}
        cmap = Cmap(colors, name="quality_status_amcth").to_categorical(definitions)
        return cmap
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
    return (None, None)
