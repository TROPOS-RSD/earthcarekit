import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap


cmap_data_sfc_class = [
    [0, "#808080", "Undefined"],
    [1, "#010080", "Water"],
    [2, "#FF6448", "Land"],
    [3, "#FFD801", "Desert"],
    [4, "#008001", "Vegetation NDVI"],
    [5, "#81007F", "Snow XMET"],
    [6, "#9470DC", "Snow NDSI"],
    [7, "#FEA501", "Sea ice XMET"],
    [8, "#8C0001", "Sunglint"],
]

def get_cmap_msi_surface_classification():
    colors = [c for _, c, _ in cmap_data_sfc_class]
    definitions = {k: l for k, _, l in cmap_data_sfc_class}
    cmap = Cmap(colors=colors, name="msi_surface_classification"
                ).to_categorical(definitions)
    return cmap


cmap_data_cloud_phase = [
    [-127, "#dedede", "Not determined"],
    [   1, "#1192e8", "Water"],
    [   2, "#93fbff", "Ice"],
    [   3, "#123598", "S'cooled"],
    [   4, "#ff2a55", "overlap"],
]

def get_cmap_msi_cloud_phase():
    colors = [c for _, c, _ in cmap_data_cloud_phase]
    definitions = {k: l for k, _, l in cmap_data_cloud_phase}
    cmap = Cmap(colors=colors, name="msi_cloud_phase").to_categorical(definitions)
    return cmap

def get_cmap_msi_cloud_mask():
    colors = [
        "#dedede",
        "#123598",
        "#1192e8",
        "#ffaa00",
        "#ff2a55",
    ]
    cmap = Cmap(
        name="msi_cloud_mask",
        colors=colors,
    ).to_categorical(
        {
            -127: "Not determined",
            0: "Clear",
            1: "Prob. clear",
            2: "Prob. cloudy",
            3: "Cloudy",
        }
    )
    return cmap
cmap_data_cloud_mask = [
    [-127, "#dedede", "Not determined"],
    [   0, "#123598", "Clear"],
    [   1, "#1192e8", "Prob. clear"],
    [   2, "#ffaa00", "Prob. cloudy"],
    [   3, "#ff2a55", "Cloudy"],
]

def get_cmap_msi_cloud_mask():
    colors = [c for _, c, _ in cmap_data_cloud_mask]
    definitions = {k: l for k, _, l in cmap_data_cloud_mask}
    cmap = Cmap(colors=colors, name="msi_cloud_mask").to_categorical(definitions)
    return cmap