import numpy as np
from numpy.typing import NDArray


def _nan_if_zero(x) -> float:
    return float(np.nan if x == 0 else x)


def get_median_from_histogram(
    counts: NDArray,
    bin_edges: NDArray,
) -> float:
    cum_counts = np.cumsum(counts)

    # Total count
    n = cum_counts[-1]

    median_bin_idx = np.searchsorted(cum_counts, n / 2)

    # Lower limit of median bin
    l_m = bin_edges[median_bin_idx]
    # Upper limit of median bin
    u_m = bin_edges[median_bin_idx + 1]
    # Summed counts of bins before median bin
    f_m1 = cum_counts[median_bin_idx - 1]
    # Count of meidan bin
    f_m = counts[median_bin_idx]
    # Median bin width
    w = u_m - l_m

    return float(l_m + (((n * 0.5) - f_m1) / _nan_if_zero(f_m)) * w)


def get_mean_from_histogram(
    counts: NDArray,
    bin_centers: NDArray,
) -> float:
    return float(np.average(bin_centers, weights=counts))
