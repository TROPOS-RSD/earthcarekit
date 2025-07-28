from dataclasses import dataclass
from logging import Logger

from ._request import get_request_json
from ._types import Entrypoint


@dataclass
class EOCollection:
    name: str
    url_queryables: str | None
    url_items: str | None


def _get_collections_url(entrypoint: Entrypoint, title: str | None = None) -> str:
    """Returns the URL of the collections search request."""
    if not isinstance(title, str) or title == "":
        title = "earthcare"
    return f"{entrypoint.value}/collections/?title={title}&limit=100&startRecord=1"


def get_available_collections(
    entrypoint: Entrypoint,
    title: str | None = None,
    logger: Logger | None = None,
) -> list[EOCollection]:
    """Requests EO collections from the Server and returns available ones."""
    url = _get_collections_url(entrypoint=entrypoint, title=title)

    data = get_request_json(url=url, logger=logger)

    eo_collections = []
    for collection in data.get("collections", []):
        collection_id = collection.get("id")
        url_queryables: str | None = None
        url_items: str | None = None

        for link in collection.get("links", []):
            _rel = link.get("rel")
            if _rel == "http://www.opengis.net/def/rel/ogc/1.0/queryables":
                url_queryables = link.get("href", None)
            if _rel == "items":
                url_items = link.get("href", None)
                if isinstance(url_items, str):
                    url_items = url_items.split("items")[0] + "items"
            if isinstance(url_queryables, str) and isinstance(url_items, str):
                break

        eoc = EOCollection(
            name=collection_id,
            url_queryables=url_queryables,
            url_items=url_items,
        )
        eo_collections.append(eoc)

    return eo_collections
