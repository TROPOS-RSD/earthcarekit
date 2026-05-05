import copy
from dataclasses import dataclass, fields

import numpy as np
import xarray as xr
from numpy.typing import NDArray

from ...profile import ProfileData
from ._typing import _LazyDataset


@dataclass
class LazyVariable:
    varname: str
    dims: tuple[str, ...]
    attrs: dict[str, str]
    values: NDArray

    _dataset: _LazyDataset["LazyVariable"]

    def __array__(self, dtype=None, copy=None):
        arr = self.values

        if dtype is not None:
            arr = arr.astype(dtype)

        if copy:
            arr = arr.copy()

        return arr

    @property
    def data(self) -> NDArray:
        return self.values

    @property
    def shape(self) -> tuple[int, ...]:
        return self.values.shape

    @property
    def sizes(self) -> dict[str, int]:
        return {dim: size for dim, size in zip(self.dims, self.shape)}

    @property
    def dtype(self) -> np.dtype:
        return self.values.dtype

    @property
    def ndim(self) -> int:
        return self.values.ndim

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
            name=self.varname,
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
