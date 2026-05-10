from dataclasses import dataclass, field


@dataclass(frozen=True)
class Site:
    """Class representing a fixed geographic site (or ground station) with associated metadata.

    Attributes:
        latitude (float): Latitude of the site in decimal degrees.
        longitude (float): Longitude of the site in decimal degrees.
        name (str): Short name or identifier of the site.
        long_name (str): Full descriptive name of the site.
        aliases (list[str]): Alternative names or identifiers for the site.
        altitude (float): Altitude of the site in meters above sea level.
        cloudnet_name (str | None): Identifier string used in CloudNet file names, or None if not applicable.
    """

    latitude: float
    """Latitude of the site in decimal degrees."""
    longitude: float
    """Longitude of the site in decimal degrees."""
    name: str = ""
    """Short name or identifier of the site."""
    long_name: str = ""
    """Full descriptive name of the site."""
    aliases: list[str] = field(default_factory=list)
    """Alternative names or identifiers for the site."""
    altitude: float = 0.0
    """Altitude of the site in meters above sea level."""
    cloudnet_name: str | None = None
    """Identifier string used in CloudNet file names, or None if not applicable."""

    @property
    def coordinates(self) -> tuple[float, float]:
        """Geodetic coordinates of the ground site (lat,lon)."""
        return (self.latitude, self.longitude)
