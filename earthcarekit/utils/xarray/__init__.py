"""
**earthcarekit.utils.xarray**

Utilities based on `xarray`.

## Notes

This module does not depend on other internal modules.

---
"""

from ._concat import concat_datasets
from ._delete import remove_dims
from ._demote_coordinate_dimension import demote_coords
from ._fill_values import _convert_all_fill_values_to_nan
from ._insert_var import insert_var
from ._merge import merge_datasets
from ._scalars import convert_scalar_var_to_str

__all__ = [
    "concat_datasets",
    "remove_dims",
    "insert_var",
    "merge_datasets",
    "convert_scalar_var_to_str",
    "_convert_all_fill_values_to_nan",
    "demote_coords",
]
