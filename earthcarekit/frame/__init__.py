"""
**earthcarekit.frame**

Functions for identifying the EarthCARE frame of a dataset and trimming it accordingly.

## Notes

This module depends on other internal modules:

- [earthcarekit.constants][]
- [earthcarekit.utils][]

---
"""

from ._trim import (
    get_frame_id,
    get_frame_index_range,
    get_frame_slice_tuple,
    trim_to_latitude_frame_bounds,
)

__all__ = [
    "get_frame_id",
    "get_frame_index_range",
    "get_frame_slice_tuple",
    "trim_to_latitude_frame_bounds",
]
