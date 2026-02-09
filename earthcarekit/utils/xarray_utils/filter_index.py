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
from .insert_var import insert_var


def filter_index(
    ds: Dataset,
    index: int | slice | NDArray,
    along_track_dim: str = ALONG_TRACK_DIM,
    trim_index_offset_var: str = "trim_index_offset",
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

    ds_new = ds.isel({along_track_dim: index})

    new_trim_index_offset: int = 0

    if isinstance(index, np.ndarray):
        new_trim_index_offset = index
    else:
        new_trim_index_offset = int(index[0])
    if trim_index_offset_var in ds_new:
        old_trim_index_offset = int(ds_new[trim_index_offset_var].values)
        trim_index_offset = old_trim_index_offset + new_trim_index_offset
        ds_new[trim_index_offset_var].values = np.asarray(trim_index_offset)
    else:
        ds_new = insert_var(
            ds=ds_new,
            var=trim_index_offset_var,
            data=new_trim_index_offset,
            index=0,
            after_var="processing_start_time",
        )
        ds_new[trim_index_offset_var] = ds_new[trim_index_offset_var].assign_attrs(
            {
                "earthcarekit": "Added by earthcarekit: Used to calculate the index in the original, untrimmed dataset, i.e. by addition."
            }
        )

    return ds_new
