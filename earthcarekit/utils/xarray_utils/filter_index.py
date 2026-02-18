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
    index: int | slice | NDArray | Sequence,
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

    Examples:
        ```python
        >>> fp = "ECA_EXBC_CPR_FMR_2A_20260108T030403Z_20260108T042349Z_09167F.h5"
        >>> with eck.read_product(fp) as ds:
        >>>     ds_filtered = eck.filter_index(ds, 123)
        >>>     print(ds_filtered.sizes)
        Frozen({'along_track': 1, 'vertical': 218})
        >>>         ds_filtered = eck.filter_index(ds, slice(0, 1000))
        >>>         print(ds_filtered.sizes)
        Frozen({'along_track': 1000, 'vertical': 218})
        >>>         ds_filtered = eck.filter_index(ds, (0, 1000))
        >>>         print(ds_filtered.sizes)
        Frozen({'along_track': 2, 'vertical': 218})
        ```
    """
    if isinstance(index, np.ndarray) and len(index.shape) == 0:
        index = int(index)
    elif isinstance(index, (Sequence, np.ndarray)):
        if len(index) == 0:
            raise ValueError(f"index must be integer or non-empty array")
        elif len(index) == 1:
            index = int(index[0])

    if isinstance(index, int):
        index = slice(index, index + 1)

    if isinstance(index, slice):
        index = slice(index.start - pad_idxs, index.stop + pad_idxs, index.step)
    else:
        index = flatten_array(index)

    ds_new = ds.copy().isel({along_track_dim: index})
    new_trim_index_offset: int | NDArray = 0

    if isinstance(index, slice):
        if isinstance(index.step, int) and index.step > 1:
            new_trim_index_offset = np.array(
                list(range(index.start, index.stop, index.step))
            )
        else:
            new_trim_index_offset = int(index.start)

    if isinstance(index, np.ndarray):
        if np.max(np.diff(index)) > 1:
            new_trim_index_offset = index
        else:
            new_trim_index_offset = int(index[0])

    if trim_index_offset_var in ds_new:
        old_trim_index_offset = ds_new[trim_index_offset_var].values
        trim_index_offset = np.asarray(old_trim_index_offset + new_trim_index_offset)

        if len(trim_index_offset.shape) == 0:
            ds_new[trim_index_offset_var] = trim_index_offset
        else:
            ds_new[trim_index_offset_var] = ("new_dim", trim_index_offset)
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
