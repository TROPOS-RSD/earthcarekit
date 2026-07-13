import logging
from typing import Any

from .core import get_enum_validated_param, get_validated_param
from .params import (
    P_FRAME_ID,
    P_ORBIT_DIRECTION,
    P_ORBIT_NUMBER,
    P_PRODUCT_TYPE,
    P_PRODUCT_VERSION,
    Params,
)

log = logging.getLogger("ecdownload")


def _get_missing_filter_input_msg(property: str) -> str:
    return f"Missing required property '{property}'"


def get_product_type_filter(
    properties: dict[str, Any],
    params: Params,
) -> str:
    product_type = params.product_type
    if product_type is None:
        msg = _get_missing_filter_input_msg(P_PRODUCT_TYPE)
        log.error(msg)
        raise ValueError(msg)
    product_type = get_enum_validated_param(properties, P_PRODUCT_TYPE, product_type)
    return f"{P_PRODUCT_TYPE} = '{product_type}'"


def get_product_version_filter(
    properties: dict[str, Any],
    params: Params,
) -> str | None:
    product_version = params.product_version
    if product_version:
        product_version = get_enum_validated_param(
            properties, P_PRODUCT_VERSION, product_version.lower()
        )
        return f"{P_PRODUCT_VERSION} = '{product_version}'"
    return None


def get_orbit_direction_filter(
    properties: dict[str, Any],
    params: Params,
) -> str | None:
    orbit_direction = params.orbit_direction
    if orbit_direction:
        orbit_direction = get_enum_validated_param(
            properties, P_ORBIT_DIRECTION, str(orbit_direction).upper()
        )
        return f"{P_ORBIT_DIRECTION} = '{orbit_direction}'"
    return None


def get_orbit_number_list_filter(orbit_numbers: list[int]) -> str:
    if len(orbit_numbers) == 1:
        filt = f"{P_ORBIT_NUMBER} = {int(orbit_numbers[0])}"
    else:
        filt = "("
        for i, orbit_number in enumerate(orbit_numbers):
            if i == 0:
                filt = f"{filt} {P_ORBIT_NUMBER} = {int(orbit_number)}"
            else:
                filt = f"{filt} OR {P_ORBIT_NUMBER} = {int(orbit_number)}"
        filt = f"{filt} )"
    return filt


def get_orbit_number_filter(
    properties: dict[str, Any],
    params: Params,
) -> str | None:
    orbit_numbers = params.orbit_numbers
    start_orbit_number = params.start_orbit_number
    end_orbit_number = params.end_orbit_number

    if orbit_numbers is None and start_orbit_number is None and end_orbit_number is None:
        return None

    get_validated_param(properties, P_ORBIT_NUMBER)

    if orbit_numbers and len(orbit_numbers) > 0:
        if start_orbit_number and end_orbit_number:
            return (
                f"( {get_orbit_number_list_filter(orbit_numbers)}"
                f" OR ( {P_ORBIT_NUMBER} >= {int(start_orbit_number)}"
                f" AND {P_ORBIT_NUMBER} <= {int(end_orbit_number)} ) )"
            )
        elif start_orbit_number:
            return (
                f"( {get_orbit_number_list_filter(orbit_numbers)}"
                f" OR {P_ORBIT_NUMBER} >= {int(start_orbit_number)} )"
            )
        elif end_orbit_number:
            return (
                f"( {get_orbit_number_list_filter(orbit_numbers)}"
                f" OR {P_ORBIT_NUMBER} <= {int(end_orbit_number)} )"
            )
        return get_orbit_number_list_filter(orbit_numbers)
    elif start_orbit_number and end_orbit_number:
        return (
            f"( {P_ORBIT_NUMBER} >= {int(start_orbit_number)}"
            f" AND {P_ORBIT_NUMBER} <= {int(end_orbit_number)} )"
        )
    elif start_orbit_number:
        return f"{P_ORBIT_NUMBER} >= {int(start_orbit_number)}"
    elif end_orbit_number:
        return f"{P_ORBIT_NUMBER} <= {int(end_orbit_number)}"
    return None


def get_frame_id_filter(
    properties: dict[str, Any],
    params: Params,
) -> str | None:
    frame_id = params.frame_id
    if frame_id:
        frame_id = get_enum_validated_param(properties, P_FRAME_ID, frame_id.upper())
        return f"{P_FRAME_ID} = '{frame_id}'"
    return None


def filter_append_and(a: str, b: str | None) -> str:
    if b:
        return f"{a} AND {b}"
    return a


def create_filter(
    properties: dict[str, Any],
    params: Params,
) -> str:
    kwargs: dict[str, Any] = dict(
        properties=properties,
        params=params,
    )

    product_type_filter: str = get_product_type_filter(**kwargs)
    product_version_filter: str | None = get_product_version_filter(**kwargs)
    orbit_direction_filter: str | None = get_orbit_direction_filter(**kwargs)
    orbit_number_filter: str | None = get_orbit_number_filter(**kwargs)
    frame_id_filter: str | None = get_frame_id_filter(**kwargs)

    filt: str = product_type_filter
    filt = filter_append_and(filt, product_version_filter)
    filt = filter_append_and(filt, orbit_direction_filter)
    filt = filter_append_and(filt, orbit_number_filter)
    filt = filter_append_and(filt, frame_id_filter)

    return filt
