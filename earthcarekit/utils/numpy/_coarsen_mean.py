import warnings

import numpy as np
from numpy.typing import ArrayLike, NDArray


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
            averaged = np.array([np.apply_along_axis(get_most_freq_int, 0, x) for x in reshaped])
    else:
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            averaged = np.nanmean(reshaped, axis=1)

    return np.moveaxis(averaged, 0, axis)
