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
    """
    Rebin 1D or 2D arrays along the first axis (0) by averaging all samples that fall within a bin.

    Args:
        v (ArrayLike): 1D or 2D array to be rebinned.
        rebin_index (ArrayLike | None, optional): Array of non-decreasing indecies mapping values in `v` to target bins. Defaults to None.
        axis0_coords (ArrayLike | None, optional): Array of reference monotonic values used to derive `rebin_index` if it is not given (for this, additional input of `bin_edges` or `bin_centers` is also required). Defaults to None.
        bin_edges (ArrayLike | None, optional): Array of N+1 bin edges. Ignored if `rebin_index` is given, otherwise `axis0_coords` is also required. Defaults to None.
        bin_centers (ArrayLike | None, optional): Array of N bin centers. Ignored if `rebin_index` is given, otherwise `axis0_coords` is also required. Defaults to None.
        ignore_nans (bool, optional): If True, NaNs are ignored during averaging. If False, bins containing NaN return NaN. Defaults to True.

    Returns:
        NDArray: Along axis 0 rebinned version of original array `v`.
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
