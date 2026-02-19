from typing import TYPE_CHECKING, Literal, Union

import xarray as xr

from .fill_values import _convert_all_fill_values_to_nan

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

# To enable static type checking while avoiding circular import error FileAgency
# is imported like this, so it can be used as a type hint later.
if TYPE_CHECKING:
    from .file_info.agency import FileAgency


def read_science_data(
    filepath: str,
    agency: Union["FileAgency", None] = None,
    ensure_nans: bool = False,
    **kwargs,
) -> xr.Dataset:
    """Opens the science data of a EarthCARE file as a `xarray.Dataset`."""
    from .file_info.agency import (
        FileAgency,  # Imported inside function to avoid circular import error
    )

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
