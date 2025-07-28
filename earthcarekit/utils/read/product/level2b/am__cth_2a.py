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


def read_product_amcth(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
) -> xr.Dataset:
    """Opens AM__CTH_2A file as a `xarray.Dataset`."""
    ds = read_science_data(filepath, agency=FileAgency.ESA)

    if not modify:
        return ds

    nadir_idx = get_nadir_index(ds, nadir_idx=150)

    ds = ds.rename({"latitude": "swath_latitude"})
    ds = ds.rename({"longitude": "swath_longitude"})
    ds = add_nadir_track(
        ds,
        nadir_idx,
        swath_lat_var="swath_latitude",
        swath_lon_var="swath_longitude",
        along_track_dim="along_track",
        across_track_dim="across_track",
        nadir_lat_var="latitude",
        nadir_lon_var="longitude",
    )
    ds = add_across_track_distance(
        ds, nadir_idx, swath_lat_var="swath_latitude", swath_lon_var="swath_longitude"
    )

    ds = rename_common_dims_and_vars(
        ds,
        along_track_dim="along_track",
        across_track_dim="across_track",
        track_lat_var="latitude",
        track_lon_var="longitude",
        swath_lat_var="swath_latitude",
        swath_lon_var="swath_longitude",
        time_var="time",
    )

    ds["cloud_top_height_MSI"].values = ds["cloud_top_height_MSI"].values / 1000.0
    ds = rename_var_info(
        ds, "cloud_top_height_MSI", long_name="CTH from M-COP", units="km"
    )

    ds["cloud_top_height_difference_ATLID_MSI"].values = (
        ds["cloud_top_height_difference_ATLID_MSI"].values / 1000.0
    )
    ds = rename_var_info(
        ds,
        "cloud_top_height_difference_ATLID_MSI",
        long_name="AM-CTH CTH difference",
        units="km",
    )

    ds = rename_var_info(
        ds,
        "quality_status",
        long_name="Quality status",
        units="",
    )

    ds["plot_cloud_top_height_difference_ATLID_MSI"] = ds[
        "cloud_top_height_difference_ATLID_MSI"
    ].copy()
    mask = ds["quality_status"].values == 4
    ds["plot_cloud_top_height_difference_ATLID_MSI"].values[mask] = 100e3

    ds = add_nadir_var(ds, "cloud_top_height_MSI")
    ds = add_nadir_var(ds, "cloud_top_height_difference_ATLID_MSI")
    ds = add_nadir_var(ds, "quality_status")
    ds = add_nadir_var(ds, "cloud_fraction")

    ds = add_header_and_meta_data(filepath=filepath, ds=ds, header=header, meta=meta)

    return ds
