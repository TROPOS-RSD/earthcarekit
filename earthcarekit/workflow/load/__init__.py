"""
**earthcarekit.workflow.load**

Convenience functions to locate, download (if needed), and open EarthCARE products.

## Notes

This module does not depend on other internal modules.

- [earthcarekit.download][]
- [earthcarekit.read][]
- [earthcarekit.typing][]
- [earthcarekit.utils][]

---
"""

from ._eclazy import eclazy
from ._ecload import ecload

__all__ = ["eclazy", "ecload"]
