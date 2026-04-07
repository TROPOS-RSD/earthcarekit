"""
**earthcarekit.utils.xarray_utils**

Utilities based on `xarray`.

---
"""

from ._concat import concat_datasets
from ._delete import remove_dims
from ._exception import EmptyFilterResultError
from ._filter_index import filter_index
from ._filter_latitude import filter_latitude
from ._filter_radius import filter_radius
from ._filter_time import filter_time, get_filter_time_mask
from ._insert_var import insert_var
from ._merge import merge_datasets
from ._scalars import convert_scalar_var_to_str

__all__ = [
    "concat_datasets",
    "remove_dims",
    "EmptyFilterResultError",
    "filter_index",
    "filter_latitude",
    "filter_radius",
    "filter_time",
    "get_filter_time_mask",
    "insert_var",
    "merge_datasets",
    "convert_scalar_var_to_str",
]
