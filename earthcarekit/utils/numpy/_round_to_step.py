from typing import overload

import numpy as np
from numpy.typing import ArrayLike, NDArray


def _prepare(value: ArrayLike, step: ArrayLike) -> tuple[NDArray[np.float64], NDArray[np.float64]]:
    value = np.asarray(value, dtype=np.float64)
    step = np.asarray(step, dtype=np.float64)
    scaled = value / step
    return (step, scaled)


@overload
def step_ceil(value: float, step: float) -> float: ...
@overload
def step_ceil(value: ArrayLike, step: float | ArrayLike) -> NDArray[np.float64]: ...
def step_ceil(value: float | ArrayLike, step: float | ArrayLike) -> float | NDArray[np.float64]:
    step, scaled = _prepare(value, step)
    result = np.ceil(scaled) * step
    if result.ndim == 0:
        return float(result[()])
    return result


@overload
def step_floor(value: float, step: float) -> float: ...
@overload
def step_floor(value: ArrayLike, step: float | ArrayLike) -> NDArray[np.float64]: ...
def step_floor(value: float | ArrayLike, step: float | ArrayLike) -> float | NDArray[np.float64]:
    step, scaled = _prepare(value, step)
    result = np.floor(scaled) * step
    if result.ndim == 0:
        return float(result[()])
    return result


@overload
def step_round(value: float, step: float) -> float: ...
@overload
def step_round(value: ArrayLike, step: float | ArrayLike) -> NDArray[np.float64]: ...
def step_round(value: float | ArrayLike, step: float | ArrayLike) -> float | NDArray[np.float64]:
    step, scaled = _prepare(value, step)
    result = np.round(scaled) * step
    if result.ndim == 0:
        return float(result[()])
    return result
