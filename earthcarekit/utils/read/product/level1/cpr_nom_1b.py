import warnings

import numpy as np
import xarray as xr

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
)
from ....rolling_mean import rolling_mean_2d
from ....xarray_utils import merge_datasets
from .._rename_dataset_content import (
    HEIGHT_VAR,
    rename_common_dims_and_vars,
    rename_var_info,
)
from ..file_info import FileAgency
from ..header_group import add_header_and_meta_data
from ..science_group import read_science_data


def read_product_cnom(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
) -> xr.Dataset:
    """Opens CPR_NOM_1B file as a `xarray.Dataset`."""
    ds = read_science_data(filepath, agency=FileAgency.JAXA)

    if not modify:
        return ds

    reflectivity_var = "radarReflectivityFactor"
    doppler_velocity_var = "dopplerVelocity"

    # change the sign of the doppler velocity
    ds[doppler_velocity_var].values = ds[doppler_velocity_var].values * -1

    # Combine same dimensions
    ds = ds.squeeze()  # Removes dimensions of size 1
    ds = ds.rename({"phony_dim_14": "phony_dim_10"})
    ds = ds.rename({"phony_dim_15": "phony_dim_11"})
    # ds = ds.rename({'phony_dim_8': 'phony_dim_5'})

    # Rename content
    ds = rename_common_dims_and_vars(
        ds,
        along_track_dim="phony_dim_10",
        vertical_dim="phony_dim_11",
        track_lat_var="latitude",
        track_lon_var="longitude",
        height_var="binHeight",
        time_var="profileTime",
        elevation_var="surfaceElevation",
    )

    # Create plotting ready radar reflectivity and doppler velocity variables
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        values_ref = 10 * np.log10(ds[reflectivity_var].values).copy()
    values_ref = rolling_mean_2d(values_ref, 3, axis=1)
    values_ref = rolling_mean_2d(values_ref, 10, axis=0)

    new_radar_reflectivity_var = f"plot_{reflectivity_var}"
    ds[new_radar_reflectivity_var] = ds[reflectivity_var].copy()
    ds[new_radar_reflectivity_var].values = values_ref
    mask = values_ref < -27
    ds[new_radar_reflectivity_var].values[values_ref < -27] = np.nan
    ds = rename_var_info(
        ds,
        new_radar_reflectivity_var,
        "Radar reflectivity",
        "Radar reflectivity",
        "dBZ",
    )

    values_dvel = ds[doppler_velocity_var].values
    values_dvel = rolling_mean_2d(values_dvel, 3, axis=1)
    values_dvel = rolling_mean_2d(values_dvel, 10, axis=0)

    new_doppler_velocity_var = f"plot_{doppler_velocity_var}"
    ds[new_doppler_velocity_var] = ds[doppler_velocity_var].copy()
    ds[new_doppler_velocity_var].values = values_dvel
    ds[new_doppler_velocity_var].values[mask] = np.nan
    ds = rename_var_info(
        ds,
        new_doppler_velocity_var,
        "Doppler velocity",
        "Doppler velocity",
        "m/s",
    )

    # Remove nans from heights
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        ds[HEIGHT_VAR].values[np.isnan(ds[HEIGHT_VAR].values)] = np.nanmin(
            ds[HEIGHT_VAR].values
        )

    ds = add_header_and_meta_data(filepath=filepath, ds=ds, header=header, meta=meta)
    return ds
