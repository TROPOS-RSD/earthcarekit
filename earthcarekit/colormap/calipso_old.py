from pathlib import Path

import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ..color import Color


def get_color_list_old(low_value_alpha: float = 1.0) -> list[tuple[int, Color]]:
    return [
        (1, Color("#002BBB").set_alpha(low_value_alpha)),
        (2, Color("#002BBB").set_alpha(low_value_alpha)),
        (3, Color("#0B7DF7")),
        (4, Color("#06A7FF")),
        (5, Color("#02D0FF")),
        (6, Color("#13F5FE")),
        (7, Color("#09F8CF")),
        (8, Color("#02FCA8")),
        (9, Color("#107682")),
        (10, Color("#00A850")),
        (11, Color("#FAFF0F")),
        (12, Color("#FAFE04")),
        (13, Color("#FCD40B")),
        (14, Color("#FBAD03")),
        (15, Color("#F68200")),
        (16, Color("#EA5B00")),
        (17, Color("#E80800")),
        (18, Color("#FE2C53")),
        (19, Color("#F45C7F")),
        (20, Color("#FE7BA8")),
        (21, Color("#474747")),
        (22, Color("#656565")),
        (23, Color("#818181")),
        (24, Color("#9E9E9E")),
        (25, Color("#B6B6B6")),
        (26, Color("#C5C5C5")),
        (27, Color("#D5D5D5")),
        (28, Color("#EAEAEA")),
        (29, Color("#EEEEEE")),
        (30, Color("#F3F3F3")),
        (31, Color("#F6F6F6")),
        (32, Color("#F8F8F8")),
        (33, Color("#FCFCFC")),
        (34, Color("#FFFFFF")),
    ]


def get_cmap(low_value_alpha: float = 1.0) -> Colormap:
    """Creates the Calipso color map."""
    calipso_colors = get_color_list_old(low_value_alpha)

    bounds = np.append(0, [c[0] for c in calipso_colors])
    colors = np.array([c[1] for c in calipso_colors])
    bad_color = calipso_colors[0][1]

    color_list = np.concatenate([[colors[i]] * (count) for i, count in enumerate(np.diff(bounds))])
    return ListedColormap(
        name=Path(__file__).stem,
        colors=color_list,
    ).with_extremes(bad=bad_color)
