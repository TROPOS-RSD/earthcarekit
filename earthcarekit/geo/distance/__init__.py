"""
**earthcarekit.geo.distance**

Algorithms to calculate geospatial distances.

## Notes

This module depends on other internal modules:

- [earthcarekit.constants][]

---
"""

from ._cumulative import get_cumulative_distances
from ._haversine import haversine
from ._vincenty import vincenty
from ._vincenty import vincenty as geodesic

__all__ = [
    "get_cumulative_distances",
    "haversine",
    "vincenty",
    "geodesic",
]
