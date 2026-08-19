from matplotlib.colors import Colormap

from ._cmap import Cmap
from ._shift_mpl_cmap import shift_mpl_colormap


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
        cmap: Colormap to be modified
        start: Lower bound of the colormap range (value between 0 and `midpoint`); defaults to 0.0.
        midpoint: New center point of the colormap (value between 0 and 1); defaults to 0.5.
            For data ranging from vmin to vmax where you want the center at value v,
            set midpoint = 1 - vmax/(vmax + abs(vmin))
        stop: Upper bound of the colormap range (value between `midpoint` and 1); defaults to 1.0.
        name: Name of the new colormap; defaults to "shifted_cmap".

    Returns:
        New colormap with shifted center
    """
    from ._get_cmap import get_cmap

    cmap_old = get_cmap(cmap)
    cmap_new = shift_mpl_colormap(
        cmap_old,
        start=start,
        midpoint=midpoint,
        stop=stop,
        name=name,
    )
    cmap_new = get_cmap(cmap_new)
    cmap_new.categorical = cmap_old.categorical
    cmap_new.ticks = cmap_old.ticks
    cmap_new.labels = cmap_old.labels
    cmap_new.norm = cmap_old.norm
    cmap_new.values = cmap_old.values
    cmap_new.gradient = cmap_old.gradient
    cmap_new.circular = cmap_old.circular
    return cmap_new
