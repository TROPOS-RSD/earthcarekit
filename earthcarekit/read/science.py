from typing import Literal, Union

import xarray as xr

from ..utils.xarray import _convert_all_fill_values_to_nan
from .info.agency import FileAgency

_engine: (
    Literal[
        "netcdf4",
        "scipy",
        "pydap",
        "h5netcdf",
        "zarr",
    ]
    | None
) = "netcdf4"


def read_science_data(
    filepath: str,
    agency: Union["FileAgency", None] = None,
    ensure_nans: bool = False,
    **kwargs,
) -> xr.Dataset:
    """Opens the science data of a EarthCARE file as a `xarray.Dataset`."""
    if agency is None:
        agency = FileAgency.from_input(filepath)

    if agency == FileAgency.ESA:
        ds = xr.open_dataset(filepath, group="ScienceData", engine=_engine, **kwargs)
    elif agency == FileAgency.JAXA:
        df_cpr_geo = xr.open_dataset(
            filepath,
            group="ScienceData/Geo",
            engine=_engine,
            phony_dims="sort",
            **kwargs,
        )
        df_cpr_data = xr.open_dataset(
            filepath,
            group="ScienceData/Data",
            engine=_engine,
            phony_dims="sort",
            **kwargs,
        )
        ds = xr.merge([df_cpr_data, df_cpr_geo])
        ds.encoding["source"] = df_cpr_data.encoding["source"]
    else:
        raise NotImplementedError()

    if ensure_nans:
        ds = _convert_all_fill_values_to_nan(ds)

    return ds
