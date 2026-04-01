import copy
from dataclasses import dataclass, field, fields
from typing import Any, Literal, Type

import h5py  # type: ignore
import numpy as np
import pandas as pd
import xarray as xr
from numpy.typing import NDArray
from pandas._typing import TimestampConvertibleTypes

from ....constants import (
    ELEVATION_VAR,
    HEIGHT_VAR,
    LAND_FLAG_VAR,
    TEMP_CELSIUS_VAR,
    TEMP_KELVIN_VAR,
    TIME_VAR,
    TRACK_LAT_VAR,
    TRACK_LON_VAR,
    TROPOPAUSE_VAR,
)
from ....profile_data import ProfileData
from ....rolling_mean import rolling_mean_1d, rolling_mean_2d
from .._get_file_info_from_str import get_file_info_from_str
from .._trim_to_frame import _get_frame_slice_tuple


def _default_slice() -> slice:
    return slice(None)


@dataclass
class LazyVariable:
    varname: str
    dims: tuple[str, ...]
    attrs: dict[str, str]
    values: NDArray
    _dataset: "LazyDataset"

    def __array__(self, dtype=None, copy=None):
        arr = self.values

        if dtype is not None:
            arr = arr.astype(dtype)

        if copy:
            arr = arr.copy()

        return arr

    @property
    def shape(self) -> tuple[int, ...]:
        return self.values.shape

    @property
    def dtype(self) -> np.dtype:
        return self.values.dtype

    @property
    def long_name(self) -> str:
        return self.attrs.get("long_name", "")

    @property
    def units(self) -> str:
        return self.attrs.get("units", "")

    def to_profile(self) -> ProfileData:
        return self._dataset.get_profile(self.varname)

    def to_xarray(self) -> xr.DataArray:
        return xr.DataArray(
            data=self.values,
            dims=self.dims,
            attrs=self.attrs,
        )

    def copy(self) -> "LazyVariable":
        kwargs = {
            f.name: copy.copy(getattr(self, f.name)) for f in fields(self) if f.name != "_dataset"
        }
        kwargs["_dataset"] = self._dataset
        return LazyVariable(**kwargs)

    def deepcopy(self) -> "LazyVariable":
        kwargs = {
            f.name: copy.deepcopy(getattr(self, f.name))
            for f in fields(self)
            if f.name != "_dataset"
        }
        kwargs["_dataset"] = self._dataset
        return LazyVariable(**kwargs)


def _get_str_attrs(attrs: dict[str, object]) -> dict[str, str]:
    _attrs = {}

    for k, v in attrs.items():
        if isinstance(v, (np.bytes_, bytes)):
            v = v.decode("utf-8")

        if isinstance(v, str):
            _attrs[k] = v

    return _attrs


