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
__version__ = "0.15.2"
__date__ = "2026-04-01"
__maintainer__ = "Leonard König"
__email__ = "koenig@tropos.de"
__title__ = "earthcarekit"

import sys

from .calval import *
from .download import ecdownload
from .plot import *
from .plot import FigureType, ecquicklook, ecswath
from .utils import (
    GroundSite,
    ProfileData,
    create_example_config,
    filter_index,
    filter_latitude,
    filter_radius,
    filter_time,
    geo,
    geodesic,
    get_config,
    get_coord_between,
    get_coords,
    get_default_config_filepath,
    get_ground_site,
    get_overpass_info,
    haversine,
    read,
    set_config,
    set_config_maap_token,
    set_config_to_maap,
    set_config_to_oads,
)
from .utils import statistics as stats
from .utils.config import _warn_user_if_not_default_config_exists
from .utils.logging import _setup_logging
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
]

_setup_logging()
_warn_user_if_not_default_config_exists()
