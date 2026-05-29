import numpy as np
from numpy.typing import ArrayLike, NDArray


def normalize_longitude(lons: ArrayLike) -> NDArray:
    """Ensures -180/+180 longitude range."""
    return ((np.array(lons) + 180) % 360) - 180
