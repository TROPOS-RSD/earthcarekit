from typing import Any, Literal

import numpy as np
from numpy.typing import ArrayLike, DTypeLike, NDArray


def isascending(
    a: ArrayLike,
    raise_error: bool = False,
    result_constant: bool = True,
) -> bool:
    """Checks whether a sequence is initially ascending.

    Args:
        a: Input sequence (e.g., list, array).
        raise_error: Raise ValueError if sequence length < 2.
        result_constant: Treat constant sequences as ascending if True.

    Returns:
        True if the sequence is ascending, False otherwise.

    Raises:
        ValueError: If `raise_error=True` and sequence length < 2.
    """
    _a: NDArray = np.array(a)
    _a = _a[~np.isnan(_a)]

    if len(_a) < 2:
        if raise_error:
            raise ValueError(f"too few latitude values ({len(_a)}) but at least 2 are needed.")
        return False
    diff = np.diff(_a)
    for d in diff:
        if d > 0:
            return True
        elif d < 0:
            return False
    return result_constant


def ismonotonic(
    a: ArrayLike,
    strict: bool = False,
    mode: Literal["any", "increasing", "decreasing"] = "any",
    raise_error: bool = False,
    ignore_nans: bool = True,
):
    """Checks whether a sequence is monotonic.

    Args:
        a: Input sequence (e.g., list, array).
        strict: Require strictly increasing/decreasing if True.
        mode: Direction to check ("any", "increasing", "decreasing").
        raise_error: Raise ValueError if not monotonic.
        ignore_nans: Skip NaN values if True.

    Returns:
        True if monotonic according to parameters, False otherwise.

    Raises:
        ValueError: If `mode` is invalid or `raise_error=True` and sequence is not monotonic.
    """
    a = np.asarray(a)
    if ignore_nans:
        a = a[~np.isnan(a)]

    signs = np.sign(np.diff(a))

    correct_signs = []

    if not strict:
        correct_signs.append(0)

    if mode == "any":
        i: int = 0
        while i < len(signs) - 1 and signs[i] == 0:
            i = i + 1

        if signs[i] != 0:
            correct_signs.append(signs[i])
    elif mode == "increasing":
        correct_signs.append(1)
    elif mode == "decreasing":
        correct_signs.append(-1)
    else:
        raise ValueError(
            f"invalid `mode` ('{mode}') given, but expecting 'any', 'increasing' or 'decreasing'"
        )

    is_monotonic = all([s in correct_signs for s in signs])

    if raise_error and not is_monotonic:
        raise TypeError(
            f"sequence must be monotonic but it is not (strict={strict}, mode='{mode}')"
        )

    return is_monotonic


def isndarray(a: Any, dtype: DTypeLike | None = None, raise_error: bool = False):
    """
    Returns True if `a` has type `numpy.ndarray` and also checks if `dtype` is lower/equal
    in type hierarchy if given (i.e. returns True if `a.dtype` is subtype of `dtype`).
    """
    if dtype is None:
        is_ndarray = isinstance(a, np.ndarray)
    else:
        is_ndarray = isinstance(a, np.ndarray) and np.issubdtype(a.dtype, dtype)

    if raise_error and not is_ndarray:
        dtype_str = "Any" if dtype is None else str(dtype)
        raise TypeError(
            f"expected type ndarray[{dtype_str}] for `a` but got {type(a).__name__}[{type(a[0]).__name__}]"
        )

    return is_ndarray


def all_same(a: ArrayLike) -> bool:
    """Check if all elements in the input array are the same.

    Args:
        a: Input array or array-like object to check.

    Returns:
        True if all elements in the array are the same, False otherwise.
    """
    a = np.asarray(a)
    return bool(np.all(a == a[0]))


def all_in(subset: ArrayLike, set: ArrayLike) -> bool:
    """Check if all elements in `subset` are present in `set`.

    Args:
        subset: The list to check.
        set: The list to check against.

    Returns:
        True if all elements of `subset` are in `set`, False otherwise.
    """
    return all(item in np.asarray(set) for item in np.asarray(subset))
