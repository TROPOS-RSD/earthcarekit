from typing import Literal

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ._vincenty import vincenty as geodesic


def get_cumulative_distances(
    lats: ArrayLike, lons: ArrayLike, units: Literal["m", "km"] = "m"
) -> NDArray:
    lats = np.array(lats)
    lons = np.array(lons)
    if lats.shape != lons.shape:
        raise ValueError(
            f"Shape mismatch: 'lats' {lats.shape} and 'lons' {lons.shape} must have the same shape"
        )
    if lats.shape[0] == 1:
        return np.array([0])
    elif lats.shape[0] == 0:
        return np.array([])
    coords = np.vstack((lats, lons)).T
    distances = geodesic(coords[0:-1], coords[1::], units=units)
    distances = np.append(0, distances)
    cumulative_distances = np.cumsum(distances)
    return cumulative_distances
