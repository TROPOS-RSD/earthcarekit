from typing import Final, overload

from pystac import Collection

from ._cache import get_default_properties_dict

COLLECTION_ORDER: Final[list[str]] = [
    "EarthCAREL0L1Products_MAAP",
    "EarthCAREL2Products_MAAP",
    "JAXAL2Products_MAAP",
    "EarthCAREAuxiliary_MAAP",
    "EarthCAREL1InstChecked_MAAP",
    "EarthCAREL2InstChecked_MAAP",
    "JAXAL2InstChecked_MAAP",
    "EarthCAREL1Validated_MAAP",
    "EarthCAREL2Validated_MAAP",
    "JAXAL2Validated_MAAP",
    "EarthCAREXMETL1DProducts10_MAAP",
    "EarthCAREOrbitData_MAAP",
]
COLLECTION_ORDER_DICT: Final[dict[str, int]] = {name: i for i, name in enumerate(COLLECTION_ORDER)}


def get_collection_name(collection: Collection | str) -> str:
    return collection.id if isinstance(collection, Collection) else collection


@overload
def sorted_collections(collections: list[str], reverse: bool = False) -> list[str]: ...
@overload
def sorted_collections(
    collections: list[Collection], reverse: bool = False
) -> list[Collection]: ...
def sorted_collections(collections, reverse=False):
    if len(collections) == 0:
        return []
    elif isinstance(collections[0], Collection):
        return sorted(
            collections,
            key=lambda c: COLLECTION_ORDER_DICT.get(c.id, len(COLLECTION_ORDER)),
            reverse=reverse,
        )
    return sorted(
        collections,
        key=lambda c: COLLECTION_ORDER_DICT.get(c, len(COLLECTION_ORDER)),
        reverse=reverse,
    )


def get_candidate_collections(
    user_collections: list[Collection] | list[str],
    product_type: str,
) -> list[str]:
    properties_dict = get_default_properties_dict()
    candidate_collections = []
    for user_coll in user_collections:
        name = get_collection_name(user_coll)
        enum = properties_dict.get(name, {}).get("product:type", {}).get("enum", [])
        if product_type in enum:
            candidate_collections.append(name)
    return sorted_collections(candidate_collections)
