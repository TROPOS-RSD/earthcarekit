from typing import Final

import numpy as np
import xarray as xr
from scipy.spatial import cKDTree  # type: ignore

from ...constants import (
    ACROSS_TRACK_DIM,
    ALONG_TRACK_DIM,
    SWATH_LAT_VAR,
    SWATH_LON_VAR,
    TIME_VAR,
)
from ...geo import sequence_geo_to_ecef
from ._generic import read_product

_SKIP_VARS: Final[list[str]] = [
    "filename",
    "file_type",
    "frame_id",
    "orbit_number",
    "orbit_and_frame",
    "baseline",
    "sensing_start_time",
    "processing_start_time",
]


def rebin_msi_to_jsg(
    ds_msi: xr.Dataset | str,
    ds_xjsg: xr.Dataset | str,
    vars: list[str] | None = None,
    k: int = 4,
    eps: float = 1e-12,
    lat_var: str = SWATH_LAT_VAR,
    lon_var: str = SWATH_LON_VAR,
    time_var: str = TIME_VAR,
    along_track_dim: str = ALONG_TRACK_DIM,
    across_track_dim: str = ACROSS_TRACK_DIM,
    lat_var_xjsg: str = SWATH_LAT_VAR,
    lon_var_xjsg: str = SWATH_LON_VAR,
    time_var_xjsg: str = TIME_VAR,
    along_track_dim_xjsg: str = ALONG_TRACK_DIM,
    across_track_dim_xjsg: str = ACROSS_TRACK_DIM,
) -> xr.Dataset:
    """
    Rebins variables from an MSI product dataset onto the geo-spacial lat/lon grid given by the related AUX_JSG_1D dataset.

    This function interpolates selected variables from `ds_msi` onto the JSG grid from `ds_xjsg`
    using quick kd-tree nearest-neighbor search with `scipy.spatial.cKDTree` followed
    by averaging the `k`-nearest points using inverse distance weighting. The resulting dataframe
    matches the along- and across-track resolution of `ds_xjsg`.

    Args:
        ds_msi (xr.Dataset | str): The source MSI dataset (e.g., MSI_RGR_1C, MSI_COP_2A, ...).
        ds_xjsg (xr.Dataset | str): The target XJSG dataset.
        vars (list[str] | None, optional): List of variable names from `ds_msi` to rebin.
            If None, all data variables are considered. Defaults to None.
        k (int, optional): Number of nearest geo-spacial neighbors to include in the kd-tree search.
            Defaults to 4.
        eps (float, optional): Numerical threshold to avoid division by zero in distance calculations during the kd-tree search.
            Defaults to 1e-12.

    Returns:
        xr.Dataset: The MSI dataset with variables rebinned to the JSG grid.
    """

    def _read_msi() -> xr.Dataset:
        if isinstance(ds_msi, str):
            return read_product(ds_msi)
        return ds_msi

    def _read_xjsg() -> xr.Dataset:
        if isinstance(ds_xjsg, str):
            return read_product(ds_xjsg)
        return ds_xjsg

    with (
        _read_msi() as ds_msi,
        _read_xjsg() as ds_xjsg,
    ):
        if vars is None:
            vars = [str(v) for v in ds_msi.variables]
        else:
            for var in vars:
                if var not in ds_msi.variables:
                    present_vars = [str(v) for v in ds_msi.variables]
                    raise KeyError(
                        f"""X-MET dataset does not contain variable "{var}". Present variables are: {", ".join(present_vars)}"""
                    )

        ds_xjsg = ds_xjsg.copy().swap_dims(
            {
                along_track_dim_xjsg: along_track_dim,
                across_track_dim_xjsg: across_track_dim,
            }
        )

        new_ds_msi = ds_msi.copy().swap_dims(
            {
                along_track_dim: f"{along_track_dim}_original",
                across_track_dim: f"{across_track_dim}_original",
            }
        )
        new_ds_msi[time_var] = ds_xjsg[time_var_xjsg].copy()

        lat_msi = ds_msi[lat_var].values.flatten()
        lon_msi = ds_msi[lon_var].values.flatten()
        coords_msi = sequence_geo_to_ecef(lat_msi, lon_msi)

        lat_jsg = ds_xjsg[lat_var_xjsg].values.flatten()
        lon_jsg = ds_xjsg[lon_var_xjsg].values.flatten()
        coords_jsg = sequence_geo_to_ecef(lat_jsg, lon_jsg)

        tree = cKDTree(coords_msi)
        dists, idxs = tree.query(coords_jsg, k=k)

        dims: str | tuple[str, str]
        for var in vars:
            if ds_msi[var].dims == (along_track_dim, across_track_dim):
                dims = (along_track_dim, across_track_dim)

                values = ds_msi[var].values
                values_flat = values.flatten()

                mask_nan = np.isnan(values_flat[idxs])

                _dists = dists
                _dists[mask_nan] = np.inf

                # Inverse distance weighting
                if k > 1:
                    weights = 1.0 / (_dists + eps)
                    weights /= np.sum(weights, axis=1, keepdims=True)
                else:
                    weights = np.ones(idxs.shape)

                if k > 1:
                    _v = values_flat[idxs]

                    if np.issubdtype(_v.dtype, np.floating):
                        m = np.all(np.isnan(_v), axis=1)
                        _v[np.isnan(_v)] = 0.0
                        _v[m] = np.nan

                    result = np.sum(_v * weights, axis=1)

                    new_values = result
                else:
                    new_values = values_flat[idxs]

                new_values = new_values.reshape(ds_xjsg.latitude_swath.shape)

                new_var = f"{var}"
                new_ds_msi[new_var] = (dims, new_values)
                new_ds_msi[new_var].attrs = ds_msi[var].attrs
            elif var not in _SKIP_VARS and var in ds_msi and var in ds_xjsg:
                new_ds_msi[var] = ds_xjsg[var].copy()
                new_ds_msi[var].attrs = ds_xjsg[var].attrs
            else:
                continue

        return new_ds_msi
