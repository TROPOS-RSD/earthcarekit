from logging import Logger
from typing import Final

import numpy as np
import pandas as pd

from ._exceptions import InvalidInputError
from ._parse_frame_ids import get_validated_frame_id
from ._parse_orbit_numbers import get_validated_orbit_number
from ._types import FrameIDStr, OrbitFrameStr, OrbitInt, _OrbitAndFrames

_FRAMES: Final[str] = "ABCDEFGH"
_NUM_FRAMES: Final[int] = 8


def get_validated_orbit_and_frame(
    orbit_and_frame: OrbitFrameStr, logger: Logger | None = None
) -> tuple[OrbitInt, FrameIDStr]:
    """Extracts validated orbit number and frame ID from string and raises InvalidInputError if string does not describe a orbit and frame"""
    try:
        orbit_number = get_validated_orbit_number(int(orbit_and_frame[0:-1]))
        frame_id = get_validated_frame_id(orbit_and_frame[-1])
    except Exception as e:
        exception_msg = f"{orbit_and_frame} is not a valid orbit and frame name. Valid names contain the orbit number followed by the frame id letter (e.g. 3000B or 03000B)."
        if logger:
            logger.exception(exception_msg)
        raise
    return orbit_number, frame_id


def get_complete_and_incomplete_orbits(
    orbit_and_frames: list[tuple[OrbitInt, OrbitFrameStr]] | None,
) -> tuple[list[OrbitInt], dict[OrbitFrameStr, list[OrbitInt]]]:
    """
    Finds complete orbits (i.e. where all frames are given) and incomplete orbits based on the given list of tuples.

    Args:
        orbit_and_frames: A list of tuples where each tuple contains
                          an orbit number (int) and a frame ID (str).

    Returns:
        tuple:
        - A list of complete orbits.
        - A dictionary where each key is a frame ID, and the value is a list of orbits assigned to that frame.
    """
    if not isinstance(orbit_and_frames, list):
        return [], {}
    if len(orbit_and_frames) == 0:
        return [], {}

    orbit_numbers: list[OrbitInt] = [oaf[0] for oaf in orbit_and_frames]
    frame_ids: list[OrbitFrameStr] = [oaf[1] for oaf in orbit_and_frames]

    df = pd.DataFrame(dict(orbit_number=orbit_numbers, frame_id=frame_ids))

    df_frames_per_orbit_lookup = df.groupby("orbit_number", as_index=False).agg(
        {"frame_id": lambda x: "".join(sorted("".join(x)))}
    )
    mask_complete_orbits = df_frames_per_orbit_lookup["frame_id"] == "ABCDEFGH"
    complete_orbits = df_frames_per_orbit_lookup.loc[mask_complete_orbits][
        "orbit_number"
    ].tolist()
    incomplete_orbits = df_frames_per_orbit_lookup.loc[~mask_complete_orbits][
        "orbit_number"
    ].tolist()
    df_incomplete_orbits = df.loc[df["orbit_number"].isin(incomplete_orbits)]
    df_orbits_per_frame_lookup = df_incomplete_orbits.groupby("frame_id").agg(
        {"orbit_number": list}
    )
    incomplete_orbits_frame_map = df_orbits_per_frame_lookup.to_dict()["orbit_number"]

    return complete_orbits, incomplete_orbits_frame_map


def get_frame_range(start_frame_id: str, end_frame_id: str) -> list[str]:
    """Returns list of frames in order of selected range (e.g. A-D -> ABCD and D-A -> DEFGHA)."""
    start_idx = _FRAMES.index(start_frame_id)
    end_idx = _FRAMES.index(end_frame_id)
    if end_idx < start_idx:
        end_idx = end_idx + _NUM_FRAMES
    frame_id_range = [
        _FRAMES[idx % _NUM_FRAMES] for idx in np.arange(start_idx, end_idx + 1)
    ]
    return frame_id_range


