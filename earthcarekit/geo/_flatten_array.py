import numpy as np
from numpy.typing import ArrayLike, NDArray


def flatten_array(sequence: ArrayLike) -> NDArray:
    if isinstance(sequence, np.ndarray):
        return sequence.flatten()

    flattened_sequence = []

    def _ensure_list(x):
        if isinstance(x, list):
            return x.copy()
        return [x].copy()

    stack = _ensure_list(sequence)  # type: ignore

    while stack:
        item = stack.pop(0)
        if isinstance(item, (list, tuple, np.ndarray)):
            stack = list(item) + stack
        else:
            flattened_sequence.append(item)

    return np.array(flattened_sequence)
