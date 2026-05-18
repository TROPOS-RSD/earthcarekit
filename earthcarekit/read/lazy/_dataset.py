import copy
import logging
from dataclasses import dataclass, field, fields
from types import MappingProxyType
from typing import Any, Final, Iterable, Literal, Type, cast

import h5py  # type: ignore
import numpy as np
import pandas as pd
import xarray as xr
from numpy.typing import NDArray
from pandas._typing import TimestampConvertibleTypes

from ...constants import (
    GEOID_OFFSET_VAR,
    HEIGHT_VAR,
    SENSOR_ELEVATION_ANGLE_VAR,
    TIME_VAR,
    TRACK_LAT_VAR,
    TROPOPAUSE_VAR,
    UNITS_RENAME_MAP,
)
from ...data.profile import Profile
from ...filter._frame import get_frame_slice_tuple
from ...typing import is_iterable_of_str
from ...utils import get_file_info_from_str
from ...utils.dict import invert_dict_nonunique
from ...utils.numpy import rolling_mean_1d, rolling_mean_2d
from ._defaults import (
    DEFAULT_NADIR_INDEX,
    ProductDefaults,
    get_common_var_transformer,
    get_defaults,
)
from ._variable import LazyVariable


def _default_slice() -> slice:
    return slice(None)


def _default_height_vars() -> set:
    return {HEIGHT_VAR, TROPOPAUSE_VAR}


def _get_str_attrs(attrs: dict[str, object] | h5py.AttributeManager) -> dict[str, str]:
    _attrs = {}

    for k, v in attrs.items():
        if isinstance(v, (np.bytes_, bytes)):
            v = v.decode("utf-8")

        if isinstance(v, str):
            _attrs[k] = v

    return _attrs


VERTICAL_DIM_NAMES: Final[set[str]] = {
    "height",
    "JSG_height",
    "CPR_height",
    "ATLID_height",
}


def _normalize_var_obj_dim_name(dim: Any) -> str:
    name = dim[0].name.split("/")[-1]
    return "vertical" if name in VERTICAL_DIM_NAMES else name


