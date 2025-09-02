from typing import Final

import numpy as np
from numpy.typing import ArrayLike, NDArray
from pyproj import Geod

_GEOD: Final[Geod] = Geod(ellps="WGS84")


def get_coord_between(
    coord1: ArrayLike,
    coord2: ArrayLike,
    f: float = 0.5,
) -> NDArray:
    """
    Interpolates between two coordinates by fraction f (0 to 1).

    Args:
        coord1 (ArrayLike): The first lat/lon point.
        coord2 (ArrayLike): The second lat/lon point.
        f (float): A fractional value between 0 and 1. Defaults to 0.5, i.e., the mid point between coord1 and coord2.

    Returns:
        NDArray: A 2-element `numpy.ndarray` representing the interpolated lat/lon point.
    """

    coord1 = np.array(coord1)
    coord2 = np.array(coord2)

    if coord1.shape != (2,):
        raise ValueError(f"coord1 must be a 2-element sequence (lat, lon)")

    if coord2.shape != (2,):
        raise ValueError(f"coord2 must be a 2-element sequence (lat, lon)")

    lon, lat = interpgeo(
        lat1=float(coord1[0]),
        lon1=float(coord1[1]),
        lat2=float(coord2[0]),
        lon2=float(coord2[1]),
        f=f,
    )
    return np.array([lat, lon])


def interpgeo(
    lat1: float,
    lon1: float,
    lat2: float,
    lon2: float,
    f: float,
) -> tuple[float, float]:
    """
    Interpolates along the geodesic from (lon1, lat1) to (lon2, lat2) by fraction f (0 to 1) and returns interpolated (lon, lat).
    """
    azi1, azi2, dist = _GEOD.inv(lon1, lat1, lon2, lat2)
    lon, lat, _ = _GEOD.fwd(lon1, lat1, azi1, f * dist)
    return lon, lat
