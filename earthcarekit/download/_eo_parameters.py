from dataclasses import dataclass
from logging import Logger

from ._eo_collection import EOCollection
from ._request import get_request_json


@dataclass
class STACQueryParameter:
    name: str
    enum: list[str] | None


def _get_stac_base_parameters() -> list[STACQueryParameter]:
    """Return list of standard STAC API parameters.

    see: https://github.com/radiantearth/stac-api-spec/tree/v1.0.0/item-search#query-parameter-table
    """
    return [
        STACQueryParameter(
            name="limit",
            enum=None,
        ),
        STACQueryParameter(
            name="datetime",
            enum=None,
        ),
        STACQueryParameter(
            name="bbox",
            enum=None,
        ),
        # TODO: Fix handling of these additional non standard parameters (e.g., fails for X-MET)
        STACQueryParameter(
            name="radius",
            enum=None,
        ),
        STACQueryParameter(
            name="lat",
            enum=None,
        ),
        STACQueryParameter(
            name="lon",
            enum=None,
        ),
    ]


def get_available_parameters(
    collection: EOCollection,
    logger: Logger | None = None,
) -> list[STACQueryParameter]:
    """Requests queryables (STAC API parameters) of a selected collection and returns available ones."""
    url_queryables = collection.url_queryables
    if not isinstance(url_queryables, str):
        return []

    data = get_request_json(url=url_queryables, logger=logger)

    raw_paraemters: dict | None = data.get("properties")
    if not isinstance(raw_paraemters, dict):
        raise ValueError(
            f'missing "properties" field in response of "{url_queryables}"'
        )

    eo_parameters: list[STACQueryParameter] = _get_stac_base_parameters()

    for name, info in raw_paraemters.items():
        eop = STACQueryParameter(
            name=name,
            enum=info.get("enum", None),
        )
        eo_parameters.append(eop)

    return eo_parameters
