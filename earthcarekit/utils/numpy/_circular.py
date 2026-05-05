import numpy as np
from numpy.typing import ArrayLike, NDArray


def circular_nanmean(degrees: ArrayLike, axis: int | None = None) -> float:
    """Compute the circular mean of angles in degrees, ignoring NaNs."""
    radians = np.deg2rad(degrees)
    sin_sum = np.nanmean(np.sin(radians), axis=axis)
    cos_sum = np.nanmean(np.cos(radians), axis=axis)
    mean_angle = np.arctan2(sin_sum, cos_sum)
    return np.rad2deg(mean_angle)


def wrap_to_interval(a: ArrayLike, min: float, max: float) -> NDArray:
    """Wrap values in `a` to the interval [`min`, `max`)."""
    a = np.array(a)
    interval = max - min
    return (a - min) % interval + min
