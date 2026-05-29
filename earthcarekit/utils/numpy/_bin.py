import numpy as np
from numpy.typing import ArrayLike, NDArray


def bins_to_centers(bins: ArrayLike) -> NDArray:
    """
    Converts bin edges to bin centers.

    Args:
        bins (ArrayLike): Array of N+1 bin edges.

    Returns:
        NDArray: Array of N bin centers.
    """
    bins = np.asarray(bins)
    return bins[0:-1] + np.diff(bins) * 0.5


def centers_to_bins(centers: ArrayLike) -> NDArray:
    """
    Estimates bin edges from bin centers, assuming edges lie halfway between centers.

    Args:
        centers (ArrayLike): Array of N bin centers.

    Returns:
        NDArray: Array of N+1 bin edges.
    """
    centers = np.asarray(centers)

    d1 = np.diff(centers)
    d2 = np.append(d1[0], d1)
    d3 = np.append(d1, d1[-1])

    bins1 = centers - d2 / 2
    bins2 = centers + d3 / 2

    return np.append(bins1, bins2[-1])
