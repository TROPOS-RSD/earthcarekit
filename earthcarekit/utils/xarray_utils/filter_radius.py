from typing import Literal

import numpy as np
import xarray as xr
from numpy.typing import NDArray

from ..constants import ALONG_TRACK_DIM, TRACK_LAT_VAR, TRACK_LON_VAR
from ..geo import haversine
from ..geo import vincenty as geodesic
from ..geo.coordinates import get_coords
from ..ground_sites import GroundSite, get_ground_site
from ..np_array_utils import pad_true_sequence
from .exception import EmptyFilterResultError


def filter_radius(
    ds: xr.Dataset,
    # *,
    radius_km: float,
    center_lat: float | None = None,
    center_lon: float | None = None,
    site: GroundSite | str | None = None,
    lat_var: str = TRACK_LAT_VAR,
    lon_var: str = TRACK_LON_VAR,
    along_track_dim: str = ALONG_TRACK_DIM,
    method: Literal["geodesic", "haversine"] = "geodesic",
    closest: bool = False,
    pad_idxs: int = 0,
) -> xr.Dataset:
    """
    Filters a dataset to include only points within a specified radius of a geographic location.

    Args:
        ds (xr.Dataset): Input dataset with geolocation data.
        radius_km (float): Radius (in kilometers) around the center location.
        site (GroundSite or str, optional): GroundSite object or name from which center location will be retrieved,
            alternatively `center_lat` and `center_lon` must be set.
        center_lat (float, optional): Latitude of the center point,
            alternatively `site` must be set.
        center_lon (float, optional): Longitude of the center point,
            alternatively `site` must be set.
        lat_var (str, optional): Name of the latitude variable. Defaults to TRACK_LAT_VAR.
        lon_var (str, optional): Name of the longitude variable. Defaults to TRACK_LON_VAR.
        along_track_dim (str, optional): Dimension along which to apply filtering. Defaults to ALONG_TRACK_DIM.
        method (Literal["geodesic", "haversine"], optional): Distance calculation method. Defaults to "geodesic".
        closest (bool, optional): If true only the single closest profile is returned, otherwise all profiles within radius. Defaults to False.

    Returns:
        xr.Dataset: Filtered dataset containing only points within the specified radius.

    Raises:
        EmptyFilterResultError: If no data points are found within the radius.
        ValueError: If the `method` is invalid.
    """
    _center_lat: float
    _center_lon: float

    if isinstance(site, str):
        site = get_ground_site(site)

    if isinstance(site, GroundSite):
        _center_lat = site.latitude
        _center_lon = site.longitude
    elif isinstance(center_lat, (int, float, np.integer, np.floating)) and isinstance(
        center_lon, (int, float, np.integer, np.floating)
    ):
        _center_lat = float(center_lat)
        _center_lon = float(center_lon)
    else:
        raise ValueError(
            f"Either 'site' or 'center_lat' and 'center_lon' must be given."
        )

    if method not in ["geodesic", "haversine"]:
        raise ValueError(
            r'Invalid method choosen. Available methods: {"geodesic", "haversine"}'
        )

    satellite_coords = get_coords(ds, lat_var=lat_var, lon_var=lon_var)

    center_coords = (_center_lat, _center_lon)

    if method == "geodesic":
        distances = geodesic(center_coords, satellite_coords)
    else:
        distances = haversine(center_coords, satellite_coords)

    mask = np.array(distances < radius_km)

    if closest:
        closest_distance = np.min(distances)
        closest_filtered_index = int(np.argmin(np.abs(distances - closest_distance)))
        mask[:] = False
        mask[closest_filtered_index] = True

    mask = pad_true_sequence(mask, pad_idxs)

    da_mask = xr.DataArray(data=mask, dims=[along_track_dim])
    if np.sum(da_mask.values) < 1:
        raise EmptyFilterResultError(
            f"Could not find valid overpass for given inputs. Data lies outside the given {radius_km} km radius around ({center_lat} degN {center_lon} degE).",
            min_distance=float(np.min(distances)),
        )

    ds = ds.where(da_mask, drop=True)

    return ds
