from typing import Callable

import numpy as np
from numpy.typing import ArrayLike, NDArray

from .._bin import centers_to_bins


def _rebin(
    func1d: Callable[[NDArray, NDArray, NDArray, bool], NDArray],
    func2d: Callable[[NDArray, NDArray, NDArray, bool], NDArray],
    v: ArrayLike,
    rebin_index: ArrayLike | None = None,
    axis0_coords: ArrayLike | None = None,
    bin_edges: ArrayLike | None = None,
    bin_centers: ArrayLike | None = None,
    ignore_nans: bool = True,
) -> NDArray:
    v = np.asarray(v)

    if rebin_index is not None:
        rebin_index = np.asarray(rebin_index, dtype=int)
    elif axis0_coords is not None:
        axis0_coords = np.asarray(axis0_coords)

        if bin_edges is not None:
            bin_edges = np.asarray(bin_edges)
        elif bin_centers is not None:
            bin_edges = centers_to_bins(bin_centers)
        else:
            raise ValueError(
                "requires either 'rebin_index' of 'axis0_coords' combined with 'bin_edges' or 'bin_centers'"
            )

        rebin_index = np.digitize(axis0_coords, bin_edges) - 1
        rebin_index = np.clip(rebin_index, 0, len(bin_edges) - 2)
    else:
        raise ValueError(
            "requires either 'rebin_index' of 'axis0_coords' combined with 'bin_edges' or 'bin_centers'"
        )

    n = int(np.max(rebin_index)) + 1
    if v.ndim == 2:
        v_new = np.full((n, v.shape[1]), np.nan)
        return func2d(v, v_new, rebin_index, ignore_nans)
    elif v.ndim == 1:
        v_new = np.full((n,), np.nan)
        return func1d(v, v_new, rebin_index, ignore_nans)
    else:
        raise ValueError(f"{v.ndim}d array not supported: requires 1d or 2d")
