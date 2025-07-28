import numpy as np
import xarray as xr

from ..constants import (
    ACROSS_TRACK_DIM,
    ACROSS_TRACK_DISTANCE,
    FROM_TRACK_DISTANCE,
    SWATH_LAT_VAR,
    SWATH_LON_VAR,
    TRACK_LAT_VAR,
    TRACK_LON_VAR,
)
from ..geo import geodesic


def add_across_track_distance(
    ds: xr.Dataset,
    nadir_idx: int,
    swath_lat_var: str,
    swath_lon_var: str,
    across_track_distance_var: str = ACROSS_TRACK_DISTANCE,
    from_track_distance_var: str = FROM_TRACK_DISTANCE,
    across_track_dim: str = "across_track",
) -> xr.Dataset:
    """Extends EarthCARE dataset containing an across-track dimension by variable containing distance from nadir."""
    # Add across-track distance variable
    last_coords = np.vstack(
        (ds[swath_lat_var].values[:, -1], ds[swath_lon_var].values[:, -1])
    ).T
    nadir_coords = np.vstack(
        (ds[swath_lat_var].values[:, nadir_idx], ds[swath_lon_var].values[:, nadir_idx])
    ).T
    across_track_distances = np.array([], dtype=np.float32)
    from_track_distances = np.array([], dtype=np.float32)
    for i in range(0, ds[swath_lat_var].values.shape[1]):
        sign = 1 if i < nadir_idx else -1
        across_track_coords = np.vstack(
            (ds[swath_lat_var].values[:, i], ds[swath_lon_var].values[:, i])
        ).T

        _dists = geodesic(last_coords, across_track_coords, units="m")
        _mean_dists = np.mean(np.atleast_1d(_dists))
        across_track_distances = np.append(across_track_distances, _mean_dists)

        _dists = geodesic(nadir_coords, across_track_coords, units="m")
        _mean_dists = np.mean(np.atleast_1d(_dists)) * sign
        from_track_distances = np.append(from_track_distances, _mean_dists)

    ds[across_track_distance_var] = ((across_track_dim), across_track_distances)
    ds[across_track_distance_var] = ds[across_track_distance_var].assign_attrs(
        units="m", name="Distance", long_name="Distance"
    )

    ds[from_track_distance_var] = ((across_track_dim), from_track_distances)
    ds[from_track_distance_var] = ds[from_track_distance_var].assign_attrs(
        units="m", name="Distance from track", long_name="Distance from track"
    )
    # indices = np.arange(len(distances))
    # distances = np.interp(
    #     indices, indices[~np.isnan(distances)], distances[~np.isnan(distances)]
    # )
    # ds[across_track_distance_var].values = distances

    return ds


def add_nadir_track(
    ds: xr.Dataset,
    nadir_idx: int,
    swath_lat_var: str,
    swath_lon_var: str,
    along_track_dim: str,
    across_track_dim: str,
    nadir_lat_var: str = TRACK_LAT_VAR,
    nadir_lon_var: str = TRACK_LON_VAR,
) -> xr.Dataset:
    """Extends EarthCARE dataset containing an across-track dimension by nadir selected lat/lon variables."""

    if swath_lat_var == nadir_lat_var:
        raise ValueError(
            f"Track latitude and swath latitude variables must be different (lat_var={swath_lat_var}, nadir_lat_var={nadir_lat_var})"
        )

    if swath_lon_var == nadir_lon_var:
        raise ValueError(
            f"Track longitude and swath longitude variables must be different (lon_var={swath_lon_var}, nadir_lon_var={nadir_lon_var})"
        )

    # Drop all samples with missing geo location
    valid_across_track = ds[swath_lat_var].notnull().all(dim=along_track_dim)
    ds = ds.isel({across_track_dim: valid_across_track.values})

    # Add nadir track as lat/lon variables
    across_track_nadir_selection = {across_track_dim: nadir_idx}
    ds = ds.assign(
        {
            nadir_lat_var: ds[swath_lat_var].isel(across_track_nadir_selection),
            nadir_lon_var: ds[swath_lon_var].isel(across_track_nadir_selection),
        }
    )
    ds[nadir_lat_var] = ds[nadir_lat_var].assign_attrs(
        units="degree_north", notes="[-90:90]", long_name="Latitude"
    )
    ds[nadir_lon_var] = ds[nadir_lon_var].assign_attrs(
        units="degree_east", notes="[-180:180]", long_name="Longitude"
    )

    return ds


def add_nadir_var(
    ds: xr.Dataset,
    var: str,
    nadir_idx: int | None = None,
    new_var: str | None = None,
    across_track_dim: str = ACROSS_TRACK_DIM,
    units: str | None = None,
    notes: str | None = None,
    long_name: str | None = None,
) -> xr.Dataset:
    if not isinstance(new_var, str):
        new_var = f"{var}_track"

    if not isinstance(nadir_idx, int):
        nadir_idx = get_nadir_index(ds)

    if not isinstance(units, str) and hasattr(ds[var], "units"):
        units = ds[var].units

    if not isinstance(notes, str) and hasattr(ds[var], "notes"):
        notes = ds[var].notes

    if not isinstance(long_name, str) and hasattr(ds[var], "long_name"):
        long_name = ds[var].long_name

    # Add nadir track as lat/lon variables
    across_track_nadir_selection = {across_track_dim: nadir_idx}
    ds = ds.assign(
        {
            new_var: ds[var].isel(across_track_nadir_selection),
        }
    )
    ds[new_var] = ds[new_var].assign_attrs(
        units=units, notes=notes, long_name=long_name
    )

    return ds


def get_nadir_index(
    ds: xr.Dataset,
    nadir_idx: int | None = None,
    sensor_elevation_angle_var: str = "sensor_elevation_angle",
    across_track_dim: str = "across_track",
) -> int:
    """
    Gets the Nadir index in the across-track dimension debending on optional parameters given.

    Parameters:
        ds (xarray.Dataset):
            A EarthCARE dataset containing a along-track dimension.
        nadir_idx (int | None, optional):
            If given, the same index is returned. Defaults to None.
        sensor_elevation_angle_var (str, optional):
            The name in the dataset's sensor elevation angle variable. Defaults to 'sensor_elevation_angle'. Defaults to 'sensor_elevation_angle'.
        across_track_dim (str, optional):
            The name of the dataset's across-track dimension. Defaults to 'across_track'.

    Returns:
        nadir_index (int):
            The across-track index position of Nadir.
    """
    if nadir_idx is not None:
        return nadir_idx
    elif sensor_elevation_angle_var in ds.variables:
        return int(
            np.median(np.nanargmax(ds[sensor_elevation_angle_var].values, axis=1))
        )
    elif SWATH_LON_VAR in ds.variables and TRACK_LON_VAR in ds.variables:
        return int(
            np.nanargmin(
                np.abs(ds[SWATH_LON_VAR].values[0] - ds[TRACK_LON_VAR].values[0])
            )
        )
    return int(np.nanargmin(np.abs(ds[across_track_dim].values)))
