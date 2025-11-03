import xarray as xr

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
)
from ....xarray_utils import merge_datasets
from .._rename_dataset_content import rename_common_dims_and_vars
from ..file_info import FileAgency
from ..science_group import read_science_data


def read_product_aald(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
    ensure_nans: bool = DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    **kwargs,
) -> xr.Dataset:
    """Opens ATL_ALD_2A file as a `xarray.Dataset`."""
    ds = read_science_data(
        filepath,
        agency=FileAgency.ESA,
        ensure_nans=ensure_nans,
        **kwargs,
    )

    if not modify:
        return ds

    ds = rename_common_dims_and_vars(
        ds,
        along_track_dim="along_track",
        track_lat_var="latitude",
        track_lon_var="longitude",
        time_var="time",
    )

    vars = [
        "aerosol_layer_top",
        "aerosol_layer_confidence",
        "aerosol_layer_base_confidence",
        "aerosol_layer_top_confidence",
        "aerosol_layer_optical_thickness_355nm",
        "aerosol_layer_optical_thickness_355nm_error",
        "aerosol_layer_mean_extinction_355nm",
        "aerosol_layer_mean_extinction_355nm_error",
        "aerosol_layer_mean_backscatter_355nm",
        "aerosol_layer_mean_backscatter_355nm_error",
        "aerosol_layer_mean_lidar_ratio_355nm",
        "aerosol_layer_mean_lidar_ratio_355nm_error",
        "aerosol_layer_mean_depolarisation_355nm",
        "aerosol_layer_mean_depolarisation_355nm_error",
    ]

    n_layers = ds["max_layers"].shape[0]

    for i in range(n_layers):
        for var in vars:
            ds = ds.assign({f"{var}{i+1}": ds[var].isel({"max_layers": i})})

    return ds
