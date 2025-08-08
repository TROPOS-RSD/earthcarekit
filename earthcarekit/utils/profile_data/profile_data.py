import warnings
from dataclasses import asdict, dataclass
from typing import Iterable, Literal, Sequence, Tuple, TypeAlias

import numpy as np
import pandas as pd
import xarray as xr
from numpy.typing import ArrayLike, NDArray

from .. import statistics as stats
from .._parse_units import parse_units
from ..constants import HEIGHT_VAR, TIME_VAR, TRACK_LAT_VAR, TRACK_LON_VAR
from ..geo import haversine
from ..np_array_utils import coarsen_mean, pad_true_sequence
from ..rolling_mean import rolling_mean_2d
from ..time import (
    TimeRangeLike,
    TimestampLike,
    num_to_time,
    time_to_num,
    to_timestamps,
    validate_time_range,
)
from ..typing import DistanceRangeLike
from ..validation import validate_height_range
from ._validate_dimensions import ensure_vertical_2d, validate_profile_data_dimensions
from .rebin import rebin_along_track, rebin_height, rebin_time


def _mean_2d(a: NDArray, axis: int = 0) -> NDArray:
    if len(a.shape) == 2:
        return np.array(nanmean(a, axis=axis))
    return np.array(a)


def _mean_1d(a: NDArray) -> NDArray:
    if a.dtype not in ["datetime64[ns]", "datetime64[s]"]:
        return np.array(nanmean(a))
    else:
        time = a
        reference_time = time[0].astype("datetime64[s]")
        time = (time - reference_time).astype("timedelta64[s]").astype(np.float64)
        new_time = np.array(nanmean(time))
        a = reference_time + new_time.astype("timedelta64[s]")
        return a


def nanmean(a: ArrayLike, axis: int | None = None) -> np.floating | NDArray:
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        return np.nanmean(np.array(a), axis=axis)


@dataclass(frozen=True)
class ProfileStatResults:
    hmin: float
    hmax: float
    mean: float
    std: float
    mean_error: float | None

    def to_dict(self) -> dict:
        return asdict(self)

    def to_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame([self.to_dict()])
        df = df.astype(
            dict(
                hmin=float,
                hmax=float,
                mean=float,
                std=float,
                mean_error=float,
            )
        )
        return df


@dataclass(frozen=True)
class ProfileComparisonResults:
    hmin: float
    hmax: float
    diff_of_means: float
    mae: float
    rmse: float
    mean_diff: float
    prediction: ProfileStatResults
    target: ProfileStatResults

    def to_dict(self) -> dict:
        d = asdict(self)
        d_pred = d["prediction"].copy()
        d_targ = d["target"].copy()

        for k, v in d_pred.items():
            if k in ["hmin", "hmax"]:
                continue
            d[f"{k}_prediction"] = v

        for k, v in d_targ.items():
            if k in ["hmin", "hmax"]:
                continue
            d[f"{k}_target"] = v

        d = {k: v for k, v in d.items() if k not in ["prediction", "target"]}

        return d

    def to_dataframe(self) -> pd.DataFrame:
        df = pd.DataFrame([self.to_dict()])
        df = df.astype(
            dict(
                hmin=float,
                hmax=float,
                diff_of_means=float,
                mae=float,
                rmse=float,
                mean_diff=float,
                mean_prediction=float,
                std_prediction=float,
                mean_error_prediction=float,
                mean_target=float,
                std_target=float,
                mean_error_target=float,
            )
        )
        return df


