import warnings

import numpy as np
import xarray as xr
from scipy.interpolate import interp1d  # type: ignore

from ....constants import (
    DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
)
from ....xarray_utils import merge_datasets
from .._rename_dataset_content import (
    rename_and_create_temperature_vars,
    rename_common_dims_and_vars,
)
from ..file_info import FileAgency
from ..science_group import read_science_data


def add_potential_temperature(
    ds: xr.Dataset,
    temperature_var: str = "temperature_kelvin",
    pressure_var: str = "pressure",
    new_var: str = "potential_temperature",
) -> xr.Dataset:
    """
    Computes potential temperature from temperature [K] and pressure [Pa] and adds it as a variable to the dataset (source: https://en.wikipedia.org/wiki/Potential_temperature, accessed: 2026-02-06).

    Args:
        ds (xr.Dataset): Dataset (e.g., AUX_MET_1D) containing temperature [K] and pressure [Pa] data.
        temperature_var (str, optional): Input temperature variable name. Defaults to "temperature_kelvin".
        pressure_var (str, optional): Input pressure variable name. Defaults to "pressure".
        new_var (str, optional): New variable name for potential temperature. Defaults to "potential_temperature".

    Returns:
        xr.Dataset: Dataset with 2 new variables for potential temperature profiles added (kelvin and celsius).
    """
    t = ds[temperature_var].values  # [K]
    p = ds[pressure_var].values  # [Pa]
    p0 = 100_000.0  # [Pa]
    rcp = 0.286
    potential_t = t * np.pow(p0 / p, rcp)

    attrs = {
        "units": "K",
        "long_name": "Potential temperature",
        "name": "Potential temperature",
    }
    ds[f"{new_var}_kelvin"] = (
        ds[temperature_var].copy().drop_attrs().assign_attrs(attrs)
    )
    ds[f"{new_var}_kelvin"].values = potential_t
    attrs["units"] = r"$^{\circ}$C"
    ds[f"{new_var}_celsius"] = (
        ds[temperature_var].copy().drop_attrs().assign_attrs(attrs)
    )
    ds[f"{new_var}_celsius"].values = potential_t - 273.15

    return ds


def read_product_xmet(
    filepath: str,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
    ensure_nans: bool = DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    **kwargs,
) -> xr.Dataset:
    """Opens AUX_MET_1D file as a `xarray.Dataset`."""
    ds = read_science_data(
        filepath,
        agency=FileAgency.ESA,
        ensure_nans=ensure_nans,
        **kwargs,
    )

    if not modify:
        return ds

    ds = rename_common_dims_and_vars(
        ds=ds,
        tropopause_var="tropopause_height_calipso",
        temperature_var="temperature",
    )

    return ds
