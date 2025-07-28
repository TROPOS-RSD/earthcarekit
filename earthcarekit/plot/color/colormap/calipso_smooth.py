import numpy as np
from matplotlib.colors import Colormap, LinearSegmentedColormap, ListedColormap

from ..color import Color
from ..format_conversion import alpha_to_hex


def get_color_list():
    """
    Based on color index values from the calipso colormap in the 'ectools' project by Shannon Mason (ECMWF):
    https://bitbucket.org/smason/workspace/projects/EC
    Original under Apache 2.0 license.
    """
    colors = [
        (0.000, Color("#123598")),
        (0.066, Color("#0C3AB8")),
        (0.214, Color("#007FFF")),
        (0.286, Color("#007FFF")),
        (0.302, Color("#00FFAA")),
        (0.313, Color("#007F7F")),
        (0.327, Color("#00AA55")),
        (0.339, Color("#FFFF00")),
        (0.364, Color("#FFFF00")),
        (0.411, Color("#FFE600")),
        (0.446, Color("#FFD400")),
        (0.481, Color("#FFAA00")),
        (0.510, Color("#FF7F00")),
        (0.533, Color("#FF5500")),
        (0.556, Color("#FF0000")),
        (0.580, Color("#FF2A55")),
        (0.597, Color("#FF557F")),
        (0.609, Color("#FF7FAA")),
        (0.621, Color("#464646")),
        (0.632, Color("#5A5A5A")),
        (0.644, Color("#6E6E6E")),
        (0.656, Color("#828282")),
        (0.673, Color("#969696")),
        (0.696, Color("#AAAAAA")),
        (0.720, Color("#B4B4B4")),
        (0.743, Color("#BEBEBE")),
        (0.767, Color("#C8C8C8")),
        (0.790, Color("#D2D2D2")),
        (0.813, Color("#D7D7D7")),
        (0.837, Color("#DCDCDC")),
        (0.860, Color("#E1E1E1")),
        (0.883, Color("#E6E6E6")),
        (0.907, Color("#EBEBEB")),
        (0.932, Color("#F0F0F0")),
        (0.959, Color("#F5F5F5")),
        (0.986, Color("#FFFFFF")),
        (1.000, Color("#FFFFFF")),
    ]
    return colors


def get_cmap() -> Colormap:
    """Creates the Calipso color map."""
    colors = get_color_list()
    cmap = LinearSegmentedColormap.from_list(
        "calipso_smooth", colors, N=256
    ).with_extremes(bad=colors[0][1])
    return cmap
