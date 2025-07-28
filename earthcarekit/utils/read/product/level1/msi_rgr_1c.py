import numpy as np
import xarray as xr

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
)
from ....swath_data.across_track_distance import (
    add_across_track_distance,
    add_nadir_track,
    get_nadir_index,
)
from ....xarray_utils import merge_datasets
from .._rename_dataset_content import rename_common_dims_and_vars, rename_var_info
from ..file_info import FileAgency
from ..header_group import add_header_and_meta_data
from ..science_group import read_science_data


def _get_rgb_from_swir1_nir_vis(ds: xr.Dataset) -> np.ndarray:
    get_min_max = lambda x: np.array([ds[x].quantile(0.01), ds[x].quantile(0.99)])

    r_min, r_max = get_min_max("swir1")
    g_min, g_max = get_min_max("nir")
    b_min, b_max = get_min_max("vis")

    r_w, g_w, b_w = [1.0, 1.0, 1.0]
    r_s, g_s, b_s = [1.0, 1.0, 1.0]

    get_v = lambda x, _w, _s, _min, _max: np.clip(
        _w * (ds[x] - _min) / (_s * (_max - _min)), a_min=0, a_max=1
    ).T

    r_v = get_v("swir1", r_w, r_s, r_min, r_max)
    g_v = get_v("nir", g_w, g_s, g_min, g_max)
    b_v = get_v("vis", b_w, b_s, b_min, b_max)

    rgb = np.stack((r_v, g_v, b_v), axis=2)
    rgb[np.isnan(rgb)] = 0.0

    return rgb


def _add_rgb(ds: xr.Dataset) -> xr.Dataset:
    rgb = _get_rgb_from_swir1_nir_vis(ds)
    # rgb = np.reshape(rgb, (rgb.shape[1], rgb.shape[0], 3))

    ds["rgb"] = (("across_track", "along_track", "rgb_color"), rgb)
    ds["rgb"].attrs["units"] = ""
    ds["rgb"].attrs["long_name"] = "False RGB image"

    return ds


def read_product_mrgr(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
) -> xr.Dataset:
    """Opens MSI_RGR_1C file as a `xarray.Dataset`."""
    ds = read_science_data(filepath, agency=FileAgency.ESA)

    if not modify:
        return ds

    ds = ds.assign(
        vis=ds["pixel_values"].isel({"band": 0}),
        nir=ds["pixel_values"].isel({"band": 1}),
        swir1=ds["pixel_values"].isel({"band": 2}),
        swir2=ds["pixel_values"].isel({"band": 3}),
        tir1=ds["pixel_values"].isel({"band": 4}),
        tir2=ds["pixel_values"].isel({"band": 5}),
        tir3=ds["pixel_values"].isel({"band": 6}),
        vis_uncertainty=ds["pixel_values_uncertainty"].isel({"band": 0}),
        nir_uncertainty=ds["pixel_values_uncertainty"].isel({"band": 1}),
        swir1_uncertainty=ds["pixel_values_uncertainty"].isel({"band": 2}),
        swir2_uncertainty=ds["pixel_values_uncertainty"].isel({"band": 3}),
        tir1_uncertainty=ds["pixel_values_uncertainty"].isel({"band": 4}),
        tir2_uncertainty=ds["pixel_values_uncertainty"].isel({"band": 5}),
        tir3_uncertainty=ds["pixel_values_uncertainty"].isel({"band": 6}),
        vis_line_quality_status=ds["line_quality_status"].isel({"band": 0}),
        nir_line_quality_status=ds["line_quality_status"].isel({"band": 1}),
        swir1_line_quality_status=ds["line_quality_status"].isel({"band": 2}),
        swir2_line_quality_status=ds["line_quality_status"].isel({"band": 3}),
        tir1_line_quality_status=ds["line_quality_status"].isel({"band": 4}),
        tir2_line_quality_status=ds["line_quality_status"].isel({"band": 5}),
        tir3_line_quality_status=ds["line_quality_status"].isel({"band": 6}),
    )
    ds = rename_var_info(ds, "tir2", "TIR-2", "TIR-2", "")
    ds = ds.drop_vars(
        ["pixel_values", "pixel_values_uncertainty", "line_quality_status"]
    )
    ds = ds.drop_dims("band")

    ds = _add_rgb(ds)

    nadir_idx = get_nadir_index(ds)
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

    ds = add_header_and_meta_data(filepath=filepath, ds=ds, header=header, meta=meta)

    return ds
