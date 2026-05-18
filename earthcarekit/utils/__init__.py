"""
**earthcarekit.utils**

Collection of basic utility functions.

## Notes

This module depends on other internal modules:

- [earthcarekit.typing][]

---
"""

from . import dict, numpy, path, xarray
from ._config import (
    create_example_config,
    get_config,
    get_default_config_filepath,
    read_config,
    set_config,
    set_config_maap_token,
    set_config_to_maap,
    set_config_to_oads,
)
from ._get_file_info_from_str import get_file_info_from_str
from ._inspect import has_param
from .path import search_files_by_regex

__all__ = [
    "dict",
    "numpy",
    "path",
    "xarray",
    "has_param",
    "get_file_info_from_str",
    "create_example_config",
    "get_config",
    "get_default_config_filepath",
    "read_config",
    "set_config",
    "set_config_maap_token",
    "set_config_to_maap",
    "set_config_to_oads",
    "search_files_by_regex",
]
