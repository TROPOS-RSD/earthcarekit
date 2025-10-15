"""
**earthcarekit**

A Python package to simplify working with EarthCARE satellite data

See also:

- [Documentation](https://tropos-rsd.github.io/earthcarekit/)
- [Development status (GitHub)](https://github.com/TROPOS-RSD/earthcarekit)
- [License (MIT)](https://github.com/TROPOS-RSD/earthcarekit/blob/main/LICENSE)
- [Citation (Zenodo)](link)

---

Copyright (c) 2025 Leonard König

---
"""

__author__ = "Leonard König"
__license__ = "MIT"
__version__ = "0.9.1"
__date__ = "2025-10-15"
__maintainer__ = "Leonard König"
__email__ = "koenig@tropos.de"
__title__ = "earthcarekit"

import sys

from .calval import *
from .download import ecdownload
from .plot import *
from .plot import FigureType, ecquicklook, ecswath
from .utils import ProfileData, filter_latitude, filter_radius, filter_time, geo, read
from .utils import statistics as stats
from .utils.config import (
    _warn_user_if_not_default_config_exists,
    create_example_config,
    get_default_config_filepath,
    set_config,
)
from .utils.geo import geodesic, get_coord_between, get_coords, haversine
from .utils.ground_sites import GroundSite, get_ground_site
from .utils.logging import _setup_logging
from .utils.overpass import get_overpass_info
from .utils.read import *

sys.modules[__name__ + ".geo"] = geo
sys.modules[__name__ + ".read"] = read
sys.modules[__name__ + ".stats"] = stats
__all__ = [
    "read",
    "stats",
    "geo",
    "ecquicklook",
    "ecswath",
    "ecdownload",
    "ProfileData",
    "filter_latitude",
    "filter_radius",
    "filter_time",
    "GroundSite",
    "get_ground_site",
    "get_overpass_info",
    "geodesic",
    "haversine",
    "get_coords",
    "get_coord_between",
    "set_config",
    "create_example_config",
    "get_default_config_filepath",
    "FigureType",
]

_setup_logging()
_warn_user_if_not_default_config_exists()
