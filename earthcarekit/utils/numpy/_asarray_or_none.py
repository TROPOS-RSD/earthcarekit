from typing import overload

import numpy as np
from numpy.typing import ArrayLike, NDArray


@overload
def asarray_or_none(a: None, **kwargs) -> None: ...
@overload
def asarray_or_none(a: ArrayLike, **kwargs) -> NDArray: ...
def asarray_or_none(a, **kwargs):
    """Convert input to `numpy.ndarray` unless it is None."""
    if a is None:
        return None
    return np.asarray(a, **kwargs)
