from dataclasses import dataclass

import numpy as np
from matplotlib.colors import Colormap, LinearSegmentedColormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap

_COLORS_PANOPLY = [
    "#0000CC",
    "#050FD9",
    "#2050FF",
    "#4297FF",
    "#6DC1FF",
    "#86DAFF",
    "#9DEFFF",
    "#AFF6FF",
    "#CFFFFF",
    "#F9F964",
    "#FFEC00",
    "#FFC400",
    "#FF9000",
    "#FF4900",
    "#FF0000",
    "#D50000",
    "#9F0000",
    "#800000",
]
_COLORS_PANOPLY16 = _COLORS_PANOPLY[1:17]


def get_cmap_panoply():
    name = "panoply"
    colors = _COLORS_PANOPLY
    cmap = Cmap(
        name=name,
        colors=colors,
        gradient=True,
    )
    return cmap


def get_cmap_panoply16():
    name = "panoply16"
    colors = _COLORS_PANOPLY16
    cmap = Cmap(
        name=name,
        colors=colors,
        gradient=False,
    )
    cmap.set_extremes(
        under=_COLORS_PANOPLY[0],
        over=_COLORS_PANOPLY[-1],
    )
    return cmap
