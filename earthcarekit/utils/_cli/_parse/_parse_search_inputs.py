from logging import Logger
from typing import Sequence

from ._parse_all_orbit_and_frame_inputs import parse_all_orbit_and_frame_inputs
from ._parse_dirpaths import parse_path_to_data
from ._parse_geo_search_bbox import parse_bbox_search
from ._parse_geo_search_radius import parse_radius_search
from ._parse_path_to_config import parse_path_to_config
from ._parse_product_type import parse_product_type_and_version
from ._parse_products import parse_products
from ._parse_time import parse_time
from ._types import (
    FrameIDStr,
    OrbitFrameStr,
    OrbitInt,
    ProductTypeVersion,
    TimestampStr,
    _BBoxSearch,
    _OrbitFrameInputs,
    _RadiusSearch,
    _SearchInputs,
    _TimestampInputs,
)


def parse_search_inputs(
    product_type: Sequence[str],
    product_version: str | None = None,
    orbit_number: Sequence[OrbitInt] | None = None,
    start_orbit_number: OrbitInt | None = None,
    end_orbit_number: OrbitInt | None = None,
    frame_id: Sequence[FrameIDStr] | None = None,
    orbit_and_frame: Sequence[OrbitFrameStr] | None = None,
    start_orbit_and_frame: OrbitFrameStr | None = None,
    end_orbit_and_frame: OrbitFrameStr | None = None,
    timestamps: Sequence[TimestampStr] | None = None,
    start_time: TimestampStr | None = None,
    end_time: TimestampStr | None = None,
    radius_search: Sequence[str | float] | None = None,
    bounding_box: Sequence[str | float] | None = None,
    logger: Logger | None = None,
) -> _SearchInputs:

    def _to_list(seq: Sequence | None) -> list | None:
        return None if seq is None else list(seq)

    product_inputs: list[ProductTypeVersion] = parse_products(
        [pt for pt in product_type],
        product_version,
        logger=logger,
    )

    orbit_frame_inputs: _OrbitFrameInputs = parse_all_orbit_and_frame_inputs(
        args_orbit_number=_to_list(orbit_number),
        args_start_orbit_number=start_orbit_number,
        args_end_orbit_number=end_orbit_number,
        args_frame_id=_to_list(frame_id),
        args_orbit_and_frame=_to_list(orbit_and_frame),
        args_start_orbit_and_frame=start_orbit_and_frame,
        args_end_orbit_and_frame=end_orbit_and_frame,
        logger=logger,
    )

    time_inputs: _TimestampInputs = parse_time(
        _to_list(timestamps),
        start_time,
        end_time,
        logger=logger,
    )

    radius_search_inputs: _RadiusSearch = parse_radius_search(_to_list(radius_search))
    bbox_search_inputs: _BBoxSearch = parse_bbox_search(_to_list(bounding_box))

    return _SearchInputs(
        products=product_inputs,
        orbit_and_frames=orbit_frame_inputs,
        timestamps=time_inputs,
        radius_search=radius_search_inputs,
        bbox_search=bbox_search_inputs,
    )
