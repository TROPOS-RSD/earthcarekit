from dataclasses import dataclass
from typing import Literal

import cartopy.crs as ccrs  # type: ignore
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import xarray as xr
from numpy.polynomial.legendre import leggauss
from numpy.typing import NDArray

from ...np_array_utils import flatten_array


def _get_lon_bounds_per_lat(
    nlon_equator: int,
    lat_centers: NDArray,
    reduced: bool = False,
) -> list[NDArray]:
    """
    Create longitude boudns per latitude.

    Args:
        nlon_equator (int): Number of longitude points at the equator.
        lat_centers (ndarray): Array of latitude centers.
        reduced (bool, optional): Whether to reduce number of longitudes near poles. Defaults to False.

    Returns:
        list[NDArray]: List of longitude bounds per given latitude center.
    """
    lon_bounds_list: list[NDArray] = []
    if not reduced:
        lon_bounds = np.linspace(-180, 180, nlon_equator + 1)
        lon_bounds_list = [lon_bounds] * len(lat_centers)
        return lon_bounds_list

    lat_radians = np.radians(lat_centers)

    for phi in lat_radians:
        scale = np.cos(phi)
        nlon_i = max(4, int(round(nlon_equator * scale)))

        lon_i = np.linspace(-180, 180, nlon_i + 1)
        lon_bounds_list.append(lon_i)

    return lon_bounds_list


def _get_regular_latitudes(nlat: int) -> tuple[NDArray, NDArray]:
    """Generate regular latitudes (equal angular distance)."""
    lat_centers = np.linspace(-90 + 90 / nlat, 90 - 90 / nlat, nlat)
    lat_bounds = np.linspace(-90, 90, nlat + 1)
    return lat_centers, lat_bounds


def _get_sinusoidal_latitudes(nlat: int) -> tuple[NDArray, NDArray]:
    """Generate sinusoidal latitudes (equal area spacing)."""
    mu_edges = np.linspace(-1, 1, nlat + 1)
    mu_centers = 0.5 * (mu_edges[:-1] + mu_edges[1:])
    lat_centers = np.degrees(np.arcsin(mu_centers))
    lat_bounds = np.degrees(np.arcsin(mu_edges))
    return lat_centers, lat_bounds


def _get_gaussian_latitudes(nlat: int) -> tuple[NDArray, NDArray]:
    """Generate Gauss-Legendre latitudes (quadrature points)."""
    mu, _ = leggauss(nlat)
    lat_centers = np.degrees(np.arcsin(mu))
    lat_bounds = np.zeros(nlat + 1)
    lat_bounds[1:-1] = 0.5 * (lat_centers[:-1] + lat_centers[1:])
    lat_bounds[0] = -90.0
    lat_bounds[-1] = 90.0
    return lat_centers, lat_bounds


