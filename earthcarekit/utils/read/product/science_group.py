from typing import TYPE_CHECKING, Union

import xarray as xr

from .fill_values import _convert_all_fill_values_to_nan

# To enable static type checking while avoiding circular import error FileAgency
# is imported like this, so it can be used as a string-based type hin later.
if TYPE_CHECKING:
    from .file_info.agency import FileAgency


def read_science_data(
    filepath: str, agency: Union["FileAgency", None] = None
) -> xr.Dataset:
    """Opens the science data of a EarthCARE file as a `xarray.Dataset`."""
    from .file_info.agency import (
        FileAgency,  # Imported inside function to avoid circular import error
    )

    if agency is None:
        agency = FileAgency.from_input(filepath)

    if agency == FileAgency.ESA:
        ds = xr.open_dataset(filepath, group="ScienceData")
    elif agency == FileAgency.JAXA:
        df_cpr_geo = xr.open_dataset(
            filepath, group="ScienceData/Geo", engine="h5netcdf", phony_dims="sort"
        )
        df_cpr_data = xr.open_dataset(
            filepath, group="ScienceData/Data", engine="h5netcdf", phony_dims="sort"
        )
        ds = xr.merge([df_cpr_data, df_cpr_geo])
        ds.encoding["source"] = df_cpr_data.encoding["source"]
    else:
        raise NotImplementedError()

    ds = _convert_all_fill_values_to_nan(ds)

    return ds
