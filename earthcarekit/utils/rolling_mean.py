import warnings
from typing import Literal

import numpy as np
from numpy.typing import NDArray


def rolling_mean_1d(x: NDArray, w: int, is_pad: bool = True) -> NDArray:
    if w > len(x):
        return np.full(len(x), np.nan)

    windows = np.lib.stride_tricks.sliding_window_view(x, w)

    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        result = np.nanmean(windows, axis=-1)

    if is_pad:
        left_pad = np.full(w // 2, np.nan)
        right_pad = np.full((w - 1) // 2, np.nan)
        return np.concatenate([left_pad, result, right_pad])
    else:
        return result


def rolling_mean_2d(
    x: NDArray,
    w: int,
    axis: Literal[0, 1] = 1,
    is_pad: bool = True,
    is_keep_full_nan_along_axis: bool = False,
    full_nan_axis: int | None = None,
) -> NDArray:
    result = np.apply_along_axis(rolling_mean_1d, axis, x, w=w, is_pad=is_pad)

    if is_keep_full_nan_along_axis:
        if full_nan_axis is None:
            full_nan_axis = (axis + 1) % 2

        nan_mask = np.isnan(x)
        mask_full_nan_along_axis = np.all(nan_mask, axis=full_nan_axis)

        if full_nan_axis == 1:
            result[mask_full_nan_along_axis, :] = np.nan
        elif full_nan_axis == 0:
            result[:, mask_full_nan_along_axis] = np.nan

    return result
