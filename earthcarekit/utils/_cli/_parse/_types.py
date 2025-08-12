from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

OrbitFrameStr: TypeAlias = str
FrameIDStr: TypeAlias = str
OrbitInt: TypeAlias = int
TimestampStr: TypeAlias = str
CollectionStr: TypeAlias = str
ProductTypeStr: TypeAlias = str
ProductVersionStr: TypeAlias = str


@dataclass
class ProductTypeVersion:
    type: str
    version: str

    @property
    def formatted_version(self) -> str | None:
        if self.version == "latest":
            return None
        return self.version


@dataclass
class _TimestampInputs:
    timestamps: list[TimestampStr]
    time_range: tuple[TimestampStr | None, TimestampStr | None]


@dataclass
class _OrbitNumbers:
    orbit_range: tuple[OrbitInt | None, OrbitInt | None]
    orbit_list: list[OrbitInt]


@dataclass
class _OrbitAndFrames:
    full_orbit_range: tuple[OrbitInt | None, OrbitInt | None]
    full_orbit_list: list[OrbitInt]
    frame_orbits: dict[OrbitFrameStr, list[OrbitInt]]


@dataclass
class _RadiusSearch:
    radius: str | None
    lat: str | None
    lon: str | None


@dataclass
class _BBoxSearch:
    bbox: str | None


@dataclass
class _OrbitFrameInputs:
    full_orbits: list[OrbitInt]
    full_orbit_range: tuple[OrbitInt | None, OrbitInt | None]
    frame_orbits: dict[FrameIDStr, list[OrbitInt]]
    frame_orbit_ranges: dict[FrameIDStr, tuple[OrbitInt | None, OrbitInt | None]]
    frame_ids: list[FrameIDStr]


@dataclass
class _SearchInputs:
    products: list[ProductTypeVersion]
    orbit_and_frames: _OrbitFrameInputs
    timestamps: _TimestampInputs
    radius_search: _RadiusSearch
    bbox_search: _BBoxSearch
