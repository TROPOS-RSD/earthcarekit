"""
**earthcarekit.data.swath**

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
from ._swath_data import Swath

__all__ = [
    "add_across_track_distance",
    "get_nadir_index",
    "Swath",
]

_DEPRECATED = {
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
