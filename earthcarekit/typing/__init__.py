"""
**earthcarekit.typing**

Globally used types and validation functions.

## Notes

This module does not depend on other internal modules.

---
"""

from ._types import (
    ColorLike,
    DistanceRangeLike,
    DistanceRangeNoneLike,
    HasAxes,
    HasFigure,
    LatLonCoordsLike,
    Number,
    NumericPairLike,
    NumericPairNoneLike,
    TimedeltaLike,
    TimeRangeLike,
    TimestampLike,
    ValueRangeLike,
)
from ._validation import (
    is_iterable_of_str,
    is_iterable_of_type,
    validate_completeness_of_args,
    validate_height_range,
    validate_numeric_pair,
    validate_numeric_range,
)
