from dataclasses import dataclass
from typing import Literal

import numpy as np
from numpy.polynomial.legendre import leggauss
from numpy.typing import NDArray


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

    for i, phi in enumerate(lat_radians):
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
        if self.is_reduced:
            lon_bounds_list = self.lon_bounds
        else:
            lon_bounds_list = [self.lon_bounds] * len(lat_bounds)
        areas = []
        for i in range(len(lat_bounds) - 1):
            phi1, phi2 = np.radians(lat_bounds[i]), np.radians(lat_bounds[i + 1])
            dphi = abs(np.sin(phi1) - np.sin(phi2))
            lon_bounds = lon_bounds_list[i]
            for j in range(len(lon_bounds) - 1):
                dlam = np.radians(lon_bounds[j + 1] - lon_bounds[j])
                area = (radius**2) * dphi * dlam
                areas.append(area)

        _areas = np.array(areas)
        if verbose:
            print(f"Mean area [km^2] {np.mean(_areas) / 1e6}")
            print(
                f"Area variation [%]: {100 * (np.max(_areas) - np.min(_areas)) / np.mean(_areas)}",
            )
        return _areas


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

    # Generate longitude bounds (handles reduced=True)
    lon_b_list = _get_lon_bounds_per_lat(nlon, lat_c, reduced)

    # Return centers or bounds
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
