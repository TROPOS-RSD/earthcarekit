from dataclasses import dataclass
from logging import Logger

from ._exceptions import InvalidInputError
from ._types import OrbitInt, _OrbitNumbers


def get_validated_orbit_number(
    orbit_number: OrbitInt, logger: Logger | None = None
) -> OrbitInt:
    """Raises InvalidInputError if orbit number is negative or too large"""
    try:
        if orbit_number < 0 or orbit_number > 99999:
            exception_msg = f"{orbit_number} is not a valid orbit number. Valid orbit numbers are positive integers up to 5 digits."
            raise InvalidInputError(exception_msg)
    except InvalidInputError as e:
        if logger:
            logger.exception(e)
        raise
    return orbit_number


def parse_orbit_numbers(
    orbit_numbers: list[int] | None,
    start_orb: int | None,
    end_orb: int | None,
    logger: Logger | None = None,
) -> _OrbitNumbers:
    orb_list: list[OrbitInt] = []
    if isinstance(orbit_numbers, list):
        orb_list = [get_validated_orbit_number(o, logger=logger) for o in orbit_numbers]
    orb_range: tuple[OrbitInt | None, OrbitInt | None] = (
        None if not start_orb else get_validated_orbit_number(start_orb, logger=logger),
        None if not end_orb else get_validated_orbit_number(end_orb, logger=logger),
    )

    if isinstance(orb_range[0], OrbitInt) and isinstance(orb_range[1], OrbitInt):
        orb_list = [o for o in orb_list if o < orb_range[0] or o > orb_range[1]]
    elif isinstance(orb_range[0], OrbitInt):
        orb_list = [o for o in orb_list if o < orb_range[0]]
    elif isinstance(orb_range[1], OrbitInt):
        orb_list = [o for o in orb_list if o > orb_range[1]]

    return _OrbitNumbers(
        orbit_range=orb_range,
        orbit_list=orb_list,
    )
