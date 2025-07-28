from pyproj import Geod

_geod = Geod(ellps="WGS84")


def interpgeo(
    lat1: float, lon1: float, lat2: float, lon2: float, f: float
) -> tuple[float, float]:
    """
    Interpolates along the geodesic from (lon1, lat1) to (lon2, lat2) by fraction f (0 to 1).
    Returns interpolated (lon, lat).
    """
    azi1, azi2, dist = _geod.inv(lon1, lat1, lon2, lat2)
    lon, lat, _ = _geod.fwd(lon1, lat1, azi1, f * dist)
    return lon, lat
