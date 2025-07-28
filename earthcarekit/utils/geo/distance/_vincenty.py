import warnings

import numpy as np
from numpy.typing import ArrayLike, NDArray


def vincenty(
    a: ArrayLike,
    b: ArrayLike,
    units: str = "km",
    tolerance: float = 1e-12,
    max_iterations: int = 10,
) -> np.float64 | NDArray[np.float64]:
    """
    Calculates the geodesic distances between points on Earth (i.e. WSG 84 ellipsoid) using Vincenty's inverse method.

    Supports single or sequences of coordiates.

    Args:
        a (ArrayLike): Coordinates [lat, lon] or array of shape (N, 2), in decimal degrees.
        b (ArrayLike): Second coordinates, same format/shape as `a`.
        units (str, optional): Output units, "km" (default) or "m".
        tolerance (float, optional): Convergence threshold in radians. Default is 1e-12.
        max_iterations (int, optional): Maximum iterations before failure. Default is 10.

    Returns:
        float or np.ndarray: The geodesic distance or distances between the point in `a` and `b`.

    Raises:
        ValueError: If input shapes are incompatible or units are invalid.

    Note:
        Uses WGS84 (a=6378137.0 m, f=1/298.257223563). May fail for nearly antipodal points.

    Examples:
        >>> geodesic([51.352757, 12.43392], [38.559, 68.856])
        4548.675334434374
        >>> geodesic([0,0], [[0,0], [10,0], [20,0]])
        array([   0.        , 1105.85483324, 2212.36625417])
        >>> geodesic([[0,0], [10,0], [20,0]], [[0,0], [10,0], [20,0]])
        array([0., 0., 0.])

    References:
        Vincenty, T. (1975). "Direct and Inverse Solutions of Geodesics on the Ellipsoid with application
        of nested equations." Survey Review, 23(176), 88-93. https://doi.org/10.1179/sre.1975.23.176.88
    """
    _a, _b = map(np.asarray, [a, b])
    coord_a, coord_b = map(np.atleast_2d, [_a, _b])
    coord_a, coord_b = map(np.radians, [coord_a, coord_b])

    if (coord_a.shape[1] != 2) or (coord_b.shape[1] != 2):
        raise ValueError(
            f"At least one passed array has a wrong shape (a={_a.shape}, b={_b.shape}). 1d arrays should be of length 2 (i.e. [lat, lon]) and 2d array should have the shape (n, 2)."
        )
    if (coord_a.shape[0] < 1) or (coord_b.shape[0] < 1):
        raise ValueError(
            f"At least one passed array contains no values (a={_a.shape}, b={_b.shape})."
        )
    if coord_a.shape[0] != coord_b.shape[0]:
        if (coord_a.shape[0] != 1) and (coord_b.shape[0] != 1):
            raise ValueError(
                f"The shapes of passed arrays dont match (a={_a.shape}, b={_b.shape}). Either both should contain the same number of coordinates or at least one of them should contain a single coordinate."
            )

    lat_1, lon_1 = coord_a[:, 0], coord_a[:, 1]
    lat_2, lon_2 = coord_b[:, 0], coord_b[:, 1]

    # WGS84 ellipsoid constants
    a = 6378137.0  # semi-major axis (equatorial radius) in meters
    f = 1 / 298.257223563  # flattening
    b = (1 - f) * a  # semi-minor axis (polar radius) in meters

    # Reduced latitudes
    beta_1 = np.arctan((1 - f) * np.tan(lat_1))
    beta_2 = np.arctan((1 - f) * np.tan(lat_2))

    initial_lon_diff = lon_2 - lon_1

    # Initialize variables for iterative solution
    lon_diff = initial_lon_diff
    sin_beta_1, cos_beta_1 = np.sin(beta_1), np.cos(beta_1)
    sin_beta_2, cos_beta_2 = np.sin(beta_2), np.cos(beta_2)
    # Track convergence for each point pair
    converged = np.full_like(lat_1, False, dtype=bool)

    for _ in range(max_iterations):
        sin_lon_diff, cos_lon_diff = np.sin(lon_diff), np.cos(lon_diff)

        sin_sigma = np.sqrt(
            (cos_beta_2 * sin_lon_diff) ** 2
            + (cos_beta_1 * sin_beta_2 - sin_beta_1 * cos_beta_2 * cos_lon_diff) ** 2
        )
        cos_sigma = (sin_beta_1 * sin_beta_2) + (cos_beta_1 * cos_beta_2 * cos_lon_diff)
        sigma = np.arctan2(sin_sigma, cos_sigma)

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            sin_alpha = cos_beta_1 * cos_beta_2 * sin_lon_diff / sin_sigma
        sin_alpha = np.nan_to_num(sin_alpha, nan=0.0)
        cos2_alpha = 1 - sin_alpha**2

        with warnings.catch_warnings():
            warnings.filterwarnings("ignore")
            cos2_sigma_m = np.where(
                cos2_alpha != 0.0,
                cos_sigma - ((2 * sin_beta_1 * sin_beta_2) / cos2_alpha),
                0.0,
            )
        cos2_sigma_m = np.nan_to_num(cos2_sigma_m, nan=0.0)

        C = f / 16 * cos2_alpha * (4 + f * (4 - 3 * cos2_alpha))

        previous_lon_diff = lon_diff
        lon_diff = initial_lon_diff + (1 - C) * f * sin_alpha * (
            sigma
            + C
            * sin_sigma
            * (cos2_sigma_m + C * cos_sigma * (-1 + 2 * cos2_sigma_m**2))
        )
        converged = converged | (np.abs(lon_diff - previous_lon_diff) < tolerance)
        if np.all(converged):
            break

    u2 = cos2_alpha * (a**2 - b**2) / b**2
    A = 1 + u2 / 16384 * (4096 + u2 * (-768 + u2 * (320 - 175 * u2)))
    B = u2 / 1024 * (256 + u2 * (-128 + u2 * (74 - 47 * u2)))

    delta_sigma = (
        B
        * sin_sigma
        * (
            cos2_sigma_m
            + B
            / 4
            * (
                cos_sigma * (-1 + 2 * cos2_sigma_m**2)
                - B
                / 6
                * cos2_sigma_m
                * (-3 + 4 * sin_sigma**2)
                * (-3 + 4 * cos2_sigma_m**2)
            )
        )
    )

    distance = b * A * (sigma - delta_sigma)

    if units == "km":
        distance = distance / 1000.0
    elif units != "m":
        raise ValueError(
            f"{vincenty.__name__}() Invalid units : {units}. Use 'm' or 'km' instead."
        )

    if len(_a.shape) == 1 and len(_b.shape) == 1:
        return distance[0]

    return distance
