import numpy as np
from numpy.typing import ArrayLike, NDArray

from ._bin import bins_to_centers


def _get_lerp_params(
    axis0_coords: NDArray,
    bin_centers: NDArray,
) -> tuple[NDArray, NDArray]:
    idx = np.searchsorted(axis0_coords, bin_centers, side="left")
    idx = np.clip(idx, 1, len(axis0_coords) - 1)
    c0 = axis0_coords[idx - 1]
    c1 = axis0_coords[idx]
    dc = c1 - c0
    w = np.where(dc != 0.0, (bin_centers - c0) / dc, 0.5)

    return (idx, w)


def _rebin_lerp_1d(
    idx: NDArray,
    w: NDArray,
    v: NDArray,
) -> NDArray:
    v0 = v[idx - 1]
    v1 = v[idx]
    dv = v1 - v0
    return v0 + w * dv


def _rebin_lerp_2d(
    idx: NDArray,
    w: NDArray,
    v: NDArray,
) -> NDArray:
    v0 = v[idx - 1, :]
    v1 = v[idx, :]

    dv = v1 - v0
    return v0 + w[:, np.newaxis] * dv


def rebin_lerp(
    v: ArrayLike,
    axis0_coords: ArrayLike,
    rebin_index: ArrayLike | None = None,
    bin_edges: ArrayLike | None = None,
    bin_centers: ArrayLike | None = None,
) -> NDArray:
    """
    Rebin 1D or 2D arrays along the first axis (0) by linearly interpolating the two samples around a bin center.

    Args:
        v (ArrayLike): 1D or 2D array to be rebinned.
        axis0_coords (ArrayLike): Array of reference monotonic values.
        rebin_index (ArrayLike | None, optional): Array of non-decreasing indecies mapping values in `v` to target bins. Defaults to None.
        bin_edges (ArrayLike | None, optional): Array of N+1 bin edges. Defaults to None.
        bin_centers (ArrayLike | None, optional): Array of N bin centers. Defaults to None.
        ignore_nans (bool, optional): If True, NaNs are ignored during interpolation. If False, bins containing NaN return NaN. Defaults to True.

    Returns:
        NDArray: Along axis 0 rebinned version of original array `v`.
    """
    v = np.asarray(v)
    axis0_coords = np.asarray(axis0_coords)

    if bin_centers is not None:
        bin_centers = np.asarray(bin_centers)
    elif bin_edges is not None:
        bin_centers = bins_to_centers(bin_edges)
    elif rebin_index is not None:
        rebin_index = np.asarray(rebin_index)
        bin_centers = bins_to_centers(
            axis0_coords[np.append(np.unique(rebin_index, return_index=True)[1], len(rebin_index))]
        )
    else:
        raise ValueError("requires either 'bin_centers', 'bin_edges' or 'rebin_index'")

    idx, w = _get_lerp_params(axis0_coords, bin_centers)
    if v.ndim == 2:
        return _rebin_lerp_2d(idx, w, v)
    elif v.ndim == 1:
        return _rebin_lerp_1d(idx, w, v)
    else:
        raise ValueError(f"{v.ndim}d array not supported: requires 1d or 2d")
