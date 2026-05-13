# from typing import Literal, Sequence

import numpy as np
from matplotlib.colors import Colormap, LinearSegmentedColormap


def _shift_mpl_colormap(
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

    n: int = cmap.N
    new_range = np.linspace(start, stop, n)
    old_range = np.empty_like(new_range)

    lower = new_range <= midpoint
    upper = ~lower

    old_range[lower] = np.interp(new_range[lower], [0.0, midpoint], [0.0, 0.5])
    old_range[upper] = np.interp(new_range[upper], [midpoint, 1.0], [0.5, 1.0])

    colors = cmap(old_range)
    return LinearSegmentedColormap.from_list(name=name, colors=colors, N=n)
