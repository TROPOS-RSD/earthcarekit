from typing import Sequence, TypeVar, overload

import numpy as np
from numpy.typing import NDArray

Scalar1 = TypeVar("Scalar1", int, float, np.datetime64, np.timedelta64)
Scalar2 = TypeVar("Scalar2", int, float, np.datetime64, np.timedelta64)


@overload
def rescale(
    a: Scalar1,
    src_min: Scalar1,
    src_max: Scalar1,
    dst_min: Scalar2,
    dst_max: Scalar2,
) -> Scalar2: ...


@overload
def rescale(
    a: Sequence[Scalar1] | NDArray,
    src_min: Scalar1,
    src_max: Scalar1,
    dst_min: Scalar2,
    dst_max: Scalar2,
) -> NDArray[np.generic]: ...


def rescale(a, src_min, src_max, dst_min, dst_max):
    """Linearly map values from one range to another.

    Args:
        a (Scalar1 | ArrayLike): Scalar or array-like values to be rescaled.
        src_min (Scalar1): Lower bound of the source range.
        src_max (Scalar1): Upper bound of the source range.
        dst_min (Scalar2): Lower bound of the destination range.
        dst_max (Scalar2): Upper bound of the destination range.

    Returns:
        Scalar2 | NDArray:
            Rescaled scalar or array. The retrun type matches the type of the destination range.

    Examples:
        >>> import numpy as np
        >>> import earthcarekit.utils.numpy as np_utils
        >>> x1 = np_utils.rescale(3, 0, 10, 0, 200)
        >>> print(x1)
        60.0

        >>> x2 = np_utils.rescale([3], 0, 10, 0, 200)
        >>> print(x2)
        [60.]

        >>> x3 = np_utils.rescale(
        ...     [0, 0.5, 1],
        ...     0,
        ...     1,
        ...     np.datetime64("2025-01-01 00:00:00"),
        ...     np.datetime64("2025-01-02 00:00:00"),
        ... )
        >>> print(x3)
        ['2025-01-01T00:00:00' '2025-01-01T12:00:00' '2025-01-02T00:00:00']

        >>> x4 = np_utils.rescale(
        ...     np.timedelta64(15, "m"),
        ...     np.timedelta64(0, "h"),
        ...     np.timedelta64(1, "h"),
        ...     0,
        ...     1,
        ... )
        >>> print(x4)
        0.25
    """
    a = np.asarray(a)
    with np.errstate(invalid="ignore"):
        fraction = (a - src_min) / (src_max - src_min)
    return dst_min + fraction * (dst_max - dst_min)
