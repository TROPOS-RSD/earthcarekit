import numpy as np
from numpy.typing import NDArray


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


def pad_true_sequence_2d(
    a: NDArray[np.bool_],
    n: int,
    axis: int = 1,
) -> NDArray[np.bool_]:
    """Pads all sequences of True values occuring along one axis in an 2d array with n True values before and after the sequence (while keeping the original size)."""

    if axis not in [0, 1]:
        raise ValueError(f"invalid axis ({axis}), expected 0 or 1")

    if axis == 0:
        a = a.T

    ncols = a.shape[1]
    idx = np.arange(ncols)

    any_true = np.asarray(a.any(axis=1))

    first_true = np.argmax(a, axis=1)
    first_true = np.where(any_true, first_true, ncols)

    last_true = ncols - 1 - np.argmax(a[:, ::-1], axis=1)
    last_true = np.where(any_true, last_true, -1)

    start = np.clip(first_true - n, 0, ncols)
    end = np.clip(last_true + n + 1, 0, ncols)

    mask = (idx >= start[:, np.newaxis]) & (idx < end[:, np.newaxis])
    mask &= any_true[:, np.newaxis]

    if axis == 0:
        mask = mask.T

    return mask


def shift_true_sequence(
    a: NDArray[np.bool_],
    n: int,
) -> NDArray[np.bool_]:
    """Offsets all sequences of True values occuring in an array (while keeping the original size)."""
    if n == 0:
        return a

    a = np.roll(a, n)
    if n > 0:
        a[:n] = False
    elif n < 0:
        a[n:] = False

    return a
