import numpy as np
import xarray as xr
from numpy.typing import NDArray
from scipy.spatial import cKDTree  # type: ignore

from ...constants import (
    ALONG_TRACK_DIM,
    HEIGHT_VAR,
    TIME_VAR,
    TRACK_LAT_VAR,
    TRACK_LON_VAR,
    VERTICAL_DIM,
)
from ...geo import sequence_ecef_to_geo, sequence_geo_to_ecef
from ...utils.xarray import remove_dims
from ._generic import read_product


def _grid_along_track(
    hgrid_coords: NDArray,
    target_coords: NDArray,
    hgrid_alt: NDArray,
    k: int = 4,
    eps: float = 1e-12,
) -> tuple[NDArray, NDArray, NDArray]:
    tree = cKDTree(hgrid_coords)
    dists, idxs = tree.query(target_coords, k=k)

    # Inverse distance weighting
    if k > 1:
        weights = 1.0 / (dists + eps)
        weights /= np.sum(weights, axis=1, keepdims=True)
        track_gridded_alt = np.einsum("ij,ijh->ih", weights, hgrid_alt[idxs])
    else:
        weights = np.ones(idxs.shape)
        track_gridded_alt = hgrid_alt[idxs]

    return idxs, weights, track_gridded_alt


def _interp_values_along_track_1d(
    kdtree_idxs: NDArray,
    kdtree_weights: NDArray,
    hgrid_values: NDArray,
    k: int = 4,
) -> NDArray:
    if k > 1:
        return np.sum(hgrid_values[kdtree_idxs] * kdtree_weights, axis=1)
    return hgrid_values[kdtree_idxs]


def _interp_values_along_track_2d(
    kdtree_idxs: NDArray,
    kdtree_weights: NDArray,
    target_gridded_alt: NDArray,
    target_alt: NDArray,
    hgrid_values: NDArray,
    k: int = 4,
) -> NDArray:
    if k > 1:
        target_gridded_values = np.einsum("ij,ijh->ih", kdtree_weights, hgrid_values[kdtree_idxs])
    else:
        target_gridded_values = hgrid_values[kdtree_idxs]

    new_values = np.empty(target_alt.shape)
    new_values[:] = np.nan

    for i in np.arange(target_alt.shape[0]):
        _new_values = np.interp(
            target_alt[i],
            target_gridded_alt[i],
            target_gridded_values[i],
        )

        new_values[i] = _new_values
    return new_values


