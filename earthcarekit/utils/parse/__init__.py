"""
**earthcarekit.utils.parse**

String parsing utilities.

## Notes

This module does not depend on other internal modules.

---
"""

from .filename import get_file_info_from_str
from .url import is_url

__all__ = ["is_url", "get_file_info_from_str"]
