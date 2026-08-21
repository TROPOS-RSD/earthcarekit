from typing import Any

import numpy as np
import xarray as xr
from numpy.typing import NDArray

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
    SWATH_LAT_VAR,
    SWATH_LON_VAR,
    UNITS_KELVIN,
    UNITS_MSI_RADIANCE,
)
from ....data.swath import (
    add_across_track_distance,
    add_nadir_track,
    drop_samples_with_missing_geo_data_along_track,
    get_nadir_index,
)
from ....filter._filter_time import get_filter_time_mask
from ....typing import TimeRangeLike
from ...info import FileAgency
from ...science import read_science_data
from .._rename_dataset_content import rename_common_dims_and_vars, rename_var_info


def _get_min_max(x: NDArray) -> tuple[float, float]:
    return (np.nanquantile(x, 0.01), np.nanquantile(x, 0.99))


def _get_v(x, _w, _s, _min, _max):
    return np.clip(_w * (x - _min) / (_s * (_max - _min)), a_min=0, a_max=1).T


def compute_rgb(
    swir1: NDArray,
    nir: NDArray,
    vis: NDArray,
    mask: Any = ...,
) -> NDArray:
    r_min, r_max = _get_min_max(swir1[mask])
    g_min, g_max = _get_min_max(nir[mask])
    b_min, b_max = _get_min_max(vis[mask])

    r_w, g_w, b_w = (1.0, 1.0, 1.0)
    r_s, g_s, b_s = (1.0, 1.0, 1.0)

    r_v = _get_v(swir1, r_w, r_s, r_min, r_max)
    g_v = _get_v(nir, g_w, g_s, g_min, g_max)
    b_v = _get_v(vis, b_w, b_s, b_min, b_max)

    rgb = np.stack((r_v, g_v, b_v), axis=2)
    rgb[np.isnan(rgb)] = 0.0

    return rgb


def update_rgb(
    ds: xr.Dataset,
    swir1_var: str = "swir1",
    nir_var: str = "nir",
    vis_var: str = "vis",
    rgb_var: str = "rgb",
    rgb_dim: str = "rgb_channel",
    along_track_dim: str = "along_track",
    across_track_dim: str = "across_track",
    time_range: TimeRangeLike | None = None,
    time_var: str = "time",
    mask: Any = ...,
) -> xr.Dataset:
    """Computes and adds a false RGB data variable to the dataset (e.g., MSI_RGR_1C).

    Args:
        ds: Input dataset with SWIR1, NIR, and VIS variables.
        swir1_var: SWIR1 variable name; defaults to "swir1".
        nir_var: NIR variable name; defaults to "nir".
        vis_var: VIS variable name; defaults to "vis".
        rgb_var: Output RGB variable name; defaults to "rgb".
        rgb_dim: RGB channel dimension name; defaults to "rgb_channel".
        along_track_dim: Along-track dimension name; defaults to "along_track".
        across_track_dim: Across-track dimension name; defaults to "across_track".
        time_range: Start/stop time range for masking; ignored when `mask` is provided.
        time_var: Time variable name; defaults to "time".
        mask: Boolean mask; RGB composite ranges computed from masked data only, then applied to full dataset.

    Returns:
        Dataset with false RGB image variable added.
    """
    if time_range and mask != ...:
        mask = get_filter_time_mask(ds, time_range, time_var=time_var)

    rgb = compute_rgb(
        swir1=ds[swir1_var].values,
        nir=ds[nir_var].values,
        vis=ds[vis_var].values,
        mask=mask,
    )

    ds[rgb_var] = ((across_track_dim, along_track_dim, rgb_dim), rgb)
    ds[rgb_var].attrs["units"] = ""
    ds[rgb_var].attrs["long_name"] = "False RGB image"
    ds[rgb_var].attrs["label"] = "False RGB image"

    return ds


def _get_vns_name(
    wavelength: str, band_name: str | None = None, is_uncertainty: bool = False
) -> str:
    sub_str = "" if not is_uncertainty else "uncertainty "
    name: str = f"Radiance {sub_str}at {wavelength} nm"
    # if band_name:
    #     return name + f" ({band_name})"
    return name


def _get_tir_name(
    wavelength: str, band_name: str | None = None, is_uncertainty: bool = False
) -> str:
    sub_str = "" if not is_uncertainty else "uncertainty "
    name: str = f"BT {sub_str}at {wavelength} µm"
    # if band_name:
    #     return name + f" ({band_name})"
    return name