def parse_orbit_and_frames(
    orbit_and_frames: list[OrbitFrameStr] | None,
    start_orbit_and_frame: OrbitFrameStr | None,
    end_orbit_and_frame: OrbitFrameStr | None,
    logger: Logger | None = None,
) -> _OrbitAndFrames:
    orbit_and_frame_list: list[tuple[OrbitInt, FrameIDStr]] = []
    if isinstance(orbit_and_frames, list):
        orbit_and_frame_list = [
            get_validated_orbit_and_frame(oaf, logger=logger)
            for oaf in orbit_and_frames
        ]

    soaf: tuple[OrbitInt, FrameIDStr] | None = None
    eoaf: tuple[OrbitInt, FrameIDStr] | None = None
    if isinstance(start_orbit_and_frame, str):
        soaf = get_validated_orbit_and_frame(start_orbit_and_frame, logger=logger)
    if isinstance(end_orbit_and_frame, str):
        eoaf = get_validated_orbit_and_frame(end_orbit_and_frame, logger=logger)

    lower: OrbitInt | None = None
    upper: OrbitInt | None = None

    if isinstance(soaf, tuple) and isinstance(eoaf, tuple):
        so, sf = soaf
        eo, ef = eoaf
        if so > eo:
            raise InvalidInputError(
                f"End orbit and frame ({end_orbit_and_frame}) is smaller than start ({start_orbit_and_frame}) but needs to be greater or equal."
            )
        if so == eo:
            if sf > ef:
                raise InvalidInputError(
                    f"End orbit and frame ({end_orbit_and_frame}) is smaller than start ({start_orbit_and_frame}) but needs to be greater or equal."
                )
            _frame_range = get_frame_range(sf, ef)
            orbit_and_frame_list = orbit_and_frame_list + [
                (so, f) for f in _frame_range
            ]
        else:
            _frame_range = get_frame_range(sf, _FRAMES[-1])
            orbit_and_frame_list = orbit_and_frame_list + [
                (so, f) for f in _frame_range
            ]
            _frame_range = get_frame_range(_FRAMES[0], ef)
            orbit_and_frame_list = orbit_and_frame_list + [
                (eo, f) for f in _frame_range
            ]
            lower = so + 1
            upper = eo - 1
    elif isinstance(soaf, tuple):
        so, sf = soaf
        if sf == _FRAMES[0]:
            lower = so
        else:
            _frame_range = get_frame_range(sf, _FRAMES[-1])
            orbit_and_frame_list = orbit_and_frame_list + [
                (so, f) for f in _frame_range
            ]
            lower = so + 1
    elif isinstance(eoaf, tuple):
        eo, ef = eoaf
        if ef == _FRAMES[-1]:
            upper = eo
        else:
            _frame_range = get_frame_range(_FRAMES[0], ef)
            orbit_and_frame_list = orbit_and_frame_list + [
                (eo, f) for f in _frame_range
            ]
            upper = eo - 1

    orbit_and_frame_list = sorted(list(set(orbit_and_frame_list)))

    complete_orbits, incomplete_orbits_frame_map = get_complete_and_incomplete_orbits(
        orbit_and_frame_list
    )

    _complete_orbits = np.sort(complete_orbits)
    mask = np.full(_complete_orbits.shape, True, dtype=bool)

    if isinstance(lower, OrbitInt) and isinstance(upper, OrbitInt):
        for i, co in enumerate(_complete_orbits):
            if lower <= co <= upper:
                mask[i] = False
            elif co - 1 == upper:
                upper = upper + 1
                mask[i] = False
            else:
                break
    elif isinstance(lower, OrbitInt):
        for i, co in enumerate(_complete_orbits):
            if lower <= co:
                mask[i] = False
            else:
                break
    elif isinstance(upper, OrbitInt):
        for i, co in enumerate(_complete_orbits):
            if co <= upper:
                mask[i] = False
            elif co - 1 == upper:
                upper = upper + 1
                mask[i] = False
            else:
                break

    if isinstance(lower, OrbitInt):
        for i in range(len(_complete_orbits) - 1, -1, -1):
            co = _complete_orbits[i]
            if co + 1 == lower:
                lower = lower - 1
                mask[i] = False
            else:
                break

    assert _complete_orbits.shape == mask.shape

    _complete_orbits = _complete_orbits[mask].tolist()
    full_orbit_range: tuple[OrbitInt | None, OrbitInt | None] = (lower, upper)

    return _OrbitAndFrames(
        full_orbit_range=full_orbit_range,
        full_orbit_list=[int(o) for o in _complete_orbits],
        frame_orbits=incomplete_orbits_frame_map,
    )
