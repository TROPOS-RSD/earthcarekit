"""
**earthcarekit.colormap**

Colormap utilities.

## Notes

This module depends on other internal modules:

- [earthcarekit.color][]
- [earthcarekit.constants][]

---
"""

from matplotlib.colors import Colormap

from ._cmap import Cmap
from ._get_cmap import _get_custom_cmaps, get_cmap, rename_cmap
from .shift import shift_cmap

cmaps: dict[str, Colormap] = _get_custom_cmaps()
"""List of custom colormaps for earthcarekit."""

__all__ = [
    "Cmap",
    "get_cmap",
    "rename_cmap",
    "shift_cmap",
]
