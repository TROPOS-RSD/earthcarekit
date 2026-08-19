import numpy as np
from numpy.typing import ArrayLike, NDArray

from ._rebin import _rebin


def _rebin_nanmean_1d(v: NDArray, v_new: NDArray, rebin_index: NDArray) -> NDArray:
    mask = np.isfinite(v)
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.bincount(rebin_index[mask], weights=v[mask], minlength=len(v_new)) / np.bincount(
            rebin_index[mask], minlength=len(v_new)
        )


def _rebin_mean_keep_nans_1d(v: NDArray, v_new: NDArray, rebin_index: NDArray) -> NDArray:
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.bincount(rebin_index, weights=v, minlength=len(v_new)) / np.bincount(
            rebin_index, minlength=len(v_new)
        )


def _rebin_mean_1d(
    v: NDArray, v_new: NDArray, rebin_index: NDArray, ignore_nans: bool = True
) -> NDArray:
    if ignore_nans:
        return _rebin_nanmean_1d(v, v_new, rebin_index)
    else:
        return _rebin_mean_keep_nans_1d(v, v_new, rebin_index)


def _rebin_mean_2d(
    v: NDArray, v_new: NDArray, rebin_index: NDArray, ignore_nans: bool = True
) -> NDArray:
    func = _rebin_nanmean_1d if ignore_nans else _rebin_mean_keep_nans_1d

    for j in range(v.shape[1]):
        v_new[:, j] = func(v[:, j], v_new[:, j], rebin_index)
    return v_new


def rebin_mean(
    v: ArrayLike,
    rebin_index: ArrayLike | None = None,
    axis0_coords: ArrayLike | None = None,
    bin_edges: ArrayLike | None = None,
    bin_centers: ArrayLike | None = None,
    ignore_nans: bool = True,
) -> NDArray:
    """Rebins 1D or 2D arrays along axis 0 by averaging samples within bins.

    Args:
        v: 1D or 2D array to rebin.
        rebin_index: Bin indices mapping `v` to target bins; derived if None.
        axis0_coords: Reference values for deriving `rebin_index`; required if `rebin_index` is None.
        bin_edges: Bin edges (N+1); used to derive `rebin_index` if given.
        bin_centers: Bin centers (N); used to derive `rebin_index` if given.
        ignore_nans: Ignore NaNs during averaging if True; bins with NaN return NaN otherwise.

    Returns:
        Rebinned array along axis 0.
    """
    return _rebin(
        func1d=_rebin_mean_1d,
        func2d=_rebin_mean_2d,
        v=v,
        rebin_index=rebin_index,
        axis0_coords=axis0_coords,
        bin_edges=bin_edges,
        bin_centers=bin_centers,
        ignore_nans=ignore_nans,
    )