@dataclass
class LazyDataset:
    """
    !!! warning
        **WARNING: EXPERIMENTAL CLASS**

        **Interface and behaviour are subject to change in future version!**

    EarthCARE data container intended as a lightweight alternative to `xarray.Dataset` for faster variable access.

    This class partially mimics the basic interface of `xarray.Dataset`, providing similar syntax for variable access
    (e.g., `ds["x"]`) and related metadata (e.g., `ds.dims`, `ds["x"].dims`, `ds["x"].values`, `ds["x"].long_name`, or `ds["x"].attrs["long_name"]`).

    Variables must be accessed at least once within a `with` block to be loaded.

    !!! warning
        Support by other `earthcarekit` tools is currently limited, but `CurtainFigure` should work.

    Example:

        ```python
        with LazyDataset(fp) as ds:
            var = "mie_attenuated_backscatter"
            ds[var].attrs["long_name"] = "Co-polar part. bsc. coeff."
            cfig = eck.CurtainFigure()
            cfig.ecplot(ds, var)
            cfig.ecplot_temperature(ds)
            cfig.ecplot_elevation(ds)
        ```
    """

    filepath: str
    trim_to_frame: bool = True
    _lat_var: str = field(default=TRACK_LAT_VAR, repr=False)
    _lon_var: str = field(default=TRACK_LON_VAR, repr=False)
    _time_var: str = field(default=TIME_VAR, repr=False)
    _height_var: str = field(default=HEIGHT_VAR, repr=False)
    _elevation_var: str = field(default=ELEVATION_VAR, repr=False)
    _temperature_var: str = field(default=TEMP_CELSIUS_VAR, repr=False)
    _land_flag: str = field(default=LAND_FLAG_VAR, repr=False)
    _tropopause_var: str = field(default=TROPOPAUSE_VAR, repr=False)
    _sci_grp: str = field(default="ScienceData", repr=False)
    _fill_value_float: float = field(default=9.969209968386869e36, repr=False)
    _is_increasing: bool = field(default=False, repr=False)
    _is_validated: bool = field(default=False, repr=False)
    _default_float_type: Type = field(default=np.float64, repr=False)
    _slice_along_track: slice = field(default_factory=_default_slice, repr=False)
    _slice_vertical: slice = field(default_factory=_default_slice, repr=False)
    _file: h5py.File = field(default=None, repr=False)

    def __enter__(self: "LazyDataset") -> "LazyDataset":
        if self._file is None:
            self._file = h5py.File(self.filepath, "r")

        self._info = get_file_info_from_str(self.filepath)

        # TODO: Extract A-NOM specific pre-processing
        if self._info["file_type"] == "ATL_NOM_1B":
            self._lat_var = "ellipsoid_latitude"
            self._lon_var = "ellipsoid_longitude"
            self._time_var = "time"
            self._height_var = "sample_altitude"
            self._elevation_var = "surface_elevation"
            self._temperature_var = "layer_temperature"
            self._land_flag = "land_flag"

        lats_untrimmed = np.array(
            self._file[self._sci_grp][self._lat_var][self._slice_along_track], dtype=np.float64
        )
        self._i0, self._i1 = _get_frame_slice_tuple(
            lats_untrimmed,
            frame_id=self._info["frame_id"],
        )
        self._data: dict[str, LazyVariable] = {}
        self._dims: dict[str, int] = {}

        def _add_info_var(_var: str) -> None:
            self._data[_var] = LazyVariable(
                varname=_var,
                dims=(),
                attrs={},
                values=np.asarray(self._info[_var]),
                _dataset=self,
            )

        _add_info_var("orbit_number")
        _add_info_var("frame_id")
        _add_info_var("orbit_and_frame")
        _add_info_var("file_type")
        _add_info_var("baseline")

        return self

    def __exit__(
        self: "LazyDataset",
        exc_type: Any,
        exc: Any,
        tb: Any,
    ) -> Literal[False]:
        if self._file:
            self._file.close()
        return False

    def __getitem__(self, key: str) -> LazyVariable:
        return self.get(key)

    def __contains__(self, item: str) -> bool:
        if self.is_open:
            return (item in self._data) or (item in self.variables)
        else:
            return item in self._data

    @classmethod
    def _filter_fill_value(
        cls,
        values: NDArray,
    ) -> NDArray:
        if np.issubdtype(values.dtype, np.floating):
            return np.where(values < cls._fill_value_float, values, np.nan)
        return values

    @property
    def is_open(self) -> bool:
        return bool(self._file.id.valid)

    @property
    def variables(self) -> list[str]:
        if self.is_open:
            return [
                var for var, ds in self._file[self._sci_grp].items() if isinstance(ds, h5py.Dataset)
            ]
        else:
            return list(self._data.keys())

    @property
    def dims(self) -> dict[str, int]:
        return self._dims

    def copy(self) -> "LazyDataset":
        kwargs = {
            f.name: copy.copy(getattr(self, f.name)) for f in fields(self) if f.name != "_file"
        }
        kwargs["_file"] = self._file
        lds = LazyDataset(**kwargs)
        lds._data = {k: v.copy() for k, v in self._data.items()}
        lds._dims = {k: copy.copy(v) for k, v in self._dims.items()}
        return lds

    def get(
        self,
        var: str,
        dtype: np.dtype | Type[Any] | None = None,
        is_time: bool = False,
        time_unit: Literal["D", "s", "ms", "us", "ns"] | None = "s",
        time_origin: (
            TimestampConvertibleTypes | Literal["julian", "unix"]
        ) = "2000-01-01T00:00:00",
        rolling_w: int | None = None,
    ) -> LazyVariable:
        if var in self._data:
            return self._data[var]

        _ini_var = var
        if var == HEIGHT_VAR:
            var = self._height_var
        elif var == TRACK_LAT_VAR:
            var = self._lat_var
        elif var == TRACK_LON_VAR:
            var = self._lon_var
        elif var in [TIME_VAR, self._time_var]:
            var = self._time_var
            is_time = True
        elif var == ELEVATION_VAR:
            var = self._elevation_var
        elif var in [TEMP_KELVIN_VAR, TEMP_CELSIUS_VAR]:
            var = self._temperature_var
        elif var == LAND_FLAG_VAR:
            var = self._land_flag

        if is_time:
            dtype = None

        idxs = slice(self._i0, self._i1) if self.trim_to_frame else slice(None)

        try:
            _var = self._file[self._sci_grp][var]
        except KeyError as e:
            if not self.is_open:
                raise ValueError(
                    "I/O operation on closed file. Variables that are not yet loaded can only be access within an active `with` block."
                ) from e
            raise e

        if is_time:
            values = np.array(
                pd.to_datetime(
                    _var[self._slice_along_track][idxs],
                    unit=time_unit,
                    origin=time_origin,
                )
            )
            # TODO: Extract A-NOM specific pre-processing
            if self._info["file_type"] == "ATL_NOM_1B":
                values = values + np.timedelta64(-2989554432, "ns")
        elif isinstance(rolling_w, int):
            values = LazyDataset._filter_fill_value(
                np.array(_var[self._slice_along_track], dtype=dtype)
            )
            if values.ndim == 2:
                values = values[(slice(None), self._slice_vertical)]
                values = rolling_mean_2d(values, rolling_w, axis=0)
            elif values.ndim == 1:
                values = rolling_mean_1d(values, rolling_w)

            if values.ndim > 0:
                values = values[idxs]
        else:
            try:
                values = LazyDataset._filter_fill_value(
                    np.array(_var[self._slice_along_track][idxs], dtype=dtype)
                )
                if values.ndim == 2:
                    values = values[(slice(None), self._slice_vertical)]
            except Exception:
                values = np.array(_var, dtype=dtype)

        # TODO: Extract A-NOM specific pre-processing
        if (
            self._info["file_type"] == "ATL_NOM_1B"
            and not is_time
            and values.ndim == 2
            and _ini_var not in [HEIGHT_VAR, ELEVATION_VAR]
        ):
            skip_height_above_elevation: int = 300
            elevation = self[ELEVATION_VAR].values[:, np.newaxis] + skip_height_above_elevation
            mask_surface = self[HEIGHT_VAR].values[0] < elevation
            values[mask_surface] = np.nan

        try:
            dims = tuple(d[0].name.split("/")[-1] for d in _var.dims)
            dims = tuple(
                "vertical" if d in ["height", "JSG_height", "CPR_height"] else d for d in dims
            )
        except Exception:
            dims = ()

        attrs = _get_str_attrs(dict(_var.attrs))

        if attrs.get("CLASS") == "DIMENSION_SCALE":
            if var in ["height", "JSG_height", "CPR_height"]:
                var = "vertical"
            values = np.arange(0, values.size)
            dims = (var,)

        lvar = LazyVariable(
            varname=var,
            dims=dims,
            attrs=attrs,
            values=values,
            _dataset=self,
        )

        self._data[var] = lvar
        for d, s in zip(dims, values.shape):
            if d not in self._dims:
                self._dims[d] = s

        if var == self._height_var and var != HEIGHT_VAR:
            self._data[HEIGHT_VAR] = lvar
        elif var == self._time_var and var != TIME_VAR:
            self._data[TIME_VAR] = lvar
        elif var == self._lat_var and var != TRACK_LAT_VAR:
            self._data[TRACK_LAT_VAR] = lvar
        elif var == self._lon_var and var != TRACK_LON_VAR:
            self._data[TRACK_LON_VAR] = lvar
        elif var == self._elevation_var and var != ELEVATION_VAR:
            self._data[ELEVATION_VAR] = lvar
        elif var == self._temperature_var and var != TEMP_KELVIN_VAR:
            self._data[TEMP_KELVIN_VAR] = lvar
            lvar2 = lvar.copy()
            lvar2.values = lvar2.values - 273.15
            self._data[TEMP_CELSIUS_VAR] = lvar2
            if _ini_var == TEMP_CELSIUS_VAR:
                lvar = lvar2
        elif var == self._land_flag and var != LAND_FLAG_VAR:
            self._data[LAND_FLAG_VAR] = lvar
        return lvar

    def get_profile(
        self,
        var: str,
        dtype: np.dtype | Type[Any] | None = None,
        time_unit: Literal["D", "s", "ms", "us", "ns"] | None = "s",
        time_origin: (
            TimestampConvertibleTypes | Literal["julian", "unix"]
        ) = "2000-01-01T00:00:00",
        rolling_w: int | None = None,
    ) -> ProfileData:
        vars = self.variables
        var_data = self.get(var, rolling_w=rolling_w, dtype=dtype)

        profile = ProfileData(
            values=var_data.values,
            height=self.get(self._height_var, dtype=self._default_float_type).values,
            time=self.get(
                self._time_var, is_time=True, time_unit=time_unit, time_origin=time_origin
            ).values,
            latitude=(
                None
                if self._lat_var not in vars
                else self.get(self._lat_var, dtype=self._default_float_type).values
            ),
            longitude=(
                None
                if self._lat_var not in vars
                else self.get(self._lon_var, dtype=self._default_float_type).values
            ),
            units=var_data.attrs.get("units"),
            label=var_data.attrs.get("long_name"),
            _validate=self._is_validated,
            _is_increasing=self._is_increasing,
        )

        if not self._is_validated:
            self._is_validated = True
            self._is_increasing = profile._is_increasing

        return profile
