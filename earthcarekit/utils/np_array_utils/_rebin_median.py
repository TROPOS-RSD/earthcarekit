import warnings

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ._rebin import _rebin


def _get_chunk_nanmedian(chunk: NDArray):
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return np.nanmedian(chunk, axis=0)


def _get_chunk_median(chunk: NDArray):
    n = len(chunk)
    k = n // 2

    tmp = np.partition(chunk, k, axis=0)

    if n % 2:
        return tmp[k]
    else:
        tmp2 = np.partition(chunk, k - 1, axis=0)
        return (tmp[k] + tmp2[k - 1]) * 0.5


def _rebin_median(
    v: NDArray, v_new: NDArray, rebin_index: NDArray, ignore_nans: bool = True
) -> NDArray:
    func = _get_chunk_nanmedian if ignore_nans else _get_chunk_median

    if not np.all(rebin_index[:-1] <= rebin_index[1:]):
        order = np.argsort(rebin_index)
        bins_sorted = rebin_index[order]
        v_sorted = v[order]
    else:
        bins_sorted = rebin_index
        v_sorted = v

    edges = np.flatnonzero(np.diff(bins_sorted)) + 1
    starts = np.append(0, edges)
    ends = np.append(edges, len(bins_sorted))

    for start, end in zip(starts, ends):
        b = bins_sorted[start]
        chunk = v_sorted[start:end]
        v_new[b] = func(chunk)

    return v_new


def _rebin_median_1d(
    v: NDArray, v_new: NDArray, rebin_index: NDArray, ignore_nans: bool = True
) -> NDArray:
    return _rebin_median(v, v_new, rebin_index, ignore_nans)


def _rebin_median_2d(
    v: NDArray, v_new: NDArray, rebin_index: NDArray, ignore_nans: bool = True
) -> NDArray:
    return _rebin_median(v, v_new, rebin_index, ignore_nans)


def rebin_median(
    v: ArrayLike,
    rebin_index: ArrayLike | None = None,
    axis0_coords: ArrayLike | None = None,
    bin_edges: ArrayLike | None = None,
    bin_centers: ArrayLike | None = None,
    ignore_nans: bool = True,
) -> NDArray:
    """
    Rebin 1D or 2D arrays along the first axis (0) by finding the median out of samples falling within a bin.

    Args:
        v (ArrayLike): 1D or 2D array to be rebinned.
        rebin_index (ArrayLike | None, optional): Array of non-decreasing indecies mapping values in `v` to target bins. Defaults to None.
        axis0_coords (ArrayLike | None, optional): Array of reference monotonic values used to derive `rebin_index` if it is not given (for this, additional input of `bin_edges` or `bin_centers` is also required). Defaults to None.
        bin_edges (ArrayLike | None, optional): Array of N+1 bin edges. Ignored if `rebin_index` is given, otherwise `axis0_coords` is also required. Defaults to None.
        bin_centers (ArrayLike | None, optional): Array of N bin centers. Ignored if `rebin_index` is given, otherwise `axis0_coords` is also required. Defaults to None.
        ignore_nans (bool, optional): If True, NaNs are ignored during median search. If False, bins containing NaN return NaN. Defaults to True.

    Returns:
        NDArray: Along axis 0 rebinned version of original array `v`.
    """
    return _rebin(
        func1d=_rebin_median_1d,
        func2d=_rebin_median_2d,
        v=v,
        rebin_index=rebin_index,
        axis0_coords=axis0_coords,
        bin_edges=bin_edges,
        bin_centers=bin_centers,
        ignore_nans=ignore_nans,
    )