def read_product_mrgr(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
    ensure_nans: bool = DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    **kwargs,
) -> xr.Dataset:
    """Opens MSI_RGR_1C file as a `xarray.Dataset`."""
    ds = read_science_data(
        filepath,
        agency=FileAgency.ESA,
        ensure_nans=ensure_nans,
        **kwargs,
    )

    if not modify:
        return ds

    ds = drop_samples_with_missing_geo_data_along_track(
        ds=ds,
        swath_lat_var="latitude",
        along_track_dim="along_track",
        across_track_dim="across_track",
    )

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

    for v in ["vis", "vis_uncertainty"]:
        _wavelength = "670"
        _name = "VIS"
        _is_uncertainty = "uncertainty" in v
        ds = rename_var_info(
            ds=ds,
            var=v,
            name=_get_vns_name(_wavelength, None, _is_uncertainty),
            long_name=_get_vns_name(_wavelength, _name, _is_uncertainty),
            units=UNITS_MSI_RADIANCE,
        )
    for v in ["nir", "nir_uncertainty"]:
        _wavelength = "865"
        _name = "NIR"
        _is_uncertainty = "uncertainty" in v
        ds = rename_var_info(
            ds=ds,
            var=v,
            name=_get_vns_name(_wavelength, None, _is_uncertainty),
            long_name=_get_vns_name(_wavelength, _name, _is_uncertainty),
            units=UNITS_MSI_RADIANCE,
        )
    for v in ["swir1", "swir1_uncertainty"]:
        _wavelength = "1650"
        _name = "SWIR-1"
        _is_uncertainty = "uncertainty" in v
        ds = rename_var_info(
            ds=ds,
            var=v,
            name=_get_vns_name(_wavelength, None, _is_uncertainty),
            long_name=_get_vns_name(_wavelength, _name, _is_uncertainty),
            units=UNITS_MSI_RADIANCE,
        )
    for v in ["swir2", "swir2_uncertainty"]:
        _wavelength = "2210"
        _name = "SWIR-2"
        _is_uncertainty = "uncertainty" in v
        ds = rename_var_info(
            ds=ds,
            var=v,
            name=_get_vns_name(_wavelength, None, _is_uncertainty),
            long_name=_get_vns_name(_wavelength, _name, _is_uncertainty),
            units=UNITS_MSI_RADIANCE,
        )
    for v in ["tir1", "tir1_uncertainty"]:
        _wavelength = "8.8"
        _name = "TIR-1"
        _is_uncertainty = "uncertainty" in v
        ds = rename_var_info(
            ds=ds,
            var=v,
            name=_get_tir_name(_wavelength, None, _is_uncertainty),
            long_name=_get_tir_name(_wavelength, _name, _is_uncertainty),
            units=UNITS_KELVIN,
        )
    for v in ["tir2", "tir2_uncertainty"]:
        _wavelength = "10.8"
        _name = "TIR-2"
        _is_uncertainty = "uncertainty" in v
        ds = rename_var_info(
            ds=ds,
            var=v,
            name=_get_tir_name(_wavelength, None, _is_uncertainty),
            long_name=_get_tir_name(_wavelength, _name, _is_uncertainty),
            units=UNITS_KELVIN,
        )
    for v in ["tir3", "tir3_uncertainty"]:
        _wavelength = "12.0"
        _name = "TIR-3"
        _is_uncertainty = "uncertainty" in v
        ds = rename_var_info(
            ds=ds,
            var=v,
            name=_get_tir_name(_wavelength, None, _is_uncertainty),
            long_name=_get_tir_name(_wavelength, _name, _is_uncertainty),
            units=UNITS_KELVIN,
        )

    ds = ds.drop_vars(["pixel_values", "pixel_values_uncertainty", "line_quality_status"])
    ds = ds.drop_dims("band")

    ds = update_rgb(ds)

    nadir_idx = get_nadir_index(ds, nadir_idx=270)

    ds = ds.rename({"latitude": SWATH_LAT_VAR})
    ds = ds.rename({"longitude": SWATH_LON_VAR})
    ds = add_nadir_track(
        ds,
        nadir_idx,
        swath_lat_var=SWATH_LAT_VAR,
        swath_lon_var=SWATH_LON_VAR,
        along_track_dim="along_track",
        across_track_dim="across_track",
        nadir_lat_var="latitude",
        nadir_lon_var="longitude",
    )
    ds = add_across_track_distance(
        ds, nadir_idx, swath_lat_var=SWATH_LAT_VAR, swath_lon_var=SWATH_LON_VAR
    )

    ds = rename_common_dims_and_vars(
        ds,
        along_track_dim="along_track",
        across_track_dim="across_track",
        track_lat_var="latitude",
        track_lon_var="longitude",
        swath_lat_var=SWATH_LAT_VAR,
        swath_lon_var=SWATH_LON_VAR,
        time_var="time",
    )

    ds = ds.reset_coords()

    return ds
