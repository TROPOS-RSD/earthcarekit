from math import ceil
from typing import Any, TypeAlias, cast

import numpy as np
import pandas as pd

from .....geo.bbox import radius_to_bbox
from .....utils._cli._parse._types import _OrbitFrameInputs, _SearchInputs
from .....utils.time import time_to_iso, to_timestamp
from ._params import Params

LonMin: TypeAlias = float
LonMax: TypeAlias = float
LatMin: TypeAlias = float
LatMax: TypeAlias = float


def split_list(lst: list, n: int) -> list[list]:
    if n <= 0:
        return []
    max_len = ceil(len(lst) / n)
    if max_len == 0:
        return []
    return [lst[i : i + max_len] for i in range(0, len(lst), max_len)]


def split_range(r: tuple[int, int], n: int) -> list[tuple[int, int]]:
    if n <= 0:
        return [r]

    start, end = r
    size = end - start + 1

    quot, rem = divmod(size, n)
    if size <= n:
        return [r]

    ranges = []
    current = start

    for i in range(n):
        length = quot + (1 if i < rem else 0)
        ranges.append((current, current + length - 1))
        current += length
    return ranges


def complete_orbit_range(orbit_range: tuple[int | None, int | None]) -> tuple[int, int] | None:
    start_orbit, end_orbit = orbit_range

    if start_orbit is None and end_orbit is None:
        return None
    elif start_orbit is None:
        return (0, cast(int, end_orbit))
    elif end_orbit is None:
        _t_ref = pd.Timestamp("2025-08-01")
        _o_ref = 6675
        _t_now = pd.Timestamp.now()
        _t_delta = _t_now - _t_ref
        _days = _t_delta.total_seconds() / (60 * 60 * 24)
        end_orbit = int(_o_ref + (_days * 16))
        return (start_orbit, end_orbit)
    return (cast(int, start_orbit), cast(int, end_orbit))


def create_full_orbit_requests(
    inputs: _OrbitFrameInputs,
    n_max: int = 2000,
    **kwargs,
) -> list[Params]:
    searches: list[Params] = []

    full_orbits = inputs.full_orbits

    # Estimate number of results
    n_items = len(full_orbits) * 8
    n_requests = int(np.ceil(n_items / n_max))

    for orbits in split_list(full_orbits, n_requests):
        params = Params(orbit_numbers=orbits, **kwargs)
        searches.append(params)

    return searches


def create_full_orbit_range_requests(
    inputs: _OrbitFrameInputs,
    n_max: int = 2000,
    **kwargs,
) -> list[Params]:
    searches: list[Params] = []

    orbit_range = complete_orbit_range(inputs.full_orbit_range)
    if orbit_range is None:
        return []

    start_orbit, end_orbit = orbit_range

    # Estimate number of results
    n_items = (end_orbit - start_orbit + 1) * 8
    n_requests = int(np.ceil(n_items / n_max))

    for orb_rng in split_range(orbit_range, n_requests):
        params = Params(
            start_orbit_number=orb_rng[0],
            end_orbit_number=orb_rng[1],
            **kwargs,
        )
        searches.append(params)

    return searches


def create_frame_orbits_requests(
    inputs: _OrbitFrameInputs,
    n_max: int = 2000,
    **kwargs,
) -> list[Params]:
    searches: list[Params] = []
    frame_orbits = inputs.frame_orbits

    for frame_id, orbits in frame_orbits.items():
        # Estimate number of results
        n_items = len(orbits)
        n_requests = int(np.ceil(n_items / n_max))

        for orbs in split_list(orbits, n_requests):
            params = Params(orbit_numbers=orbs, frame_id=frame_id, **kwargs)
            searches.append(params)

    return searches


def create_frame_orbit_range_requests(
    inputs: _OrbitFrameInputs,
    n_max: int = 2000,
    **kwargs,
) -> list[Params]:
    searches: list[Params] = []
    frame_orbit_ranges = inputs.frame_orbit_ranges

    for frame_id, frame_orbit_range in frame_orbit_ranges.items():
        orbit_range = complete_orbit_range(frame_orbit_range)
        if orbit_range is None:
            continue

        start_orbit, end_orbit = orbit_range

        # Estimate number of results
        n_items = end_orbit - start_orbit + 1
        n_requests = int(np.ceil(n_items / n_max))

        for orb_rng in split_range(orbit_range, n_requests):
            params = Params(
                start_orbit_number=orb_rng[0],
                end_orbit_number=orb_rng[1],
                frame_id=frame_id,
                **kwargs,
            )
            searches.append(params)

    return searches


