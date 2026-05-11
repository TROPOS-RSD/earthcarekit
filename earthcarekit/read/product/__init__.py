from ...filter import filter_frame as _deprecated_filter_frame
from ._concat import concat_datasets, read_products
from ._generic import read_product
from ._header_file import read_hdr_fixed_header
from ._rebin_msi_to_jsg import rebin_msi_to_jsg
from ._rebin_xmet_to_vertical_track import rebin_xmet_to_vertical_track
from ._search import search_product
from .level1.msi_rgr_1c import _add_rgb as update_rgb_of_mrgr
from .level2a.msi_cop_2a import add_isccp_cloud_type

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
