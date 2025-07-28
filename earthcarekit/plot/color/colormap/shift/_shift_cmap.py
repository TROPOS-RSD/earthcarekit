from typing import Literal, Sequence

import matplotlib.colors
import numpy as np
from matplotlib.colors import Colormap

from ..cmap import Cmap
from ._basic_mpl_shift_colormap import shift_mpl_colormap


def shift_cmap(
    cmap: str | Colormap | None,
    start: float = 0.0,
    midpoint: float = 0.5,
    stop: float = 1.0,
    name: str = "shifted_cmap",
) -> Cmap:
    """Create a colormap with its center point shifted to a specified value.

    This function is useful for data with asymmetric ranges (e.g., negative min and
    positive max) where you want the center of the colormap to align with a specific
    value like zero.

    Args:
        cmap (str | Colormap | None): Colormap to be modified
        start (float): Lower bound of the colormap range (value between 0 and `midpoint`). Defaults to 0.0.
        midpoint (float): New center point of the colormap (value between 0 and 1). Defaults to 0.5.
            For data ranging from vmin to vmax where you want the center at value v,
            set midpoint = 1 - vmax/(vmax + abs(vmin))
        stop (float): Upper bound of the colormap range (value between `midpoint` and 1). Defaults to 1.0.
        name (str): Name of the new colormap. Defaults to "shifted_cmap".

    Returns:
        Cmap: New colormap with shifted center
    """
    from ..colormap import get_cmap

    cmap = get_cmap(cmap)
    cmap = shift_mpl_colormap(
        cmap,
        start=start,
        midpoint=midpoint,
        stop=stop,
        name=name,
    )
    cmap = get_cmap(cmap)

    return cmap
