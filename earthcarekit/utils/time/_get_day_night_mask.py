import numpy as np
import pandas as pd
from numpy.typing import ArrayLike, NDArray


def _get_sec_of_day(time: NDArray):
    sod = (time - time.astype("datetime64[D]")) / np.timedelta64(1, "s")
    return sod


def _get_hour_of_day(time: NDArray):
    hod = _get_sec_of_day(time) / 3600.0
    return hod


def _get_day_of_year(time: NDArray):
    year_start = time.astype("datetime64[Y]")
    doy = (time.astype("datetime64[D]") - year_start) / np.timedelta64(1, "D")
    doy = doy.astype(float) + 1.0
    return doy


def get_day_night_mask(
    time: pd.DatetimeIndex | ArrayLike,
    lats: ArrayLike,
    lons: ArrayLike,
    sun_altitude_threshold: float = 0.0,
) -> NDArray[np.bool]:
    """
    Calculates a day/night mask from UTC timestamps and lat/lon positions.

    Args:
        times (pandas.DatetimeIndex | NDArray):
            UTC Timestamps.
        lats (float | NDArray):
            Latitude(s) in degrees (scalar or same length as `times`).
        lons (float | NDArray):
            Longitude(s) in degrees, positive east (scalar or same length as `times`).
        sun_altitude_threshold (float, optional):
            Threshold in degrees for "day" (0 = horizon, -6 = civil twilight,
            -12 = nautical twilight, -18 = astronomical twilight)

    Returns:
        NDArray[bool]: Day/night mask (True = day, False = night)

    References:
        NOAA Global Monitoring Laboratory, "Low Accuracy Equations"
            https://gml.noaa.gov/grad/solcalc/sollinks.html (accessed 2025-01-21)
        Wikipedia contributors (2025), "Hour angle"
            https://en.wikipedia.org/wiki/Hour_angle?utm_source=chatgpt.com (accessed 2025-01-21)
    """

    if isinstance(time, pd.DatetimeIndex):
        time_np = time.values.astype("datetime64[s]")
    else:
        time_np = np.asarray(time).astype("datetime64[s]")

    hour = _get_hour_of_day(time_np)

    day_of_year = _get_day_of_year(time_np)

    lats = np.asarray(lats, dtype=float)
    lons = np.asarray(lons, dtype=float)
    n = len(hour)
    if lats.ndim == 0:
        lats = np.full(n, lats)
    if lons.ndim == 0:
        lons = np.full(n, lons)

    # Fractional year
    gamma_rad = 2.0 * np.pi / 365.0 * (day_of_year - 1.0 + (hour - 12.0) / 24.0)

    # Solar declination angle
    decl_rad = (
        0.006918
        - 0.399912 * np.cos(gamma_rad)
        + 0.070257 * np.sin(gamma_rad)
        - 0.006758 * np.cos(2 * gamma_rad)
        + 0.000907 * np.sin(2 * gamma_rad)
        - 0.002697 * np.cos(3 * gamma_rad)
        + 0.00148 * np.sin(3 * gamma_rad)
    )

    # Local solar time
    lst = (hour + lons / 15.0) % 24.0

    # Solar hour angle (0 deg at solar noon, 15 deg per hour, negative=morning, positive=afternoon)
    hour_angle = np.deg2rad(15.0 * (lst - 12.0))

    # Solar elevation angle
    lat_rad = np.deg2rad(lats)
    sin_elev = np.sin(lat_rad) * np.sin(decl_rad) + np.cos(lat_rad) * np.cos(
        decl_rad
    ) * np.cos(hour_angle)
    elev_deg = np.rad2deg(np.arcsin(np.clip(sin_elev, -1.0, 1.0)))

    day_night_mask = elev_deg > sun_altitude_threshold
    return day_night_mask
