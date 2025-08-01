from typing import Iterable, Sequence, TypeAlias

import numpy as np
import numpy.typing as npt

Number: TypeAlias = float | int
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
LatLonCoordsLike: TypeAlias = NumericPairLike


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
    _pair: tuple[Number, Number] = validate_numeric_pair(input, fallback)

    if _pair[0] > _pair[1]:
        raise TypeError("Both elements must be numeric ('int' or 'float')")

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

    _pair: tuple[Number, Number] = (
        float(pair[0]),
        float(pair[1]),
    )

    return _pair
