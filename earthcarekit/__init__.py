"""
**earthcarekit**

A Python package to simplify working with EarthCARE satellite data

Copyright (c) 2025 Leonard König

Licensed under the MIT License (see [LICENSE](https://github.com/TROPOS-RSD/earthcarekit/blob/main/LICENSE) file or [https://opensource.org/license/mit](https://opensource.org/license/mit)).
"""

__author__ = "Leonard König"
__license__ = "MIT"
__version__ = "0.3.2rc1"
__date__ = "2025-08-25"
__maintainer__ = "Leonard König"
__email__ = "koenig@tropos.de"
__title__ = "earthcarekit"

from .calval import *
from .download import ecdownload
from .plot import *
from .plot import ecquicklook, ecswath
from .utils import ProfileData, filter_radius, filter_time, read, set_config
from .utils import statistics as stats
from .utils.config import _warn_user_if_not_default_config_exists, create_example_config
from .utils.geo import geodesic, haversine
from .utils.ground_sites import GroundSite, get_ground_site
from .utils.logging import _setup_logging
from .utils.overpass import get_overpass_info
from .utils.read import *

__all__ = [
    "ecquicklook",
    "ecswath",
    "ecdownload",
    "ProfileData",
    "filter_radius",
    "filter_time",
    "read",
    "set_config",
    "geodesic",
    "haversine",
    "GroundSite",
    "get_ground_site",
    "get_overpass_info",
    "stats",
]

_setup_logging()
_warn_user_if_not_default_config_exists()
