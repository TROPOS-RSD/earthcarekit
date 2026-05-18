"""
**earthcarekit.data.profile**

Atmospheric vertical profile data utilities.

## Notes

This module depends on other internal modules:

- [earthcarekit.constants][]
- [earthcarekit.geo][]
- [earthcarekit.utils][]
- [earthcarekit.typing][]

---
"""

from ._profile_data import Profile
from ._validate_dimensions import (
    ensure_along_track_2d,
    ensure_vertical_2d,
    validate_profile_data_dimensions,
)

_DEPRECATED = {
    "ProfileData": Profile,
}


def __getattr__(name):
    import warnings

    if name in _DEPRECATED:
        warnings.warn(
            f"'{name}' is deprecated; use '{_DEPRECATED[name].__name__}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return _DEPRECATED[name]

    raise AttributeError(name)
