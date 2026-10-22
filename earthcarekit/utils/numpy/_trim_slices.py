import numpy as np
from numpy.typing import ArrayLike


def _counter_to_slice(counter: int) -> slice:
    """Converts a net trim count to a slice object."""
    if counter > 0:
        return slice(counter, None)
    elif counter < 0:
        return slice(0, counter)
    return slice(None)


def trim_slices(
    a1: ArrayLike, a2: ArrayLike, axis: int, max_iter: int = 100
) -> tuple[slice, slice]:
    """Computes slices to align two arrays by iteratively trimming their edges.

    Args:
        a1: First array.
        a2: Second array.
        axis: Axis along which to align.
        max_iter: Maximum trimming iterations allowed.

    Returns:
        Tuple of slices to apply to `a1` and `a2` for alignment.

    Raises:
        ValueError: If arrays cannot be aligned within `max_iter` steps.
    """
    a1 = np.asarray(a1)
    a2 = np.asarray(a2)

    trim_start1, trim_end1 = 0, 0
    trim_start2, trim_end2 = 0, 0

    for _ in range(max_iter):
        len1 = a1.shape[axis] - trim_start1 - trim_end1
        len2 = a2.shape[axis] - trim_start2 - trim_end2

        if len1 == len2:
            break

        idx1_start = trim_start1
        idx1_end = a1.shape[axis] - 1 - trim_end1
        idx2_start = trim_start2
        idx2_end = a2.shape[axis] - 1 - trim_end2

        first_diff = np.median(
            np.take(a1, idx1_start, axis=axis) - np.take(a2, idx2_start, axis=axis)
        )
        last_diff = np.median(np.take(a1, idx1_end, axis=axis) - np.take(a2, idx2_end, axis=axis))

        if first_diff > last_diff:
            if len1 > len2:
                trim_start1 += 1
            else:
                trim_start2 += 1
        else:
            if len1 > len2:
                trim_end1 += 1
            else:
                trim_end2 += 1

    if a1.shape[axis] - trim_start1 - trim_end1 != a2.shape[axis] - trim_start2 - trim_end2:
        raise ValueError(f"Could not align dimensions within {max_iter} iterations.")

    return _counter_to_slice(trim_start1 - trim_end1), _counter_to_slice(trim_start2 - trim_end2)


def trim_slices_vertical(
    height1: ArrayLike, height2: ArrayLike, max_iter: int = 100
) -> tuple[slice, slice]:
    """Computes slices to align vertical dimensions (axis=1) of two arrays.

    Args:
        height1: First array.
        height2: Second array.
        max_iter: Maximum trimming iterations allowed.

    Returns:
        Tuple of slices to apply to `height1` and `height2`.

    Raises:
        ValueError: If vertical alignment fails within `max_iter` steps.
    """
    return trim_slices(height1, height2, axis=1, max_iter=max_iter)


def trim_slices_along_track(
    latitude1: ArrayLike, latitude2: ArrayLike, max_iter: int = 100
) -> tuple[slice, slice]:
    """Computes slices to align along-track dimensions of two arrays.

    Args:
        latitude1: First array.
        latitude2: Second array.
        max_iter: Maximum trimming iterations allowed.

    Returns:
        Tuple of slices to apply to `latitude1` and `latitude2`.

    Raises:
        ValueError: If along-track alignment fails within `max_iter` steps.
    """
    return trim_slices(latitude1, latitude2, axis=0, max_iter=max_iter)
