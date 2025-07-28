import warnings

import numpy as np
import xarray as xr
from scipy.interpolate import interp1d  # type: ignore
from scipy.spatial import cKDTree  # type: ignore

from ....constants import (
    ALONG_TRACK_DIM,
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
    HEIGHT_VAR,
    TIME_VAR,
    TRACK_LAT_VAR,
    TRACK_LON_VAR,
    VERTICAL_DIM,
)
from ....geo import sequence_geo_to_ecef
from ....xarray_utils import merge_datasets, remove_dims
from .._rename_dataset_content import (
    rename_and_create_temperature_vars,
    rename_common_dims_and_vars,
)
from ..file_info import FileAgency
from ..header_group import add_header_and_meta_data
from ..science_group import read_science_data


def rebin_xmet_to_vertical_track(
    ds_xmet: xr.Dataset,
    ds_vert: xr.Dataset,
    vars: list[str] | None = None,
    k: int = 4,
    eps: float = 1e-12,
    lat_var: str = TRACK_LAT_VAR,
    lon_var: str = TRACK_LON_VAR,
    time_var: str = TIME_VAR,
    height_var: str = HEIGHT_VAR,
    along_track_dim: str = ALONG_TRACK_DIM,
    height_dim: str = VERTICAL_DIM,
    xmet_lat_var: str = "latitude",
    xmet_lon_var: str = "longitude",
    xmet_height_var: str = "geometrical_height",
    xmet_height_dim: str = "height",
    xmet_horizontal_grid_dim: str = "horizontal_grid",
) -> xr.Dataset:
    """
    Rebins variables from an AUX_MET_1D (XMET) dataset onto the vertical curtain track of given by another dataset (e.g. ATL_EBD_2A).

    This function interpolates selected variables from `ds_xmet` onto a EarthCARE
    vertical track given in `ds_vert`, using quick horizontal kd-tree nearest-neighbor search with `scipy.spatial.cKDTree` followed
    by averaging the `k`-nearest vertical XMET profiles using inverse distance weighting. The resulting
    profiles are then interpolated in the vertical to match the height resolution of `ds_vert`.

    Args:
        ds_xmet (xr.Dataset): The source XMET dataset from which vertical curtain along track will be interpolated.
        ds_vert (xr.Dataset): The target dataset containing the vertical curtain track.
        vars (list[str] | None, optional): List of variable names from `ds_xmet` to rebin.
            If None, all data variables are considered.
        k (int, optional): Number of nearest horizontal neighbors to include in the kd-tree search.
            Defaults to 4.
        eps (float, optional): Numerical threshold to avoid division by zero in distance calculations during the kd-tree search.
            Defaults to 1e-12.
        lat_var (str, optional): Name of the latitude variable in `ds_vert`.
            Defaults to TRACK_LAT_VAR.
        lon_var (str, optional): Name of the longitude variable in `ds_vert`.
            Defaults to TRACK_LON_VAR.
        time_var (str, optional): Name of the time variable in `ds_vert`.
            Defaults to TIME_VAR.
        height_var (str, optional): Name of the height variable in `ds_vert`.
            Defaults to HEIGHT_VAR.
        along_track_dim (str, optional): Name of the along-track dimension in `ds_vert`.
            Defaults to ALONG_TRACK_DIM.
        height_dim (str, optional): Name of the vertical or height dimension in `ds_vert`.
            Defaults to VERTICAL_DIM.
        xmet_lat_var (str, optional): Name of the latitude variable in `ds_xmet`.
            Defaults to "latitude".
        xmet_lon_var (str, optional): Name of the longitude variable in `ds_xmet`.
            Defaults to "longitude".
        xmet_height_var (str, optional): Name of the height variable in `ds_xmet`.
            Defaults to "geometrical_height".
        xmet_height_dim (str, optional): Name of the vertical dimension in `ds_xmet`.
            Defaults to "height".
        xmet_horizontal_grid_dim (str, optional): Name of the horizontal grid dimension in `ds_xmet`.
            Defaults to "horizontal_grid".

    Returns:
        xr.Dataset: A new dataset containing the selected XMET variables interpolated to the grid of the
            vertical curtain given in `ds_vert`. This new dataset has the same along-track and vertical
            dimensions as `ds_vert`.

    Raises:
        KeyError: If any specified variable or coordinate name is not found in `ds_xmet`.
    """
    if vars is None:
        vars = [str(v) for v in ds_xmet.variables]
    else:
        for var in vars:
            if var not in ds_xmet.variables:
                present_vars = [str(v) for v in ds_xmet.variables]
                raise KeyError(
                    f"""X-MET dataset does not contain variable "{var}". Present variables are: {", ".join(present_vars)}"""
                )

    new_ds_xmet = ds_xmet.copy().swap_dims({xmet_height_dim: "tmp_xmet_height"})
    new_ds_xmet[time_var] = ds_vert[time_var].copy()
    new_ds_xmet[height_var] = ds_vert[height_var].copy()

    hgrid_lat = ds_xmet[xmet_lat_var].values.flatten()
    hgrid_lon = ds_xmet[xmet_lon_var].values.flatten()
    hgrid_alt = ds_xmet[xmet_height_var].values
    hgrid_coords = sequence_geo_to_ecef(hgrid_lat, hgrid_lon)

    track_lat = ds_vert[lat_var].values
    track_lon = ds_vert[lon_var].values
    track_alt = ds_vert[height_var].values
    track_coords = sequence_geo_to_ecef(track_lat, track_lon)

    tree = cKDTree(hgrid_coords)
    dists, idxs = tree.query(track_coords, k=k)

    # Inverse distance weighting
    if k > 1:
        weights = 1.0 / (dists + eps)
        weights /= np.sum(weights, axis=1, keepdims=True)
        height = np.einsum("ij,ijh->ih", weights, hgrid_alt[idxs])
    else:
        weights = np.ones(idxs.shape)
        height = hgrid_alt[idxs]

    dims: str | tuple[str, str]
    for var in vars:
        values = ds_xmet[var].values
        if len(values.shape) == 0:
            continue

        if len(values.shape) == 1:
            dims = along_track_dim

            if k > 1:
                result = np.sum(values[idxs] * weights, axis=1)
                new_values = result
            else:
                new_values = values[idxs]
        else:
            dims = (along_track_dim, height_dim)

            if k > 1:
                result = np.einsum("ij,ijh->ih", weights, values[idxs])
            else:
                result = values[idxs]

            new_values = np.empty(track_alt.shape)
            new_values[:] = np.nan

            for i in np.arange(track_alt.shape[0]):
                _new_values = np.interp(
                    track_alt[i],
                    height[i],
                    result[i],
                )
                # _new_values = interp(track_alt[i])

                # Fill nans
                # _new_values[np.isnan(_new_values) & (track_alt[i] < height[i, 0])] = result[i, 0]
                # _new_values[np.isnan(_new_values) & (track_alt[i] > height[i, -1])] = result[i, -1]

                new_values[i] = _new_values

        new_var = f"{var}"
        new_ds_xmet[new_var] = (dims, new_values)
        new_ds_xmet[new_var].attrs = new_ds_xmet[var].attrs

    new_ds_xmet = remove_dims(new_ds_xmet, [xmet_horizontal_grid_dim, xmet_height_dim])

    return new_ds_xmet


def read_product_xmet(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
) -> xr.Dataset:
    """Opens AUX_MET_1D file as a `xarray.Dataset`."""
    ds = read_science_data(filepath, agency=FileAgency.ESA)

    if not modify:
        return ds

    ds = rename_common_dims_and_vars(
        ds=ds,
        tropopause_var="tropopause_height_calipso",
        temperature_var="temperature",
    )

    ds = add_header_and_meta_data(filepath=filepath, ds=ds, header=header, meta=meta)

    return ds
