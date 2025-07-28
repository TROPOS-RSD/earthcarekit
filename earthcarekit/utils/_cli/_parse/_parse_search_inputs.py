from logging import Logger

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
    product_type: list[str],
    product_version: str | None = None,
    orbit_number: list[OrbitInt] | None = None,
    start_orbit_number: OrbitInt | None = None,
    end_orbit_number: OrbitInt | None = None,
    frame_id: list[FrameIDStr] | None = None,
    orbit_and_frame: list[OrbitFrameStr] | None = None,
    start_orbit_and_frame: OrbitFrameStr | None = None,
    end_orbit_and_frame: OrbitFrameStr | None = None,
    timestamps: list[TimestampStr] | None = None,
    start_time: TimestampStr | None = None,
    end_time: TimestampStr | None = None,
    radius_search: list[str] | None = None,
    bounding_box: list[str] | None = None,
    logger: Logger | None = None,
) -> _SearchInputs:
    product_inputs: list[ProductTypeVersion] = parse_products(
        product_type,
        product_version,
        logger=logger,
    )

    orbit_frame_inputs: _OrbitFrameInputs = parse_all_orbit_and_frame_inputs(
        args_orbit_number=orbit_number,
        args_start_orbit_number=start_orbit_number,
        args_end_orbit_number=end_orbit_number,
        args_frame_id=frame_id,
        args_orbit_and_frame=orbit_and_frame,
        args_start_orbit_and_frame=start_orbit_and_frame,
        args_end_orbit_and_frame=end_orbit_and_frame,
        logger=logger,
    )

    time_inputs: _TimestampInputs = parse_time(
        timestamps,
        start_time,
        end_time,
        logger=logger,
    )

    radius_search_inputs: _RadiusSearch = parse_radius_search(radius_search)
    bbox_search_inputs: _BBoxSearch = parse_bbox_search(bounding_box)

    return _SearchInputs(
        products=product_inputs,
        orbit_and_frames=orbit_frame_inputs,
        timestamps=time_inputs,
        radius_search=radius_search_inputs,
        bbox_search=bbox_search_inputs,
    )
