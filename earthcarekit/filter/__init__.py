"""
**earthcarekit.filter**

Dataset filtering utilities.

## Notes

This module depends on other internal modules:

- [earthcarekit.constants][]
- [earthcarekit.geo][]
- [earthcarekit.site][]
- [earthcarekit.typing][]
- [earthcarekit.utils][]

---
"""

from ._exception import EmptyFilterResultError
from ._filter_index import filter_index
from ._filter_latitude import filter_latitude
from ._filter_radius import filter_radius
from ._filter_time import filter_time, get_filter_time_mask

__all__ = [
    "filter_index",
    "filter_latitude",
    "filter_radius",
    "filter_time",
]
