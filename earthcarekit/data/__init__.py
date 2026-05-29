"""
**earthcarekit.data**

Containers and utilities for atmospheric data, including vertically
resolved profiles and satellite imager swath data.

## Notes

This module depends on other internal modules:

- [earthcarekit.constants][]
- [earthcarekit.geo][]
- [earthcarekit.utils][]
- [earthcarekit.typing][]

---
"""

from .profile import Profile
from .swath import Swath

_DEPRECATED = {
    "ProfileData": Profile,
    "SwathData": Swath,
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
