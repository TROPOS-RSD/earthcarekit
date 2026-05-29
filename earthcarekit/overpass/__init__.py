"""
**earthcarekit.overpass**

Utilities for processing satellite overpasses relative to ground stations.

## Notes

This module depends on other internal modules:

- [earthcarekit.constants][]
- [earthcarekit.filter][]
- [earthcarekit.geo][]
- [earthcarekit.read][]
- [earthcarekit.site][]
- [earthcarekit.utils][]

---
"""

from ._overpass_info import OverpassInfo, get_closest_distance, get_overpass_info

__all__ = [
    "OverpassInfo",
    "get_closest_distance",
    "get_overpass_info",
]
