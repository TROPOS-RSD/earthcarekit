from logging import Logger

import pandas as pd

from ._exceptions import InvalidInputError
from ._types import TimestampStr, _TimestampInputs


def format_datetime_string(
    datetime_string: str,
    logger: Logger | None = None,
) -> TimestampStr:
    """Formats time string and raises ValueError if unsuccessful."""
    try:
        timestamp = pd.Timestamp(datetime_string)
        if timestamp.tzinfo is None:
            timestamp = timestamp.tz_localize("UTC")
        return timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")
    except ValueError as e:
        msg = f"Given time string '{datetime_string}' is not valid. Here is the original error:"
        if logger:
            logger.exception(f"{msg}\n{e}")
        raise


def parse_time(
    timestamps: list[TimestampStr] | None,
    start_time: TimestampStr | None,
    end_time: TimestampStr | None,
    logger: Logger | None = None,
) -> _TimestampInputs:
    timestamps = (
        []
        if not timestamps
        else [format_datetime_string(t, logger=logger) for t in timestamps]
    )
    start_time = (
        None if not start_time else format_datetime_string(start_time, logger=logger)
    )
    end_time = None if not end_time else format_datetime_string(end_time, logger=logger)

    if isinstance(start_time, TimestampStr) and isinstance(end_time, TimestampStr):
        if start_time > end_time:
            raise InvalidInputError(
                f"Start ({start_time}) time must be greater than end time ({end_time})"
            )
        timestamps = [t for t in timestamps if t < start_time or t > end_time]
    elif isinstance(start_time, TimestampStr):
        timestamps = [t for t in timestamps if t < start_time]
    elif isinstance(end_time, TimestampStr):
        timestamps = [t for t in timestamps if t > end_time]

    return _TimestampInputs(
        timestamps=timestamps,
        time_range=(start_time, end_time),
    )
