import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from .cmap import Cmap

# Colormap self-designed
cmap_data_status = [
    [-4, "#000000", "No info"],
    [-3, "#542d16", "Subsurface (both)"],
    [-2, "#a6761d", "Subsurface (lidar)"],
    [-1, "#6e5526", "Subsurface (radar)"],
    [0, "#999999", "Unassigned"],
    [1, "#ffffff", "Clear (both)"],
    [2, "#fead5c", "Clear (lidar)"],
    [3, "#fff4c2", "Clear (radar)"],
    [4, "#56c749", "Target (both)"],
    [5, "#bbb47b", "Target (lidar)"],
    [6, "#31a354", "Target (radar)"],
]


def get_cmap_status():
    colors = [c for _, c, _ in cmap_data_status]
    definitions = {k: l for k, _, l in cmap_data_status}
    cmap = Cmap(colors=colors, name="synergetic_status").to_categorical(definitions)
    return cmap


# Colormap from ACTC file baseline BC
cmap_data_quality = [
    [0, "#a2653e", "Surface (high conf."],
    [1, "#ffffff", "Clear (high conf.)"],
    [2, "#75bbfd", "Hydrometeor (high conf. both)"],
    [3, "#d0fefe", "Hydrometeor (high conf. lidar-only)"],
    [4, "#ff000d", "Aerosol (mod conf.)"],
    [5, "#01ff07", "Stratosphere (mod conf.)"],
    [6, "#ffffe4", "Clear (mod conf. lidar only)"],
    [7, "#c7fdb5", "Stratosphere (mod conf. lidar only)"],
    [8, "#0165fc", "Hydrometeor (mod conf.)"],
    [9, "#fdfdfe", "Clear (mod conf.)"],
    [10, "#d8dcd6", "Clear (low conf.)"],
    [11, "#04d9ff", "Hydrometeor (low conf.)"],
    [12, "#929591", "Unknown (low conf.)"],
    [13, "#7a9703", "Radar artefact (low conf.)"],
    [14, "#03012d", "Extinguished (low conf.)"],
    [15, "#cfaf7b", "Surface (low conf.)"],
    [16, "#bf00bf", "No data"],
]


def get_cmap_quality():
    colors = [c for _, c, _ in cmap_data_quality]
    definitions = {k: l for k, _, l in cmap_data_quality}
    cmap = Cmap(colors=colors, name="synergetic_quality").to_categorical(definitions)
    return cmap


# Colormap self-designed
cmap_data_insect = [
    [-3, "#000000", "No data"],
    [-2, "#65ffff", "Hydrometeors"],
    [-1, "#fff4c2", "No insect (no lidar)"],
    [0, "#ffffff", "No insect (lidar clear)"],
    [1, "#9e669b", "Poss. insects in clutter (no lidar)"],
    [2, "#dcafba", "Poss. insects (no lidar)"],
    [3, "#9e4c37", "Likely insects in clutter"],
    [4, "#eb3e13", "Likely insects"],
]


def get_cmap_insect():
    colors = [c for _, c, _ in cmap_data_insect]
    definitions = {k: l for k, _, l in cmap_data_insect}
    cmap = Cmap(colors=colors, name="synergetic_insect").to_categorical(definitions)
    return cmap
