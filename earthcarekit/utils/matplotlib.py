"""
**earthcarekit.utils.matplotlib**

Utilities based on `matplotlib`.

## Notes

- [earthcarekit.utils.numpy][]

---
"""

from typing import Protocol

import numpy as np
from matplotlib.colors import LogNorm, Normalize
from numpy.typing import ArrayLike, NDArray

from .numpy import step_round

__all__ = ["PercentileNorm", "PercentileLogNorm"]


class _SupportsPercentile(Protocol):
    vmin: float | None
    vmax: float | None
    pmin: float
    pmax: float
    round: bool
    step: float | None


def _compute_percentile(A: NDArray, p: float, round: bool, step: float | None) -> float:
    result = np.nanpercentile(A, p)
    if round:
        step = step if step is not None else 10 ** np.floor(np.log10(result))
        result = step_round(result, step)
    return result


def _autoscale_None(obj: _SupportsPercentile, A: ArrayLike) -> None:
    A = np.asarray(A)

    is_all_nan = np.all(np.isnan(A))

    if not is_all_nan and obj.vmin is None:
        obj.vmin = _compute_percentile(A, obj.pmin, obj.round, obj.step)

    if not is_all_nan and obj.vmax is None:
        obj.vmax = _compute_percentile(A, obj.pmax, obj.round, obj.step)

    if is_all_nan and obj.vmin is not None and obj.vmax is None:
        obj.vmax = obj.vmin


class PercentileNorm(Normalize):
    """Normalize data using percentile-based limits."""

    def __init__(
        self,
        vmin: float | None = None,
        vmax: float | None = None,
        clip: bool = False,
        pmin: float = 1,
        pmax: float = 99,
        round: bool = False,
        step: float | None = None,
    ):
        """Initialize the percentile-based normalization.

        Args:
            vmin: Minimum limit; overrides `pmin`.
            vmax: Maximum limit; overrides `pmax`.
            clip: Whether to clip values to the `[min, max]` range.
            pmin: Percentile used for `vmin`; defaults to 1.
            pmax: Percentile used for `vmax`; defaults to 99.
            round: Whether to round percentile-based limits to next `step`.
            step: Scaling step used for rounding limits; defaults to
        """
        self.pmin = pmin
        self.pmax = pmax
        self.round = round
        self.step = step

        super().__init__(vmin=vmin, vmax=vmax, clip=clip)

    def autoscale_None(self, A: ArrayLike):
        _autoscale_None(self, A)
        super().autoscale_None(A)


class PercentileLogNorm(LogNorm):
    """Normalize data to the 0-1 range using percentile-based limits on a log scale."""

    def __init__(
        self,
        vmin: float | None = None,
        vmax: float | None = None,
        clip: bool = False,
        pmin: float = 1,
        pmax: float = 99,
        round: bool = False,
        step: float | None = None,
    ):
        """Initialize the percentile-based 0-1 log scale normalization.

        Args:
            vmin: Minimum limit; overrides `pmin`.
            vmax: Maximum limit; overrides `pmax`.
            clip: Whether to clip values to the `[min, max]` range.
            pmin: Percentile used for `vmin`; defaults to 1.
            pmax: Percentile used for `vmax`; defaults to 99.
            round: Whether to round percentile-based limits to next `step`.
            step: Scaling step used for rounding limits; defaults to
        """
        self.pmin = pmin
        self.pmax = pmax
        self.round = round
        self.step = step

        super().__init__(vmin=vmin, vmax=vmax, clip=clip)

    def autoscale_None(self, A: ArrayLike):
        _autoscale_None(self, A)
        super().autoscale_None(A)
