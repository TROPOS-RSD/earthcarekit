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
) -> NDArray:
    pad_width = [(0, 0), (0, 0)]
    pad_width[axis] = (1, 0)

    cum_sum = np.cumsum(np.nan_to_num(x, nan=0.0), axis=axis)
    cum_sum = np.pad(cum_sum, pad_width=pad_width, mode="constant")

    valid = np.isfinite(x).astype(int)
    valid_cum_sum = np.cumsum(valid, axis=axis)
    valid_cum_sum = np.pad(valid_cum_sum, pad_width=pad_width, mode="constant")

    if axis == 0:
        roll_sum = cum_sum[w:] - cum_sum[:-w]
        valid_sum = valid_cum_sum[w:] - valid_cum_sum[:-w]
    else:
        roll_sum = cum_sum[:, w:] - cum_sum[:, :-w]
        valid_sum = valid_cum_sum[:, w:] - valid_cum_sum[:, :-w]

    roll_sum[valid_sum == 0] = np.nan

    if is_pad:
        pad_width = [(0, 0), (0, 0)]
        half = w // 2
        pad_width[axis] = (half, w - half - 1)
        return np.pad(
            roll_sum / w,
            pad_width=pad_width,
            mode="constant",
            constant_values=np.nan,
        )
    return roll_sum / w
