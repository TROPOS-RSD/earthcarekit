import numpy as np
from numpy.typing import ArrayLike, NDArray


def downsample(
    a: ArrayLike,
    n: int,
    axis: int = 0,
) -> NDArray:
    """Downsample an array by selecting evenly spaced samples along one axis.

    Args:
        a: Input array or array-like object to downsample.
        n: Number of samples to select.
        axis: The axis along which the array `a` will be downsampled.

    Returns:
        The downsampled array.
    """
    if n < 1:
        raise ValueError("'n' must be at least 1")

    a = np.asarray(a)
    n_original = a.shape[axis]

    if n_original == 0:
        raise ValueError(f"Can't downsample empty axis ({axis}): {a.shape=})")

    indices = np.rint(np.linspace(0, n_original - 1, n)).astype(np.intp)

    shape = [1] * a.ndim
    shape[axis] = indices.size
    indices = np.reshape(indices, shape)

    return np.take_along_axis(a, indices=indices, axis=axis)
