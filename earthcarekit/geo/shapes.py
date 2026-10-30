"""
**earthcarekit.shapes**

Geometric shapes compatible with `pystac_client` search queries.

Generate `shapely` geometries (`Polygon`/`MultiPolygon`) for spatial filtering.
Shapes can be passed directly to the `intersect` argument of `pystac_client` search queries.
Shapes extending across the dateline are automatically split into `MultiPolygon` objects.

Functions:
    - [earthcarekit.shapes.radius][]: Circle geometry around a point.
    - [earthcarekit.shapes.bbox][]: Rectangular bounding box geometry.

## Notes

This module does not depend on other internal modules.

---
"""

import numpy as np
from pyproj import CRS, Transformer
from shapely.geometry import MultiPolygon, Point, Polygon, box
from shapely.ops import transform


def _get_raw_circle_shape(lat: float, lon: float, radius_km: float, *, n: int = 16) -> Polygon:
    crs = CRS.from_proj4(f"+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84")
    return transform(
        Transformer.from_crs(crs, crs.geodetic_crs, always_xy=True).transform,
        Point(0, 0).buffer(radius_km * 1000, quad_segs=n),
    )


def radius(lat: float, lon: float, radius_km: float, *, n: int = 16) -> Polygon | MultiPolygon:
    """Generates a circular geometry around a point compatible with `pystac_client` search queries.

    Shapes extending across the dateline are automatically split into `MultiPolygon` objects.

    Args:
        lat: Latitude of the center point in degrees.
        lon: Longitude of the center point in degrees.
        radius_km: Radius in kilometers.
        n: Number of line segments used to approximate circle.

    Returns:
        A circular geometry.
    """
    shape = _get_raw_circle_shape(lat, lon, radius_km, n=n)
    # return shape

    # Check if dateline crossed
    coords = np.asarray(shape.exterior.coords)
    lon_radians = np.deg2rad(coords[:, 0])

    condition = np.abs(np.diff(lon_radians)) > 1.5 * np.pi
    idxs = np.where(condition)[0] + 1

    if idxs.size == 0:
        # Dateline is not crossed, so shape should be valid as is
        return shape

    sign = np.sign(coords[1, 0] - coords[0, 0])

    gap = 0.000001
    max_lon = 180.0 - gap * 0.5
    max_lat = 90.0 - gap * 0.5

    if idxs.size == 2:
        # The shape includes one of the poles

        a1 = coords[: idxs[0]]
        a2 = coords[idxs[1] :]

        # Add extra coords at dateline to reduce gap
        a1 = np.r_[
            a1, np.asarray([[np.sign(a1[-1, 0]) * np.max([np.abs(a1[-1, 0]), max_lon]), a1[-1, 1]]])
        ]
        a2 = np.r_[
            np.asarray([[np.sign(a2[0, 0]) * np.max([np.abs(a2[0, 0]), max_lon]), a2[0, 1]]]), a2
        ]

        a = np.r_[a1, a2]

        b = coords[idxs[0] : idxs[1]]

        # Add extra coords at dateline to reduce gap
        b = np.r_[
            np.asarray([[np.sign(b[0, 0]) * np.max([np.abs(b[0, 0]), max_lon]), b[0, 1]]]),
            b,
            np.asarray([[np.sign(b[-1, 0]) * np.max([np.abs(b[-1, 0]), max_lon]), b[-1, 1]]]),
        ]

        new_shape = MultiPolygon([Polygon(a), Polygon(b)])
    elif idxs.size == 1:
        # The shape extents across the dateline and does not include a pole

        # Ensure non-overlapping geometries by creating a gap between first and last coord
        coords[0, 0] = coords[0, 0] + sign * gap

        # Split at dateline
        a = coords[: idxs[0]]
        b = coords[idxs[0] :]

        # Add extra coords at dateline to reduce gap
        a = np.r_[
            a, np.asarray([[np.sign(a[-1, 0]) * np.max([np.abs(a[-1, 0]), max_lon]), a[-1, 1]]])
        ]
        b = np.r_[np.asarray([[np.sign(b[0, 0]) * np.max([np.abs(b[0, 0]), max_lon]), b[0, 1]]]), b]

        # Extend geometries up to the pole
        a_rev = a[::-1].copy()
        a_rev[:, 1] = np.sign(lat) * max_lat
        a = np.r_[a, a_rev]

        b_rev = b[::-1].copy()
        b_rev[:, 1] = np.sign(lat) * max_lat
        b = np.r_[b, b_rev]

        new_shape = MultiPolygon([Polygon(a), Polygon(b)])
    else:
        raise ValueError("invalid shape")

    return new_shape


def bbox(min_lat: float, min_lon: float, max_lat: float, max_lon: float) -> Polygon | MultiPolygon:
    """Generates a rectangular bounding box geometry compatible with `pystac_client` search queries.

    Shapes extending across the dateline are automatically split into `MultiPolygon` objects.

    Args:
        min_lat: Minimum latitude (south edge) in degrees.
        min_lon: Minimum longitude (west edge) in degrees.
        max_lat: Maximum latitude (north edge) in degrees.
        max_lon: Maximum longitude (east edge) in degrees.

    Returns:
        A rectangular geometry.
    """
    if min_lon > max_lon:
        a = box(min_lon, min_lat, 180.0, max_lat)
        b = box(-179.999999, min_lat, max_lon, max_lat)
        return MultiPolygon([a, b])
    elif max_lon - min_lon > 179.999999:
        a = box(min_lon, min_lat, 0.0, max_lat)
        b = box(0.000001, min_lat, max_lon, max_lat)
        return MultiPolygon([a, b])
    return box(min_lon, min_lat, max_lon, max_lat)
