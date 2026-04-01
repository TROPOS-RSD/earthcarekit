from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray


def lookup_value_by_number(n: float, numbers: ArrayLike, values: ArrayLike) -> Any:
    """
    Returns the value corresponding to the number closest to a given number, using interpolation.

    Args:
        n (float): A single number to look up.
        numbers (NDArray): A series of of monotonically increasing numbers.
        values (NDArray[Any]): A series of values corresponding to each number in `numbers`.

    Returns:
        v (Any): The value from `values` that corresponds to the closest number in `numbers` to `n`.

    Raises:
        ValueError: If `numbers` and `values` have different lengths.
    """
    if n is None:
        raise ValueError(f"{lookup_value_by_number.__name__}() missing `n`")
    if numbers is None:
        raise ValueError(f"{lookup_value_by_number.__name__}() missing `numbers`")
    if values is None:
        raise ValueError(f"{lookup_value_by_number.__name__}() missing `values`")

    n = float(n)
    numbers = np.asarray(numbers)
    values = np.asarray(values)

    if numbers.shape[0] == 0:
        raise ValueError(
            f"{lookup_value_by_number.__name__}() `numbers` is empty but needs at least on element"
        )
    if values.shape[0] != numbers.shape[0]:
        raise ValueError(
            f"{lookup_value_by_number.__name__}() First shapes must be the same for `values` ({values.shape[0]}) and `numbers` ({numbers.shape[0]})"
        )

    idx0 = int(np.searchsorted(numbers, n).astype(int) - 1)
    idx1 = int(np.searchsorted(numbers, n).astype(int))

    idx0 = int(np.min([len(numbers) - 1, np.max([0, idx0])]))
    idx1 = int(np.min([len(numbers) - 1, np.max([0, idx1])]))

    if numbers[idx0] > n:
        idx0 = idx1

    total_diff = numbers[idx1] - numbers[idx0]

    diff = n - numbers[idx0]

    if total_diff == 0:
        frac = 0
    else:
        frac = diff / total_diff

    total_amount = values[idx1] - values[idx0]
    v = values[idx0] + total_amount * frac

    return v


def get_number_range(
    start: float, end: float, freq: float | None = None, periods: int | None = None
) -> NDArray[np.floating | np.integer]:
    """
    Generates a sequence of numbers based on frequency or number of periods.

    Args:
        freq (float, optional): A number defining the frequency of sampled values in the sequence.
        periods (int, optional): A number of defining the number of evenly spaced values to sample.

    Returns:
        number_range (np.ndarray[np.floating | np.integer]): A sequence of numbers,
            either sampled by frequency or evenly spaced n times.
    """
    if freq is None and periods is None:
        raise TypeError(
            f"{get_number_range.__name__}() missing 1 required argument: 'freq' or 'periods'"
        )
    elif isinstance(freq, float) and isinstance(periods, int):
        raise TypeError(
            f"{get_number_range.__name__}() expected 1 out of the 2 required arguments 'freq' and 'periods' but got both"
        )
    elif isinstance(freq, float):
        mod = start % freq
        s = start - mod
        if mod != 0.0:
            s += freq
        mod = end % freq
        e = end - mod
        result = np.arange(s, e + freq, freq)
        return np.array(result)
    elif isinstance(periods, int):
        result = np.linspace(start, end, periods)
        return np.array(result)
    else:
        raise RuntimeError(f"{get_number_range.__name__}() implementation error")
