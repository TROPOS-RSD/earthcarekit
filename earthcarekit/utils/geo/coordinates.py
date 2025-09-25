import numpy as np
import xarray as xr
from numpy.typing import ArrayLike, NDArray

from ..constants import TRACK_LAT_VAR, TRACK_LON_VAR
from ..np_array_utils import flatten_array


def get_coords(
    ds: xr.Dataset,
    *,
    lat_var: str = TRACK_LAT_VAR,
    lon_var: str = TRACK_LON_VAR,
    flatten: bool = False,
) -> NDArray:
    """Takes a `xarray.Dataset` and returns the lat/lon coordinates as a numpy array.

    Args:
        lat_var (str, optional): Name of the latitude variable. Defaults to TRACK_LAT_VAR.
        lon_var (str, optional): Name of the longitude variable. Defaults to TRACK_LON_VAR.
        flatten (bool, optional):
            If True, the coordinates will be flattened to a 2D array

            - 1st dimension: time
            - 2nd dimension: lat/lon

    Returns:
        numpy.array: The extracted lat/lon coordinates.
    """
    lat = ds[lat_var].values
    lon = ds[lon_var].values
    coords = np.stack((lat, lon)).transpose()

    if len(coords.shape) > 2 and flatten:
        coords = coords.reshape(-1, 2)
    return coords


def get_central_coords(
    latitude: ArrayLike,
    longitude: ArrayLike,
) -> tuple[float, float]:
    """Calculates the central lat/lon coordinates."""
    from .convertsions import ecef_to_geo, geo_to_ecef

    lats: NDArray = flatten_array(latitude)
    lons: NDArray = flatten_array(longitude)

    coords_ecef = np.array([geo_to_ecef(lat=lt, lon=ln) for lt, ln in zip(lats, lons)])
    coords_ecef_min = np.nanmin(coords_ecef, axis=0)
    coords_ecef_max = np.nanmax(coords_ecef, axis=0)
    coords_ecef_central = (coords_ecef_min + coords_ecef_max) * 0.5
    coords_geo_central = ecef_to_geo(
        coords_ecef_central[0], coords_ecef_central[1], coords_ecef_central[2]
    )
    return (coords_geo_central[0], coords_geo_central[1])


def get_central_latitude(
    latitude: ArrayLike,
) -> float:
    """Calculates the central latitude coordinate."""
    lats: NDArray = flatten_array(latitude)
    lons: NDArray = np.zeros(lats.shape)

    central_coords = get_central_coords(lats, lons)

    return central_coords[0]


def get_central_longitude(
    longitude: ArrayLike,
) -> float:
    """Calculates the central longitude coordinate."""
    lons: NDArray = flatten_array(longitude)
    lats: NDArray = np.zeros(lons.shape)

    central_coords = get_central_coords(lats, lons)

    return central_coords[1]
