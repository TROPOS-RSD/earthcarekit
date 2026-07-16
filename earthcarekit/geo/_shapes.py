from pyproj import CRS, Transformer
from shapely.geometry import Point, Polygon, box
from shapely.ops import transform


class Shapes:
    @staticmethod
    def radius(lat: float, lon: float, radius_km: float) -> Polygon:
        crs = CRS.from_proj4(f"+proj=aeqd +lat_0={lat} +lon_0={lon} +datum=WGS84")
        return transform(
            Transformer.from_crs(crs, crs.geodetic_crs, always_xy=True).transform,
            Point(0, 0).buffer(radius_km * 1000),
        )

    @staticmethod
    def bbox(min_lat: float, min_lon: float, max_lat: float, max_lon: float) -> Polygon:
        return box(min_lat, min_lon, max_lat, max_lon)
