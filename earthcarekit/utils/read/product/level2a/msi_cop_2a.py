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


def add_isccp_cloud_type(
    ds: xr.Dataset,
    new_var: str = "isccp_cloud_type",
    cot_var: str = "cloud_optical_thickness",
    cth_var: str = "cloud_top_height",
    along_track_dim: str = ALONG_TRACK_DIM,
    across_track_dim: str = ACROSS_TRACK_DIM,
) -> xr.Dataset:
    """
    Adds a variable to the dataset containing ISCCP cloud types calculated from cloud optical thickness (COT)
    and cloud top height (CTH).

    Args:
        ds (xr.Dataset): A MSI_COP_2A dataset.
        new_var (str, optional): Name of the new ISCCP cloud type variable. Defaults to "isccp_cloud_type".
        cot_var (str, optional): Name of the COT variable in `ds`. Defaults to "cloud_optical_thickness".
        cth_var (str, optional): Name of the CTH variable in `ds`. Defaults to "cloud_top_height".
        along_track_dim (str, optional): Name of the along-track dimension in `ds`. Defaults to ALONG_TRACK_DIM.
        across_track_dim (str, optional): Name of the across-track dimension in `ds`. Defaults to ACROSS_TRACK_DIM.

    Returns:
        xr.Dataset: The input dataset with added ISCCP cloud type variable.

    References:
        International Satellite Cloud Climatology Project (ISCCP), "ISCCP Definition of Cloud Types."
            https://isccp.giss.nasa.gov/cloudtypes.html (accessed 2025-09-25)
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
            "long_name": "ISCCP cloud type calculated from M-COP",
            "definition": "0: Clear, 1: Cumulus, 2: Altocumulus, 3: Cirrus, 4: Stratocumulus, 5: Altostratus, 6: Cirrostratus, 7: Stratus, 8: Nimbostratus, 9: Deep convection, -127: Not determined",
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
