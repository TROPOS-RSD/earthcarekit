"""
**earthcarekit.profile**

Atmospheric vertical profile data utilities.

## Notes

This module depends on other internal modules:

- [earthcarekit.constants][]
- [earthcarekit.geo][]
- [earthcarekit.utils][]
- [earthcarekit.typing][]

---
"""

from ._profile_data import ProfileData
from ._validate_dimensions import (
    ensure_along_track_2d,
    ensure_vertical_2d,
    validate_profile_data_dimensions,
)
