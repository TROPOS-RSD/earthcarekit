import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap

cmap_data = [
    [-3, "#000000", "Surface", "_missing"],
    [-2, "#FFFFFF", "No retrievals", "_missing"],
    [-1, "#283E91", "Attenuated", "_attenuated"],
    [0, "#31BAF0", "Clear sky", "_clear"],
    [1, "#76CFDF", "Likely clear sky", "_clear"],
    [2, "#88D4E4", "Likely clear sky", "_clear"],
    [3, "#98DAE8", "Likely clear sky", "_clear"],
    [4, "#A4DDF0", "Likely clear sky", "_clear"],
    [5, "#BCB8B8", "Low altitude aerosols", ""],
    [6, "#F0DA13", "Aerosol/thin cloud", ""],
    [7, "#F3AA19", "Aerosol/thin cloud", ""],
    [8, "#CD7320", "Thick aerosol/cloud", ""],
    [9, "#F32320", "Thick aerosol/cloud", ""],
    [10, "#9F1D24", "Thick cloud", ""],
]


def apply_alpha(t, kw):
    """apply cmap_data tupel t from the keyword arg dict"""
    return Color(t[1]).set_alpha(kw[f"alpha{t[3]}"])


def get_cmap(
    alpha_clear: float = 1.0,
    alpha_missing: float = 1.0,
    alpha_attenuated: float = 1.0,
    alpha: float = 1.0,
):
    kw = locals()
    colors = [apply_alpha(t, kw) for t in cmap_data]
    definitions: dict = {k: l for k, _, l, _ in cmap_data}
    cmap = Cmap(colors=colors, name="featuremask").to_categorical(definitions)
    return cmap
