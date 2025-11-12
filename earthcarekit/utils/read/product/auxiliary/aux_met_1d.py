import warnings

import xarray as xr
from scipy.interpolate import interp1d  # type: ignore

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
)
from ....xarray_utils import merge_datasets
from .._rename_dataset_content import (
    rename_and_create_temperature_vars,
    rename_common_dims_and_vars,
)
from ..file_info import FileAgency
from ..science_group import read_science_data


def read_product_xmet(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
    ensure_nans: bool = DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    **kwargs,
) -> xr.Dataset:
    """Opens AUX_MET_1D file as a `xarray.Dataset`."""
    ds = read_science_data(
        filepath,
        agency=FileAgency.ESA,
        ensure_nans=ensure_nans,
        **kwargs,
    )

    if not modify:
        return ds

    ds = rename_common_dims_and_vars(
        ds=ds,
        tropopause_var="tropopause_height_calipso",
        temperature_var="temperature",
    )

    return ds
