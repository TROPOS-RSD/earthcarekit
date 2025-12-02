import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap


def get_cmap_msi_surface_classification():
    colors = [
        "#808080",
        "#010080",
        "#FF6448",
        "#FFD801",
        "#008001",
        "#81007F",
        "#9470DC",
        "#FEA501",
        "#8C0001",
    ]
    cmap = Cmap(
        name="msi_surface_classification",
        colors=colors,
    ).to_categorical(
        {
            0: "Undefined",
            1: "Water",
            2: "Land",
            3: "Desert",
            4: "Vegetation NDVI",
            5: "Snow XMET",
            6: "Snow NDSI",
            7: "Sea ice XMET",
            8: "Sunglint",
        }
    )
    return cmap


def get_cmap_msi_cloud_phase():
    colors = [
        "#dedede",
        "#1192e8",
        "#93fbff",
        "#123598",
        "#ff2a55",
    ]
    cmap = Cmap(
        name="msi_cloud_phase",
        colors=colors,
    ).to_categorical(
        {
            -127: "Not determined",
            1: "Water",
            2: "Ice",
            3: "S'cooled",
        }
    )
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
