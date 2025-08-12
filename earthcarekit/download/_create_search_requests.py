from itertools import islice
from logging import Logger
from typing import cast

import pandas as pd

from ..utils._cli import console_exclusive_info
from ._collection_selection import (
    CollectionStr,
    ProductTypeStr,
    get_collection_product_type_dict,
)
from ._eo_collection import EOCollection, get_available_collections
from ._eo_product import get_available_parameters, get_available_products
from ._eo_search_request import EOSearchRequest
from ._parse import get_collection_names_available_to_user, parse_user_type
from ._product_types import get_collection_names_matching_product_availability
from ._types import (
    CollectionStr,
    Entrypoint,
    FrameIDStr,
    OrbitFrameStr,
    OrbitInt,
    ProductTypeVersion,
    ProductVersionStr,
    TimestampStr,
    UserType,
    _BBoxSearch,
    _OrbitFrameInputs,
    _RadiusSearch,
    _SearchInputs,
    _TimestampInputs,
)


def split_list_into_chunks(lst: list, size: int) -> list[list]:
    """Splits a list into chunks or sublists each containing at most N elements"""
    iterator = iter(lst)
    return [list(islice(iterator, size)) for _ in range((len(lst) + size - 1) // size)]


def create_search_request_list(
    entrypoint: Entrypoint,
    search_inputs: _SearchInputs,
    input_user_type: str | None = None,
    candidate_coll_names_user: list[CollectionStr] | None = None,
    logger: Logger | None = None,
) -> list[EOSearchRequest]:

    products: list[ProductTypeVersion] = search_inputs.products
    orbit_and_frames: _OrbitFrameInputs = search_inputs.orbit_and_frames
    timestamps: _TimestampInputs = search_inputs.timestamps
    radius_search: _RadiusSearch = search_inputs.radius_search
    bbox_search: _BBoxSearch = search_inputs.bbox_search
    frame_ids: list[FrameIDStr | None] = cast(
        list[FrameIDStr | None],
        orbit_and_frames.frame_ids,
    )
    if len(frame_ids) == 0:
        frame_ids = [None]

    collections: list[EOCollection] = get_available_collections(
        entrypoint=entrypoint, logger=logger
    )
    collection_product_type_dict: dict[CollectionStr, list[ProductTypeStr]] = (
        get_collection_product_type_dict(collections)
    )

    if isinstance(input_user_type, str):
        user_type: UserType = parse_user_type(input_user_type)
        candidate_coll_names_user = get_collection_names_available_to_user(
            user_type, entrypoint=entrypoint
        )
    elif not isinstance(candidate_coll_names_user, list):
        raise ValueError(f"Missing candidate_coll_names_user")

    if entrypoint == Entrypoint.MAAP:
        candidate_coll_names_user = [
            c if "_MAAP" in c else f"{c}_MAAP" for c in candidate_coll_names_user
        ]
    else:
        candidate_coll_names_user = [
            c if "_MAAP" not in c else c.replace("_MAAP", "")
            for c in candidate_coll_names_user
        ]

    planned_requests: list[EOSearchRequest] = []
    for product in products:
        is_only_timerange: bool = isinstance(
            timestamps.time_range[0], TimestampStr
        ) or isinstance(timestamps.time_range[1], TimestampStr)

        candidate_coll_names_all = get_collection_names_matching_product_availability(
            product,
            collection_product_type_dict,
        )
        candidate_coll_names: list[CollectionStr] = list(
            set(candidate_coll_names_all) & set(candidate_coll_names_user)
        )
        candidate_colls: list[EOCollection] = [
            c for c in collections if c.name in candidate_coll_names
        ]

        for t in timestamps.timestamps:
            new_search_request = EOSearchRequest(
                candidate_collections=candidate_colls,
                product_type=product.type,
                product_version=product.formatted_version,
                radius=radius_search.radius,
                lat=radius_search.lat,
                lon=radius_search.lon,
                bbox=bbox_search.bbox,
                start_time=t,
                end_time=t,
                orbit_number=None,
                start_orbit_number=None,
                end_orbit_number=None,
                frame_id=None,
            )
            planned_requests.append(new_search_request)

        if isinstance(orbit_and_frames.full_orbit_range[0], int) or isinstance(
            orbit_and_frames.full_orbit_range[1], int
        ):
            is_only_timerange = False
            new_search_request = EOSearchRequest(
                candidate_collections=candidate_colls,
                product_type=product.type,
                product_version=product.formatted_version,
                radius=radius_search.radius,
                lat=radius_search.lat,
                lon=radius_search.lon,
                bbox=bbox_search.bbox,
                start_time=timestamps.time_range[0],
                end_time=timestamps.time_range[1],
                orbit_number=None,
                start_orbit_number=orbit_and_frames.full_orbit_range[0],
                end_orbit_number=orbit_and_frames.full_orbit_range[1],
                frame_id=None,
            )
            planned_requests.append(new_search_request)

        if len(orbit_and_frames.full_orbits) > 0:
            max_orbs: int = 50
            full_orbit_chunks = split_list_into_chunks(
                orbit_and_frames.full_orbits, max_orbs
            )
            for chunk in full_orbit_chunks:
                is_only_timerange = False
                new_search_request = EOSearchRequest(
                    candidate_collections=candidate_colls,
                    product_type=product.type,
                    product_version=product.formatted_version,
                    radius=radius_search.radius,
                    lat=radius_search.lat,
                    lon=radius_search.lon,
                    bbox=bbox_search.bbox,
                    start_time=timestamps.time_range[0],
                    end_time=timestamps.time_range[1],
                    orbit_number=chunk,
                    start_orbit_number=None,
                    end_orbit_number=None,
                    frame_id=None,
                )
                planned_requests.append(new_search_request)

        for frame_id, orbit_range in orbit_and_frames.frame_orbit_ranges.items():
            if isinstance(orbit_range[0], int) or isinstance(orbit_range[1], int):
                is_only_timerange = False
                new_search_request = EOSearchRequest(
                    candidate_collections=candidate_colls,
                    product_type=product.type,
                    product_version=product.formatted_version,
                    radius=radius_search.radius,
                    lat=radius_search.lat,
                    lon=radius_search.lon,
                    bbox=bbox_search.bbox,
                    start_time=timestamps.time_range[0],
                    end_time=timestamps.time_range[1],
                    orbit_number=None,
                    start_orbit_number=orbit_range[0],
                    end_orbit_number=orbit_range[1],
                    frame_id=frame_id,
                )
                planned_requests.append(new_search_request)

        for frame_id, orbits in orbit_and_frames.frame_orbits.items():
            if len(orbits) > 0:
                is_only_timerange = False
                new_search_request = EOSearchRequest(
                    candidate_collections=candidate_colls,
                    product_type=product.type,
                    product_version=product.formatted_version,
                    radius=radius_search.radius,
                    lat=radius_search.lat,
                    lon=radius_search.lon,
                    bbox=bbox_search.bbox,
                    start_time=timestamps.time_range[0],
                    end_time=timestamps.time_range[1],
                    orbit_number=orbits,
                    start_orbit_number=None,
                    end_orbit_number=None,
                    frame_id=frame_id,
                )
                planned_requests.append(new_search_request)

        if is_only_timerange:
            for frame_id in frame_ids:
                new_search_request = EOSearchRequest(
                    candidate_collections=candidate_colls,
                    product_type=product.type,
                    product_version=product.formatted_version,
                    radius=radius_search.radius,
                    lat=radius_search.lat,
                    lon=radius_search.lon,
                    bbox=bbox_search.bbox,
                    start_time=timestamps.time_range[0],
                    end_time=timestamps.time_range[1],
                    orbit_number=None,
                    start_orbit_number=None,
                    end_orbit_number=None,
                    frame_id=frame_id,
                )
            planned_requests.append(new_search_request)

    if logger and len(planned_requests) == 0:
        console_exclusive_info()
        logger.warning(
            "There are not enough user inputs to create valid search requests."
        )
        logger.warning(
            "Please ensure that you specify at least individual orbits or timestamps, or alternatively an orbit or time range."
        )

    return planned_requests
