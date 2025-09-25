import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap


def get_cmap():
    colors = [
        "#FFFFFF",
        "#E6E6E6",
        "#999999",
        "#DDCC78",
        "#E76E2E",
        "#882100",
        "#000000",
        "#781C82",
        "#3A8AC9",
        "#B4DEF7",
        "#117833",
        "#86BA6B",
    ]

    definitions = {
        0: "No signal",
        1: "Clean atmosphere",
        2: "Non-typed particles/low conc.",
        3: "Aerosol: small",
        4: "Aerosol: large, spherical",
        5: "Aerosol: mixture, partly non-spherical",
        6: "Aerosol: large, non-spherical",
        7: "Cloud: non-typed",
        8: "Cloud: water droplets",
        9: "Cloud: likely water droplets",
        10: "Cloud: ice crystals",
        11: "Cloud: likely ice crystals",
    }

    cmap = (
        Cmap(
            colors=colors,
            name="polly_tc",
        )
        .to_categorical(definitions)
        .with_extremes(under="#FFFFFF00", over="#FFFFFF00")
    )
    return cmap
