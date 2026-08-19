import numpy as np
import xarray as xr

from ....constants import (
    ACROSS_TRACK_DIM,
    ALONG_TRACK_DIM,
    DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
    SWATH_LAT_VAR,
    SWATH_LON_VAR,
)
from ....data.swath._across_track_distance import (
    add_across_track_distance,
    add_nadir_track,
    drop_samples_with_missing_geo_data_along_track,
    get_nadir_index,
)
from ...info import FileAgency
from ...science import read_science_data
from .._rename_dataset_content import rename_common_dims_and_vars


def add_isccp_cloud_type(
    ds: xr.Dataset,
    new_var: str = "isccp_cloud_type",
    cot_var: str = "cloud_optical_thickness",
    cth_var: str = "cloud_top_height",
    along_track_dim: str = ALONG_TRACK_DIM,
    across_track_dim: str = ACROSS_TRACK_DIM,
) -> xr.Dataset:
    """Adds ISCCP cloud type classification to the dataset.

    Args:
        ds: MSI_COP_2A dataset with COT and CTH.
        new_var: Name of the ISCCP cloud type variable; defaults to "isccp_cloud_type".
        cot_var: Cloud optical thickness variable name; defaults to "cloud_optical_thickness".
        cth_var: Cloud top height variable name; defaults to "cloud_top_height".
        along_track_dim: Along-track dimension name.
        across_track_dim: Across-track dimension name.

    Returns:
        Dataset with ISCCP cloud type variable added.

    References:
        - International Satellite Cloud Climatology Project (ISCCP). ISCCP Definition of Cloud Types.
        Retrieved September 25, 2025. https://isccp.giss.nasa.gov/cloudtypes.html
    """
    cot = ds[cot_var].values
    cth = ds[cth_var].values

    cu = np.where((cth >= 100) & (cth < 3200) & (cot >= 0.01) & (cot < 3.6))
    ac = np.where((cth >= 3200) & (cth < 6500) & (cot >= 0.01) & (cot < 3.6))
    ci = np.where((cth >= 6500) & (cth < 19300) & (cot >= 0.01) & (cot < 3.6))
    sc = np.where((cth >= 100) & (cth < 3200) & (cot >= 3.6) & (cot < 23))
    asc = np.where((cth >= 3200) & (cth < 6500) & (cot >= 3.6) & (cot < 23))
    cs = np.where((cth >= 6500) & (cth < 19300) & (cot >= 3.6) & (cot < 23))
    st = np.where((cth >= 100) & (cth < 3200) & (cot >= 23))
    ns = np.where((cth >= 3200) & (cth < 6500) & (cot >= 23))
    cb = np.where((cth >= 6500) & (cth < 19300) & (cot >= 23))
    clear = np.where((cot < 0.01) & (cot >= 0))

    cloud_type = np.empty(shape=cot.shape, dtype=int)
    cloud_type[:, :] = -127

    cloud_type[cu] = 1
    cloud_type[ac] = 2
    cloud_type[ci] = 3
    cloud_type[sc] = 4
    cloud_type[asc] = 5
    cloud_type[cs] = 6
    cloud_type[st] = 7
    cloud_type[ns] = 8
    cloud_type[cb] = 9
    cloud_type[clear] = 0

    da = xr.DataArray(
        cloud_type,
        dims=(along_track_dim, across_track_dim),
        name=new_var,
        attrs={
            "units": "",
            "label": "ISCCP cloud type calculated from M-COP",
            "definition": "0: Clear, 1: Cumulus, 2: Altocumulus, 3: Cirrus, 4: Stratocumulus, 5: Altostratus, 6: Cirrostratus, 7: Stratus, 8: Nimbostratus, 9: Deep convection, -127: Not determined",
            "earthcarekit": "Added by earthcarekit",
        },
    )
    ds[new_var] = da

    return ds


def read_product_mcop(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
    ensure_nans: bool = DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    **kwargs,
) -> xr.Dataset:
    """Opens MSI_COP_2A file as a `xarray.Dataset`."""
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
        ds,
        nadir_idx,
        swath_lat_var=SWATH_LAT_VAR,
        swath_lon_var=SWATH_LON_VAR,
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

    ds = add_isccp_cloud_type(ds)

    return ds
