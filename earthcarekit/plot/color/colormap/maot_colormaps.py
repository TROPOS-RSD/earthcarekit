import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap

cmap_data = [
    [ 0, "#FFFFFFFF", "Undefined"],
    [ 1, "#1E5EACFF", "Sus. input"],
    [ 2, "#2D88BDFF", "Water"],
    [ 3, "#4AB1CEFF", "Land"],
    [ 4, "#88DAD7FF", "Cloud edge"],
    [ 5, "#D2D484FF", "Cloud"],
    [ 6, "#C0A242FF", "Algo. converged"],
    [ 7, "#AB7625FF", "Homogenious"],
    [ 8, "#964C13FF", "Sus. angstrom"],
    [ 9, "#7D1700FF", "Missing lines before"],
    [10, "#999999FF", "Unexp. bright surface"], # a color was missing for that category
]

def get_cmap_maot_quality_mask():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: l for k, _, l in cmap_data}
    cmap = Cmap(colors=colors, name="maot_quality_mask"
                ).to_categorical(definitions)
    return cmap
