from typing import Iterable, Sequence

import numpy as np
import pandas as pd
import xarray as xr
from numpy.typing import NDArray
from xarray import Dataset

from ..constants import ALONG_TRACK_DIM, TIME_VAR, TRACK_LAT_VAR
from ..np_array_utils import flatten_array, pad_true_sequence
from ..time import TimeRangeLike, TimestampLike, to_timestamp
from ..typing import NumericPairLike, NumericPairNoneLike, validate_numeric_pair


def filter_index(
    ds: Dataset,
    index: int | slice | NDArray,
    along_track_dim: str = ALONG_TRACK_DIM,
    pad_idxs: int = 0,
) -> Dataset:
    """
    Filters a dataset given an along-track index number, list/array or range/slice.

    Args:
        ds (Dataset): Input dataset with along-track dimension.
        index (int | slice | NDArray): Index(es) to filter.
        along_track_dim (str, optional): Dimension along which to apply filtering. Defaults to ALONG_TRACK_DIM.
        pad_idxs (int, optional): Number of additional samples added at both sides of the selection.
            This input is ignored when `index` is an array-like. Defaults to 0.

    Returns:
        Dataset: Filtered dataset.
    """
    if isinstance(index, int):
        index = slice(index, index + 1)

    if isinstance(index, slice):
        index = slice(index.start - pad_idxs, index.stop + pad_idxs, index.step)
    else:
        index = flatten_array(index)

    return ds.isel({along_track_dim: index})
