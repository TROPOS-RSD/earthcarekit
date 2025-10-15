import xarray as xr

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
)
from ....swath_data.across_track_distance import (
    add_across_track_distance,
    add_nadir_track,
    add_nadir_var,
    get_nadir_index,
)
from ....xarray_utils import merge_datasets
from .._rename_dataset_content import rename_common_dims_and_vars, rename_var_info
from ..file_info import FileAgency
from ..header_group import add_header_and_meta_data
from ..science_group import read_science_data


def read_product_actc(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
    **kwargs,
) -> xr.Dataset:
    """Opens AC__TC__2B file as a `xarray.Dataset`."""
    ds = read_science_data(
        filepath,
        agency=FileAgency.ESA,
        **kwargs,
    )

    if not modify:
        return ds

    ds = rename_common_dims_and_vars(
        ds,
        along_track_dim="along_track",
        vertical_dim="JSG_height",
        track_lat_var="latitude",
        track_lon_var="longitude",
        height_var="height",
        time_var="time",
        elevation_var="elevation",
    )

    ds = rename_var_info(
        ds,
        "synergetic_target_classification",
        long_name="Synergetic target classification (HiRes)",
    )
    ds = rename_var_info(
        ds,
        "synergetic_target_classification_medium_resolution",
        long_name="Synergetic target classification (MedRes)",
    )
    ds = rename_var_info(
        ds,
        "synergetic_target_classification_low_resolution",
        long_name="Synergetic target classification (LowRes)",
    )

    ds = add_header_and_meta_data(filepath=filepath, ds=ds, header=header, meta=meta)

    return ds
