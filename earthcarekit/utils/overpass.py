import logging

logger: logging.Logger = logging.getLogger(__name__)

from dataclasses import dataclass
from typing import Any, Literal, overload

import numpy as np
import pandas as pd
import xarray as xr
from numpy.typing import NDArray

from .config import read_config
from .constants import ALONG_TRACK_DIM, TIME_VAR, TRACK_LAT_VAR, TRACK_LON_VAR
from .geo import geodesic, get_coords, get_cumulative_distances
from .geo.string_formatting import format_coords
from .ground_sites import GroundSite, get_ground_site
from .np_array_utils import ismonotonic
from .read import read_product, search_product
from .time import TimestampLike, to_timestamp
from .typing import LatLonCoordsLike, validate_numeric_pair
from .xarray_utils import EmptyFilterResultError, filter_radius


@dataclass
class OverpassInfo:
    site_name: str
    site_lat_deg_north: float
    site_lon_deg_east: float
    site_radius_km: float
    start_index: int
    end_index: int
    start_time: pd.Timestamp
    end_time: pd.Timestamp
    start_lat_deg_north: float
    start_lon_deg_east: float
    end_lat_deg_north: float
    end_lon_deg_east: float
    closest_index: int
    closest_lat_deg_north: float
    closest_lon_deg_east: float
    closest_time: pd.Timestamp
    closest_distance_km: float
    along_track_distance_km: float
    frame_crosses_pole: bool
    samples: int
    site: GroundSite

    @property
    def site_coords(self) -> tuple[float, float]:
        """Returns lat/lon coordinates of the overpassed site or center."""
        return self.site_lat_deg_north, self.site_lon_deg_east

    @property
    def index_range(self) -> tuple[int, int]:
        """Returns start and end indecies of the overpass."""
        return self.start_index, self.end_index

    @property
    def time_range(self) -> tuple[pd.Timestamp, pd.Timestamp]:
        """Returns start and end times of the overpass."""
        return self.start_time, self.end_time

    @property
    def start_coords(self) -> tuple[float, float]:
        """Returns lat/lon coordinates of the satellite at the start of the overpass."""
        return self.start_lat_deg_north, self.start_lon_deg_east

    @property
    def end_coords(self) -> tuple[float, float]:
        """Returns lat/lon coordinates of the satellite at the end of the overpass."""
        return self.end_lat_deg_north, self.end_lon_deg_east

    @property
    def closest_coords(self) -> tuple[float, float]:
        """Returns lat/lon coordinates of the satellite at the end of the overpass."""
        return self.closest_lat_deg_north, self.closest_lon_deg_east

    @property
    def duration(self) -> pd.Timedelta:
        return self.end_time - self.start_time


def get_closest_distance(
    ds: xr.Dataset,
    *,
    site_lat: float | int | None = None,
    site_lon: float | int | None = None,
    site_name: str | None = None,
    lat_var: str = TRACK_LAT_VAR,
    lon_var: str = TRACK_LON_VAR,
) -> float:
    if not isinstance(site_name, str) and not (
        isinstance(site_lat, (float, int)),
        isinstance(site_lon, (float, int)),
    ):
        raise TypeError(
            f"Missing arguments. At least either `site_name` or `site_lat` and `site_lon` must be given."
        )

    if isinstance(site_name, str):
        site = get_ground_site(site_name)
        if not isinstance(site_lat, (float, int)):
            site_lat = site.latitude
        if not isinstance(site_lon, (float, int)):
            site_lon = site.longitude

    assert isinstance(site_lat, (float, int))
    assert isinstance(site_lon, (float, int))

    site_lat = float(site_lat)
    site_lon = float(site_lon)
    site_coords = (site_lat, site_lon)

    # Closest sample
    along_track_coords = get_coords(ds, lat_var=lat_var, lon_var=lon_var)
    distances = geodesic(along_track_coords, site_coords, units="km")
    closest_distance = float(np.min(distances))

    return closest_distance


