import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from .cmap import Cmap

# Colormap self-designed
cmap_data_detection = [
    [-1, "#999999", "Not detected"],
    [0, "#a65628", "Ground"],
    [1, "#ffffff", "Clear"],
    [2, "#636363", "Extinguished"],
    [3, "#7b4173", "Likely extinguished"],
    [4, "#1e206e", "Target det., no reliable meas."],
    [5, "#9c9ede", "Target det., only refl. reliable"],
    [6, "#6b5ecf", "Target det., refl. enhanced MS"],
    [7, "#c6dbef", "Target det., only Doppler reliable"],
    [8, "#c7e9c0", "Target det., both reliable"],
    [9, "#e7ba52", "Ground clutter (separated)"],
    [10, "#c49c94", "Ground clutter (overlapping)"],
    [11, "#fd8d3c", "Uncertain"],
    [12, "#e7969c", "Second-trip echo"],
]


def get_cmap_detection():
    colors = [c for _, c, _ in cmap_data_detection]
    definitions = {k: l for k, _, l in cmap_data_detection}
    cmap = Cmap(colors=colors, name="cpr_status_detection").to_categorical(definitions)
    return cmap


# Colormap self-designed
cmap_data_multi_scat = [
    [0, "#ffffff", "Not detmined"],
    [1, "#aec7e8", "Single scat."],
    [2, "#6b5ecf", "Moderate multi. scat."],
    [3, "#393b79", "Strong multi. scat."],
]


def get_cmap_multi_scat():
    colors = [c for _, c, _ in cmap_data_multi_scat]
    definitions = {k: l for k, _, l in cmap_data_multi_scat}
    cmap = Cmap(colors=colors, name="cpr_status_multi_scat").to_categorical(definitions)
    return cmap
