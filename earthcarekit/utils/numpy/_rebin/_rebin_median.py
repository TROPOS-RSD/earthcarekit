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
    """Rebins 1D or 2D arrays along axis 0 by computing the median within bins.

    Args:
        v: 1D or 2D array to rebin.
        rebin_index: Bin indices mapping `v` to target bins; derived if None.
        axis0_coords: Reference values for deriving `rebin_index`; required if `rebin_index` is None.
        bin_edges: Bin edges (N+1); used to derive `rebin_index` if given.
        bin_centers: Bin centers (N); used to derive `rebin_index` if given.
        ignore_nans: Ignore NaNs during median search if True; bins with NaN return NaN otherwise.

    Returns:
        Rebinned array along axis 0.
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