def _get_overpass_info(
    ds: xr.Dataset,
    site_radius_km: float | int,
    site: GroundSite | str,
    *,
    time_var: str = TIME_VAR,
    lat_var: str = TRACK_LAT_VAR,
    lon_var: str = TRACK_LON_VAR,
    along_track_dim: str = ALONG_TRACK_DIM,
) -> OverpassInfo:
    _site: GroundSite
    if isinstance(site, str):
        _site = get_ground_site(site)
    elif isinstance(site, GroundSite):
        _site = site
    else:
        raise TypeError(
            f"invalid type '{type(site).__name__}' for site, expected type 'GroundSite' or 'str'"
        )

    site_name: str | None = _site.long_name

    site_lat = _site.latitude
    site_lon = _site.longitude

    assert isinstance(site_lat, (float, int))
    assert isinstance(site_lon, (float, int))

    site_lat = float(site_lat)
    site_lon = float(site_lon)
    site_coords = (site_lat, site_lon)

    try:
        ds_filtered = filter_radius(
            ds,
            radius_km=site_radius_km,
            site=site,
            lat_var=lat_var,
            lon_var=lon_var,
            along_track_dim=along_track_dim,
        )
    except EmptyFilterResultError as e:
        raise ValueError(
            f"This is not a valid overpass. Track does not overlap radius area."
        )

    # Times
    original_time = ds[time_var].values
    time = ds_filtered[time_var].values
    start_time = time[0]
    end_time = time[-1]

    assert start_time <= end_time

    # Duration
    duration = to_timestamp(end_time) - to_timestamp(start_time)

    assert duration >= pd.Timedelta(0)

    # Indexes
    start_index = np.argmin(np.abs(original_time - start_time))
    end_index = np.argmin(np.abs(original_time - end_time))

    assert start_index <= end_index

    # Latitudes
    original_lat = ds[lat_var].values
    lat = ds_filtered[lat_var].values
    start_lat = lat[0]
    end_lat = lat[-1]

    assert start_lat == original_lat[start_index]
    assert end_lat == original_lat[end_index]

    # Longitudes
    original_lon = ds[lon_var].values
    lon = ds_filtered[lon_var].values
    start_lon = lon[0]
    end_lon = lon[-1]

    assert start_lon == original_lon[start_index]
    assert end_lon == original_lon[end_index]

    # Closest sample
    along_track_coords = get_coords(ds_filtered, lat_var=lat_var, lon_var=lon_var)
    distances = geodesic(along_track_coords, site_coords, units="km")
    closest_distance = np.min(distances)
    closest_filtered_index = np.argmin(np.abs(distances - closest_distance))
    closest_time = time[closest_filtered_index]
    closest_index = np.argmin(np.abs(original_time - closest_time))
    closest_lat = lat[closest_filtered_index]
    closest_lon = lat[closest_filtered_index]
    along_track_distance = get_cumulative_distances(lat, lon, units="km")[-1]

    assert start_time <= closest_time
    assert closest_time <= end_time
    assert start_index <= closest_index
    assert closest_index <= end_index

    # Pole crossing
    is_crossing_pole = ismonotonic(original_lat)

    # Site name
    if not isinstance(site_name, str):
        site_name = format_coords(lat=site_coords[0], lon=site_coords[1])

    return OverpassInfo(
        site_name=site_name,
        site_lat_deg_north=site_coords[0],
        site_lon_deg_east=site_coords[1],
        site_radius_km=site_radius_km,
        start_index=int(start_index),
        end_index=int(end_index),
        start_time=to_timestamp(start_time),
        end_time=to_timestamp(end_time),
        start_lat_deg_north=start_lat,
        start_lon_deg_east=start_lon,
        end_lat_deg_north=end_lat,
        end_lon_deg_east=end_lon,
        closest_index=int(closest_index),
        closest_lat_deg_north=closest_lat,
        closest_lon_deg_east=closest_lon,
        closest_time=to_timestamp(closest_time),
        closest_distance_km=float(closest_distance),
        along_track_distance_km=along_track_distance,
        frame_crosses_pole=is_crossing_pole,
        samples=len(time),
        site=_site,
    )


def get_overpass_info(
    product: str | xr.Dataset,
    site_radius_km: float | int,
    site: GroundSite | str,
    *,
    time_var: str = TIME_VAR,
    lat_var: str = TRACK_LAT_VAR,
    lon_var: str = TRACK_LON_VAR,
    along_track_dim: str = ALONG_TRACK_DIM,
) -> OverpassInfo:
    if isinstance(product, str):
        with read_product(product) as ds:
            result = _get_overpass_info(
                ds,
                site_radius_km=site_radius_km,
                site=site,
                time_var=time_var,
                lat_var=lat_var,
                lon_var=lon_var,
                along_track_dim=along_track_dim,
            )
    elif isinstance(product, xr.Dataset):
        result = _get_overpass_info(
            product,
            site_radius_km=site_radius_km,
            site=site,
            time_var=time_var,
            lat_var=lat_var,
            lon_var=lon_var,
            along_track_dim=along_track_dim,
        )
    else:
        raise TypeError(
            f"`product` has invalid type '{type(product).__name__}', expected 'str' (i.e. filepath) or 'xr.Dataset'"
        )

    return result
