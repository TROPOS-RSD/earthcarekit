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
    """
    Class storing details about an overpass, including duration, distance, time, closest index, etc.

    Attributes:
        site_name (str): Name of the site flown over.
        site_lat_deg_north (float): Latitude of the site in degrees north.
        site_lon_deg_east (float): Longitude of the site in degrees north.
        site_radius_km (float): Radius in kilometers around the site the overpass took place.
        start_index (int): Index at the start of the overpass.
        end_index (int): Index at the end of the overpass.
        start_time (pd.Timestamp): Time at the start of the overpass.
        end_time (pd.Timestamp): Time at the end of the overpass.
        start_lat_deg_north (float): Latitude at the start of the overpass.
        start_lon_deg_east (float): Latitude at the end of the overpass.
        end_lat_deg_north (float): Longitude at the start of the overpass.
        end_lon_deg_east (float): Longitude at the end of the overpass.
        closest_index (int): Index of the data sample that is geographically closest to the site.
        closest_lat_deg_north (float): Latitude of the data sample that is geographically closest to the site.
        closest_lon_deg_east (float): Longitude of the data sample that is geographically closest to the site.
        closest_time (pd.Timestamp): Timestamp of the data sample that is geographically closest to the site.
        closest_distance_km (float): Distance in kilometers of the data sample that is geographically closest to the site.
        along_track_distance_km (float): Distance in kilometers along the overpass track withing the set radius.
        frame_crosses_pole (bool): Whether the original track crosses a pole at any point (not necessarily within the radius).
        samples (int): Number of data sample within the radius.
        site (GroundSite): Site as an `earthcarekit.GroundSite` object.
    """

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
        """Returns lat/lon coordinates where the satellite is geographically closest to the site."""
        return self.closest_lat_deg_north, self.closest_lon_deg_east

    @property
    def duration(self) -> pd.Timedelta:
        """Returns the duration of the overpass."""
        return self.end_time - self.start_time

    def to_dict(self) -> dict:
        """Returns overpass info as a Python `dict`."""
        d = dict(
            site_name=self.site_name,
            site_lat_deg_north=self.site_lat_deg_north,
            site_lon_deg_east=self.site_lon_deg_east,
            site_radius_km=self.site_radius_km,
            start_index=self.start_index,
            end_index=self.end_index,
            start_time=self.start_time,
            end_time=self.end_time,
            start_lat_deg_north=self.start_lat_deg_north,
            start_lon_deg_east=self.start_lon_deg_east,
            end_lat_deg_north=self.end_lat_deg_north,
            end_lon_deg_east=self.end_lon_deg_east,
            closest_index=self.closest_index,
            closest_lat_deg_north=self.closest_lat_deg_north,
            closest_lon_deg_east=self.closest_lon_deg_east,
            closest_time=self.closest_time,
            closest_distance_km=self.closest_distance_km,
            along_track_distance_km=self.along_track_distance_km,
            frame_crosses_pole=self.frame_crosses_pole,
            samples=self.samples,
        )
        return d

    def to_dataframe(self) -> pd.DataFrame:
        """Returns overpass info as a `pandas.Dataframe`."""
        df = pd.DataFrame([self.to_dict()])
        df = df.astype(
            dict(
                site_name=str,
                site_lat_deg_north=float,
                site_lon_deg_east=float,
                site_radius_km=float,
                start_index=int,
                end_index=int,
                start_time=pd.Timestamp,
                end_time=pd.Timestamp,
                start_lat_deg_north=float,
                start_lon_deg_east=float,
                end_lat_deg_north=float,
                end_lon_deg_east=float,
                closest_index=int,
                closest_lat_deg_north=float,
                closest_lon_deg_east=float,
                closest_time=pd.Timestamp,
                closest_distance_km=float,
                along_track_distance_km=float,
                frame_crosses_pole=bool,
                samples=int,
            )
        )
        return df


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
    radius_km: float | int,
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
            radius_km=radius_km,
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
        site_radius_km=radius_km,
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
    ds: str | xr.Dataset,
    site: GroundSite | str,
    radius_km: float | int = 100.0,
    *,
    time_var: str = TIME_VAR,
    lat_var: str = TRACK_LAT_VAR,
    lon_var: str = TRACK_LON_VAR,
    along_track_dim: str = ALONG_TRACK_DIM,
) -> OverpassInfo:
    """
    Extract details about an overpass, including duration, distance, time, closest index, etc.

    Args:
        ds (str | xr.Dataset): Path to or instance of a dataset containing along-track satellite data.
        site (GroundSite | str): Site name or object over which the satellite is passing.
        radius_km (float | int, optional): Radius to look for an overpass in kilometers. Defaults to 100.
        time_var (str, optional): Name of the dataset variable containing time data. Defaults to "time".
        lat_var (str, optional): Name of the dataset variable containing latitude data. Defaults to "latitude".
        lon_var (str, optional): Name of the dataset variable containing longitude data. Defaults to "longitude".
        along_track_dim (str, optional): Name of the along-track or temporal dataset dimension. Defaults to "along_track".

    Raises:
        TypeError: If `ds` is not of type `str` (i.e., filepath) or `xr.Dataset`.

    Returns:
        OverpassInfo: _description_
    """
    if isinstance(ds, str):
        with read_product(ds) as _ds:
            result = _get_overpass_info(
                _ds,
                radius_km=radius_km,
                site=site,
                time_var=time_var,
                lat_var=lat_var,
                lon_var=lon_var,
                along_track_dim=along_track_dim,
            )
    elif isinstance(ds, xr.Dataset):
        result = _get_overpass_info(
            ds,
            radius_km=radius_km,
            site=site,
            time_var=time_var,
            lat_var=lat_var,
            lon_var=lon_var,
            along_track_dim=along_track_dim,
        )
    else:
        raise TypeError(
            f"`ds` has invalid type '{type(ds).__name__}', expected 'str' (i.e. filepath) or 'xr.Dataset'"
        )

    return result