def create_orbit_frame_requests(
    inputs: _SearchInputs,
    n_max: int = 2000,
    **kwargs,
) -> list[Params]:
    in_oafs = inputs.orbit_and_frames
    return [
        *create_full_orbit_requests(in_oafs, n_max=n_max, **kwargs),
        *create_full_orbit_range_requests(in_oafs, n_max=n_max, **kwargs),
        *create_frame_orbits_requests(in_oafs, n_max=n_max, **kwargs),
        *create_frame_orbit_range_requests(in_oafs, n_max=n_max, **kwargs),
    ]


def create_time_range_requests(inputs: _SearchInputs, n_max: int = 2000, **kwargs) -> list[Params]:
    searches: list[Params] = []
    in_time = inputs.timestamps
    start_time, end_time = in_time.time_range
    if start_time is None and end_time is None:
        return []

    frame_ids: list[str] | list[None] = inputs.orbit_and_frames.frame_ids
    if len(frame_ids) == 0:
        frame_ids = [None]

    for frame_id in frame_ids:
        n_frames = 8 if frame_id is None else 1

        _st = to_timestamp(start_time) if start_time else to_timestamp("2024-07-31")
        _et = to_timestamp(end_time) if end_time else pd.Timestamp.now()

        # Estimate number of results
        _t_delta = _et - _st
        _days = _t_delta.total_seconds() / (60 * 60 * 24)
        n_orbits = max(1, int(_days * 16.0))
        n_items = n_orbits * n_frames
        n_requests = int(np.ceil(n_items / n_max))

        for i in range(n_requests):
            params = Params(
                start_time=time_to_iso(_st + (_t_delta / n_requests) * i),
                end_time=time_to_iso(_st + (_t_delta / n_requests) * (i + 1)),
                frame_id=frame_id,
                **kwargs,
            )
            searches.append(params)

    return searches


def create_timestamp_requests(inputs: _SearchInputs, n_max: int = 2000, **kwargs) -> list[Params]:
    searches: list[Params] = []

    for timestamp in inputs.timestamps.timestamps:
        timestamp = time_to_iso(timestamp)
        params = Params(
            start_time=timestamp,
            end_time=timestamp,
            **kwargs,
        )
        searches.append(params)

    return searches


def get_requests(inputs: _SearchInputs) -> list[Params]:

    orbit_direction: str | None = inputs.orbit_direction

    # Ensure correct bounding box format for STAC search
    bbox: tuple[LatMin, LonMin, LatMax, LonMax] | None = None
    rad: str | None = inputs.radius_search.radius
    lt: str | None = inputs.radius_search.lat
    ln: str | None = inputs.radius_search.lon
    radius: float | None = None if rad is None else float(rad)
    lat: float | None = None if lt is None else float(lt)
    lon: float | None = None if ln is None else float(ln)
    if isinstance(radius, float) and isinstance(lat, float) and isinstance(lon, float):
        lon_min, lon_max, lat_min, lat_max = radius_to_bbox(
            lat=lat,
            lon=lon,
            radius_km=radius,
        )
        bbox = (lat_min, lon_min, lat_max, lon_max)
    elif inputs.bbox_search.bbox:
        bb = tuple(float(x) for x in inputs.bbox_search.bbox.split(","))
        bbox = (bb[1], bb[0], bb[3], bb[2])

    start_time: str | None = inputs.timestamps.time_range[0]
    end_time: str | None = inputs.timestamps.time_range[1]

    n_max = 120

    product_type: str
    product_version: str | None
    kwargs: dict[str, Any]
    searches: list[Params] = []
    for product in inputs.products:
        product_type = product.type
        product_version = None if product.version == "latest" else product.version

        kwargs = dict(
            product_type=product_type,
            product_version=product_version,
            orbit_direction=orbit_direction,
            bbox=bbox,
            max_items=2000,
            start_time=start_time,
            end_time=end_time,
        )
        searches.extend(create_orbit_frame_requests(inputs, n_max=n_max, **kwargs))

        if len(searches) == 0:
            kwargs = dict(
                product_type=product_type,
                product_version=product_version,
                orbit_direction=orbit_direction,
                bbox=bbox,
                max_items=2000,
            )
            searches.extend(create_time_range_requests(inputs, n_max=n_max, **kwargs))

        kwargs = dict(
            product_type=product_type,
            product_version=product_version,
            max_items=2000,
        )
        searches.extend(create_timestamp_requests(inputs, n_max=n_max, **kwargs))

    return searches
