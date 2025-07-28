import xarray as xr

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
)
from ....xarray_utils import merge_datasets
from .._rename_dataset_content import rename_common_dims_and_vars
from ..file_info import FileAgency
from ..header_group import add_header_and_meta_data
from ..science_group import read_science_data


def read_product_acth(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
) -> xr.Dataset:
    """Opens ATL_CTH_2A file as a `xarray.Dataset`."""
    ds = read_science_data(filepath, agency=FileAgency.ESA)

    if not modify:
        return ds

    ds = rename_common_dims_and_vars(
        ds,
        along_track_dim="along_track",
        track_lat_var="latitude",
        track_lon_var="longitude",
        time_var="time",
    )

    ds = add_header_and_meta_data(filepath=filepath, ds=ds, header=header, meta=meta)

    return ds
