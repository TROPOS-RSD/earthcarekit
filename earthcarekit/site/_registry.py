from typing import Final

from ._ground_site import GroundSite
from ._sites import _GROUND_SITES_LIST


def _get_ground_site_registry() -> dict[str, GroundSite]:
    out: dict[str, GroundSite] = {}
    for gs in _GROUND_SITES_LIST:
        for site in gs.aliases:
            assert site not in out
            out[site] = gs
    return out


SITES: Final[dict[str, GroundSite]] = _get_ground_site_registry()


def get_ground_site(site: str | GroundSite) -> GroundSite:
    """Retruns ground site data based on name and raises `ValueError` if no matching ground site is found and `TypeError`."""
    if isinstance(site, GroundSite):
        return site
    if not isinstance(site, str):
        raise TypeError(
            f"{get_ground_site.__name__}() Expected type `{str.__name__}` but got `{type(site).__name__}` (name={site})"
        )
    site = site.lower()

    try:
        return SITES[site]
    except KeyError as e:
        gss = [gs.name for gs in _GROUND_SITES_LIST]
        error_msg = f"""No matching ground site found: '{site}'. Supported site names are: '{gss[0]}', {"', '".join(gss[1:-1])}', and '{gss[-1]}'."""
        raise ValueError(error_msg) from e
