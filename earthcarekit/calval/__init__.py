"""
**earthcarekit.calval**

Functions for EarthCARE calibration and validation.

## Notes

This module depends on other internal modules:

- [earthcarekit.constants][]
- [earthcarekit.filter][]
- [earthcarekit.plot][]
- [earthcarekit.data][]
- [earthcarekit.read][]
- [earthcarekit.site][]
- [earthcarekit.typing][]
- [earthcarekit.utils][]

---
"""

from ._compare_bsc_ext_lr_depol import compare_bsc_ext_lr_depol
from ._compute_anom_depol_statistics import compute_anom_depol_statistics

__all__ = [
    "compare_bsc_ext_lr_depol",
    "compute_anom_depol_statistics",
]

_DEPRECATED = {
    "perform_anom_depol_statistics": compute_anom_depol_statistics,
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
