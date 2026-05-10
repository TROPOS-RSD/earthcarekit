"""
**earthcarekit.site**

Ground site utilities.

## Notes

This module does not depend on other internal modules.

---
"""

from ._registry import SITES, get_site
from ._site import Site

__all__ = ["Site", "get_site", "SITES"]

_DEPRECATED = {
    "GroundSite": Site,
    "get_ground_site": get_site,
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
