import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from .cmap import Cmap


cmap_data_mie = [
    [-3, "#E6E6E6", "Missing"],
    [-2, "#000000", "Surface"], 
    [-1, "#999999", "Attenuated"],
    [0,  "#FFFFFF", "Clear"],
    [1,  "#a1d99b", "Cloud/Aerosol"],
]

def get_cmap_mie():
    colors = [c for _, c, _ in cmap_data_mie]
    definitions = {k: l for k, _, l in cmap_data_mie}
    cmap = Cmap(colors=colors, name="atl_status_mie").to_categorical(definitions)
    return cmap

cmap_data_rayleigh = [
    [-3, "#E6E6E6", "Missing"],
    [-2, "#000000", "Surface"], 
    [-1, "#999999", "Attenuated"],
    [1,  "#b1c59b", "Not attenuated"],
]

def get_cmap_rayleigh():
    colors = [c for _, c, _ in cmap_data_rayleigh]
    definitions = {k: l for k, _, l in cmap_data_rayleigh}
    cmap = Cmap(colors=colors, name="atl_status_rayleigh").to_categorical(definitions)
    return cmap

cmap_data_extq = [
    [0, "#b3de69", "Nominal"],
    [1, "#8dd3c7", "Good, no layers"], 
    [2, "#e78ac3", "OE not convered"],
    [100,  "#fc8d62", "Warning max layers"],
    [102,  "#e41a1c", "OE not conv. + max layer"],
    [200,  "#666666", "L1 issue"],
]

def get_cmap_extq():
    colors = [c for _, c, _ in cmap_data_extq]
    definitions = {k: l for k, _, l in cmap_data_extq}
    cmap = Cmap(colors=colors, name="atl_status_extq").to_categorical(definitions)
    return cmap

cmap_data_q = [
    [0, "#b3de69", "Good, Nominal"],
    [1, "#8dd3c7", "Likely good"], 
    [2, "#e78ac3", "Likely bad"],
    [3,  "#fc8d62", "Bad"],
    [4,  "#666666", "L1 missing"],
]

def get_cmap_q():
    colors = [c for _, c, _ in cmap_data_q]
    definitions = {k: l for k, _, l in cmap_data_q}
    cmap = Cmap(colors=colors, name="atl_status_q").to_categorical(definitions)
    return cmap