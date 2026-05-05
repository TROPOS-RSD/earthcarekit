import numpy as np
from numpy.typing import ArrayLike, NDArray


def clamp(a: ArrayLike, min: float, max: float) -> NDArray:
    """
    Limits given values to a range between a minimum and maximum value.

    Args:
        a (ArrayLike): Input array or array-like object to be clamped.
        min (float): Minimum limit.
        max (float): Maximum limit.

    Returns:
        NDArray: Clampled array.
    """
    if np.isnan(max):
        max = np.nanmax(a)
    if np.isnan(min):
        min = np.nanmin(a)
    return np.maximum(np.minimum(np.asarray(a), max), min)
