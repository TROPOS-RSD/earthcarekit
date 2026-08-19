import numpy as np
from numpy.typing import ArrayLike, NDArray


def normalize(
    a: ArrayLike,
    vmin: float = 0,
    vmax: float = 1,
) -> NDArray:
    """Normalizes a sequence to [vmin, vmax], preserving NaNs.

    Args:
        a: Input sequence (may contain NaNs).
        vmin: Minimum of output range; defaults to 0.
        vmax: Maximum of output range; defaults to 1.

    Returns:
        Normalized array with NaNs preserved.

    Raises:
        ValueError: If `vmin >= vmax`.
    """
    if vmin >= vmax:
        raise ValueError(f"vmin ({vmin}) must be smaller than vmax ({vmax})")

    a_old = np.asarray(a, dtype=float)
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
