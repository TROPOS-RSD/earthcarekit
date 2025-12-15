import numpy as np
import xarray as xr

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
from ....swath_data.across_track_distance import (
    add_across_track_distance,
    add_nadir_track,
    drop_samples_with_missing_geo_data_along_track,
    get_nadir_index,
)
from ....xarray_utils import merge_datasets
from .._rename_dataset_content import rename_common_dims_and_vars, rename_var_info
from ..file_info import FileAgency
from ..science_group import read_science_data


def _get_bitmasks(ds: xr.Dataset, var: str, n: int):
    bits = ds[var].values.astype(np.uint16)

    masks = {i: 1 << i for i in range(n + 1)}
    bitmasks = {name: (bits & mask) > 0 for name, mask in masks.items()}

    return bits, bitmasks


def _get_dominant_classes(ds: xr.Dataset, var: str, n: int):
    bits, bitmasks = _get_bitmasks(ds=ds, var=var, n=n)

    new_values = np.zeros(bits.shape)
    for i in range(1, n + 1):
        new_values[bitmasks[i]] = i

    return new_values


def add_surface_classification_plot_var(
    ds: xr.Dataset,
    var: str = "surface_classification",
    n: int = 8,
):
    """Adds a plottable variable for the M-CM "surface_classification" to the given dataset, called "plot_surface_classification"."""
    new_values = _get_dominant_classes(ds, var=var, n=n)

    new_var = f"plot_{var}"
    ds[new_var] = ds[var].copy()
    ds[new_var].values = new_values
    ds[new_var] = ds[new_var].assign_attrs(
        {
            "long_name": "Surface classification",
            "definition": "0: Undefined, 1: Water, 2: Land, 3: Desert, 4: Vegetation NDVI, 5: Snow XMET, 6: Snow NDSI, 7: Sea ice XMET, 8: Sunglint",
            "units": "",
            "earthcarekit": "Added by earthcarekit: class integers converted from bitwise",
        }
    )

    return ds


def add_quality_status_plot_var(ds, var: str, n: int = 4):
    """Adds a plottable variable for the M-CM "cloud_[mask/type/phase]_quality_status" variable to the given dataset, called "plot_cloud_[mask/type/phase]_quality_status"."""
    if var not in [
        "cloud_mask_quality_status",
        "cloud_type_quality_status",
        "cloud_phase_quality_status",
    ]:
        raise ValueError(f"invalid MCM quality status variable '{var}'")

    new_values = _get_dominant_classes(ds, var=var, n=n)

    new_var = f"plot_{var}"
    ds[new_var] = ds[var].copy()
    ds[new_var].values = new_values
    ds[new_var] = ds[new_var].assign_attrs(
        {
            "definition": "0: Undefined, 1: Poor, 2: Low, 3: Medium, 4: High",
            "units": "",
            "earthcarekit": "Added by earthcarekit: class integers converted from bitwise",
        }
    )

    return ds


def read_product_mcm(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
    ensure_nans: bool = DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    **kwargs,
) -> xr.Dataset:
    """Opens MSI_CM__2A file as a `xarray.Dataset`."""
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

    nadir_idx = get_nadir_index(ds, nadir_idx=266)
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

    ds = add_surface_classification_plot_var(ds)
    ds = add_quality_status_plot_var(ds, var="cloud_mask_quality_status")
    ds = add_quality_status_plot_var(ds, var="cloud_type_quality_status")
    ds = add_quality_status_plot_var(ds, var="cloud_phase_quality_status")

    return ds
