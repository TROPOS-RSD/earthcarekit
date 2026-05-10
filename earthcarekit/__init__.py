"""
**earthcarekit**

A Python package to simplify working with EarthCARE satellite data

See also:

- [Documentation](https://tropos-rsd.github.io/earthcarekit/)
- [Development status (GitHub)](https://github.com/TROPOS-RSD/earthcarekit)
- [License (Apache-2.0)](https://github.com/TROPOS-RSD/earthcarekit/blob/main/LICENSE)
- [Citation (Zenodo)](http://doi.org/10.5281/zenodo.16813294)

---

Copyright © 2025 TROPOS

---
"""

__author__ = "Leonard König"
__license__ = "Apache-2.0"
__version__ = "0.15.4"
__date__ = "2026-04-22"
__maintainer__ = "Leonard König"
__email__ = "koenig@tropos.de"
__title__ = "earthcarekit"

import sys

from . import color, colormap, geo, read, stats
from .calval import *
from .data import Profile, Swath
from .download import ecdownload
from .filter import filter_index, filter_latitude, filter_radius, filter_time
from .geo import geodesic, get_coord_between, get_coords, haversine
from .overpass import get_overpass_info
from .plot import *
from .plot import FigureType, ecquicklook, ecswath
from .read import *
from .site import GroundSite, get_ground_site
from .utils import (
    create_example_config,
    get_config,
    get_default_config_filepath,
    search_files_by_regex,
    set_config,
    set_config_maap_token,
    set_config_to_maap,
    set_config_to_oads,
)
from .utils._config import _warn_user_if_not_default_config_exists
from .utils._logging import _setup_logging

__all__ = [
    "read",
    "stats",
    "geo",
    "color",
    "colormap",
    "ecquicklook",
    "ecswath",
    "ecdownload",
    "Profile",
    "Swath",
    "GroundSite",
    "get_ground_site",
    "get_overpass_info",
    "geodesic",
    "haversine",
    "get_coords",
    "get_coord_between",
    "get_config",
    "set_config",
    "set_config_maap_token",
    "set_config_to_maap",
    "set_config_to_oads",
    "create_example_config",
    "get_default_config_filepath",
    "FigureType",
    "filter_index",
    "filter_latitude",
    "filter_radius",
    "filter_time",
    "search_files_by_regex",
]

_DEPRECATED = {
    "ProfileData": Profile,
    "SwathData": Swath,
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


_setup_logging()
_warn_user_if_not_default_config_exists()
