from typing import Final

from cmcrameri import cm as cmcramericm  # type: ignore
from matplotlib import colormaps as mpl_cmaps
from matplotlib.colors import Colormap, ListedColormap

from ..constants import DEFAULT_CMAP
from . import (
    atl_quality_status,
    atl_quality_status_ext,
    atl_simple_cls,
    atl_status_mie,
    atl_status_ray,
    atl_tc,
    atl_tc2,
    calipso,
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
    msi_surface_cls,
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
from ._plotly import get_all_plotly_cmaps
from ._typing import CmapFn, CmapLike

_CMAP_FUNCTIONS: Final[tuple[CmapFn, ...]] = (
    atl_simple_cls.get_cmap,
    atl_quality_status_ext.get_cmap,
    atl_status_mie.get_cmap,
    atl_quality_status.get_cmap,
    atl_status_ray.get_cmap,
    atl_tc.get_cmap,
    atl_tc2.get_cmap,
    calipso.get_cmap,
    calipso_smooth.get_cmap,
    chiljet.get_cmap,
    chiljet2.get_cmap,
    cpr_doppler_velocity_cls.get_cmap,
    cpr_hydrometeor_cls.get_cmap,
    cpr_simplified_convective_cls.get_cmap,
    cpr_status_detection.get_cmap,
    cpr_status_multi_scat.get_cmap,
    doppler_velocity.get_cmap,
    featuremask.get_cmap,
    fire.get_cmap,
    heat.get_cmap,
    labview.get_cmap,
    maot_quality_mask.get_cmap,
    msi_bt_enhanced.get_cmap,
    msi_cloud_mask.get_cmap,
    msi_cloud_phase.get_cmap,
    msi_cloud_type.get_cmap,
    msi_cloud_type_short_labels.get_cmap,
    msi_surface_cls.get_cmap,
    pollynet_tc.get_cmap,
    radar_reflectivity.get_cmap,
    ratio.get_cmap,
    ray.get_cmap,
    synergetic_insect.get_cmap,
    synergetic_quality.get_cmap,
    synergetic_status.get_cmap,
    synergetic_tc.get_cmap,
)


def _rev(cmap_fn: CmapFn) -> CmapFn:
    def rev_cmap_fn(**kwargs) -> Cmap:
        return cmap_fn(**kwargs).reversed()

    return rev_cmap_fn


REGISTRY: Final[dict[str, CmapFn]] = {
    **{fn().name: fn for fn in _CMAP_FUNCTIONS},
    **{fn().name + "_r": _rev(fn) for fn in _CMAP_FUNCTIONS if fn().categorical is False},
}


def get_cmaps() -> dict[str, Colormap]:
    return {k: cmap_func() for k, cmap_func in REGISTRY.items()}


def _get_cmap(cmap: str | Colormap | None, **kwargs) -> Cmap:
    if cmap is None:
        return _get_cmap(DEFAULT_CMAP, **kwargs)

    if isinstance(cmap, str):
        if cmap in REGISTRY:
            return REGISTRY[cmap](**kwargs)

        if len(kwargs) > 0:
            raise TypeError(f"get_cmap() got an unexpected keyword argument '{tuple(kwargs)[0]}'")

        crameri_cmaps = cmcramericm.cmaps
        if cmap in crameri_cmaps:
            return Cmap.from_colormap(crameri_cmaps[cmap])

        plotly_cmaps = get_all_plotly_cmaps()
        if cmap in plotly_cmaps:
            return Cmap.from_colormap(plotly_cmaps[cmap])

    if len(kwargs) > 0:
        raise TypeError(f"get_cmap() got an unexpected keyword argument '{tuple(kwargs)[0]}'")

    return Cmap.from_colormap(mpl_cmaps.get_cmap(cmap))


def get_cmap(cmap: CmapLike | None, **kwargs) -> Cmap:
    """Return a colormap given by `cmap`.

    Args:
        cmap (CmapLike | None):
            - If a colormap, return it.
            - If a `str`, return first matching colormap from `earthcarekit`, `cmcrameri`,
              `plotly`, or `matplotlib` (in that order).
            - If a `list` of colors, create a corresponding descrete colormap.
            - If None, return the default colormap ("viridis").
    Returns:
        Cmap:
            The resolved colormap.
    """
    if isinstance(cmap, (str, Colormap)) or cmap is None:
        return _get_cmap(cmap, **kwargs)

    if len(kwargs) > 0:
        raise TypeError(f"get_cmap() got an unexpected keyword argument '{tuple(kwargs)[0]}'")

    if isinstance(cmap, Cmap):
        return cmap.copy()

    return Cmap.from_colormap(ListedColormap(cmap))
