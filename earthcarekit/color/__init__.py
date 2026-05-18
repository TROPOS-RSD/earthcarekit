"""
**earthcarekit.color**

Color utilities.

## Notes

This module does not depend on other internal modules.

---
"""

from ._color import Color, ColorLike
from ._conversion import alpha_to_hex
from ._registry import EC_COLORS

__all__ = [
    "alpha_to_hex",
    "Color",
]
