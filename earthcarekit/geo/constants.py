from typing import Final

from pyproj import Geod

GEOD: Final[Geod] = Geod(ellps="WGS84")
