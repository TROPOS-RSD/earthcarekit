import logging
from typing import Any, Final, TypeVar

from pystac import Collection
from pystac_client import Client

log = logging.getLogger("ecdownload")

T = TypeVar("T")
URL_MAAP: Final[str] = "https://catalog.maap.eo.esa.int/catalogue"


def get_catalog() -> Client:
    """Open the MAAP STAC catalog."""
    log.debug(f"Open catalog: '{URL_MAAP}'")
    return Client.open(URL_MAAP)


def get_collections(
    catalog: Client,
) -> list[Collection]:
    """Get list of available EarthCARE collections."""
    log.debug("Search EarthCARE collections")
    search = catalog.collection_search(max_collections=30, q="earthcare")
    result = list(search.collections())
    log.debug(f"Found {len(result)} EarthCARE collections.")
    return result


def get_queryables(
    catalog: Client,
    collection: Collection | str,
) -> dict[str, Any]:
    """Get set of queryables of a specified collection."""
    collection_id = collection.id if isinstance(collection, Collection) else collection
    log.debug(f"Requesting queryables of '{collection_id}'")
    return catalog.get_merged_queryables([collection_id])


def get_properties(
    queryables: dict[str, Any],
) -> dict[str, Any]:
    """Extract the set of available properties (i.e., search parameters) from a given set of queryables."""
    log.debug("Accessing 'properties' from queryables")
    return queryables.get("properties", {})


def get_validated_param(
    properties: dict[str, Any],
    name: str,
) -> dict[str, Any]:
    log.debug(f"Validating parameter '{name}'")
    prop = properties.get(name)

    if prop is None:
        msg = f"Parameter not available in queryables: '{name}'"
        log.error(msg)
        raise ValueError(msg)

    return dict(prop)


def get_enum_validated_param(
    properties: dict[str, Any],
    name: str,
    value: T,
) -> T:
    prop = get_validated_param(properties, name)

    log.debug(f"Accessing 'enum' of parameter '{name}'")
    enum = prop.get("enum")

    if enum is not None and value not in enum:
        msg = (
            f"""Value of parameter '{name}' not available in enum: '{value}';"""
            f"""expected values include: '{"', '".join(list(enum))}'"""
        )
        log.error(msg)
        raise ValueError(msg)

    log.debug(f"Enum validation complete -> '{name}': '{value}'")
    return value
