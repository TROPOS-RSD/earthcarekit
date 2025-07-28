import os
from typing import overload

import xarray as xr

from ..header_group import read_header_data
from .file_info import FileInfoEnum


class FileLatency(FileInfoEnum):
    NEAR_REAL_TIME = "N"
    OFFLINE = "O"
    NOT_APPLICABLE = "X"

    @classmethod
    def from_input(cls, input: str | xr.Dataset) -> "FileLatency":
        """Infers the EarthCARE product latency indicator (i.e. N for Near-real time, O for Offline, X for not applicable) from a given name, file or dataset."""
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

        return get_file_latency(input)


def _get_file_latency_from_dataset(ds: xr.Dataset) -> FileLatency:
    try:
        return FileLatency(str(ds.File_Class.values)[1])
    except AttributeError as e:
        filepath = ds.encoding["source"]
        filename = os.path.basename(filepath)
        file_class = filename.split(".")[0].split("_")[1]
        return FileLatency(file_class[1])


@overload
def get_file_latency(product: str) -> FileLatency: ...
@overload
def get_file_latency(product: xr.Dataset) -> FileLatency: ...
def get_file_latency(product: str | xr.Dataset) -> FileLatency:
    if isinstance(product, str):
        with read_header_data(product) as ds:
            file_class = _get_file_latency_from_dataset(ds)
    elif isinstance(product, xr.Dataset):
        file_class = _get_file_latency_from_dataset(product)
    else:
        raise NotImplementedError()
    return file_class
