"""
**earthcarekit.read**

File reading utilities.

## Notes

This module depends on other internal modules:

- [earthcarekit.constants][]
- [earthcarekit.filter][]
- [earthcarekit.geo][]
- [earthcarekit.profile][]
- [earthcarekit.stats][]
- [earthcarekit.swath][]
- [earthcarekit.typing][]
- [earthcarekit.utils][]

---
"""

from ..filter import filter_frame as _deprecated_filter_frame
from ..utils.path import search_files_by_regex
from .any import read_any
from .header import read_header_data
from .info import (
    FileAgency,
    FileLatency,
    FileMissionID,
    FileType,
    ProductInfo,
    get_file_type,
    get_product_info,
    get_product_infos,
    is_earthcare_product,
)
from .lazy import LazyDataset, LazyVariable
from .netcdf import read_nc
from .pollynet import read_polly
from .product import (
    add_isccp_cloud_type,
    read_hdr_fixed_header,
    read_product,
    read_products,
    rebin_msi_to_jsg,
    search_product,
)
from .product._rebin_xmet_to_vertical_track import rebin_xmet_to_vertical_track
from .product.auxiliary.aux_met_1d import add_potential_temperature
from .product.level1.atl_nom_1b import add_depol_ratio, add_scattering_ratio
from .science import read_science_data

__all__ = [
    "read_hdr_fixed_header",
    "read_header_data",
    "read_product",
    "read_products",
    "read_science_data",
    "read_nc",
    "rebin_xmet_to_vertical_track",
    "rebin_msi_to_jsg",
    "search_product",
    "FileAgency",
    "FileLatency",
    "FileMissionID",
    "FileType",
    "ProductInfo",
    "get_file_type",
    "get_product_info",
    "get_product_infos",
    "is_earthcare_product",
    "search_files_by_regex",
    "read_polly",
    "read_any",
    "add_depol_ratio",
    "add_scattering_ratio",
    "add_isccp_cloud_type",
    "add_potential_temperature",
    "LazyDataset",
    "LazyVariable",
]

_DEPRECATED = {
    "trim_to_latitude_frame_bounds": _deprecated_filter_frame,
}


def __getattr__(name):
    import warnings

    if name in _DEPRECATED:
        warnings.warn(
            f"'{name}' is deprecated; use 'eck.{_DEPRECATED[name].__name__}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return _DEPRECATED[name]

    raise AttributeError(name)
