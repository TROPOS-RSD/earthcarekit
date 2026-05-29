import numpy as np
from numpy.typing import ArrayLike, NDArray


def normalize(
    values: ArrayLike,
    vmin: float = 0,
    vmax: float = 1,
) -> NDArray:
    """
    Normalizes a list or array of numbers to a specified range [vmin, vmax], preserving NaNs.

    The input is linearly scaled such that the minimum non-NaN value maps to `vmin`
    and the maximum to `vmax`. NaN values are preserved in their original positions.

    Args:
        values (ArrayLike): A sequence of numeric values, possibly containing NaNs.
        vmin (float): The minimum value of the normalized output range. Defaults to 0.
        vmax (float): The maximum value of the normalized output range. Defaults to 1.

    Returns:
        A `numpy.ndarray` of the same shape as `values`, with values scaled to [vmin, vmax]
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
