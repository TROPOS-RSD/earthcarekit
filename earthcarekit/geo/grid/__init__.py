"""
**earthcarekit.geo.grid**

Geospatial gridding utilities.

## Notes

This module depends on other internal modules:

- [earthcarekit.geo][]
- [earthcarekit.utils.numpy][]

---
"""

from ._create_global_grid import SphericalGrid, create_spherical_grid

__all__ = [
    "SphericalGrid",
    "create_spherical_grid",
]
