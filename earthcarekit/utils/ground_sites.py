from dataclasses import dataclass, field


@dataclass(frozen=True)
class GroundSite:
    """Class representing a geographic site (or ground station) with associated metadata.

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


GROUND_SITES: list[GroundSite] = [
    GroundSite(
        name="TROPOS",
        long_name="TROPOS (LPZ)",
        aliases=["tropos"],
        latitude=51.352757,
        longitude=12.43392,
        altitude=125,
        cloudnet_name="leipzig",
    ),
    GroundSite(
        name="Leipzig",
        long_name="Leipzig (GER)",
        aliases=["leipzig", "lpz"],
        latitude=51.352757,
        longitude=12.43392,
        altitude=125,
        cloudnet_name="leipzig",
    ),
    GroundSite(
        name="Mindelo",
        long_name="Mindelo (CPV)",
        aliases=["mindelo", "cpv"],
        latitude=16.878,
        longitude=-24.995,
        altitude=13,
        cloudnet_name="mindelo",
    ),
    GroundSite(
        name="Dushanbe",
        long_name="Dushanbe (TJK)",
        aliases=["dushanbe", "tjk"],
        latitude=38.559,
        longitude=68.856,
        altitude=864,
        cloudnet_name="dushanbe",
    ),
    GroundSite(
        name="Melpitz",
        long_name="Melpitz (GER)",
        aliases=["melpitz"],
        latitude=51.526,
        longitude=12.928,
        altitude=83,
        cloudnet_name="melpitz",
    ),
    GroundSite(
        name="Limassol",
        long_name="Limassol (CYP)",
        aliases=["limassol", "cyp", "cyprus"],
        latitude=34.67667,
        longitude=33.04417,
        altitude=3,
        cloudnet_name="limassol",
    ),
    GroundSite(
        name="Antikythera",
        long_name="Antikythera (GRC)",
        aliases=["antikythera", "grc", "greece"],
        latitude=35.86,
        longitude=23.31,
        altitude=193,
        cloudnet_name="antikythera",
    ),
    GroundSite(
        name="Evora",
        long_name="Evora (PRT)",
        aliases=["evora", "prt", "portugal"],
        latitude=38.576,
        longitude=-7.911,
        altitude=290,
        cloudnet_name="evora",
    ),
    GroundSite(
        name="HPB",
        long_name="Hohenpeissenberg (GER)",
        aliases=["hpb", "hohenpeissenberg"],
        latitude=47.801473,
        longitude=11.009348,
        altitude=990,
        cloudnet_name="hpb",
    ),
    GroundSite(
        name="Warsaw",
        long_name="Warsaw (POL)",
        aliases=["warsaw", "pol", "poland"],
        latitude=52.233608,
        longitude=21.020265,
        altitude=113,
        cloudnet_name="warsaw",
    ),
    GroundSite(
        name="Kuopio",
        long_name="Kuopio (FIN)",
        aliases=["kuopio", "fin", "finland"],
        latitude=62.965698,
        longitude=27.666004,
        altitude=78,
        cloudnet_name="kuopio",
    ),
    GroundSite(
        name="Cabauw",
        long_name="Cabauw (NL)",
        aliases=["cabauw", "nl", "netherlands"],
        latitude=51.9677,
        longitude=4.9271,
        altitude=0,
        cloudnet_name=None,
    ),
    GroundSite(
        name="Koganei",
        long_name="Koganei (JP)",
        aliases=["koganei", "jp", "japan"],
        latitude=35.7,
        longitude=139.48,
        altitude=70,
        cloudnet_name=None,
    ),
    GroundSite(
        name="Neumayer III",
        long_name="Neumayer-Station III",
        aliases=["neumayer", "neumayer3", "neumayeriii"],
        latitude=-70.674444,
        longitude=-8.274167,
        altitude=41,
        cloudnet_name=None,
    ),
]


def get_ground_site(site: str | GroundSite) -> GroundSite:
    """Retruns ground site data based on name and raises `ValueError` if no matching ground site is found and `TypeError`."""
    if isinstance(site, GroundSite):
        return site
    if not isinstance(site, str):
        raise TypeError(
            f"{get_ground_site.__name__}() Expected type `{str.__name__}` but got `{type(site).__name__}` (name={site})"
        )
    site = site.lower()
    for gs in GROUND_SITES:
        if site in gs.aliases:
            return gs
    raise ValueError(f"No matching ground site found: '{site}'")
