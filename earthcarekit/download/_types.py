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

__all__ = [
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
