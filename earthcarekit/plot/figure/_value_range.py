from dataclasses import dataclass
from typing import Self, Sequence

import numpy as np
from matplotlib.colors import LogNorm, Normalize
from numpy.typing import NDArray

from ...typing import ValueRangeLike, validate_value_range
from ...utils import numpy as np_utils
from ...utils.sentinels import UNSET, Unset


def _nan_to_none(value: float) -> float | None:
    return None if np.isnan(value) else value


@dataclass
class ValueRange:
    _data_min: float = np.nan
    _data_max: float = np.nan
    _vmin: float | None = None
    _vmax: float | None = None
    _log_scale: bool = False
    _pad_frac: float = 0.0

    def __init__(
        self: Self,
        value_range: ValueRangeLike | None | Unset = UNSET,
        log_scale: bool | Unset = UNSET,
        pad_frac: float | Unset = UNSET,
    ):
        self.set_pad_frac(pad_frac)
        self.set_value_range(value_range)
        self.set_log_scale(log_scale)

    def set_pad_frac(self: Self, value: float | Unset):
        if not isinstance(value, Unset):
            self._pad_frac = value

    def set_value_range(self: Self, value: ValueRangeLike | None | Unset):
        if not isinstance(value, Unset):
            self._vmin, self._vmax = validate_value_range(value)

    def get_nan_value_range(self: Self, step: float | None = None) -> tuple[float, float]:
        vmin = self._vmin if self._vmin is not None else self._data_min
        vmax = self._vmax if self._vmax is not None else self._data_max

        if step is not None:
            vmin = np_utils.step_ceil(vmin, step)
            vmax = np_utils.step_floor(vmax, step)

        pad = (vmax - vmin) * self._pad_frac

        return (vmin - pad, vmax + pad)

    def get_value_range(self: Self, step: float | None = None) -> tuple[float | None, float | None]:
        vmin, vmax = self.get_nan_value_range(step)
        return (_nan_to_none(vmin), _nan_to_none(vmax))

    def get_log_scale(self: Self) -> bool:
        return self._log_scale

    def set_log_scale(self: Self, value: bool | Unset) -> None:
        if not isinstance(value, Unset):
            self._log_scale = value

    def update_data(
        self: Self,
        data: Sequence | NDArray,
        use_min_max: bool = False,
        percentile: float = 1.0,
    ) -> None:
        data = np.asarray(data)
        vmin = np.nanmin(data) if use_min_max else np.nanpercentile(data, percentile)
        vmax = np.nanmax(data) if use_min_max else np.nanpercentile(data, 100.0 - percentile)

        if np.isnan(self._data_min) or vmin < self._data_min:
            self._data_min = vmin

        if np.isnan(self._data_max) or vmax > self._data_max:
            self._data_max = vmax

    def get_norm(self: Self) -> Normalize:
        if self._log_scale is True:
            return LogNorm(*self.get_value_range())
        return Normalize(*self.get_value_range())


def select_value_range(
    data: Sequence | NDArray,
    value_range: Sequence | NDArray | None,
    pad_frac: float = 0.0,
    use_min_max: bool = False,
) -> tuple[float, float]:
    data = np.asarray(data)

    vmin = np.nan
    vmax = np.nan

    if isinstance(value_range, (Sequence, np.ndarray)) and len(value_range) > 1:
        if isinstance(value_range[0], (int, float, np.integer, np.floating)):
            vmin = float(value_range[0])
        if isinstance(value_range[-1], (int, float, np.integer, np.floating)):
            vmax = float(value_range[-1])

    if np.isnan(vmin):
        vmin = np.nanmin(data) if use_min_max else np.nanpercentile(data, 1)
    if np.isnan(vmax):
        vmax = np.nanmax(data) if use_min_max else np.nanpercentile(data, 99)

    pad = (vmax - vmin) * pad_frac

    new_value_range = (vmin - pad, vmax + pad)

    return new_value_range
