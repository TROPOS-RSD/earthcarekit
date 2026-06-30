import numpy as np
from numpy.typing import ArrayLike


def _nan_if_zero(x) -> float:
    return float(np.nan if x == 0 else x)


def get_hist_percentile(
    values: ArrayLike,
    edges: ArrayLike,
    q: float,
) -> float:
    """Estimate `q`-th percentile from a histogram.

    Args:
        values (ArrayLike):
            Values of the histogram (e.g., counts or density).
        edges (ArrayLike):
            Sequence of monotonically increasing bin edges of the histogram (length(`values`)+1).
        q (float): Percentage of the percentile to compute (0-100).

    Returns:
        float: The scalar estimated `q`-th percentile.
    """
    edges = np.asarray(edges)
    values = np.asarray(values)

    cum_counts = np.cumsum(values)
    total = cum_counts[-1]
    target = (q * 0.01) * total

    idx = np.searchsorted(cum_counts, target)

    lower = edges[idx]
    upper = edges[idx + 1]
    width = upper - lower

    prev_cum_count = 0 if idx == 0 else cum_counts[idx - 1]
    curr_cum_count = values[idx]

    frac = (target - prev_cum_count) / _nan_if_zero(curr_cum_count)

    return float(lower + frac * width)


def get_hist_median(
    values: ArrayLike,
    edges: ArrayLike,
) -> float:
    """Estimate median from a histogram.

    Args:
        values (ArrayLike):
            Values of the histogram (e.g., counts or density).
        edges (ArrayLike):
            Sequence of monotonically increasing bin edges of the histogram (length(`values`)+1).

    Returns:
        float: The scalar estimated median (i.e., 50-th percentile).
    """
    return get_hist_percentile(values, edges, 50)


np.percentile
np.histogram


def get_hist_mean(
    values: ArrayLike,
    centers: ArrayLike,
) -> float:
    """Estimate mean from a histogram.

    Args:
        values (ArrayLike):
            Values of the histogram (e.g., counts or density).
        centers (ArrayLike):
            Sequence of monotonically increasing bin centers of the histogram (length(`values`)).

    Returns:
        float: The scalar estimated mean.
    """
    return float(np.average(np.asarray(centers), weights=np.asarray(values)))
