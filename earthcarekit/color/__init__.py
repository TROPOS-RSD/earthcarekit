"""
**earthcarekit.color**

Color utilities.

## Notes

This module does not depend on other internal modules.

---
"""

from ._color import Color, ColorLike
from ._conversion import alpha_to_hex

__all__ = [
    "Color",
    "alpha_to_hex",
]
