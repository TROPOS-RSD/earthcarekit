from pathlib import Path

import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color


def get_color_list_ectools(low_value_alpha: float = 1.0) -> list[tuple[int, Color]]:
    """
    Based on color index values from the calipso colormap in the 'ectools' project by Shannon Mason (ECMWF):
    https://bitbucket.org/smason/workspace/projects/EC
    Original under Apache 2.0 license.
    """
    return [
        (34, Color("#123598").set_alpha(low_value_alpha)),  # original value: #002BBB
        (76, Color("#007fff").set_alpha(low_value_alpha)),
        (79, Color("#00ffaa")),
        (82, Color("#007f7f")),
        (86, Color("#00aa55")),
        (101, Color("#ffff00")),
        (110, Color("#ffe600")),
        (119, Color("#ffd400")),
        (128, Color("#ffaa00")),
        (134, Color("#ff7f00")),
        (140, Color("#ff5500")),
        (146, Color("#ff0000")),
        (152, Color("#ff2a55")),
        (155, Color("#ff557f")),
        (158, Color("#ff7faa")),
        (161, Color("#464646")),
        (164, Color("#5a5a5a")),
        (167, Color("#6e6e6e")),
        (170, Color("#828282")),
        (176, Color("#969696")),
        (182, Color("#aaaaaa")),
        (188, Color("#b4b4b4")),
        (194, Color("#bebebe")),
        (200, Color("#c8c8c8")),
        (206, Color("#d2d2d2")),
        (212, Color("#d7d7d7")),
        (218, Color("#dcdcdc")),
        (224, Color("#e1e1e1")),
        (230, Color("#e6e6e6")),
        (236, Color("#ebebeb")),
        (243, Color("#f0f0f0")),
        (250, Color("#f5f5f5")),
        (257, Color("#ffffff")),
    ]


def get_cmap(low_value_alpha: float = 1.0) -> Colormap:
    """Creates the Calipso color map."""
    calipso_colors = get_color_list_ectools(low_value_alpha)

    bounds = np.append(0, [c[0] for c in calipso_colors])
    colors = np.array([c[1] for c in calipso_colors])
    bad_color = calipso_colors[0][1]

    color_list = np.concatenate([[colors[i]] * (count) for i, count in enumerate(np.diff(bounds))])
    return ListedColormap(color_list, name=Path(__file__).stem).with_extremes(bad=bad_color)
