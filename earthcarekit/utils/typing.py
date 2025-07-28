from typing import Iterable, Sequence, TypeAlias

import numpy as np
import numpy.typing as npt

Number: TypeAlias = float | int
NumericPairLike: TypeAlias = (
    tuple[Number, Number] | list[Number] | Sequence[Number] | npt.NDArray[np.number]
)

ValueRangeLike: TypeAlias = (
    tuple[Number | None, Number | None]
    | list[Number | None]
    | Sequence[Number | None]
    | npt.NDArray[np.number]
)
DistanceRangeLike: TypeAlias = NumericPairLike
LatLonCoordsLike: TypeAlias = NumericPairLike


def validate_numeric_range(input: ValueRangeLike, fallback: list) -> ValueRangeLike:
    if isinstance(input, np.ndarray):
        if input.ndim != 1 or input.shape[0] != 2:
            raise ValueError(f"Expected 1D array of length 2, got shape {input.shape}")
        pair = input.tolist()
    else:
        pair = list(input)

    if len(pair) != 2:
        raise ValueError(f"Expected exactly 2 elements, got {len(pair)}")

    if not all(isinstance(x, Number) for x in pair):
        raise TypeError("Both elements must be numeric ('int' or 'float')")

    return pair


def validate_numeric_pair(input: NumericPairLike) -> tuple[float, float]:
    """
    Validates that the input is a pair with exactly 2 numeric elements.

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

    if not all(isinstance(x, Number) for x in pair):
        raise TypeError("Both elements must be numeric ('int' or 'float')")

    return float(pair[0]), float(pair[1])
