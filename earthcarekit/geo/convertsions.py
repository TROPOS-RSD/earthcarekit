import math
from typing import SupportsFloat

import numpy as np
from numpy.typing import NDArray

from ..constants import SEMI_MAJOR_AXIS_METERS, SEMI_MINOR_AXIS_METERS


def geo_to_ecef(
    lat: SupportsFloat,
    lon: SupportsFloat,
    alt: SupportsFloat | None = None,
    target_radius: float = 1.0,
    perfect_sphere: bool = True,
    semi_major: float = SEMI_MAJOR_AXIS_METERS,
    semi_minor: float = SEMI_MINOR_AXIS_METERS,
) -> tuple[float, float, float]:
    """Converts geodetic coordinates (latitude, longitude, altitude) to Earth-centered, Earth-fixed (ECEF) coordinates.

    Args:
        lat: Latitude in degrees (positive north, negative south).
        lon: Longitude in degrees (positive east, negative west).
        alt: Height above the Earth ellipsoid in meters; None assumes ellipsoid surface.
        target_radius: Target mean radius of the ECEF coordinate system; defaults to 1.0.
        perfect_sphere: If True, use a sphere with radius `target_radius`; otherwise, use ellipsoid.
        semi_major: Semi-major axis of the ellipsoid in meters; defaults to WGS 84 (6378137).
        semi_minor: Semi-minor axis of the ellipsoid in meters; defaults to WGS 84 (6356752.314245).

    Returns:
        ECEF coordinates (x, y, z) in meters

            - x: Axis through equator at prime meridian (lat=0°, lon=0°).
            - y: Axis through equator at 90°E (lat=0°, lon=90°).
            - z: Axis through north pole (lat=90°).
    """
    lat = float(lat)
    lon = float(lon)
    if alt is None:
        alt = 0.0
    else:
        alt = float(alt)

    def sin(x):
        return math.sin(x)

    def cos(x):
        return math.cos(x)

    def sqrt(x):
        return math.sqrt(x)

    lat = math.radians(lat)
    lon = math.radians(lon)

    if perfect_sphere:
        # Calculate ECEF coordinates
        f = 1 - (semi_major / semi_major)  # Flattening of the ellipsoid
        N = semi_major / sqrt(1 - (f * sin(lat)) ** 2)  # Prime vertical radius of curvature

        x = (N + alt) * cos(lat) * cos(lon)
        y = (N + alt) * cos(lat) * sin(lon)
        z = ((semi_major**2 / semi_major**2) * N + alt) * sin(lat)

        # # Alternative
        # e2 = 1 - (semi_minor**2 / semi_major**2) # Square of the first numerical eccentricity of the ellipsoid
        # N = semi_major / sqrt(1 - e2 * (sin(lat) ** 2)) # Prime vertical radius of curvature

        # Scale ECEF coordinates to target radius
        R = ((semi_major + semi_major) / 2) / target_radius
        x = -x / R
        y = -y / R
        z = z / R
    else:
        # Calculate ECEF coordinates
        f = 1 - (semi_minor / semi_major)  # Flattening of the ellipsoid
        N = semi_major / sqrt(1 - (f * sin(lat)) ** 2)  # Prime vertical radius of curvature

        x = (N + alt) * cos(lat) * cos(lon)
        y = (N + alt) * cos(lat) * sin(lon)
        z = ((semi_minor**2 / semi_major**2) * N + alt) * sin(lat)

        # # Alternative
        # e2 = 1 - (semi_minor**2 / semi_major**2) # Square of the first numerical eccentricity of the ellipsoid
        # N = semi_major / sqrt(1 - e2 * (sin(lat) ** 2)) # Prime vertical radius of curvature

        # Scale ECEF coordinates to target radius
        R = ((semi_major + semi_minor) / 2) / target_radius
        x = -x / R
        y = -y / R
        z = z / R

    return x, y, z


