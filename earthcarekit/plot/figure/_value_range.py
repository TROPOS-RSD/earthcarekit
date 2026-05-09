from typing import Sequence

import numpy as np
from numpy.typing import NDArray


def select_value_range(
    data: Sequence | NDArray,
    value_range: Sequence | NDArray | None,
    pad_frac: float = 0.0,
    use_min_max: bool = False,
) -> tuple[float, float]:
    data = np.asarray(data)

    vmin = np.nan
    vmax = np.nan

    if isinstance(value_range, (Sequence, np.ndarray)):
        if len(value_range) > 1:
            _vmin = value_range[0]
            _vmax = value_range[-1]
        if isinstance(_vmin, (int, float)):
            vmin = float(_vmin)
        if isinstance(_vmax, (int, float)):
            vmax = float(_vmax)

    if np.isnan(vmin):
        if use_min_max:
            vmin = np.nanmin(data)
        else:
            vmin = np.nanpercentile(data, 1)
    if np.isnan(vmax):
        if use_min_max:
            vmax = np.nanmax(data)
        else:
            vmax = np.nanpercentile(data, 99)

    vrange = vmax - vmin

    new_value_range = (vmin - vrange * pad_frac, vmax + vrange * pad_frac)

    return new_value_range
