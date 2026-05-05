"""
**earthcarekit.swath**

Swath data utilities.

## Notes

This module depends on other internal modules:

- [earthcarekit.constants][]
- [earthcarekit.geo][]
- [earthcarekit.typing][]
- [earthcarekit.utils][]

---
"""

from ._across_track_distance import (
    add_across_track_distance,
    add_nadir_track,
    add_nadir_var,
    drop_samples_with_missing_geo_data_along_track,
    get_nadir_index,
)
from ._swath_data import SwathData

__all__ = [
    "add_across_track_distance",
    "get_nadir_index",
    "SwathData",
]
