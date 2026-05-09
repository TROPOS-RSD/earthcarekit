import xarray as xr

from ....read import FileType


def get_default_profile_range(
    var: str,
    ds: xr.Dataset | None = None,
) -> tuple[float | None, float | None] | None:
    if ds is not None and not isinstance(ds, FileType):
        try:
            FileType.from_input(ds)
        except ValueError:
            pass

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
    elif var in [
        "crosspolar_attenuated_backscatter",
        "crosspolar_attenuated_backscatter_10km",
        "crosspolar_attenuated_backscatter_1km",
    ]:
        _max = 0.2e-6
        return (-_max * pad_frac, _max)
    elif var in [
        "particle_backscatter_coefficient_355nm",
        "particle_backscatter_coefficient_355nm_medium_resolution",
        "particle_backscatter_coefficient_355nm_low_resolution",
        "aerosol_backscatter_10km",
        "cloud_backscatter_10km",
        "cloud_backscatter_1km",
    ]:
        _max = max_bsc
        return (-_max * pad_frac, _max)
    elif var in [
        "particle_extinction_coefficient_355nm",
        "particle_extinction_coefficient_355nm_medium_resolution",
        "particle_extinction_coefficient_355nm_low_resolution",
        "aerosol_extinction_10km",
        "cloud_extinction_10km",
        "cloud_extinction_1km",
    ]:
        _max = max_ext
        return (-_max * pad_frac, _max)
    elif var in [
        "lidar_ratio_355nm",
        "lidar_ratio_355nm_medium_resolution",
        "lidar_ratio_355nm_low_resolution",
        "aerosol_lidar_ratio_10km",
        "cloud_lidar_ratio_10km",
        "cloud_lidar_ratio_1km",
    ]:
        _max = max_lr
        return (-_max * pad_frac, _max)
    elif var in [
        "particle_linear_depol_ratio_355nm",
        "particle_linear_depol_ratio_355nm_medium_resolution",
        "particle_linear_depol_ratio_355nm_low_resolution",
        "aerosol_depolarization_10km",
        "cloud_depolarization_10km",
        "cloud_depolarization_1km",
        "volume_depolarization_ratio_10km",
        "volume_depolarization_ratio_1km",
        "depol_ratio",
        "depol_ratio_from_means",
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
