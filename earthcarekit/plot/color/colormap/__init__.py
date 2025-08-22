from matplotlib.colors import Colormap

from .cmap import Cmap
from .colormap import _get_custom_cmaps, get_cmap, rename_cmap
from .shift import shift_cmap

cmaps: dict[str, Colormap] = _get_custom_cmaps()
"""List of custom colormaps for earthcarekit."""
