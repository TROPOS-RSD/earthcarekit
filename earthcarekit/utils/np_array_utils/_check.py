from typing import Any, Literal

import numpy as np
from numpy.typing import ArrayLike, DTypeLike, NDArray


def isascending(
    a: ArrayLike,
    raise_error: bool = False,
    result_constant: bool = True,
) -> bool:
    """
    Check whether a sequence is initially ascending.

    Args:
        lats (ArrayLike): Input sequence (e.g., `list`, `numpy.array`, etc.).
        raise_error (bool, optional): If True, raises ValueError if the sequence is too short (< 2). Defaults to False.
        result_constant (bool, optional): If True, a constant sequence counts as acending. Defaults to True.

    Returns:
        is_ascending (bool): True if the sequence is ascending, False otherwise.

    Raises:
        ValueError: If given `mode` is invalid.
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
    """
    Check whether a sequence is monotonic.

    Args:
        a (ArrayLike): Input sequence (e.g., `list`, `numpy.array`, etc.).
        strict (bool, optional): If True, checks for strictly increasing or decreasing sequences.
            If False, allows equal adjacent elements. Defaults to False.
        mode (Literal['any', 'increasing', 'decreasing'], optional): Direction of monotonicity to check. Defaults to 'any'.
            - 'any': Checks if the sequence is either increasing or decreasing,
                     depending on the initial difference of the first two elements.
            - 'increasing': Checks only for increasing order.
            - 'decreasing': Checks only for decreasing order.
        raise_error (bool): If True, raises ValueError if the sequence is not monotonic.

    Returns:
        is_monotonic (bool): True if the sequence is monotonic according to the specified parameters, False otherwise.

    Raises:
        ValueError: If given `mode` is invalid.
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


def isndarray(input: Any, dtype: DTypeLike | None = None, raise_error: bool = False):
    """
    Returns True if `input` has type `numpy.ndarray` and also checks if `dtype` is lower/equal
    in type hierarchy if given (i.e. returns True if `input.dtype` is subtype of `dtype`).
    """
    if dtype is None:
        is_ndarray = isinstance(input, np.ndarray)
    else:
        is_ndarray = isinstance(input, np.ndarray) and np.issubdtype(input.dtype, dtype)

    if raise_error and not is_ndarray:
        dtype_str = "Any" if dtype is None else str(dtype)
        raise TypeError(
            f"expected type ndarray[{dtype_str}] for `input` but got {type(input).__name__}[{type(input[0]).__name__}]"
        )

    return is_ndarray


def all_same(a: ArrayLike) -> bool:
    """
    Check if all elements in the input array are the same.

    Args:
        a (ArrayLike): Input array or array-like object to check.

    Returns:
        bool: True if all elements in the array are the same, False otherwise.
    """
    a = np.asarray(a)
    return bool(np.all(a == a[0]))
