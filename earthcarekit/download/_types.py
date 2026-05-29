from enum import StrEnum

# Re-export shared type aliases and search-input dataclasses used by the
# download/search code. These live under the CLI parsing types module.
from ..utils._cli._parse._types import (
    CollectionStr,
    FrameIDStr,
    ProductTypeStr,
    ProductTypeVersion,
    TimestampStr,
    _BBoxSearch,
    _OrbitFrameInputs,
    _RadiusSearch,
    _SearchInputs,
    _TimestampInputs,
)
from ._constants import URL_MAAP, URL_OADS

__all__ = [
    "UserType",
    "Entrypoint",
    # Shared type aliases
    "CollectionStr",
    "FrameIDStr",
    "ProductTypeStr",
    "ProductTypeVersion",
    "TimestampStr",
    # Shared search/input dataclasses
    "_BBoxSearch",
    "_OrbitFrameInputs",
    "_RadiusSearch",
    "_SearchInputs",
    "_TimestampInputs",
]


class UserType(StrEnum):
    COMMISSIONING = "commissioning"
    CALVAL = "calval"
    OPEN = "public"


class Entrypoint(StrEnum):
    MAAP = URL_MAAP
    OADS = URL_OADS
