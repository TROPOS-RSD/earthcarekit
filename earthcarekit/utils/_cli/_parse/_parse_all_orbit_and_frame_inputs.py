from dataclasses import dataclass
from logging import Logger

import numpy as np

from ._exceptions import InvalidInputError
from ._parse_frame_ids import parse_frame_ids
from ._parse_orbit_and_frames import parse_orbit_and_frames
from ._parse_orbit_numbers import parse_orbit_numbers
from ._types import FrameIDStr, OrbitFrameStr, OrbitInt, _OrbitFrameInputs


def validate_combination_of_given_orbit_and_frame_range_inputs(
    start_orbit_and_frame: FrameIDStr | None,
    end_orbit_and_frame: FrameIDStr | None,
    start_orbit_number: OrbitInt | None,
    end_orbit_number: OrbitInt | None,
    orbit_numbers: list[OrbitInt] | None,
    frame_ids: list[FrameIDStr] | None,
    logger: Logger | None = None,
) -> None:
    """Raises an InvalidInputError, if combined orbit and frame options (-soaf, -eoaf) are used in combination with any other orbit (-o, -so, -eo) or frames (-f) option (exception: -oaf)."""
    try:
        if (start_orbit_and_frame is not None or end_orbit_and_frame is not None) and (
            start_orbit_number is not None
            or end_orbit_number is not None
            or orbit_numbers is not None
            or frame_ids is not None
        ):
            exception_msg = f"Options to select a range of obit and frame names (-soaf, -eoaf) can not be used in combination with the options to select only a range of orbits (-o, -so, -eo) or single frames (-f)."
            raise InvalidInputError(exception_msg)
    except InvalidInputError as e:
        if logger:
            logger.exception(e)
        raise


def parse_all_orbit_and_frame_inputs(
    args_orbit_number: list[OrbitInt] | None,
    args_start_orbit_number: OrbitInt | None,
    args_end_orbit_number: OrbitInt | None,
    args_frame_id: list[FrameIDStr] | None,
    args_orbit_and_frame: list[OrbitFrameStr] | None,
    args_start_orbit_and_frame: OrbitFrameStr | None,
    args_end_orbit_and_frame: OrbitFrameStr | None,
    logger: Logger | None = None,
) -> _OrbitFrameInputs:
    validate_combination_of_given_orbit_and_frame_range_inputs(
        start_orbit_and_frame=args_start_orbit_and_frame,
        end_orbit_and_frame=args_end_orbit_and_frame,
        start_orbit_number=args_start_orbit_number,
        end_orbit_number=args_end_orbit_number,
        orbit_numbers=args_orbit_number,
        frame_ids=args_frame_id,
        logger=logger,
    )

    full_orbits: list[OrbitInt] = []
    frame_orbits: dict[FrameIDStr, list[OrbitInt]] = {
        "A": [],
        "B": [],
        "C": [],
        "D": [],
        "E": [],
        "F": [],
        "G": [],
        "H": [],
    }
    full_orbit_range: tuple[OrbitInt | None, OrbitInt | None] = (None, None)
    frame_orbit_ranges: dict[
        FrameIDStr,
        tuple[OrbitInt | None, OrbitInt | None],
    ] = {
        "A": (None, None),
        "B": (None, None),
        "C": (None, None),
        "D": (None, None),
        "E": (None, None),
        "F": (None, None),
        "G": (None, None),
        "H": (None, None),
    }
    orbit_numbers = parse_orbit_numbers(
        args_orbit_number,
        args_start_orbit_number,
        args_end_orbit_number,
        logger=logger,
    )

    frame_ids = parse_frame_ids(args_frame_id)

    if len(frame_ids) == 0:
        full_orbits = [int(o) for o in np.unique(np.append(full_orbits, orbit_numbers.orbit_list)).flatten().tolist()]  # type: ignore
        full_orbit_range = orbit_numbers.orbit_range  # type: ignore
    else:
        for f in frame_ids:
            frame_orbits[f].extend(orbit_numbers.orbit_list)  # type: ignore
            frame_orbit_ranges[f] = orbit_numbers.orbit_range  # type: ignore

    orbit_and_frames = parse_orbit_and_frames(
        args_orbit_and_frame,
        args_start_orbit_and_frame,
        args_end_orbit_and_frame,
        logger=logger,
    )

    full_orbits = [int(o) for o in np.unique(np.append(full_orbits, orbit_and_frames.full_orbit_list)).flatten().tolist()]  # type: ignore
    if all([x is None for x in full_orbit_range]):
        full_orbit_range = orbit_and_frames.full_orbit_range  # type: ignore

    for k, v in orbit_and_frames.frame_orbits.items():  # type: ignore
        frame_orbits[k] = [int(o) for o in np.unique(np.append(frame_orbits[k], v)).flatten().tolist()]  # type: ignore

    return _OrbitFrameInputs(
        frame_orbits=frame_orbits,
        full_orbit_range=full_orbit_range,
        frame_orbit_ranges=frame_orbit_ranges,
        full_orbits=full_orbits,
        frame_ids=frame_ids,
    )