@dataclass(frozen=True)
class SphericalGrid:
    lat_centers: NDArray
    lon_centers: NDArray | list[NDArray]
    lat_bounds: NDArray
    lon_bounds: NDArray | list[NDArray]
    is_reduced: bool

    def _get_cell_areas(self, radius: float = 6371e3, verbose: bool = True):
        """Compute the area of each grid cell."""
        lat_bounds = self.lat_bounds
        lon_bounds_list: list[NDArray]
        if self.is_reduced and isinstance(self.lon_bounds, list):
            lon_bounds_list = self.lon_bounds
        elif not self.is_reduced and isinstance(self.lon_bounds, np.ndarray):
            lon_bounds_list = [self.lon_bounds] * len(lat_bounds)
        else:
            raise TypeError(
                f"SphericalGrid: lon_bounds has invalid type {type(self.lon_bounds)} for is_reduced={self.is_reduced}.",
                "Expected type list[NDArray] for is_reduced=True and NDArray for is_reduced=False.",
            )
        areas = []
        for i in range(len(lat_bounds) - 1):
            phi1 = np.radians(lat_bounds[i])
            phi2 = np.radians(lat_bounds[i + 1])
            dphi = abs(np.sin(phi1) - np.sin(phi2))
            lon_bounds = lon_bounds_list[i]
            for j in range(len(lon_bounds) - 1):
                dlam = np.radians(lon_bounds[j + 1] - lon_bounds[j])
                area = (radius**2) * dphi * dlam
                areas.append(area)

        _areas = np.array(areas)
        if verbose:
            print(f"Mean area [km^2] {np.mean(_areas) / 1e6:.1f}")
            print(
                f"Area variation [%]: {100 * (np.max(_areas) - np.min(_areas)) / np.mean(_areas):.4f}",
            )
        return _areas

    def _preview(
        self,
        figsize=(10, 6),
        projection: (
            ccrs.Projection
            | Literal[
                "orthographic",
                "platecarree",
                "sinusoidal",
                "robinson",
                "eckertiv",
                "equalearth",
            ]
        ) = ccrs.PlateCarree(),
        color="tab:blue",
        lw=3,
    ):
        if isinstance(projection, str):
            if projection == "orthographic":
                projection = ccrs.Orthographic(central_latitude=45)
            elif projection == "platecarree":
                projection = ccrs.PlateCarree()
            elif projection == "sinusoidal":
                projection = ccrs.Sinusoidal()
            elif projection == "robinson":
                projection = ccrs.Robinson()
            elif projection == "eckertiv":
                projection = ccrs.EckertIV()
            elif projection == "equalearth":
                projection = ccrs.EqualEarth()

        fig, ax = plt.subplots(subplot_kw={"projection": projection}, figsize=figsize)

        ax.coastlines(resolution="110m", lw=1)  # type: ignore
        ax.gridlines(linestyle="dashed", color="black", alpha=0.5)  # type: ignore
        ax.set_global()  # type: ignore

        lats = self.lat_bounds
        lons = self.lon_bounds

        for i, lt in enumerate(lats):
            _ln = np.unique(flatten_array(lons))
            _lt = np.atleast_1d(lt).repeat(len(_ln))
            ax.plot(
                _ln,
                _lt,
                transform=ccrs.PlateCarree(),
                zorder=10,
                color=color,
                linewidth=lw,
            )

        if isinstance(lons, list):
            for i, ln in enumerate(lons):
                for j in range(len(ln) - 1):
                    _ln = np.array(ln[j]).repeat(2)
                    _lt = np.atleast_1d(lats[i : i + 2])
                    ax.plot(
                        _ln,
                        _lt,
                        transform=ccrs.PlateCarree(),
                        zorder=10,
                        color=color,
                        linewidth=lw,
                    )
        else:
            for i, ln in enumerate(lons):
                _lt = lats
                _ln = np.atleast_1d(ln).repeat(len(lats))
                ax.plot(
                    _ln,
                    _lt,
                    transform=ccrs.PlateCarree(),
                    zorder=10,
                    color=color,
                    linewidth=lw,
                )
        return fig, ax


def create_spherical_grid(
    nlat: int,
    nlon: int | None = None,
    reduced: bool = False,
    lat_spacing: Literal["regular", "sinusoidal", "gaussian"] = "regular",
) -> SphericalGrid:
    """
    Generate a spherical gird with regular, sinusoidal or gaussian latitudes and uniform or reduced longitudes.

    Args:
        nlat (int): Number of latitude.
        nlon (int | None): Nuber of longitudes at the equator. If None, set to `nlat * 2`. Defaults to None.
        reduced (bool): If True, reduces longitudes near poles using `~cos(latitude)` scaling. Defaults to False.
        lat_spacing ("regular" or "sinusoidal" or "gaussian", optional): Method used to place latitudes. Defaults to "regular".

    Returns:
        SphericalGrid: A container storing

        - lat_centers: A `numpy.array` of latitude bin centers.
        - lon_centers: A `numpy.array` of longitude bin centers or if `is_reduced=True` a list of `numpy.array` per latitude center.
        - lat_bounds: A `numpy.array` of latitude bin bounds.
        - lon_bounds: A `numpy.array` of longitude bin bounds or if `is_reduced=True` a list of `numpy.array` per latitude bound.
        - is_reduced (bool): Whether the grid has reduced number of longitudes near the poles.
    """

    if nlon is None:
        nlon = nlat + nlat

    if lat_spacing == "regular":
        lat_c, lat_b = _get_regular_latitudes(nlat)
    elif lat_spacing == "sinusoidal":
        lat_c, lat_b = _get_sinusoidal_latitudes(nlat)
    elif lat_spacing == "gaussian":
        lat_c, lat_b = _get_gaussian_latitudes(nlat)
    else:
        raise ValueError("grid_type must be 'regular', 'gaussian', or 'sinusoidal'")

    lon_b_list = _get_lon_bounds_per_lat(nlon, lat_c, reduced)

    lon_b: NDArray | list[NDArray]
    if reduced:
        lon_b = lon_b_list
        lon_c = [0.5 * (lb[:-1] + lb[1:]) for lb in lon_b_list]
    else:
        lon_b = lon_b_list[0]
        lon_c = 0.5 * (lon_b[:-1] + lon_b[1:])

    return SphericalGrid(
        lat_centers=lat_c,
        lon_centers=lon_c,
        lat_bounds=lat_b,
        lon_bounds=lon_b,
        is_reduced=reduced,
    )
