import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex
from .cmap import Cmap


def get_cmap_maot_quality_mask():
    colors = [
        "#FFFFFFFF",
        "#1E5EACFF",
        "#2D88BDFF",
        "#4AB1CEFF",
        "#88DAD7FF",
        "#D2D484FF",
        "#C0A242FF",
        "#AB7625FF",
        "#964C13FF",
        "#7D1700FF",
    ]
    cmap = Cmap(
        name="maot_quality_mask",
        colors=colors,
    ).to_categorical(
        {
            0: "Undefined",
            1: "Sus. input",
            2: "Water",
            3: "Land",
            4: "Cloud edge",
            5: "Cloud",
            6: "Algo. converged",
            7: "Homogenious",
            8: "Sus. angstrom",
            9: "Missing lines before",
            10: "Unexp. bright surface",
        }
    )
    return cmap
