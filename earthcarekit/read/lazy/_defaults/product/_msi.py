import numpy as np
from numpy.typing import NDArray

from .....geo import geodesic
from ..._typing import _LazyDataset
from ..._variable import LazyVariable


def _tranform_swath_latitude(
    lds: _LazyDataset[LazyVariable], lvar: LazyVariable
) -> tuple[LazyVariable, *tuple[LazyVariable]]:
    lvar_original = lvar.copy()
    lvar_original.varname = "latitude_swath"
    lvar_original.attrs["earthcarekit"] = (
        "Added by earthcarekit: A copy of the original 'latitude' variable."
    )

    nadir_index: int = lds.nadir_index or 0
    lvar.values = lvar.values[:, nadir_index]
    lvar.dims = ("along_track",)
    lvar.attrs = {
        "long_name": "Latitude",
        "units": "degree_north",
        "notes": "[-90:90]",
        "earthcarekit": "Modified by earthcarekit: Extracted along-track latitude; original data moved to 'swath_latitude' variable.",
    }
    return (lvar, lvar_original)


def _tranform_swath_longitude(
    lds: _LazyDataset[LazyVariable], lvar: LazyVariable
) -> tuple[LazyVariable, *tuple[LazyVariable]]:
    lvar_original = lvar.copy()
    lvar_original.varname = "longitude_swath"
    lvar_original.attrs["earthcarekit"] = (
        "Added by earthcarekit: A copy of the original 'longitude' variable."
    )

    nadir_index: int = lds.nadir_index or 0
    lvar.values = lvar.values[:, nadir_index]
    lvar.dims = ("along_track",)
    lvar.attrs = {
        "long_name": "Longitude",
        "units": "degree_east",
        "notes": "[-180:180]",
        "earthcarekit": "Modified by earthcarekit: Extracted along-track longitude; original data moved to 'swath_longitude' variable.",
    }
    return (lvar, lvar_original)


def _generate_across_track_distance(
    lds: _LazyDataset[LazyVariable],
) -> tuple[LazyVariable, LazyVariable]:
    swath_lat_var = "latitude_swath"
    swath_lon_var = "longitude_swath"
    nadir_index: int = lds.nadir_index or 0
    last_coords = np.vstack((lds[swath_lat_var].values[:, -1], lds[swath_lon_var].values[:, -1])).T
    nadir_coords = np.vstack(
        (lds[swath_lat_var].values[:, nadir_index], lds[swath_lon_var].values[:, nadir_index])
    ).T
    across_track_distances = np.array([], dtype=np.float32)
    from_track_distances = np.array([], dtype=np.float32)
    for i in range(0, lds[swath_lat_var].values.shape[1]):
        sign = 1 if i < nadir_index else -1
        across_track_coords = np.vstack(
            (lds[swath_lat_var].values[:, i], lds[swath_lon_var].values[:, i])
        ).T

        _dists = geodesic(last_coords, across_track_coords, units="m")
        _mean_dists = np.mean(np.atleast_1d(_dists))
        across_track_distances = np.append(across_track_distances, _mean_dists)

        _dists = geodesic(nadir_coords, across_track_coords, units="m")
        _mean_dists = np.mean(np.atleast_1d(_dists)) * sign
        from_track_distances = np.append(from_track_distances, _mean_dists)

    lvar_across = LazyVariable(
        varname="across_track_distance",
        dims=("across_track",),
        attrs={"long_name": "Distance", "units": "m"},
        values=across_track_distances,
        _dataset=lds,
    )
    lvar_from = LazyVariable(
        varname="from_track_distance",
        dims=("across_track",),
        attrs={"long_name": "Distance from track", "units": "m"},
        values=from_track_distances,
        _dataset=lds,
    )

    return lvar_across, lvar_from


def _generate_from_track_distance(
    lds: _LazyDataset[LazyVariable],
) -> tuple[LazyVariable, LazyVariable]:
    lvar_across, lvar_from = _generate_across_track_distance(lds)
    return lvar_from, lvar_across


def _get_bitmasks(bits: NDArray, n: int) -> tuple:
    bits = bits.astype(np.uint16)

    masks: dict[int, int] = {i: 1 << i for i in range(n + 1)}
    bitmasks: dict = {name: (bits & mask) > 0 for name, mask in masks.items()}

    return bits, bitmasks


def _get_dominant_classes(bits: NDArray, n: int) -> NDArray:
    bits, bitmasks = _get_bitmasks(bits, n)

    new_values = np.zeros(bits.shape)
    for i in range(1, n + 1):
        new_values[bitmasks[i]] = i

    return new_values
