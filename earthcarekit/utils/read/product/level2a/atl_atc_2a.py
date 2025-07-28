import xarray as xr

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
)
from ....xarray_utils import merge_datasets
from .._rename_dataset_content import (
    ELEVATION_VAR,
    TROPOPAUSE_VAR,
    rename_common_dims_and_vars,
    rename_var_info,
)
from ..file_info import FileAgency
from ..header_group import add_header_and_meta_data
from ..science_group import read_science_data


def read_product_atc(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
) -> xr.Dataset:
    """Opens ATL_TC__2A file as a `xarray.Dataset`."""
    ds = read_science_data(filepath, agency=FileAgency.ESA)

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
        tropopause_var="tropopause_height",
        elevation_var="elevation",
    )

    ds = rename_var_info(
        ds,
        "simple_classification",
        "Simple classification",
        "Simple classification",
        "-",
    )
    for res, res_label in zip(
        ["", "_medium_resolution", "_low_resolution"], ["HiRes", "MedRes", "LowRes"]
    ):
        ds = rename_var_info(
            ds,
            f"classification{res}",
            name=f"Target classification ({res_label})",
            long_name=f"Target classification ({res_label})",
            units="-",
        )

    ds[TROPOPAUSE_VAR] = ds["tropopause_height"]
    ds[ELEVATION_VAR] = ds["elevation"]

    ds = add_header_and_meta_data(filepath=filepath, ds=ds, header=header, meta=meta)

    return ds
