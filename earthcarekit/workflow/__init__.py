"""
**earthcarekit.workflow**

Provides high-level workflows that combine multiple operations into convenient,
single-call interfaces.

## Notes

This module depends on other internal modules:

- [earthcarekit.download][]
- [earthcarekit.read][]
- [earthcarekit.typing][]
- [earthcarekit.utils][]

---
"""

from . import load
from .load import eclazy, ecload

__all__ = ["ecload", "eclazy"]
