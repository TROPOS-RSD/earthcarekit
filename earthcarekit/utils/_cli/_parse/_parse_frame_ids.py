from logging import Logger
from typing import Final

from ._exceptions import InvalidInputError
from ._types import FrameIDStr

_FRAMES: Final[str] = "ABCDEFGH"
_NUM_FRAMES: Final[int] = 8


def get_validated_frame_id(
    frame_id: FrameIDStr,
    logger: Logger | None = None,
) -> FrameIDStr:
    """Formats frame ID and raises InvalidInputError if it is invalid"""
    try:
        frame_id = frame_id.upper()
        if len(frame_id) != 1:
            exception_msg = f"Got an empty string as frame ID. Valid frames are single letters from A to H."
            raise InvalidInputError(exception_msg)
        if frame_id not in "ABCDEFGH":
            exception_msg = f"{frame_id} is not a valid frame ID. Valid frames are single letters from A to H."
            raise InvalidInputError(exception_msg)
    except InvalidInputError as e:
        if logger:
            logger.exception(e)
        raise
    return frame_id


def parse_frame_ids(
    frame_ids: list[FrameIDStr] | None,
    logger: Logger | None = None,
) -> list[FrameIDStr]:
    if not isinstance(frame_ids, list):
        return []
    frame_ids = list(set([get_validated_frame_id(f, logger=logger) for f in frame_ids]))
    if len(frame_ids) == _NUM_FRAMES:
        return []
    else:
        return frame_ids
