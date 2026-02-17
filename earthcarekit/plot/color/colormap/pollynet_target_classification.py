import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap

cmap_data = [
    [0, "#FFFFFF", "No signal"],
    [1, "#E6E6E6", "Clean atmosphere"],
    [2, "#999999", "Non-typed particles/low conc."],
    [3, "#DDCC78", "Aerosol: small"],
    [4, "#E76E2E", "Aerosol: large, spherical"],
    [5, "#882100", "Aerosol: mixture, partly non-spherical"],
    [6, "#000000", "Aerosol: large, non-spherical"],
    [7, "#781C82", "Cloud: non-typed"],
    [8, "#3A8AC9", "Cloud: water droplets"],
    [9, "#B4DEF7", "Cloud: likely water droplets"],
    [10, "#117833", "Cloud: ice crystals"],
    [11, "#86BA6B", "Cloud: likely ice crystals"],
]


def get_cmap():
    colors = [c for _, c, _ in cmap_data]
    definitions = {k: l for k, _, l in cmap_data}
    cmap = (
        Cmap(colors=colors, name="polly_tc")
        .to_categorical(definitions)
        .with_extremes(under="#FFFFFF00", over="#FFFFFF00")
    )
    return cmap
