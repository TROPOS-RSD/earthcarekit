from dataclasses import dataclass, field


@dataclass(frozen=True)
class Site:
    """Represents a fixed geographic site (or ground station) with metadata.

    Attributes:
        latitude: Site latitude in decimal degrees.
        longitude: Site longitude in decimal degrees.
        name: Short name or identifier.
        long_name: Full descriptive name.
        aliases: Alternative names or identifiers.
        altitude: Altitude above sea level in meters.
        cloudnet_name: CloudNet file identifier, or None if not applicable.
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
