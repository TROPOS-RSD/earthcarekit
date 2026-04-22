from collections.abc import Iterable
from itertools import islice
from typing import Any, Protocol, Sequence, TypeAlias, TypeGuard, TypeVar

import numpy as np
import numpy.typing as npt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

Number: TypeAlias = float | int | np.number
NumericPairLike: TypeAlias = (
    tuple[Number, Number] | list[Number] | Sequence[Number] | npt.NDArray[np.number]
)
NumericPairNoneLike: TypeAlias = (
    tuple[Number | None, Number | None]
    | list[Number | None]
    | Sequence[Number | None]
    | npt.NDArray[np.number]
)

ValueRangeLike: TypeAlias = NumericPairLike | NumericPairNoneLike
DistanceRangeLike: TypeAlias = NumericPairLike
DistanceRangeNoneLike: TypeAlias = NumericPairLike | NumericPairNoneLike
LatLonCoordsLike: TypeAlias = NumericPairLike

T = TypeVar("T")


class HasFigure(Protocol):
    """Protocol for objects exposing a `.fig` attribute of type `matplotlib.figure.Figure`."""

    fig: Figure


class HasAxes(Protocol):
    """Protocol for objects exposing a `.ax` attribute of type `matplotlib.axes.Axes`."""

    ax: Axes


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


def validate_numeric_pair(
    input: NumericPairLike | NumericPairNoneLike,
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
