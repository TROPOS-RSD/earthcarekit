"""
**earthcarekit.utils.time**

Datetime utilities.

## Notes

This module depends on other internal modules:

- [earthcarekit.typing][]

---
"""

from ...typing import TimeRangeNoneLike
from ._day_night import get_day_night_mask
from ._time import (
    TimedeltaLike,
    TimeRangeLike,
    TimestampComparisonResult,
    TimestampLike,
    check_if_same_timestamp,
    format_time_range_text,
    get_time_range,
    lookup_value_by_timestamp,
    num_to_time,
    time_to_iso,
    time_to_num,
    time_to_str,
    times_to_iso,
    times_to_str,
    to_timedelta,
    to_timedeltas,
    to_timestamp,
    to_timestamps,
    validate_time_range,
)

__all__ = [
    "get_day_night_mask",
    "TimedeltaLike",
    "TimeRangeLike",
    "TimeRangeNoneLike",
    "TimestampComparisonResult",
    "TimestampLike",
    "check_if_same_timestamp",
    "format_time_range_text",
    "get_time_range",
    "lookup_value_by_timestamp",
    "num_to_time",
    "time_to_iso",
    "time_to_num",
    "time_to_str",
    "times_to_iso",
    "times_to_str",
    "to_timedelta",
    "to_timedeltas",
    "to_timestamp",
    "to_timestamps",
    "validate_time_range",
]


_DEPRECATED = {
    "time_to_string": time_to_str,
}


def __getattr__(name):
    import warnings

    if name in _DEPRECATED:
        warnings.warn(
            f"'{name}' is deprecated; use '{_DEPRECATED[name].__name__}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return _DEPRECATED[name]

    raise AttributeError(name)
