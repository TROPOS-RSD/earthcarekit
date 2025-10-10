import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap

_COLORS = [
    "#E6E6E6",
    "#FFFFFF",
    "#0B4D79",
    "#17BECF",
    "#93FBFF",
    "#2CA02C",
    "#FFFF9A",
    "#E5AE38",
    "#FF7E0E",
    "#D62628",
    "#5D003F",
]


def get_cmap():
    colors = _COLORS
    definitions = {
        -127: "No data",
        0: "Clear",
        1: "Cumulus",
        2: "Altocumulus",
        3: "Cirrus",
        4: "Stratocumulus",
        5: "Altostratus",
        6: "Cirrostratus",
        7: "Stratus",
        8: "Nimbostratus",
        9: "Deep convection",
    }

    cmap = (
        Cmap(
            colors=colors,
            name="msi_cloud_type",
        )
        .to_categorical(definitions)
        .with_extremes(under="#FFFFFF00", over="#FFFFFF00")
    )
    return cmap


def get_cmap_with_short_labels():
    colors = _COLORS
    definitions = {
        -127: "No data",
        0: "Clear",
        1: "Cu",
        2: "Ac",
        3: "Ci",
        4: "Sc",
        5: "As",
        6: "Cs",
        7: "St",
        8: "Ns",
        9: "Dcv",
    }

    cmap = (
        Cmap(
            colors=colors,
            name="msi_cloud_type_short_labels",
        )
        .to_categorical(definitions)
        .with_extremes(under="#FFFFFF00", over="#FFFFFF00")
    )
    return cmap
