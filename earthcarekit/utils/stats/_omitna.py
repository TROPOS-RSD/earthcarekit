import warnings

import numpy as np
from numpy.typing import ArrayLike, NDArray


def nan_mean(a: ArrayLike, axis: int | None = None) -> NDArray | float:
    """Compute the mean while ignoring NaNs."""
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        a = np.asarray(a)
        return np.nanmean(a, axis=axis)


def nan_std(a: ArrayLike, axis: int | None = None) -> NDArray | float:
    """Compute the standard deviation while ignoring NaNs."""
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        a = np.asarray(a)
        return np.nanstd(a, axis=axis)


def nan_min(a: ArrayLike, axis: int | None = None) -> NDArray | float:
    """Compute the minimum while ignoring NaNs."""
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        a = np.asarray(a)
        if len(a) > 0:
            return np.nanmin(a, axis=axis)
        else:
            return np.nan


def nan_max(a: ArrayLike, axis: int | None = None) -> NDArray | float:
    """Compute the maximum while ignoring NaNs."""
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        a = np.asarray(a)
        if len(a) > 0:
            return np.nanmax(a, axis=axis)
        else:
            return np.nan


def nan_sem(a: ArrayLike, axis: int | None = None) -> NDArray | float:
    """Compute the standard error of the mean while ignoring NaNs."""
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        a = np.asarray(a)
        return np.nanstd(a, axis=axis) / np.sqrt(np.size(a, axis=0))


def nan_rmse(predictions: ArrayLike, targets: ArrayLike) -> float:
    """Root mean squared error (RMSE)"""
    predictions = np.asarray(predictions)
    targets = np.asarray(targets)
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        result = np.sqrt(np.nanmean((targets - predictions) ** 2))
    return result


def nan_mae(predictions: ArrayLike, targets: ArrayLike) -> float:
    """Mean absolute error (MAE)"""
    predictions = np.asarray(predictions)
    targets = np.asarray(targets)
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        result = np.nanmean(np.abs(targets - predictions))
    return result


def nan_mean_diff(predictions: ArrayLike, targets: ArrayLike) -> float:
    """Mean of element-wise differences (i.e., `mean(target - prediction)`)."""
    predictions = np.asarray(predictions)
    targets = np.asarray(targets)
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        result = np.nanmean(targets - predictions)
    return result


def nan_diff_of_means(predictions: ArrayLike, targets: ArrayLike) -> float:
    """Difference between means of target and prediction (i.e., `mean(target) - mean(prediction)`)."""
    predictions = np.asarray(predictions)
    targets = np.asarray(targets)
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        result = np.nanmean(targets) - np.nanmean(predictions)
    return result