def rebin_xmet_to_vertical_track(
    ds_xmet: xr.Dataset | str,
    ds_vert: xr.Dataset | str,
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
    """Rebins AUX_MET_1D (XMET) variables onto the vertical curtain track of another dataset.

    Interpolates selected variables from `ds_xmet` to `ds_vert`'s vertical track using kd-tree nearest-neighbor
    search with inverse distance weighting of `k` horizontal neighbors, followed by vertical interpolation.

    Args:
        ds_xmet: Source XMET dataset.
        ds_vert: Target dataset defining the vertical curtain track (e.g., ATL_EBD_2A).
        vars: Variables to rebin; uses all if None.
        k: Number of nearest horizontal neighbors for interpolation; defaults to 4.
        eps: Numerical threshold to avoid division by zero; defaults to 1e-12.
        lat_var: Latitude variable name in `ds_vert`.
        lon_var: Longitude variable name in `ds_vert`.
        time_var: Time variable name in `ds_vert`.
        height_var: Height variable name in `ds_vert`.
        along_track_dim: Along-track dimension name in `ds_vert`.
        height_dim: Vertical dimension name in `ds_vert`.
        xmet_lat_var: Latitude variable name in `ds_xmet`.
        xmet_lon_var: Longitude variable name in `ds_xmet`.
        xmet_height_var: Height variable name in `ds_xmet`.
        xmet_height_dim: Vertical dimension name in `ds_xmet`.
        xmet_horizontal_grid_dim: Horizontal grid dimension name in `ds_xmet`.

    Returns:
        A new dataset with XMET variables interpolated to `ds_vert`'s vertical track.

    Raises:
        KeyError: If any specified variable or coordinate is missing in `ds_xmet`.
    """
    # Return given dataset, if nadir cross-section has already been extracted from it.
    if (
        isinstance(ds_xmet, xr.Dataset)
        and along_track_dim in ds_xmet.sizes
        and height_dim in ds_xmet.sizes
    ):
        return ds_xmet

    def _read_xmet() -> xr.Dataset:
        if isinstance(ds_xmet, str):
            return read_product(ds_xmet)
        return ds_xmet

    def _read_vert() -> xr.Dataset:
        if isinstance(ds_vert, str):
            return read_product(ds_vert)
        return ds_vert

    with (
        _read_xmet() as ds_xmet,
        _read_vert() as ds_vert,
    ):
        if vars is None:
            vars = [str(v) for v in ds_xmet.variables]
        else:
            for var in vars:
                if var not in ds_xmet.variables:
                    present_vars = [str(v) for v in ds_xmet.variables]
                    raise KeyError(
                        f"""X-MET dataset does not contain variable "{var}". Present variables are: {", ".join(present_vars)}"""
                    )

        if xmet_height_dim in ds_xmet.sizes:
            new_ds_xmet = ds_xmet.copy().swap_dims({xmet_height_dim: "tmp_xmet_height"})
        elif VERTICAL_DIM in ds_xmet.sizes:
            new_ds_xmet = ds_xmet.copy().swap_dims({VERTICAL_DIM: "tmp_xmet_height"})
        else:
            raise ValueError(
                f"no dimension named '{xmet_height_dim}' or '{VERTICAL_DIM}' in X-MET dataset ({ds_xmet.sizes})"
            )
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

        idxs, weights, height = _grid_along_track(
            hgrid_coords=hgrid_coords,
            target_coords=track_coords,
            hgrid_alt=hgrid_alt,
            k=k,
            eps=eps,
        )

        # Handle longitudes separately to account for sign changes at the dateline
        if xmet_lon_var in vars:
            vars.remove(xmet_lon_var)

        new_coords = _interp_values_along_track_1d(
            kdtree_idxs=idxs,
            kdtree_weights=weights.reshape((*weights.shape, 1)),
            hgrid_values=hgrid_coords,
            k=k,
        )

        new_lons = sequence_ecef_to_geo(
            x=new_coords[:, 0],
            y=new_coords[:, 1],
            z=new_coords[:, 2],
        )[:, 1]

        new_ds_xmet[xmet_lon_var] = xr.DataArray(
            data=new_lons,
            dims=along_track_dim,
            attrs=new_ds_xmet[xmet_lon_var].attrs,
        )

        # Handle all remaining variables
        dims: str | tuple[str, str]
        for var in vars:
            values = ds_xmet[var].values
            if len(values.shape) == 0:
                continue

            if len(values.shape) == 1:
                dims = along_track_dim

                new_values = _interp_values_along_track_1d(
                    kdtree_idxs=idxs,
                    kdtree_weights=weights,
                    hgrid_values=values,
                    k=k,
                )
            else:
                dims = (along_track_dim, height_dim)

                new_values = _interp_values_along_track_2d(
                    kdtree_idxs=idxs,
                    kdtree_weights=weights,
                    target_gridded_alt=height,
                    target_alt=track_alt,
                    hgrid_values=values,
                    k=k,
                )

            new_var = f"{var}"
            new_ds_xmet[new_var] = (dims, new_values)
            new_ds_xmet[new_var].attrs = ds_xmet[var].attrs

        # Remove original horizontal grid dims and associated variables
        new_ds_xmet = remove_dims(new_ds_xmet, [xmet_horizontal_grid_dim, xmet_height_dim])

        return new_ds_xmet
