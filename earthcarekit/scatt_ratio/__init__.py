"""
**earthcarekit.scatt_ratio**

Provides functions to compute scattering ratios from attenuated backscatter signals.

## Notes

This module depends on other internal modules:

- [earthcarekit.utils][]

---
"""

from ._scatt_ratio import (
    RatioType,
    RatioTypeLike,
    ScattRatioResult,
    add_depol_ratio,
    add_scatt_ratio,
    calc_bsr,
    calc_bsr_m1,
    calc_pdr,
    calc_scatt_ratio,
    calc_sr,
    get_depol_profile,
)

__all__ = [
    "RatioType",
    "RatioTypeLike",
    "ScattRatioResult",
    "add_depol_ratio",
    "add_scatt_ratio",
    "calc_bsr",
    "calc_bsr_m1",
    "calc_pdr",
    "calc_scatt_ratio",
    "calc_sr",
    "get_depol_profile",
]
