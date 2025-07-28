from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

import numpy as np
from cmcrameri import cm as cmcramericm  # type: ignore
from matplotlib import colormaps as mpl_cmaps
from matplotlib.cm import ScalarMappable
from matplotlib.colors import (
    BoundaryNorm,
    Colormap,
    LinearSegmentedColormap,
    ListedColormap,
    Normalize,
)

from ....utils.constants import DEFAULT_CMAP
from ..color import Color
from .calipso import get_cmap as get_cmap_calipso
from .calipso import get_cmap_calipso_old
from .calipso_smooth import get_cmap as get_cmap_calipso_smooth
from .chiljet import get_cmap as get_cmap_chiljet
from .chiljet2 import get_cmap as get_cmap_chiljet2
from .cmap import Cmap
from .doppler_velocity import get_cmap as get_cmap_doppler_velocity
from .ggplot_like_hcl import get_cmaps as get_ggplot_like_hcl_cmaps
from .hsl import get_cmap as get_cmap_hsl
from .labview import get_cmap as get_cmap_labview
from .plotly_colormaps import get_all_plotly_cmaps
from .radar_reflectivity import get_cmap as get_cmap_radar_reflectivity
from .simple_classification import get_cmap as get_cmap_simple_classification
from .synergistic_target_classification import (
    get_cmap as get_cmap_synergistic_target_classification,
)
from .target_classification import get_cmap as get_cmap_target_classification


def rename_cmap(cmap: Colormap, name: str) -> Colormap:
    """Returns the given `cmap` with the new `name`."""
    result_cmap = cmap.copy()
    result_cmap.name = name
    return result_cmap


_cmaps = [
    get_cmap_calipso(),
    get_cmap_calipso_old(),
    get_cmap_calipso_smooth(),
    get_cmap_labview(),
    get_cmap_chiljet(),
    get_cmap_chiljet2(),
    get_cmap_hsl(),
    get_cmap_simple_classification(),
    get_cmap_synergistic_target_classification(),
    get_cmap_target_classification(),
    get_cmap_radar_reflectivity(),
    get_cmap_doppler_velocity(),
    rename_cmap(cmcramericm.lipari.with_extremes(bad="black"), name="ray"),
    rename_cmap(
        cmcramericm.roma_r.with_extremes(bad=cmcramericm.roma_r(0)), name="ratio"
    ),
    rename_cmap(mpl_cmaps.get_cmap("YlOrRd"), "fire"),
    rename_cmap(mpl_cmaps.get_cmap("YlOrRd"), "heat"),
    *get_ggplot_like_hcl_cmaps(),
]


def _get_custom_cmaps() -> dict[str, Colormap]:
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
    if isinstance(cmap, list):
        cmap = ListedColormap(cmap)
    return Cmap.from_colormap(_get_cmap(cmap))
