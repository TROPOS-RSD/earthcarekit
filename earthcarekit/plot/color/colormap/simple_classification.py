import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap


def get_cmap(
    alpha_clear: float = 1.0,
    alpha_missing: float = 1.0,
    alpha_attenuated: float = 1.0,
    alpha: float = 1.0,
):
    definitions = {
        -3: "Missing",
        -2: "Surface",
        -1: "Attenuated",
        0: "Clear",
        1: "Liquid cloud",
        2: "Ice cloud",
        3: "Aerosol",
        4: "Strat. cloud",
        5: "Strat. aerosol",
    }
    colors = [
        Color("#D3D3D3").set_alpha(alpha_missing),  # Missing
        Color("#000000").set_alpha(alpha),  # Surface
        Color("#696969").set_alpha(alpha_attenuated),  # Attenuated
        Color("#FFFFFF").set_alpha(alpha_clear),  # Clear
        Color("#0000FF").set_alpha(alpha),  # Liquid cloud
        Color("#00FFFF").set_alpha(alpha),  # Ice cloud
        Color("#DEB887").set_alpha(alpha),  # Aerosol
        Color("#800080").set_alpha(alpha),  # Stratospheric cloud
        Color("#FF00FF").set_alpha(alpha),  # Stratospheric aerosol
    ]
    cmap = Cmap(colors=colors, name="simple_classification").to_categorical(definitions)
    return cmap
