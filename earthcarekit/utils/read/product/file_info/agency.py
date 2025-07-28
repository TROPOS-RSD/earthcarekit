import os
from typing import overload

import xarray as xr

from ..header_group import read_header_data
from .file_info import FileInfoEnum


class FileAgency(FileInfoEnum):
    ESA = "E"
    JAXA = "J"

    @classmethod
    def from_input(cls, input: str | xr.Dataset) -> "FileAgency":
        """Infers the EarthCARE product agency (i.e. ESA or JAXA) from a given file or dataset."""
        if isinstance(input, str):
            try:
                return cls[input.upper()]
            except AttributeError:
                pass
            except KeyError:
                pass
            try:
                return cls(input.upper())
            except ValueError:
                pass

        return get_file_agency(input)


def _get_file_agency_from_dataset(ds: xr.Dataset) -> FileAgency:
    try:
        return FileAgency(str(ds.File_Class.values)[0])
    except AttributeError as e:
        filepath = ds.encoding["source"]
        filename = os.path.basename(filepath)
        file_class = filename.split(".")[0].split("_")[1]
        return FileAgency(file_class[0])


@overload
def get_file_agency(product: str) -> FileAgency: ...
@overload
def get_file_agency(product: xr.Dataset) -> FileAgency: ...
def get_file_agency(product: str | xr.Dataset) -> FileAgency:
    if isinstance(product, str):
        with read_header_data(product) as ds:
            file_class = _get_file_agency_from_dataset(ds)
    elif isinstance(product, xr.Dataset):
        file_class = _get_file_agency_from_dataset(product)
    else:
        raise NotImplementedError()
    return file_class
