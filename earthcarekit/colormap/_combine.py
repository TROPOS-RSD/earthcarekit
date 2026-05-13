import numpy as np
from matplotlib.colors import Colormap, ListedColormap

from ._cmap import Cmap
from ._get_cmap import get_cmap


def combine_cmaps(
    cmap1: str | Colormap | None,
    cmap2: str | Colormap | None,
    name: str = "combined_cmap",
    n: int = 256,
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

    cmap1 = get_cmap(cmap1)
    cmap2 = get_cmap(cmap2)

    n_half, remainder = divmod(n, 2)

    cmap1_colors = cmap1(np.linspace(0.0, 1.0, n_half))
    cmap2_colors = cmap2(np.linspace(0.0, 1.0, n_half + remainder))

    combined_colors = np.vstack((cmap1_colors, cmap2_colors))

    return get_cmap(ListedColormap(combined_colors, name=name))
