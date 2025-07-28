from typing import Literal, Sequence

import matplotlib.colors
import numpy as np
from matplotlib.colors import Colormap


def shift_mpl_colormap(
    cmap: Colormap,
    start: float = 0.0,
    midpoint: float = 0.5,
    stop: float = 1.0,
    name: str = "shifted_cmap",
):
    """Create a colormap with its center point shifted to a specified value.

    This function is useful for data with asymmetric ranges (e.g., negative min and
    positive max) where you want the center of the colormap to align with a specific
    value like zero.

    Args:
        cmap (Colormap): Colormap to be modified
        start (float): Lower bound of the colormap range (value between 0 and `midpoint`). Defaults to 0.0.
        midpoint (float): New center point of the colormap (value between 0 and 1). Defaults to 0.5.
            For data ranging from vmin to vmax where you want the center at value v,
            set midpoint = 1 - vmax/(vmax + abs(vmin))
        stop (float): Upper bound of the colormap range (value between `midpoint` and 1). Defaults to 1.0.
        name (str): Name of the new colormap. Defaults to "shifted_cmap".

    Returns:
        matplotlib.colors.LinearSegmentedColormap: New colormap with shifted center
    """

    color_dict: dict[str, list] = {
        "red": [],
        "green": [],
        "blue": [],
        "alpha": [],
    }

    regular_indices = np.linspace(start, stop, 257)

    shifted_indices = np.hstack(
        [
            np.linspace(0.0, midpoint, 128, endpoint=False),
            np.linspace(midpoint, 1.0, 129, endpoint=True),
        ]
    )

    for reg_idx, shift_idx in zip(regular_indices, shifted_indices):
        r, g, b, a = cmap(reg_idx)
        color_dict["red"].append((shift_idx, r, r))
        color_dict["green"].append((shift_idx, g, g))
        color_dict["blue"].append((shift_idx, b, b))
        color_dict["alpha"].append((shift_idx, a, a))

    segmentdata: dict[
        Literal["red", "green", "blue", "alpha"], Sequence[tuple[float, ...]]
    ] = dict(
        red=color_dict["red"],
        green=color_dict["green"],
        blue=color_dict["blue"],
        alpha=color_dict["alpha"],
    )

    new_cmap = matplotlib.colors.LinearSegmentedColormap(name, segmentdata)
    return new_cmap