@dataclass
class ProfileData:
    values: NDArray
    height: NDArray
    time: NDArray
    latitude: NDArray | None = None
    longitude: NDArray | None = None
    color: str | None = None
    label: str | None = None
    units: str | None = None
    platform: str | None = None
    error: NDArray | None = None

    def __post_init__(self):

        if isinstance(self.values, Iterable):
            self.values = np.atleast_2d(self.values)
        if isinstance(self.height, Iterable):
            self.height = np.asarray(self.height)
        if isinstance(self.time, Iterable):
            self.time = pd.to_datetime(np.asarray(self.time)).to_numpy()
        if isinstance(self.latitude, Iterable):
            self.latitude = np.asarray(self.latitude)
        if isinstance(self.longitude, Iterable):
            self.longitude = np.asarray(self.longitude)
        if isinstance(self.error, Iterable):
            self.error = np.atleast_2d(self.error)
            if self.values.shape != self.error.shape:
                raise ValueError(
                    f"`error` must have same shape as `values`: values.shape={self.values.shape} != error.shape={self.error.shape}"
                )
        if isinstance(self.units, str):
            self.units = parse_units(self.units)

        validate_profile_data_dimensions(
            values=self.values,
            height=self.height,
            time=self.time,
            latitude=self.latitude,
            longitude=self.longitude,
        )

    @property
    def shape(self):
        return self.values.shape

    @classmethod
    def from_dataset(
        self,
        ds: xr.Dataset,
        var: str,
        error_var: str | None = None,
        height_var: str = HEIGHT_VAR,
        time_var: str = TIME_VAR,
        lat_var: str = TRACK_LAT_VAR,
        lon_var: str = TRACK_LON_VAR,
        color: str | None = None,
        label: str | None = None,
        units: str | None = None,
        platform: str | None = None,
    ) -> "ProfileData":
        values = ds[var].values
        height = ds[height_var].values
        time = ds[time_var].values

        latitude: NDArray | None = None
        if lat_var in ds:
            latitude = ds[lat_var].values

        longitude: NDArray | None = None
        if lon_var in ds:
            longitude = ds[lon_var].values

        if not isinstance(label, str):
            label = None if not hasattr(ds[var], "long_name") else ds[var].long_name

        if not isinstance(label, str):
            label = None if not hasattr(ds[var], "name") else ds[var].name  # type: ignore

        if not isinstance(label, str):
            label = None if not hasattr(ds[var], "label") else ds[var].label

        if not isinstance(units, str):
            units = None if not hasattr(ds[var], "units") else ds[var].units

        if not isinstance(units, str):
            units = None if not hasattr(ds[var], "unit") else ds[var].unit

        error: NDArray | None = None
        if isinstance(error_var, str):
            error = ds[error_var].values

        return ProfileData(
            values=values,
            height=height,
            time=time,
            latitude=latitude,
            longitude=longitude,
            color=color,
            label=label,
            units=units,
            platform=platform,
            error=error,
        )

    def print_shapes(self):
        if isinstance(self.values, Iterable):
            print(f"values={self.values.shape}")
        if isinstance(self.height, Iterable):
            print(f"height={self.height.shape}")
        if isinstance(self.time, Iterable):
            print(f"time={self.time.shape}")
        if isinstance(self.latitude, Iterable):
            print(f"latitude={self.latitude.shape}")
        if isinstance(self.longitude, Iterable):
            print(f"longitude={self.longitude.shape}")

    def mean(self) -> "ProfileData":
        """Returns mean profile."""
        new_values = _mean_2d(self.values)
        new_height = _mean_2d(self.height)
        new_error: NDArray | None = None
        if isinstance(self.error, np.ndarray):
            new_error = _mean_2d(self.error)

        if isinstance(self.time, np.ndarray):
            new_time = _mean_1d(self.time)
        else:
            new_time = None

        if isinstance(self.latitude, np.ndarray):
            new_latitude = _mean_1d(self.latitude)
        else:
            new_latitude = None

        if isinstance(self.longitude, np.ndarray):
            new_longitude = _mean_1d(self.longitude)
        else:
            new_longitude = None

        new_color = self.color
        new_label = self.label
        new_units = self.units
        new_platform = self.platform

        return ProfileData(
            values=new_values,
            height=new_height,
            time=new_time,
            latitude=new_latitude,
            longitude=new_longitude,
            color=new_color,
            label=new_label,
            units=new_units,
            platform=new_platform,
            error=new_error,
        )

    def rolling_mean(self, window_size: int, axis: Literal[0, 1] = 0) -> "ProfileData":
        """Returns mean profile."""
        if len(self.values.shape) == 2:
            new_values = rolling_mean_2d(self.values, w=window_size, axis=axis)
            new_error: NDArray | None = None
            if isinstance(self.error, np.ndarray):
                new_error = self.error
            return ProfileData(
                values=new_values,
                height=self.height,
                time=self.time,
                latitude=self.latitude,
                longitude=self.longitude,
                color=self.color,
                label=self.label,
                units=self.units,
                platform=self.platform,
                error=new_error,
            )

        msg = f"VerticalProfile contains only one profile and thus {self.rolling_mean.__name__}() is not applied."
        warnings.warn(msg)
        return self

    def layer_mean(self, hmin: float, hmax: float) -> NDArray:
        """Returns layer mean values."""
        layer_mask = np.logical_and(hmin <= self.height, self.height <= hmax)
        layer_mean_values = self.values
        layer_mean_values[~layer_mask] = np.nan
        if len(layer_mean_values.shape) == 2:
            layer_mean_values = _mean_2d(layer_mean_values, axis=1)
        else:
            layer_mean_values = np.array(nanmean(layer_mean_values))
        return layer_mean_values

    def rebin_height(
        self,
        height_bin_centers: Iterable[float] | NDArray,
        method: Literal["interpolate", "mean"] = "mean",
    ) -> "ProfileData":
        """
        Rebins profiles to new height bins.

        Parameters:
            new_height (np.ndarray):
                Target height bin centers as a 1D array (shape represents vertical dimension)

        Returns:
            rebinned_profiles (VerticalProfiles):
                Profiles rebinned along the vertical dimension according to `height_bin_centers`.
        """
        if self.height.shape == np.array(height_bin_centers).shape and np.all(
            np.array(self.height) == np.array(height_bin_centers)
        ):
            return ProfileData(
                values=self.values,
                height=self.height,
                time=self.time,
                latitude=self.latitude,
                longitude=self.longitude,
                color=self.color,
                label=self.label,
                units=self.units,
                platform=self.platform,
                error=self.error,
            )

        new_values = rebin_height(
            self.values,
            self.height,
            height_bin_centers,
            method=method,
        )
        new_height = np.asarray(height_bin_centers)
        if len(new_values.shape) == 2:
            new_height = np.atleast_2d(new_height)
            if new_height.shape[0] == 1:
                new_height = new_height[0]
        new_error: NDArray | None = None
        if isinstance(self.error, np.ndarray):
            new_error = rebin_height(
                self.error,
                self.height,
                height_bin_centers,
                method=method,
            )
        return ProfileData(
            values=new_values,
            height=new_height,
            time=self.time,
            latitude=self.latitude,
            longitude=self.longitude,
            color=self.color,
            label=self.label,
            units=self.units,
            platform=self.platform,
            error=new_error,
        )

    def rebin_time(
        self,
        time_bin_centers: Sequence[TimestampLike] | ArrayLike,
        method: Literal["interpolate", "mean"] = "mean",
    ) -> "ProfileData":
        """
        Rebins profiles to new time bins.

        Args:
            time_bin_centers (Iterable[TimestampLike] | ArrayLike):
                Target time bin centers as a 1D array (shape represents temporal dimension)

        Returns:
            rebinned_profiles (VerticalProfiles):
                Profiles rebinned along the temporal dimension according to `height_bin_centers`.
        """
        time_bin_centers = to_timestamps(time_bin_centers)
        new_values = rebin_time(self.values, self.time, time_bin_centers, method=method)
        if len(self.height.shape) == 2:
            new_height = rebin_time(
                self.height, self.time, time_bin_centers, method=method
            )
        else:
            new_height = self.height
        new_error: NDArray | None = None
        if isinstance(self.error, np.ndarray):
            new_error = rebin_time(
                self.error, self.time, time_bin_centers, method=method
            )

        if isinstance(self.latitude, np.ndarray) and isinstance(
            self.longitude, np.ndarray
        ):
            new_coords = rebin_time(
                np.vstack([self.latitude, self.longitude]).T,
                self.time,
                time_bin_centers,
                is_geo=True,
                method=method,
            )
            new_latitude = new_coords[:, 0]
            new_longitude = new_coords[:, 0]
        else:
            new_latitude = None
            new_longitude = None
        return ProfileData(
            values=new_values,
            height=new_height,
            time=pd.to_datetime(to_timestamps(time_bin_centers)).to_numpy(),
            latitude=new_latitude,
            longitude=new_longitude,
            color=self.color,
            label=self.label,
            units=self.units,
            platform=self.platform,
            error=new_error,
        )

    def rebin_along_track(
        self,
        latitude_bin_centers: ArrayLike,
        longitude_bin_centers: ArrayLike,
    ) -> "ProfileData":
        """
        Rebins profiles to new time bins.

        Args:
            latitude_bin_centers (ArrayLike):
                Target time bin centers as a 1D array (shape represents temporal dimension)

        Returns:
            rebinned_profiles (VerticalProfiles):
                Profiles rebinned along the temporal dimension according to `height_bin_centers`.
        """
        has_lat = self.latitude is not None
        has_lon = self.longitude is not None

        if not has_lat or not has_lon:
            missing = []
            if not has_lat:
                missing.append("latitude")
            if not has_lon:
                missing.append("longitude")
            raise ValueError(
                f"{ProfileData.__name__} instance is missing {' and '.join(missing)} data"
            )

        latitude_bin_centers = np.asarray(latitude_bin_centers)
        longitude_bin_centers = np.asarray(longitude_bin_centers)

        new_values = rebin_along_track(
            self.values,
            np.asarray(self.latitude),
            np.asarray(self.longitude),
            latitude_bin_centers,
            longitude_bin_centers,
        )
        new_error: NDArray | None = None
        if isinstance(self.error, np.ndarray):
            new_error = rebin_along_track(
                self.error,
                np.asarray(self.latitude),
                np.asarray(self.longitude),
                latitude_bin_centers,
                longitude_bin_centers,
            )
        new_times = rebin_along_track(
            self.time,
            np.asarray(self.latitude),
            np.asarray(self.longitude),
            latitude_bin_centers,
            longitude_bin_centers,
        )
        return ProfileData(
            values=new_values,
            height=self.height,
            time=new_times,
            latitude=np.array(latitude_bin_centers),
            longitude=np.array(longitude_bin_centers),
            color=self.color,
            label=self.label,
            units=self.units,
            platform=self.platform,
            error=new_error,
        )

    def to_dict(self) -> dict:
        """Returns stored profile data as `dict`."""
        return asdict(self)

    def select_height_range(
        self,
        height_range: DistanceRangeLike,
    ) -> "ProfileData":
        """Retruns only data within the specified `height_range`."""
        height_range = validate_height_range(height_range)

        if len(self.height.shape) == 2:
            ref_height = self.height[0]
        else:
            ref_height = self.height

        mask = np.logical_and(
            height_range[0] <= ref_height, ref_height <= height_range[1]
        )

        sel_values = self.values[:, mask]
        sel_error: NDArray | None = None
        if isinstance(self.error, np.ndarray):
            sel_error = self.error[:, mask]

        if len(self.height.shape) == 2:
            sel_height = self.height[:, mask]
        else:
            sel_height = self.height[mask]

        return ProfileData(
            values=sel_values,
            height=sel_height,
            time=self.time,
            latitude=self.latitude,
            longitude=self.longitude,
            color=self.color,
            label=self.label,
            units=self.units,
            platform=self.platform,
            error=sel_error,
        )

    def select_time_range(
        self,
        time_range: TimeRangeLike | None,
        pad_idxs: int = 0,
    ) -> "ProfileData":
        """Retruns only data within the specified `time_range`."""
        if time_range is None:
            return self
        elif not isinstance(self.time, np.ndarray):
            raise ValueError(
                f"{ProfileData.__name__}.{self.select_time_range.__name__}() missing `time` data"
            )

        time_range = validate_time_range(time_range)

        times = to_timestamps(self.time)
        mask = np.logical_and(time_range[0] <= times, times <= time_range[1])
        mask = pad_true_sequence(mask, pad_idxs)

        sel_values = self.values[mask]
        sel_error: NDArray | None = None
        if isinstance(self.error, np.ndarray):
            sel_error = self.error[:, mask]
        sel_time = self.time[mask]

        if len(self.height.shape) == 2:
            sel_height = self.height[mask]
        else:
            sel_height = self.height

        if isinstance(self.latitude, np.ndarray):
            sel_latitude = self.latitude[mask]
        else:
            sel_latitude = None

        if isinstance(self.longitude, np.ndarray):
            sel_longitude = self.longitude[mask]
        else:
            sel_longitude = None

        return ProfileData(
            values=sel_values,
            height=sel_height,
            time=sel_time,
            latitude=sel_latitude,
            longitude=sel_longitude,
            color=self.color,
            label=self.label,
            units=self.units,
            platform=self.platform,
            error=sel_error,
        )

    def coarsen_mean(self, n: int, is_bin: bool = False) -> "ProfileData":
        """Returns downsampled profile data."""
        if len(self.values.shape) == 2:
            new_values: NDArray
            new_values = coarsen_mean(self.values, n=n, is_bin=is_bin)
            new_error: NDArray | None = None
            if isinstance(self.error, np.ndarray):
                new_error = coarsen_mean(self.error, n=n, is_bin=is_bin)
            new_time: NDArray = coarsen_mean(self.time, n=n)

            new_height: NDArray
            if len(self.height.shape) == 2:
                new_height = coarsen_mean(self.height, n=n)
            else:
                new_height = self.height

            new_latitude: NDArray | None
            if isinstance(self.latitude, np.ndarray):
                new_latitude = coarsen_mean(self.latitude, n=n)
            else:
                new_latitude = None

            new_longitude: NDArray | None
            if isinstance(self.longitude, np.ndarray):
                new_longitude = coarsen_mean(self.longitude, n=n)
            else:
                new_longitude = None

            return ProfileData(
                values=new_values,
                height=new_height,
                time=new_time,
                latitude=new_latitude,
                longitude=new_longitude,
                color=self.color,
                label=self.label,
                units=self.units,
                platform=self.platform,
                error=new_error,
            )

        msg = f"VerticalProfile contains only one profile and thus {self.coarsen_mean.__name__}() is not applied."
        warnings.warn(msg)
        return self

    def stats(
        self,
        height_range: DistanceRangeLike | None = None,
    ) -> ProfileStatResults:
        p = self
        _hmin: float = float(np.nanmin(p.height))
        _hmax: float = float(np.nanmax(p.height))
        if height_range is not None:
            height_range = validate_height_range(height_range)
            _hmin = height_range[0]
            _hmax = height_range[1]
            p = p.select_height_range(height_range)

        p = p.mean()
        _mean: float = float(stats.nan_mean(p.values))
        _std: float = float(stats.nan_std(p.values))
        _mean_error: float | None = None
        if isinstance(p.error, np.ndarray):
            _mean_error = float(stats.nan_mean(p.error))
        return ProfileStatResults(
            hmin=_hmin,
            hmax=_hmax,
            mean=_mean,
            std=_std,
            mean_error=_mean_error,
        )

    def compare_to(
        self,
        target: "ProfileData",
        height_range: DistanceRangeLike | None = None,
    ) -> ProfileComparisonResults:
        p = self
        p = p.mean()
        t = target
        t = t.mean()

        get_mean_abs_diff = lambda x: float(np.nanmean(np.abs(np.diff(x))))
        if get_mean_abs_diff(p.height) > get_mean_abs_diff(t.height):
            t = t.rebin_height(p.height)
        else:
            p = p.rebin_height(t.height)

        _hmin: float = float(np.nanmin(p.height))
        _hmax: float = float(np.nanmax(p.height))
        if height_range is not None:
            height_range = validate_height_range(height_range)
            _hmin = height_range[0]
            _hmax = height_range[1]
            p = p.select_height_range(height_range)
            t = t.select_height_range(height_range)

        stats_pred = p.stats()
        stats_targ = t.stats()
        _diff_of_means: float = float(stats.nan_diff_of_means(p.values, t.values))
        _mae: float = float(stats.nan_mae(p.values, t.values))
        _rmse: float = float(stats.nan_rmse(p.values, t.values))
        _mean_diff: float = float(stats.nan_mean_diff(p.values, t.values))

        return ProfileComparisonResults(
            hmin=_hmin,
            hmax=_hmax,
            diff_of_means=_diff_of_means,
            mae=_mae,
            rmse=_rmse,
            mean_diff=_mean_diff,
            prediction=stats_pred,
            target=stats_targ,
        )

    def to_mega(self) -> "ProfileData":
        import logging

        logger = logging.getLogger()

        if isinstance(self.units, str):
            if self.units in ["m-1 sr-1", "m-1"]:
                return ProfileData(
                    values=self.values * 1e6,
                    height=self.height,
                    time=self.time,
                    latitude=self.latitude,
                    longitude=self.longitude,
                    color=self.color,
                    label=self.label,
                    units=f"M{self.units}",
                    platform=self.platform,
                    error=(
                        None
                        if not isinstance(self.error, np.ndarray)
                        else self.error * 1e6
                    ),
                )
            elif self.units in ["Mm-1 sr-1", "Mm-1"]:
                logger.warning(
                    f"""Profile units already converted to "{self.units}"."""
                )
                return self.copy()
            else:
                logger.warning(
                    f"""Can not convert profile to "Mm-1 sr-1" or "Mm-1" since it's original units are: "{self.units}"."""
                )
                return self.copy()
        logger.warning(
            f"""Can not convert profile to "Mm-1 sr-1" or "Mm-1" since units are not given."""
        )

        return self.copy()

    def copy(self) -> "ProfileData":
        return ProfileData(
            values=self.values,
            height=self.height,
            time=self.time,
            latitude=self.latitude,
            longitude=self.longitude,
            color=self.color,
            label=self.label,
            units=self.units,
            platform=self.platform,
            error=self.error,
        )
