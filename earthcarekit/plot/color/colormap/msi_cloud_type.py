import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap

cmap_data = [
    [-127, "#E6E6E6", "No data", "No data"],
    [0, "#FFFFFF", "Clear", "Clear"],
    [1, "#0B4D79", "Cumulus", "Cu"],
    [2, "#17BECF", "Altocumulus", "Ac"],
    [3, "#93FBFF", "Cirrus", "Ci"],
    [4, "#2CA02C", "Stratocumulus", "Sc"],
    [5, "#FFFF9A", "Altostratus", "As"],
    [6, "#E5AE38", "Cirrostratus", "Cs"],
    [7, "#FF7E0E", "Stratus", "St"],
    [8, "#D62628", "Nimbostratus", "Ns"],
    [9, "#5D003F", "Deep convection", "Dcv"],
]


def get_cmap():
    colors = [c for _, c, _, _ in cmap_data]
    definitions = {k: l for k, _, l, _ in cmap_data}
    cmap = (
        Cmap(colors=colors, name="msi_cloud_type")
        .to_categorical(definitions)
        .with_extremes(under="#FFFFFF00", over="#FFFFFF00")
    )
    return cmap


def get_cmap_with_short_labels():
    colors = [c for _, c, _, _ in cmap_data]
    definitions = {k: l for k, _, _, l in cmap_data}
    cmap = (
        Cmap(colors=colors, name="msi_cloud_type_short_labels")
        .to_categorical(definitions)
        .with_extremes(under="#FFFFFF00", over="#FFFFFF00")
    )
    return cmap
