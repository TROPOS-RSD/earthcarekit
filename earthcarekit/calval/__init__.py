"""
**earthcarekit.calval**

Functions for EarthCARE calibration and validation.

## Notes

This module depends on other internal modules:

- [earthcarekit.constants][]
- [earthcarekit.filter][]
- [earthcarekit.plot][]
- [earthcarekit.profile][]
- [earthcarekit.read][]
- [earthcarekit.site][]
- [earthcarekit.typing][]
- [earthcarekit.utils][]

---
"""

from ._compare_bsc_ext_lr_depol import compare_bsc_ext_lr_depol
from ._perform_anom_depol_statistics import perform_anom_depol_statistics

__all__ = [
    "compare_bsc_ext_lr_depol",
    "perform_anom_depol_statistics",
]