def _get_var_obj_dims(var_obj: h5py.Dataset, known_sizes: dict[str, int]) -> tuple[str, ...]:
    dims: tuple[str, ...]

    try:
        dims = tuple(_normalize_var_obj_dim_name(d) for d in var_obj.dims)
    except Exception:
        dims = ()

    if var_obj.ndim == len(dims):
        return dims

    size_to_dims = invert_dict_nonunique(known_sizes)

    dims_tmp: list[str] = []
    for size in var_obj.shape:
        if size_to_dims.get(size):
            dims_tmp.append(size_to_dims[size][0])
        else:
            for i in range(1, var_obj.ndim + len(known_sizes) + 2):
                new_dim = f"phony_dim_{i}"
                if new_dim not in known_sizes:
                    dims_tmp.append(new_dim)
                    break

    return tuple(dims_tmp)


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

    Attributes:
        filepath (str): Path to a EarthCARE data file in HDF5/NetCDF-4 format (.h5).
        trim_to_frame (bool, optional): Whether to trim the dataset to latitude frame bounds. Defaults to True.
        in_memory (bool, optional): If True, load dataset variables eagerly into memory. Otherwise, variables are loaded lazily upon access.
            If `vars` is provided, only the specified variables are loaded. Defaults to False.
        to_geoid (bool, optional): If True, converts variables representing height/altitude values from HAE (WGS84) to AMSL (EGM96) using the `geoid_offset` variable. Defaults to False.
        vars (str | Iterable[str] | None, optional): Variable name or collection of names to load at initialization.
            If None and `in_memory` is True, all variables are still loaded. Defaults to None.

    Example:

        >>> with LazyDataset(fp) as ds:
        >>>     var = "mie_attenuated_backscatter"
        >>>     ds[var].attrs["long_name"] = "Co-polar part. bsc. coeff."
        >>>     cfig = eck.CurtainFigure()
        >>>     cfig.ecplot(ds, var)
        >>>     cfig.ecplot_temperature(ds)
        >>>     cfig.ecplot_elevation(ds)
    """

    filepath: str
    trim_to_frame: bool = True
    in_memory: bool = False
    to_geoid: bool = False
    vars: str | Iterable[str] | None = field(default=None, repr=False)
    logger = logging.getLogger(__name__)
    _sci_grp: str = field(default="ScienceData", repr=False)
    _fill_value_float: float = field(default=9e36, repr=False)
    _is_increasing: bool = field(default=False, repr=False)
    _is_validated: bool = field(default=False, repr=False)
    _slice_along_track: slice = field(default_factory=_default_slice, repr=False)
    _slice_vertical: slice = field(default_factory=_default_slice, repr=False)
    _slice_across_track: slice = field(default_factory=_default_slice, repr=False)
    _file: h5py.File = field(default=None, repr=False)
    _varname_map: dict[str, str] = field(default_factory=dict, repr=False)
    _height_vars: set[str] = field(default_factory=_default_height_vars, repr=False)
    _read: bool = field(default=True, repr=False)

    def __post_init__(self) -> None:
        self._info: dict[str, Any] = get_file_info_from_str(self.filepath)
        file_type = self._info["file_type"]
        self._is_jaxa: bool = self._info["agency"] == "J"
        self._nadir_index: int | None = DEFAULT_NADIR_INDEX.get(file_type)
        self._loaded_vars: list[str] = []
        self._data: dict[str, LazyVariable] = {}
        self._sizes: dict[str, int] = {}
        self._defaults: ProductDefaults | None = get_defaults(file_type)

        if self._defaults:
            self._varname_map = self._defaults.get_varname_map() | self._varname_map
            self._height_vars = self._height_vars.union(self._defaults.height_vars)

        if self._read is False:
            return

        if self.in_memory and self._file is None:
            self.open()
            self.load(self.vars)
            self.close()

    def __enter__(self: "LazyDataset") -> "LazyDataset":
        if self._read is False:
            return self

        if self._file is None or not bool(self._file.id.valid):
            self._file = h5py.File(self.filepath, "r")

        if self._is_jaxa:
            lats_untrimmed = np.array(
                self._file["ScienceData/Geo"][self._varname_map.get(TRACK_LAT_VAR, TRACK_LAT_VAR)][
                    self._slice_along_track
                ],
                dtype=np.float64,
            )
            for height_var in ["height", "binHeight", "bin_height"]:
                try:
                    height_shape = self._file["ScienceData/Geo"][height_var].shape
                    break
                except KeyError:
                    continue
            else:
                raise KeyError("missing height variable")

            self._sizes["along_track"] = height_shape[0]
            self._sizes["vertical"] = height_shape[1]
        else:
            lats_untrimmed = np.array(
                self._file[self._sci_grp][self._varname_map.get(TRACK_LAT_VAR, TRACK_LAT_VAR)][
                    self._slice_along_track
                ],
                dtype=np.float64,
            )

        self._slice_across_track_valid: slice
        if self._nadir_index is not None:
            lats_untrimmed = lats_untrimmed[:, self._slice_across_track]
            lats_untrimmed = LazyDataset._filter_fill_value(lats_untrimmed)
            idxs = np.argwhere(~np.isnan(lats_untrimmed).all(axis=0))
            self._slice_across_track_valid = slice(int(idxs[0][0]), int(idxs[-1][0]) + 1)
            lats_untrimmed = lats_untrimmed[:, self._slice_across_track_valid]

            angle_var = self._varname_map.get(
                SENSOR_ELEVATION_ANGLE_VAR, SENSOR_ELEVATION_ANGLE_VAR
            )
            vars = self.variables
            if angle_var in vars:
                sensor_elevation_angle = np.array(
                    self._file[self._sci_grp][angle_var][:, self._slice_across_track][
                        :, self._slice_across_track_valid
                    ],
                    dtype=np.float32,
                )
                sensor_elevation_angle = LazyDataset._filter_fill_value(sensor_elevation_angle)
                self._nadir_index = int(np.median(np.nanargmax(sensor_elevation_angle, axis=1)))
            elif (
                "viewing_zenith_angle" in vars
            ):  # TODO: extract M-AOT specific nadir index extraction
                angle = np.array(
                    self._file[self._sci_grp]["viewing_zenith_angle"][:, self._slice_across_track][
                        :, self._slice_across_track_valid
                    ],
                    dtype=np.float32,
                )
                angle = LazyDataset._filter_fill_value(angle)
                self._nadir_index = int(np.median(np.nanargmin(angle, axis=1)))

            lats_untrimmed = lats_untrimmed[:, self._nadir_index]
        else:
            self._slice_across_track_valid = slice(None)

        self._slice_along_track_frame: slice = slice(
            *get_frame_slice_tuple(
                lats_untrimmed,
                frame_id=self._info["frame_id"],
            )
        )

        def _add_info_var(_var: str, _rename: str | None = None) -> None:
            if _rename is None:
                _rename = _var
            _lvar = LazyVariable(
                varname=_rename,
                dims=(),
                attrs={},
                values=np.asarray(self._info[_var]),
                _dataset=self,
            )
            self._add_var(_lvar.varname, _lvar)

        _add_info_var("filename")
        _add_info_var("file_type")
        _add_info_var("frame_id")
        _add_info_var("orbit_number")
        _add_info_var("orbit_and_frame")
        _add_info_var("baseline")
        _add_info_var("start_sensing_time", "sensing_start_time")
        _add_info_var("start_processing_time", "processing_start_time")

        lvar_trim_index_offset = LazyVariable(
            varname="trim_index_offset",
            dims=(),
            attrs={},
            values=np.asarray(
                self._slice_along_track_frame.start if self.trim_to_frame else 0, dtype=int
            ),
            _dataset=self,
        )
        self._add_var(lvar_trim_index_offset.varname, lvar_trim_index_offset)

        if self._nadir_index is not None:
            lvar_nadir_index = LazyVariable(
                varname="nadir_index",
                dims=(),
                attrs={"long_name": "Nadir index"},
                values=np.asarray(self._nadir_index),
                _dataset=self,
            )
            self._add_var(lvar_nadir_index.varname, lvar_nadir_index)

        if self.vars is not None:
            self.load(self.vars)

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
            return self.contains(item)
        return self.contains_loaded(item)

    def contains_loaded(self, item: str) -> bool:
        return item in self._data

    def contains(self, item: str) -> bool:
        return self.contains_loaded(item) or (item in self.variables)

    def __getattr__(self, name):
        try:
            return self._data[name]
        except KeyError:
            raise AttributeError(f"'{LazyDataset.__name__}' object has no attribute '{name}'")

    def __dir__(self):
        return super().__dir__() + list(self._data.keys())

    def open(self) -> None:
        if not self.is_open:
            self.__enter__()

    def close(self) -> None:
        if self.is_open:
            self.__exit__(None, None, None)

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
        """Whether the underlying file is open for read."""
        try:
            return bool(self._file.id.valid)
        except AttributeError:
            return False

    @property
    def variables(self) -> list[str]:
        """Names of variables available for access.

        Returns a list of variable names. If the underlying file is still open,
        the list includes both already loaded variables and variables that can be loaded lazily.
        Otherwise, only loaded variables are included.
        """
        if self.is_open:
            if self._is_jaxa:
                return [
                    var
                    for var, var_obj in self._file["ScienceData/Geo"].items()
                    if (
                        isinstance(var_obj, h5py.Dataset)
                        and _get_str_attrs(var_obj.attrs).get("CLASS") != "DIMENSION_SCALE"
                    )
                ] + [
                    var
                    for var, var_obj in self._file["ScienceData/Data"].items()
                    if (
                        isinstance(var_obj, h5py.Dataset)
                        and _get_str_attrs(var_obj.attrs).get("CLASS") != "DIMENSION_SCALE"
                    )
                ]
            return [
                var
                for var, var_obj in self._file[self._sci_grp].items()
                if (
                    isinstance(var_obj, h5py.Dataset)
                    and _get_str_attrs(var_obj.attrs).get("CLASS") != "DIMENSION_SCALE"
                )
            ]
        return list(self._data.keys())

    @property
    def optional_variables(self) -> list[str]:
        if self._defaults:
            return list(self._defaults.generators.keys()) + list(
                self._defaults.optional_generators.keys()
            )
        return []

    @property
    def sizes(self) -> MappingProxyType[str, int]:
        """Mapping from dimension names to lengths."""
        return MappingProxyType(self._sizes)

    @property
    def dims(self) -> list[str]:
        """List of dimension names."""
        return list(self.sizes.keys())

    @property
    def nadir_index(self) -> int | None:
        """Index of the across-track nadir pixel or None if not applicable."""
        return self._nadir_index

    def copy(self) -> "LazyDataset":
        kwargs = {
            f.name: copy.copy(getattr(self, f.name)) for f in fields(self) if f.name != "_file"
        }
        kwargs["_file"] = self._file
        lds = LazyDataset(**kwargs)
        lds._data = {k: v.copy() for k, v in self._data.items()}
        lds._sizes = {k: copy.copy(v) for k, v in self._sizes.items()}
        return lds

    def get(self, var: str) -> LazyVariable:
        """Retrieves a variables by name.

        Variables are returned under the following conditions:

        1. If the variable is already loaded.
        2. If not loaded but a generator exists for the given `var`, generates the variable first.
        3. Otherwise, attempts to load the variable from the underlying dataset file.

        Args:
            var (str): Name of the variable to retrieve.

        Returns:
            LazyVariable: The requested variable.

        Raises:
            KeyError: If `var` refers to a dimension or the variable cannot be loaded.
        """
        if var in self._data:
            return self._data[var]
        elif self._defaults:
            generator = self._defaults.generators.get(var)
            if generator is not None:
                generated_lvars = generator(self)
                for generated_lvar in generated_lvars:
                    if generated_lvar.varname not in self._data:
                        self._add_var(generated_lvar.varname, generated_lvar)
                return generated_lvars[0]

            generator = self._defaults.optional_generators.get(var)
            if generator is not None:
                generated_lvars = generator(self)
                for generated_lvar in generated_lvars:
                    if generated_lvar.varname not in self._data:
                        self._add_var(generated_lvar.varname, generated_lvar)
                return generated_lvars[0]

        lvar_loaded = self._load_var(var)
        if lvar_loaded is None:
            raise KeyError(f"'{var}' is a dimension, not a variable")

        return lvar_loaded

    def _load_var_obj(self, var: str) -> h5py.Dataset:
        """Reads a variable from the underlying file.

        Args:
            var (str): Name of variable to read from file.

        Raises:
            ValueError: If file is closed.
            KeyError: If `var` does not exist in file.

        Returns:
            h5py.Dataset: The requested variable.
        """
        try:
            if self._is_jaxa:
                try:
                    var_obj = self._file["ScienceData/Geo"][var]
                except KeyError:
                    var_obj = self._file["ScienceData/Data"][var]
            else:
                var_obj = self._file[self._sci_grp][var]

            assert isinstance(var_obj, h5py.Dataset)

            return cast(h5py.Dataset, var_obj)

        except KeyError as e:
            if not self.is_open:
                raise ValueError(f"I/O operation on closed file; '{var}' was not loaded yet") from e
            raise e

    def _load_var(
        self,
        var: str,
        dtype: np.dtype | Type[Any] | None = None,
        is_time: bool = False,
        time_unit: Literal["D", "s", "ms", "us", "ns"] | None = "s",
        time_origin: (
            TimestampConvertibleTypes | Literal["julian", "unix"]
        ) = "2000-01-01T00:00:00",
        rolling_w: int | None = None,
    ) -> LazyVariable | None:
        """
        Reads variable from underlying file and applies post-processing according to kind and available defaults.

        Args:
            var (str): Name of the variable.
            dtype (np.dtype | Type[Any] | None, optional): Data type to convert to. Defaults to None.
            is_time (bool, optional): Whether values represent time and should to be converted to `np.datetime`. Defaults to False.
            time_unit (Literal["D", "s", "ms", "us", "ns"] | None, optional): The unit in which time is measured. Defaults to "s".
            time_origin (TimestampConvertibleTypes | Literal["julian", "unix"], optional): The reference date since when time is measured. Defaults to "2000-01-01T00:00:00".
            rolling_w (int | None, optional): Window size for optional rolling mean smoothing. Defaults to None.

        Raises:
            RuntimeError: If `var` is already loaded.

        Returns:
            LazyVariable | None: Returns None if `var` refers to a dimension name. Otherwise, returns the requested and post-processed variable.
        """
        self.logger.debug("* Loading '%s'", var)

        if var in self._data:
            raise RuntimeError(f"variable already loaded: '{var}'")

        var = self._varname_map.get(var, var)

        if var == self._varname_map.get(TIME_VAR, TIME_VAR):
            is_time = True

        var_obj: h5py.Dataset = self._load_var_obj(var)

        attrs: dict[str, str] = _get_str_attrs(var_obj.attrs)
        if attrs.get("CLASS") == "DIMENSION_SCALE":
            return None
        if "units" in attrs:
            attrs["units"] = UNITS_RENAME_MAP.get(attrs["units"], attrs["units"])

        dims = _get_var_obj_dims(var_obj=var_obj, known_sizes=self._sizes)

        _slice: list[slice] = [slice(None)] * len(dims)
        _slice_frame: list[slice] = [slice(None)] * len(dims)
        _slice_across_track_valid: list[slice] = [slice(None)] * len(dims)

        if "along_track" in dims:
            iat = dims.index("along_track")
            _slice[iat] = self._slice_along_track
            _slice_frame[iat] = self._slice_along_track_frame
        if "vertical" in dims:
            _slice[dims.index("vertical")] = self._slice_vertical
        if "across_track" in dims:
            iat = dims.index("across_track")
            _slice[iat] = self._slice_across_track
            _slice_across_track_valid[iat] = self._slice_across_track_valid

        values: NDArray
        if is_time:
            values = np.array(pd.to_datetime(var_obj[*_slice], unit=time_unit, origin=time_origin))
        else:
            values = LazyDataset._filter_fill_value(np.array(var_obj[*_slice], dtype=dtype))

        if isinstance(rolling_w, int):
            if values.ndim == 2 and "along_track" in dims:
                values = rolling_mean_2d(values, rolling_w, axis=dims.index("along_track"))
            elif values.ndim == 1 and dims[0] == "along_track":
                values = rolling_mean_1d(values, rolling_w)

        if self.trim_to_frame:
            values = values[*_slice_frame]

        if self._nadir_index is not None:
            values = values[*_slice_across_track_valid]

        if self.to_geoid and var in self._height_vars and var != GEOID_OFFSET_VAR:
            geoid_offset = self.get(GEOID_OFFSET_VAR)
            if values.ndim == 2 and dims[0] == "along_track":
                values = values - geoid_offset.values[:, np.newaxis]
            elif values.ndim == 1 and dims[0] == "along_track":
                values = values - geoid_offset.values
            elif values.ndim == 2 and dims[1] == "along_track":
                values = values - geoid_offset.values[np.newaxis, :]

        if str(values.dtype) == "|S1":
            values = np.array([b"".join(row).decode("utf-8").strip() for row in values])
            dims = (dims[0],)

        lvar = LazyVariable(
            varname=var,
            dims=dims,
            attrs=attrs,
            values=values,
            _dataset=self,
        )

        self._perform_default_transforms(var, lvar)

        for d, s in zip(dims, values.shape):
            self._sizes.setdefault(d, s)

        self._add_common_var(var, lvar)

        self._add_var(var, lvar)

        return lvar

    def _add_var(self, var: str, lvar: LazyVariable) -> None:
        self.logger.debug("  Adding '%s'", var)

        self._data[var] = lvar
        self._loaded_vars.append(var)

    def load(self, vars: str | Iterable[str] | None = None) -> "LazyDataset":
        if vars is None:
            vars = self.variables
            if self._defaults:
                vars = vars + list(self._defaults.generators.keys())

        if is_iterable_of_str(vars):
            for var in vars:
                self.get(var)
        elif isinstance(vars, str):
            self.get(vars)
        else:
            raise TypeError("expected iterable of strings")

        return self

    def get_profile(
        self,
        var: str,
    ) -> Profile:
        vars = self.variables
        lvar = self.get(var)
        if lvar.dims != ("along_track", "vertical"):
            raise RuntimeError(
                f"not a profile; '{var}' does not contain time/height data: {lvar.dims}"
            )

        profile = Profile(
            values=lvar.values,
            height=self["height"].values,
            time=self["time"].values,
            latitude=(None if "latitude" not in vars else self["latitude"].values),
            longitude=(None if "longitude" not in vars else self["longitude"].values),
            units=lvar.attrs.get("units"),
            label=lvar.attrs.get("long_name"),
            _validate=self._is_validated,
            _is_increasing=self._is_increasing,
        )

        if not self._is_validated:
            self._is_validated = True
            self._is_increasing = profile._is_increasing

        return profile

    def to_xarray(self) -> xr.Dataset:
        ds = xr.Dataset(
            {da.name: da for da in [self[var].to_xarray() for var in self._loaded_vars]}
        )
        ds.encoding["source"] = self.filepath
        return ds

    @classmethod
    def from_xarray(cls, ds: xr.Dataset) -> "LazyDataset":
        new_lds = cls(
            filepath=ds.encoding["source"],
            trim_to_frame=ds["trim_index_offset"].values != 0,
            in_memory=False,
            _read=False,
        )

        for _var in ds.variables:
            var = str(_var)
            dims = ds[var].dims
            shape = ds[var].shape
            lvar = LazyVariable(
                varname=var,
                dims=cast(tuple[str, ...], dims),
                attrs=cast(dict[str, str], ds[var].attrs),
                values=ds[var].values,
                _dataset=new_lds,
            )

            new_lds._data[var] = lvar
            new_lds._loaded_vars.append(var)
            for d, s in zip(dims, shape):
                new_lds._sizes.setdefault(cast(str, d), s)

        return new_lds

    def _get_common_var(self, var: str) -> str | None:
        return {v: k for k, v in self._varname_map.items()}.get(var)

    def _add_common_var(
        self,
        var: str,
        lvar: LazyVariable,
    ) -> bool:
        """Added variable(s) to dataset if given inputs refer to a common variable (e.g., "height", "time", "elevation", ...).

        If `var` refers to a common variable, transforms it for normalization adds given `LazyVariable` to given `LazyDataset`
        instance and returns True. Otherwise, no side effects and returns False.

        Args:
            var (str): Original name of variable (i.e., not standard name but name as used in original dataset file, e.g., "sample_altitude" in A-NOM instead of standard name "height").
            lvar (_LazyVariable): Variable instance that may be transformed.

        Returns:
            bool: If variables where added to dataset returns True. Otherwise, just returns False.
        """
        common_var = self._get_common_var(var)
        if not common_var:
            return False

        func = get_common_var_transformer(common_var)
        if not func:
            return False

        func(common_var, self, lvar)
        return True

    def _perform_default_transforms(self, var: str, lvar: LazyVariable) -> bool:
        if self._defaults:
            func = self._defaults.transforms.get(var)
            if func:
                lvars = func(self, lvar)
                lvar = lvars[0]
                for x in lvars[1:]:
                    self._add_var(x.varname, x)
                return True
        return False
