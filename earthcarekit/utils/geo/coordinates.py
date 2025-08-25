import numpy as np
import xarray as xr
from numpy.typing import NDArray

from ..constants import TRACK_LAT_VAR, TRACK_LON_VAR


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
    lat = ds[lat_var]
    lon = ds[lon_var]
    coords = np.stack((lat, lon)).transpose()

    if len(coords.shape) > 2 and flatten:
        coords = coords.reshape(-1, 2)
    return coords
