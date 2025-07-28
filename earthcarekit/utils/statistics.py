import warnings

import numpy as np
from numpy.typing import ArrayLike


def nan_mean(a: ArrayLike, axis: int = 0) -> ArrayLike:
    """Compute the mean while ignoring NaNs."""
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        a = np.asarray(a)
        return np.nanmean(a, axis=axis)


def nan_std(a: ArrayLike, axis: int = 0) -> ArrayLike:
    """Compute the standard deviation while ignoring NaNs."""
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        a = np.asarray(a)
        return np.nanstd(a, axis=axis)


def nan_min(a: ArrayLike, axis: int = 0) -> ArrayLike:
    """Compute the minimum while ignoring NaNs."""
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        a = np.asarray(a)
        if len(a) > 0:
            return np.nanmin(a, axis=axis)
        else:
            return np.nan


def nan_max(a: ArrayLike, axis: int = 0) -> ArrayLike:
    """Compute the maximum while ignoring NaNs."""
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        a = np.asarray(a)
        if len(a) > 0:
            return np.nanmax(a, axis=axis)
        else:
            return np.nan


def nan_sem(a: ArrayLike, axis: int = 0) -> ArrayLike:
    """Compute the standard error of the mean while ignoring NaNs."""
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        a = np.asarray(a)
        return np.nanstd(a, axis=axis) / np.sqrt(np.size(a, axis=0))
