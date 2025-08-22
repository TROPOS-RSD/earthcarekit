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
        -3: "Surface",
        -2: "No retrievals",
        -1: "Attenuated",
        0: "Clear sky",
        1: "Likely clear sky",
        2: "Likely clear sky",
        3: "Likely clear sky",
        4: "Likely clear sky",
        5: "Low altitude aerosols",
        6: "Aerosol/thin cloud",
        7: "Aerosol/thin cloud",
        8: "Thick aerosol/cloud",
        9: "Thick aerosol/cloud",
        10: "Thick cloud",
    }

    colors = [
        Color("#000000").set_alpha(alpha_missing),  # Surface
        Color("#FFFFFF").set_alpha(alpha_missing),  # No retrievals
        Color("#283E91").set_alpha(alpha_attenuated),  # Attenuated
        Color("#31BAF0").set_alpha(alpha_clear),  # Clear sky
        Color("#76CFDF").set_alpha(alpha_clear),  # Likely clear sky
        Color("#88D4E4").set_alpha(alpha_clear),  # Likely clear sky
        Color("#98DAE8").set_alpha(alpha_clear),  # Likely clear sky
        Color("#A4DDF0").set_alpha(alpha_clear),  # Likely clear sky
        Color("#BCB8B8").set_alpha(alpha),  # Low altitude aerosols
        Color("#F0DA13").set_alpha(alpha),  # Aerosol/thin cloud
        Color("#F3AA19").set_alpha(alpha),  # Aerosol/thin cloud
        Color("#CD7320").set_alpha(alpha),  # Thick aerosol/cloud
        Color("#F32320").set_alpha(alpha),  # Thick aerosol/cloud
        Color("#9F1D24").set_alpha(alpha),  # Thick cloud
    ]
    cmap = Cmap(colors=colors, name="featuremask").to_categorical(definitions)
    return cmap
