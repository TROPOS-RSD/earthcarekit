from logging import Logger
from typing import Any, Final, TypeVar

from pystac import Collection
from pystac_client import Client

T = TypeVar("T")
URL_MAAP: Final[str] = "https://catalog.maap.eo.esa.int/catalogue"


def get_catalog(logger: Logger | None = None) -> Client:
    """Open the MAAP STAC catalog."""
    if logger:
        logger.debug(f"Open catalog: <{URL_MAAP}>")
    return Client.open(URL_MAAP)


def get_collections(
    catalog: Client,
    logger: Logger | None = None,
) -> list[Collection]:
    """Get list of available EarthCARE collections."""
    if logger:
        logger.debug("Search EarthCARE collections")
    search = catalog.collection_search(max_collections=30, q="earthcare")
    result = list(search.collections())
    if logger:
        logger.debug(f"Found {len(result)} EarthCARE collections.")
    return result


def get_queryables(
    catalog: Client,
    collection: Collection | str,
    logger: Logger | None = None,
) -> dict[str, Any]:
    """Get set of queryables of a specified collection."""
    collection_id = collection.id if isinstance(collection, Collection) else collection
    if logger:
        logger.debug(f"Requesting queryables of '{collection_id}'")
    return catalog.get_merged_queryables([collection_id])


def get_properties(
    queryables: dict[str, Any],
    logger: Logger | None = None,
) -> dict[str, Any]:
    """Extract the set of available properties (i.e., search parameters) from a given set of queryables."""
    if logger:
        logger.debug("Accessing 'properties' from queryables")
    return queryables.get("properties", {})


def get_validated_param(
    properties: dict[str, Any],
    name: str,
    logger: Logger | None = None,
) -> dict[str, Any]:
    if logger:
        logger.debug(f"Validating parameter '{name}'")
    prop = properties.get(name)

    if prop is None:
        msg = f"Parameter not available in queryables: '{name}'"
        if logger:
            logger.error(msg)
        raise ValueError(msg)

    return dict(prop)


def get_enum_validated_param(
    properties: dict[str, Any],
    name: str,
    value: T,
    logger: Logger | None = None,
) -> T:
    prop = get_validated_param(properties, name, logger=logger)

    if logger:
        logger.debug(f"Accessing 'enum' of parameter '{name}'")
    enum = prop.get("enum")

    if enum is not None and value not in enum:
        msg = (
            f"""Value of parameter '{name}' not available in enum: '{value}';"""
            f"""expected values include: '{"', '".join(list(enum))}'"""
        )
        if logger:
            logger.error(msg)
        raise ValueError(msg)

    if logger:
        logger.debug(f"Enum validation complete -> '{name}': '{value}'")
    return value
