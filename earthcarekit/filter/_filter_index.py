from typing import Sequence, TypeAlias

import numpy as np
from numpy.typing import NDArray
from xarray import Dataset

from ..constants import ALONG_TRACK_DIM
from ..utils.numpy import flatten_array
from ._handle_trim_index_offset import update_trim_index_offset

_Start: TypeAlias = int
_Stop: TypeAlias = int


def filter_index(
    ds: Dataset,
    index: int | slice | tuple[_Start, _Stop] | NDArray | Sequence,
    along_track_dim: str = ALONG_TRACK_DIM,
    trim_index_offset_var: str = "trim_index_offset",
    pad_idxs: int = 0,
) -> Dataset:
    """
    Filters a dataset given an along-track index number, list/array or range/slice.

    Args:
        ds (Dataset): Input dataset with along-track dimension.
        index (int | slice | tuple[_Start, _Stop] | NDArray | Sequence): Index(es) to filter.
        along_track_dim (str, optional): Dimension along which to apply filtering. Defaults to ALONG_TRACK_DIM.
        pad_idxs (int, optional): Number of additional samples added at both sides of the selection.
            This input is ignored when `index` is an array-like. Defaults to 0.

    Returns:
        Dataset: Filtered dataset.

    Examples:
        >>> ds = eck.ecload("CPR_FMR_2A", "09167F", download=True)
        >>> ds_filtered = eck.filter_index(ds, 123)
        >>> print(ds_filtered.sizes)
        Frozen({'along_track': 1, 'vertical': 218})

        >>> ds_filtered = eck.filter_index(ds, slice(0, 1000))
        >>> print(ds_filtered.sizes)
        Frozen({'along_track': 1000, 'vertical': 218})

        A 2-element tuple is interpreted as ``(start, stop)`` and treated like a [``slice()``](https://docs.python.org/3/library/functions.html#slice):

        >>> ds_filtered = eck.filter_index(ds, (0, 1000))
        >>> print(ds_filtered.sizes)
        Frozen({'along_track': 1000, 'vertical': 218})

        Any other n-element tuple is treated as a sequence of indices to select:

        >>> ds_filtered = eck.filter_index(ds, (0, 1000, 2000))
        >>> print(ds_filtered.sizes)
        Frozen({'along_track': 3, 'vertical': 218})

        Finally, any other sequence is treated as a sequence of indices to select:

        >>> ds_filtered = eck.filter_index(ds, [0, 1000])
        >>> print(ds_filtered.sizes)
        Frozen({'along_track': 2, 'vertical': 218})
    """
    if isinstance(index, tuple) and len(index) == 2:
        index = slice(int(index[0]), int(index[1]))

    if isinstance(index, (Sequence, np.ndarray)):
        if len(index) == 0:
            raise ValueError("index must be integer or non-empty array")
        elif len(index) == 1:
            index = int(index[0])

    if isinstance(index, (int, np.integer)):
        index = slice(index, index + 1)

    if isinstance(index, slice):
        index = slice(index.start - pad_idxs, index.stop + pad_idxs, index.step)
    else:
        index = flatten_array(index)

    ds_new = ds.copy().isel({along_track_dim: index})
    new_trim_index_offset: int | NDArray = 0

    if isinstance(index, slice):
        if isinstance(index.step, int) and index.step > 1:
            new_trim_index_offset = np.array(list(range(index.start, index.stop, index.step)))
        else:
            new_trim_index_offset = int(index.start)

    if isinstance(index, np.ndarray):
        if np.max(np.diff(index)) > 1:
            new_trim_index_offset = index
        else:
            new_trim_index_offset = int(index[0])

    ds_new = update_trim_index_offset(
        ds=ds_new,
        offset=int(np.atleast_1d(new_trim_index_offset)[0]),
        var=trim_index_offset_var,
    )

    return ds_new
