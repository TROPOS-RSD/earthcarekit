import re
from collections.abc import Iterable, Sequence
from itertools import islice
from typing import Any, TypeGuard, TypeVar

import numpy as np

from ._types import (
    DistanceRangeLike,
    Number,
    NumberPairLike,
    NumberPairNoneLike,
    ValueRangeLike,
)

T = TypeVar("T")


def validate_numeric_pair(
    input: NumberPairLike | NumberPairNoneLike,
    fallback: tuple[Number, Number] | None = None,
) -> tuple[float, float]:
    """Validates that the input is a pair with exactly 2 numeric elements.

    Args:
        input (NumericPairLike | NumericPairNoneLike): A sequence of 2 numbers.
        fallback (tuple[Number, Number], optional): Used to replace None values in `input`.

    Returns:
        A tuple of two floats.

    Raises:
        `TypeError` or `ValueError` if validation fails.
    """
    if isinstance(input, np.ndarray):
        if input.ndim != 1 or input.shape[0] != 2:
            raise ValueError(f"Expected 1D array of length 2, got shape {input.shape}")
        pair = input.tolist()
    else:
        pair = list(input)

    if len(pair) != 2:
        raise ValueError(f"Expected exactly 2 elements, got {len(pair)}")

    if fallback and not isinstance(pair[0], Number):
        pair[0] = fallback[0]

    if fallback and not isinstance(pair[1], Number):
        pair[1] = fallback[1]

    if not all(isinstance(x, Number) for x in pair):
        raise TypeError("Both elements must be numeric ('int' or 'float')")

    _pair: tuple[float, float] = (
        float(pair[0]),
        float(pair[1]),
    )

    return _pair


def validate_numeric_range(
    input: ValueRangeLike,
    fallback: tuple[Number, Number] | None = None,
) -> tuple[float, float]:
    """Validates that the input is a pair with exactly 2 numeric elements that monotonically increasing.

    Args:
        input (ValueRangeLike): A sequence of 2 numbers.
        fallback (tuple[Number, Number], optional): Used to replace None values in `input`.

    Returns:
        A tuple of monotonically increasing two floats.

    Raises:
        `TypeError` or `ValueError` if validation fails.
    """
    _pair: tuple[float, float] = validate_numeric_pair(input, fallback)

    if _pair[0] > _pair[1]:
        raise ValueError(f"The first element must be smaller than the second: {_pair}")

    return _pair


def validate_value_range(
    input: ValueRangeLike | None,
) -> tuple[float | Any | None, float | Any | None]:
    if input is None:
        return (None, None)

    if not isinstance(input, (Sequence, np.ndarray)):
        raise TypeError(f"invalid type '{type(input).__name__}' for value range")

    try:
        vmin = input[0]
        vmax = input[1]
    except KeyError:
        raise KeyError(f"expected 2 elements in value range but got {len(input)}")

    if vmin is not None:
        return (None, vmax)
    if vmax is None:
        return (vmin, None)
    return (vmin, vmax)


def is_non_str_sequence_of_length(
    x: Any,
    length: int | None = None,
    min_length: int | None = None,
    max_length: int | None = None,
) -> TypeGuard[Sequence]:
    """
    Checks if an object is a non-`str` iterable.

    Args:
        x (Any): Object to validate.

    Returns:
        TypeGuard[Iterable]: True if `x` is a non-`str` iterable, False otherwise.

    Examples:
        >>> is_non_str_sequence_of_length(["a", "b"])
        True
        >>> is_non_str_sequence_of_length(["a", "b"], length=2)
        True
        >>> is_non_str_sequence_of_length(["a", "b"], min_length=3)
        False
        >>> is_non_str_sequence_of_length("ab", str)
        False
        >>> is_non_str_sequence_of_length([1, 2])
        True
        >>> is_non_str_sequence_of_length([1, "b"])
        True
    """
    if isinstance(x, str) or not isinstance(x, (Sequence, np.ndarray)):
        return False

    if (
        (length is not None and len(x) != length)
        or (min_length is not None and len(x) < min_length)
        or (max_length is not None and len(x) > max_length)
    ):
        return False

    return True


