"""
**earthcarekit.colormap**

Colormap utilities.

## Notes

This module depends on other internal modules:

- [earthcarekit.color][]
- [earthcarekit.constants][]

---
"""

from matplotlib.colors import Colormap

from . import (
    atl_quality_status,
    atl_quality_status_ext,
    atl_simple_cls,
    atl_status_mie,
    atl_status_ray,
    atl_tc,
    atl_tc2,
    calipso,
    calipso_old,
    calipso_smooth,
    chiljet,
    chiljet2,
    cpr_doppler_velocity_cls,
    cpr_hydrometeor_cls,
    cpr_simplified_convective_cls,
    cpr_status_detection,
    cpr_status_multi_scat,
    doppler_velocity,
    featuremask,
    fire,
    heat,
    labview,
    maot_quality_mask,
    msi_bt_enhanced,
    msi_cloud_mask,
    msi_cloud_phase,
    msi_cloud_type,
    msi_cloud_type_short_labels,
    msi_surface_classification,
    pollynet_tc,
    radar_reflectivity,
    ratio,
    ray,
    synergetic_insect,
    synergetic_quality,
    synergetic_status,
    synergetic_tc,
)
from ._cmap import Cmap
from ._combine import combine_cmaps
from ._get_cmap import _get_custom_cmaps, get_cmap
from ._rename import rename_cmap
from ._shift import shift_cmap

cmaps: dict[str, Colormap] = _get_custom_cmaps()
"""List of custom colormaps for earthcarekit."""

__all__ = [
    "Cmap",
    "combine_cmaps",
    "get_cmap",
    "rename_cmap",
    "shift_cmap",
]