def ecef_to_geo(
    x: SupportsFloat,
    y: SupportsFloat,
    z: SupportsFloat,
    target_radius: float = 1.0,
    perfect_sphere: bool = True,
    semi_major: float = SEMI_MAJOR_AXIS_METERS,
    semi_minor: float = SEMI_MINOR_AXIS_METERS,
) -> tuple[float, float, float]:
    """Converts Earth-centered, Earth-fixed (ECEF) coordinates (x, y, z) to geodetic coordinates.

    Args:
        x: Cartesian ECEF x-coordinate in meters.
        y: Cartesian ECEF y-coordinate in meters.
        z: Cartesian ECEF z-coordinate in meters.
        target_radius: Target mean radius of the ECEF coordinate system; defaults to 1.0.
        perfect_sphere: If True, assume a spherical Earth; otherwise, use ellipsoidal (WGS 84).
        semi_major: Semi-major axis of the ellipsoid in meters; defaults to WGS 84 (6378137).
        semi_minor: Semi-minor axis of the ellipsoid in meters; defaults to WGS 84 (6356752.314245).

    Returns:
        Geodetic coordinates (latitude, longitude, altitude)

            - lat: Latitude in degrees (positive north, negative south).
            - lon: Longitude in degrees (positive east, negative west).
            - alt: Height above the ellipsoid in meters.
    """
    x = float(x)
    y = float(y)
    z = float(z)

    # Undo scaling
    R = ((semi_major + (semi_major if perfect_sphere else semi_minor)) / 2) / target_radius
    x = -x * R
    y = -y * R
    z = z * R

    lon = math.atan2(y, x)

    if perfect_sphere:
        r = math.sqrt(x**2 + y**2 + z**2)
        lat = math.asin(z / r)
        alt = r - semi_major
    else:
        e2 = 1 - (semi_minor**2 / semi_major**2)
        p = math.sqrt(x**2 + y**2)
        # Initial guess
        lat = math.atan2(z, p * (1 - e2))
        # Iterative refienment
        for _ in range(5):
            N = semi_major / math.sqrt(1 - e2 * math.sin(lat) ** 2)
            alt = p / math.cos(lat) - N
            lat = math.atan2(z, p * (1 - e2 * (N / (N + alt))))
        N = semi_major / math.sqrt(1 - e2 * math.sin(lat) ** 2)
        alt = p / math.cos(lat) - N

    return math.degrees(lat), math.degrees(lon), alt


def sequence_geo_to_ecef(
    lats: NDArray | list[SupportsFloat],
    lons: NDArray | list[SupportsFloat],
    alts: NDArray | list[SupportsFloat] | SupportsFloat | None = None,
    target_radius: float = 1.0,
    perfect_sphere: bool = True,
    semi_major: float = SEMI_MAJOR_AXIS_METERS,
    semi_minor: float = SEMI_MINOR_AXIS_METERS,
) -> NDArray:
    """Converts sequences of geodetic coordinates to Earth-centered, Earth-fixed (ECEF) coordinates.

    Args:
        lats: Latitude values in degrees (positive north, negative south).
        lons: Longitude values in degrees (positive east, negative west).
        alts: Height above the ellipsoid in meters; None assumes ellipsoid surface.
        target_radius: Target mean radius of the ECEF coordinate system; defaults to 1.0.
        perfect_sphere: If True, assume a spherical Earth; otherwise, use ellipsoidal (WGS 84).
        semi_major: Semi-major axis of the ellipsoid in meters; defaults to WGS 84 (6378137).
        semi_minor: Semi-minor axis of the ellipsoid in meters; defaults to WGS 84 (6356752.314245).

    Returns:
        ECEF coordinates as a 2D array (N, 3), where N is the number of input points.
    """
    lats = np.asarray(lats)
    lons = np.asarray(lons)
    if alts is None:
        alts = np.zeros(lats.shape)
    elif isinstance(alts, (float, int)):
        alts = np.repeat(float(alts), lats.shape)
    else:
        alts = np.asarray(alts)
    coords: NDArray = np.stack((lats, lons, alts)).T
    xyz = np.array(
        [
            list(
                geo_to_ecef(
                    c[0],
                    c[1],
                    c[2],
                    target_radius=target_radius,
                    perfect_sphere=perfect_sphere,
                    semi_major=semi_major,
                    semi_minor=semi_minor,
                )
            )
            for c in coords
        ]
    )
    return xyz


def sequence_ecef_to_geo(
    x: NDArray | list[SupportsFloat],
    y: NDArray | list[SupportsFloat],
    z: NDArray | list[SupportsFloat],
    target_radius: float = 1.0,
    perfect_sphere: bool = True,
    semi_major: float = SEMI_MAJOR_AXIS_METERS,
    semi_minor: float = SEMI_MINOR_AXIS_METERS,
) -> NDArray:
    """Converts sequences of Earth-centered, Earth-fixed (ECEF) coordinates to geodetic coordinates.

    Args:
        x: ECEF x-coordinates in meters.
        y: ECEF y-coordinates in meters.
        z: ECEF z-coordinates in meters.
        target_radius: Target mean radius of the ECEF coordinate system; defaults to 1.0.
        perfect_sphere: If True, assume a spherical Earth; otherwise, use ellipsoidal (WGS 84).
        semi_major: Semi-major axis of the ellipsoid in meters; defaults to WGS 84 (6378137).
        semi_minor: Semi-minor axis of the ellipsoid in meters; defaults to WGS 84 (6356752.314245).

    Returns:
        Geodetic coordinates as a 2D array (N, 3); (latitude, longitude, altitude) for each input point.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    z = np.asarray(z)

    xyz: NDArray = np.stack((x, y, z)).T
    coords = np.array(
        [
            list(
                ecef_to_geo(
                    c[0],
                    c[1],
                    c[2],
                    target_radius=target_radius,
                    perfect_sphere=perfect_sphere,
                    semi_major=semi_major,
                    semi_minor=semi_minor,
                )
            )
            for c in xyz
        ]
    )
    return coords
