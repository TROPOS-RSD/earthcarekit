import warnings
from numbers import Number
from typing import Any, Literal

import numpy as np
from numpy.typing import ArrayLike, DTypeLike, NDArray

from .debug import get_calling_function_name


def circular_nanmean(degrees: ArrayLike, axis: int | None = None) -> float:
    """
    Compute the circular mean of angles in degrees, ignoring NaNs.
    """
    radians = np.deg2rad(degrees)
    sin_sum = np.nanmean(np.sin(radians), axis=axis)
    cos_sum = np.nanmean(np.cos(radians), axis=axis)
    mean_angle = np.arctan2(sin_sum, cos_sum)
    return np.rad2deg(mean_angle)


def wrap_to_interval(a: ArrayLike, min: float, max: float) -> NDArray:
    """
    Wrap values in `a` to the interval [`min`, `max`).
    """
    a = np.array(a)
    interval = max - min
    return (a - min) % interval + min


def isascending(
    a: ArrayLike,
    raise_error: bool = False,
    result_constant: bool = True,
) -> bool:
    """
    Check whether a sequence is initially ascending.

    Parameters:
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
            raise ValueError(
                f"too few latitude values ({len(_a)}) but at least 2 are needed."
            )
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

    Parameters:
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
        correct_signs.append(signs[0])
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


def lookup_value_by_number(n: float, numbers: NDArray, values: NDArray) -> Any:
    """
    Returns the value corresponding to the number closest to a given number, using interpolation.

    Parameters:
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

    Parameters:
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


def normalize(
    values: list[Number] | np.ndarray,
    vmin: float = 0,
    vmax: float = 1,
) -> np.ndarray:
    """
    Normalizes a list or array of numbers to a specified range [vmin, vmax], preserving NaNs.

    The input is linearly scaled such that the minimum non-NaN value maps to `vmin`
    and the maximum to `vmax`. NaN values are preserved in their original positions.

    Args:
        values (list[Number] | np.ndarray): A sequence of numeric values, possibly containing NaNs.
        vmin (float): The minimum value of the normalized output range. Defaults to 0.
        vmax (float): The maximum value of the normalized output range. Defaults to 1.

    Returns:
        A `numpy.array` of the same shape as `values`, with values scaled to [vmin, vmax]
        and NaNs preserved.

    Raises:
        ValueError: If `vmin` is equal (i.e. zero output range) or greater than `vmax`.
    """
    if vmin >= vmax:
        raise ValueError(f"vmin ({vmin}) must be smaller than vmax ({vmax})")

    a_old = np.asarray(values, dtype=float)
    vmin_old = np.nanmin(a_old)
    vmax_old = np.nanmax(a_old)

    if np.isnan(vmin_old) or vmin_old == vmax_old:
        a_new = np.full_like(a_old, np.nan)
    else:
        a_new = (a_old - vmin_old) / (vmax_old - vmin_old)

    # Scale
    a_new = a_new * (vmax - vmin)

    # Shift
    a_new = a_new + vmin

    return a_new


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


def pad_true_sequence(
    a: NDArray[np.bool_],
    n: int,
) -> NDArray[np.bool_]:
    """Pads all sequences of True values occuring in an array with n True values before and after the sequence (while keeping the original size)."""
    idx = np.flatnonzero(a)
    if idx.size == 0:
        return a.copy()
    mask: NDArray[np.bool_] = np.full(a.shape, False, dtype=bool)
    start = max(0, idx[0] - n)
    end = min(len(a), idx[-1] + n + 1)
    mask[start:end] = True
    return mask


def get_most_freq_int(a: ArrayLike):
    a = np.asarray(a)
    min_val = a.min()
    if min_val < 0:
        shifted = a - min_val
        return np.bincount(shifted).argmax() + min_val
    else:
        return np.bincount(a).argmax()


def coarsen_mean(
    a: ArrayLike,
    n: int,
    axis: int = 0,
    is_bin: bool = False,
) -> NDArray:
    """
    Downsamples a array by averaging every n adjacient elements together, discarding residual elements at the end.

    Args:
        a (ArrayLike): Input array or array-like object to downsample.
        n (int): Number of elements to be averaged together.
        axis (int): The axis along which the array `a` will be downsampled.

    Returns:
        np.ndarray: The downsampled array.
    """
    a = np.asarray(a)
    a = np.moveaxis(a, axis, 0)

    # Discard residual data points
    trimmed_len = (a.shape[0] // n) * n
    trimmed = a[:trimmed_len]
    reshaped = trimmed.reshape(-1, n, *a.shape[1:])

    # Average
    is_datetime = np.issubdtype(a.dtype, np.datetime64)
    averaged: NDArray
    if is_datetime:
        averaged = reshaped.astype("datetime64[ns]").astype("int64").mean(axis=1)
        averaged = averaged.astype("datetime64[ns]")
    elif is_bin:
        if len(a.shape) == 1:
            averaged = np.apply_along_axis(get_most_freq_int, 0, reshaped)
        elif len(a.shape) == 2:
            averaged = np.array(
                [np.apply_along_axis(get_most_freq_int, 0, x) for x in reshaped]
            )
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            averaged = np.nanmean(reshaped, axis=1)

    return np.moveaxis(averaged, 0, axis)
