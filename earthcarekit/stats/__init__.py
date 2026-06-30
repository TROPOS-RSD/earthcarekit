"""
**earthcarekit.stats**

Statistics utilities.

## Notes

This module does not depend on other internal modules.

---
"""

from ._histogram import get_hist_mean, get_hist_median, get_hist_percentile
from ._omitna import (
    nan_diff_of_means,
    nan_mae,
    nan_max,
    nan_mean,
    nan_mean_diff,
    nan_min,
    nan_rmse,
    nan_sem,
    nan_std,
)

__all__ = [
    "get_hist_mean",
    "get_hist_median",
    "get_hist_percentile",
    "nan_diff_of_means",
    "nan_mae",
    "nan_max",
    "nan_mean",
    "nan_mean_diff",
    "nan_min",
    "nan_rmse",
    "nan_sem",
    "nan_std",
]
