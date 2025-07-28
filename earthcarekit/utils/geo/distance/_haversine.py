from typing import Literal

import numpy as np
from numpy.typing import ArrayLike

from ...constants import MEAN_EARTH_RADIUS_METERS


def haversine(
    a: ArrayLike,
    b: ArrayLike,
    units: Literal["m", "km"] = "km",
    radius_m: float = MEAN_EARTH_RADIUS_METERS,
):
    """
    Calculates the great-circle (spherical) distance between pairs of latitude/longitude coordinates
    using the haversine formula.

    Args:
        a (ArrayLike): An array-like object of shape (..., 2) containing latitude and longitude
            coordinates in degrees. The last dimension must be 2: (lat, lon).
        b (ArrayLike): An array-like object of the same shape as `a`, containing corresponding
            latitude and longitude coordinates.
        units (Literal["m", "km"], optional): Unit of the output distance. Must be either
            "km" for kilometers or "m" for meters. Defaults to "km".
        radius (float, optional): Radius of the sphere to use for distance calculation.
            Defaults to MEAN_EARTH_RADIUS_METERS (based on WSG 84 ellipsoid: ~6371008.77 meters).
            Note: If `units="km"`, this value is automatically converted to kilometers.

    Returns:
        np.ndarray: Array of great-circle distances between `a` and `b`, in the specified units.
            The shape matches the input shape excluding the last dimension.

    Raises:
        ValueError: If the shapes of `a` and `b` are incompatible or `units` is not one of "m" or "km".

    Examples:
        >>> haversine([51.352757, 12.43392], [38.559, 68.856])
        4537.564747442274
        >>> haversine([0,0], [[0,0], [10,0], [20,0]])
        array([   0.        , 1111.95079735, 2223.90159469])
        >>> haversine([[0,0], [10,0], [20,0]], [[0,0], [10,0], [20,0]])
        array([0., 0., 0.])
    """

    if units not in ["m", "km"]:
        raise ValueError(
            f"{haversine.__name__}() Invalid units : {units}. Use 'm' or 'km' instead."
        )

    radius: float = radius_m
    if units == "km":
        radius = radius / 1000.0

    a = np.array(a)
    b = np.array(b)

    coord_a = np.atleast_2d(a)
    coord_b = np.atleast_2d(b)

    if (coord_a.shape[1] != 2) or (coord_b.shape[1] != 2):
        raise ValueError(
            f"At least one passed array has a wrong shape (a={a.shape}, b={b.shape}). 1d arrays should be of length 2 (i.e. [lat, lon]) and 2d array should have the shape (n, 2)."
        )
    if (coord_a.shape[0] < 1) or (coord_b.shape[0] < 1):
        raise ValueError(
            f"At least one passed array contains no values (a={a.shape}, b={b.shape})."
        )
    if coord_a.shape[0] != coord_b.shape[0]:
        if (coord_a.shape[0] != 1) and (coord_b.shape[0] != 1):
            raise ValueError(
                f"The shapes of passed arrays dont match (a={a.shape}, b={b.shape}). Either both should contain the same number of coordinates or at least one of them should contain a single coordinate."
            )

    coord_a = np.radians(coord_a)
    coord_b = np.radians(coord_b)

    phi_1, lambda_1 = coord_a[:, 0], coord_a[:, 1]
    phi_2, lambda_2 = coord_b[:, 0], coord_b[:, 1]

    hav = lambda theta: (1 - np.cos(theta)) / 2

    h = hav(phi_2 - phi_1) + np.cos(phi_1) * np.cos(phi_2) * hav(lambda_2 - lambda_1)

    d = 2 * radius * np.arcsin(np.sqrt(h))

    if len(a.shape) == 1 and len(b.shape) == 1:
        return d[0]

    return d
