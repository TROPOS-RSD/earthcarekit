import numpy as np
from numpy.typing import ArrayLike


def all_in(subset: ArrayLike, set: ArrayLike) -> bool:
    """
    Check if all elements in `subset` are present in `set`.

    Args:
        subset (ArrayLike): The list to check.
        set (ArrayLike): The list to check against.

    Returns:
        bool: True if all elements of `subset` are in `set`, False otherwise.
    """
    return all(item in np.asarray(set) for item in np.asarray(subset))
