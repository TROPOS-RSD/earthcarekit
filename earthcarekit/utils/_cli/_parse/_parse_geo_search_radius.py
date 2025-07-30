from ._types import _RadiusSearch


def parse_radius_search(
    radius_search: list[str | float] | None,
) -> _RadiusSearch:
    """Convert user's radius inputs to query parameters, that can be used in search requests."""
    if radius_search is not None:
        radius = str(int(radius_search[0]))
        lat = str(float(radius_search[1]))
        lon = str(float(radius_search[2]))
        return _RadiusSearch(radius=radius, lat=lat, lon=lon)
    return _RadiusSearch(radius=None, lat=None, lon=None)
