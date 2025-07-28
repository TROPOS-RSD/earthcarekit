from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from ..utils._cli._parse._types import (
    CollectionStr,
    FrameIDStr,
    OrbitFrameStr,
    OrbitInt,
    ProductTypeStr,
    ProductTypeVersion,
    ProductVersionStr,
    TimestampStr,
    _BBoxSearch,
    _OrbitAndFrames,
    _OrbitFrameInputs,
    _OrbitNumbers,
    _RadiusSearch,
    _SearchInputs,
    _TimestampInputs,
)
from ._constants import URL_MAAP, URL_OADS


class UserType(StrEnum):
    COMMISSIONING = "commissioning"
    CALVAL = "calval"
    OPEN = "public"


class Entrypoint(StrEnum):
    MAAP = URL_MAAP
    OADS = URL_OADS