def is_iterable_of_type(
    x: Any,
    t: type[T],
    max_checks: int | None = None,
) -> TypeGuard[Iterable[T]]:
    """
    Checks if an object is a non-`str` iterable of a given type `T`.

    Args:
        x (Any): Object to validate.
        t (type): Expected type `T` for all elements in the iterable.
        max_checks (int | None, optional): Maximum number of elements to inspect. If None, all elements are checked. Defaults to None.

    Returns:
        TypeGuard[Iterable[T]]: True if `x` is a non-`str` iterable whose checked elements are of the expected type `T`, False otherwise.

    Examples:
        >>> is_iterable_of_type(["a", "b"], str)
        True
        >>> is_iterable_of_type("ab", str)
        False
        >>> is_iterable_of_type([1, 2], int)
        True
        >>> is_iterable_of_type([1, "b"], int)
        False
        >>> is_iterable_of_type([1, "b"], int, max_checks=1)
        True
    """
    if isinstance(x, str):
        return False
    try:
        iterator = x if max_checks is None else islice(x, max_checks)
        return all(isinstance(i, t) for i in iterator)
    except TypeError:
        return False


def is_iterable_of_str(
    x: Any,
    max_checks: int | None = None,
) -> TypeGuard[Iterable[str]]:
    """
    Checks if an object is a non-`str` iterable of strings.

    Args:
        x (Any): Object to validate.
        max_checks (int | None, optional): Maximum number of elements to inspect. If None, all elements are checked. Defaults to None.

    Returns:
        TypeGuard[Iterable[str]]: True if `x` is a non-`str` iterable whose checked elements are of the expected type `str`, False otherwise.

    Examples:
        >>> is_iterable_of_str(["a", "b"])
        True
        >>> is_iterable_of_str("ab")
        False
        >>> is_iterable_of_str(["a", 2])
        False
        >>> is_iterable_of_str(["a", 2], max_checks=1)
        True
    """
    return is_iterable_of_type(x, str, max_checks)


def validate_completeness_of_args(
    function_name: str,
    required_names: Sequence[str],
    positional_values: Sequence[Any] | None = None,
    **kwargs,
) -> list[str]:
    """
    Validates that required positional and optional argument groups are complete.

    For example, if `required_names = ['x', 'y']`, this function will:
    - Check if `x` and `y` are both provided in positional arguments (if used).
    - Check if optional arguments like `x1`, `x2`, ..., `y1`, `y2`, ... are all matched
      across the required names (e.g., if `x2` is given, `y2` must also be present).

    Parameters:
        function_name (str): Name of the function (used in error messages).
        required_names (Sequence[str]): Base names of required argument groups (e.g. ['x', 'y']).
        positional_values (Sequence[Any], optional): Positional argument values to validate.
        **kwargs: Optional keyword arguments to validate for matching suffixes.

    Returns:
        List[str]: List of suffixes (as strings) used in optional arguments for the first group.

    Raises:
        TypeError: If any required arguments are missing.
    """
    # Check required positional arguments
    if positional_values is not None:
        missing = [required_names[i] for i, v in enumerate(positional_values) if v is None]
        if missing:
            msg = f"{function_name}() missing {len(missing)} required positional argument{'s' if len(missing) > 1 else ''}: "
            msg += ", ".join(f"'{name}'" for name in missing)
            raise TypeError(msg)

    # Check completeness of optional argument groups (e.g., x1/y1, x2/y2, ...)
    suffixes_by_name: list[list[str]] = [[] for _ in required_names]
    for key in kwargs:
        for i, name in enumerate(required_names):
            match = re.fullmatch(f"{name}(\\d*)", key)
            if match:
                suffix = match.group(1)
                suffixes_by_name[i].append(suffix)

    # Find mismatched suffixes between argument groups
    missing = []
    for i in range(len(suffixes_by_name) - 1):
        for j in range(i + 1, len(suffixes_by_name)):
            suffixes_i = np.array(suffixes_by_name[i])
            suffixes_j = np.array(suffixes_by_name[j])
            missing_from_j = np.setdiff1d(suffixes_i, suffixes_j)
            missing_from_i = np.setdiff1d(suffixes_j, suffixes_i)
            missing += [f"'{required_names[j]}{s}'" for s in missing_from_j]
            missing += [f"'{required_names[i]}{s}'" for s in missing_from_i]

    # Raise error if mismatches were found
    if missing:
        unique_missing = sorted(set(missing))
        msg = f"{function_name}() missing {len(unique_missing)} required argument{'s' if len(unique_missing) > 1 else ''}: "
        msg += ", ".join(unique_missing)
        raise TypeError(msg)

    return suffixes_by_name[0]


def validate_height_range(height_range: DistanceRangeLike) -> tuple[float, float]:
    """Returns validated height range and raises `ValueError` if invalid."""
    if isinstance(height_range, Iterable):
        if len(height_range) == 2:
            if all([isinstance(x, (int, float, np.floating, np.integer)) for x in height_range]):
                return float(height_range[0]), float(height_range[1])
    raise ValueError(f"invalid height range: {height_range}")
