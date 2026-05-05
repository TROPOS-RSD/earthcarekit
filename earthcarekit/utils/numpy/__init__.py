"""
**earthcarekit.utils.numpy**

Utilities based on `numpy`.

## Notes

This module does not depend on other internal modules.

---
"""

from ._bin import bins_to_centers, centers_to_bins
from ._check import all_in, all_same, isascending, ismonotonic, isndarray
from ._circular import circular_nanmean, wrap_to_interval
from ._clamp import clamp
from ._coarsen_mean import coarsen_mean, get_most_freq_int
from ._flatten import flatten_array
from ._misc import get_number_range, lookup_value_by_number
from ._normalize import normalize
from ._rebin import rebin_lerp, rebin_mean, rebin_median
from ._rolling_mean import rolling_mean_1d, rolling_mean_2d
from ._true_sequence import pad_true_sequence, pad_true_sequence_2d, shift_true_sequence

__all__ = [
    "bins_to_centers",
    "centers_to_bins",
    "all_same",
    "all_in",
    "isascending",
    "ismonotonic",
    "isndarray",
    "circular_nanmean",
    "wrap_to_interval",
    "clamp",
    "coarsen_mean",
    "get_most_freq_int",
    "flatten_array",
    "get_number_range",
    "lookup_value_by_number",
    "normalize",
    "rebin_lerp",
    "rebin_mean",
    "rebin_median",
    "pad_true_sequence",
    "pad_true_sequence_2d",
    "shift_true_sequence",
    "rolling_mean_1d",
    "rolling_mean_2d",
]
