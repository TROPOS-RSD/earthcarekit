from dataclasses import dataclass, replace
from typing import Literal, Self, TypeAlias, TypeVar, overload

from pystac_client.item_search import IntersectsLike

from .....utils import sentinels

South: TypeAlias = float
West: TypeAlias = float
North: TypeAlias = float
East: TypeAlias = float

T = TypeVar("T")


@overload
def _set(a: sentinels.Unset, b: T) -> T: ...
@overload
def _set(a: T, b: T) -> T: ...
def _set(a, b):
    return a if not isinstance(a, sentinels.Unset) else b


@dataclass(frozen=True)
class Params:
    product_type: str
    product_version: str | None = None
    orbit_numbers: list[int] | None = None
    start_orbit_number: int | None = None
    end_orbit_number: int | None = None
    frame_id: str | None = None
    orbit_direction: str | Literal["ASCENDING", "DESCENDING"] | None = None
    radius: float | None = None
    lat: float | None = None
    lon: float | None = None
    bbox: tuple[South, West, North, East] | None = None
    intersects: IntersectsLike | None = None
    start_time: str | None = None
    end_time: str | None = None
    max_items: int = 2000

    def replace(
        self: Self,
        product_type: str | sentinels.Unset = sentinels.UNSET,
        product_version: str | None | sentinels.Unset = sentinels.UNSET,
        orbit_numbers: list[int] | None | sentinels.Unset = sentinels.UNSET,
        start_orbit_number: int | None | sentinels.Unset = sentinels.UNSET,
        end_orbit_number: int | None | sentinels.Unset = sentinels.UNSET,
        frame_id: str | None | sentinels.Unset = sentinels.UNSET,
        orbit_direction: str
        | Literal["ASCENDING", "DESCENDING"]
        | None
        | sentinels.Unset = sentinels.UNSET,
        radius: float | None | sentinels.Unset = sentinels.UNSET,
        lat: float | None | sentinels.Unset = sentinels.UNSET,
        lon: float | None | sentinels.Unset = sentinels.UNSET,
        bbox: tuple[South, West, North, East] | None | sentinels.Unset = sentinels.UNSET,
        intersects: IntersectsLike | None | sentinels.Unset = sentinels.UNSET,
        start_time: str | None | sentinels.Unset = sentinels.UNSET,
        end_time: str | None | sentinels.Unset = sentinels.UNSET,
        max_items: int | sentinels.Unset = sentinels.UNSET,
    ) -> Self:
        return replace(
            self,
            product_type=_set(product_type, self.product_type),
            product_version=_set(product_version, self.product_version),
            orbit_numbers=_set(orbit_numbers, self.orbit_numbers),
            start_orbit_number=_set(start_orbit_number, self.start_orbit_number),
            end_orbit_number=_set(end_orbit_number, self.end_orbit_number),
            frame_id=_set(frame_id, self.frame_id),
            orbit_direction=_set(orbit_direction, self.orbit_direction),
            radius=_set(radius, self.radius),
            lat=_set(lat, self.lat),
            lon=_set(lon, self.lon),
            bbox=_set(bbox, self.bbox),
            # We ignore type here since Mypy infers IntersectsLike as object
            intersects=_set(intersects, self.intersects),  # type: ignore
            start_time=_set(start_time, self.start_time),
            end_time=_set(end_time, self.end_time),
            max_items=_set(max_items, self.max_items),
        )
