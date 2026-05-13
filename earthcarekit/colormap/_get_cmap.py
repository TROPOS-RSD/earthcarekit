from cmcrameri import cm as cmcramericm  # type: ignore
from matplotlib import colormaps as mpl_cmaps
from matplotlib.colors import (
    Colormap,
    ListedColormap,
)

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
from ._plotly import get_all_plotly_cmaps


def _get_custom_cmaps() -> dict[str, Colormap]:
    _cmaps = [
        atl_simple_cls.get_cmap(),
        atl_quality_status_ext.get_cmap(),
        atl_status_mie.get_cmap(),
        atl_quality_status.get_cmap(),
        atl_status_ray.get_cmap(),
        atl_tc.get_cmap(),
        atl_tc2.get_cmap(),
        calipso.get_cmap(),
        calipso_old.get_cmap(),
        calipso_smooth.get_cmap(),
        chiljet.get_cmap(),
        chiljet2.get_cmap(),
        cpr_doppler_velocity_cls.get_cmap(),
        cpr_hydrometeor_cls.get_cmap(),
        cpr_simplified_convective_cls.get_cmap(),
        cpr_status_detection.get_cmap(),
        cpr_status_multi_scat.get_cmap(),
        doppler_velocity.get_cmap(),
        featuremask.get_cmap(),
        fire.get_cmap(),
        heat.get_cmap(),
        labview.get_cmap(),
        maot_quality_mask.get_cmap(),
        msi_bt_enhanced.get_cmap(),
        msi_cloud_mask.get_cmap(),
        msi_cloud_phase.get_cmap(),
        msi_cloud_type.get_cmap(),
        msi_cloud_type_short_labels.get_cmap(),
        msi_surface_classification.get_cmap(),
        pollynet_tc.get_cmap(),
        radar_reflectivity.get_cmap(),
        ratio.get_cmap(),
        ray.get_cmap(),
        synergetic_insect.get_cmap(),
        synergetic_quality.get_cmap(),
        synergetic_status.get_cmap(),
        synergetic_tc.get_cmap(),
    ]
    return {cm.name: cm for cm in _cmaps}


def _get_cmap(cmap: str | Colormap | None) -> Colormap:
    if cmap is None:
        return _get_cmap(DEFAULT_CMAP)

    if isinstance(cmap, str):
        custom_cmaps = _get_custom_cmaps()
        if cmap in custom_cmaps:
            return custom_cmaps[cmap]

        crameri_cmaps = cmcramericm.cmaps
        if cmap in crameri_cmaps:
            return crameri_cmaps[cmap]

        plotly_cmaps = get_all_plotly_cmaps()
        if cmap in plotly_cmaps:
            return plotly_cmaps[cmap]

    return mpl_cmaps.get_cmap(cmap)


def get_cmap(cmap: str | Colormap | list | None) -> Cmap:
    """
    Return a color map given by `cmap`.

    Parameters:
        cmap (str | matplotlib.colors.Colormap | list | None):
            - If a `Colormap`, return it.
            - If a `str`, return matching custom color map or
              if not matching look it up in `cmcrameri.cm.cmaps`
              and `matplotlib.colormaps`.
            - If a `list` of colors, create a corresponding descrete color map.
            - If None, return the Colormap defined in `image.cmap`.
    Returns:
        cmap (Cmap):
            A color map matching the given `cmap`.
    """
    if isinstance(cmap, Cmap):
        return cmap.copy()
    if isinstance(cmap, list):
        cmap = ListedColormap(cmap)
    return Cmap.from_colormap(_get_cmap(cmap))
