"""
**earthcarekit.download**

A download tool for EarthCARE data based on ESA MAAP.

## Notes

This module depends on other internal modules:

- [earthcarekit.read][]
- [earthcarekit.utils][]

---
"""

from . import maap
from .main import ecdownload

__all__ = [
    "ecdownload",
    "maap",
]
