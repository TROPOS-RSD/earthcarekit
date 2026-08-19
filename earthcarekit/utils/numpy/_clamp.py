from typing import Sequence, TypeVar, overload

import numpy as np
from numpy.typing import NDArray

Scalar = TypeVar("Scalar", int, float, np.datetime64, np.timedelta64)


@overload
def clamp(a: Scalar, min: Scalar, max: Scalar) -> Scalar: ...


@overload
def clamp(a: Sequence[Scalar] | NDArray, min: Scalar, max: Scalar) -> NDArray[np.generic]: ...


def clamp(a, min, max):
    """Limits given values to a range between a minimum and maximum value.

    Args:
        a: Input array or array-like object to be clamped.
        min: Minimum limit.
        max: Maximum limit.

    Returns:
        A clampled scalar or array.

    Examples:
        >>> import numpy as np
        >>> import earthcarekit.utils.numpy as np_utils
        >>> x1 = np_utils.clamp(1.2, 0, 1)
        >>> print(x1)
        1.0

        >>> x2 = np_utils.clamp([1.0, 1.2, 0.8, -0.1], 0, 1)
        >>> print(x2)
        [1.  1.  0.8 0. ]

        >>> x3 = np_utils.clamp(
        ...     np.datetime64("2025-02-23"),
        ...     np.datetime64("2025-01-01"),
        ...     np.datetime64("2025-01-02"),
        ... )
        >>> print(x3)
        2025-01-02

        >>> x4 = np_utils.clamp(
        ...     np.timedelta64(70, "m"), np.timedelta64(0, "h"), np.timedelta64(1, "h")
        ... )
        >>> print(x4)
        60 minutes
    """
    a = np.asarray(a)
    if np.isnan(max):
        max = np.nanmax(a)
    if np.isnan(min):
        min = np.nanmin(a)
    return np.maximum(np.minimum(np.asarray(a), max), min)
