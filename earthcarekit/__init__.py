"""
**earthcarekit**

A Python package to simplify working with EarthCARE satellite data

Copyright (c) 2025 Leonard König

Licensed under the MIT License (see [LICENSE](https://github.com/TROPOS-RSD/earthcarekit/blob/main/LICENSE) file).

Find documentation [here](https://github.com/TROPOS-RSD/earthcarekit).
"""

__author__ = "Leonard König"
__license__ = "MIT"
__version__ = "0.5.0"
__date__ = "2025-09-02"
__maintainer__ = "Leonard König"
__email__ = "koenig@tropos.de"
__title__ = "earthcarekit"

from .calval import *
from .download import ecdownload
from .plot import *
from .plot import ecquicklook, ecswath
from .utils import ProfileData, filter_radius, filter_time
from .utils import geo as geo
from .utils import read
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

__all__ = [
    "read",
    "stats",
    "geo",
    "ecquicklook",
    "ecswath",
    "ecdownload",
    "ProfileData",
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
]

_setup_logging()
_warn_user_if_not_default_config_exists()
