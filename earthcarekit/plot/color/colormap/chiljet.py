import numpy as np
from matplotlib.colors import Colormap, LinearSegmentedColormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex


def get_cmap():
    name = "chiljet"
    colors = [
        "#DEDEDE",
        "#0000FF",
        "#009E9E",
        "#00FF00",
        "#FEFE00",
        "#FE7E00",
        "#FF0000",
        "#7E007E",
    ]
    positions = [
        0.0,
        0.234375,
        0.359375,
        0.484375,
        0.609375,
        0.734375,
        0.859375,
        1.0,
    ]
    color_dict = list(zip(positions, colors))
    cmap = LinearSegmentedColormap.from_list(name, color_dict)
    return cmap
