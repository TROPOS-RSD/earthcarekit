import os
from typing import overload

import xarray as xr

from ..header_group import read_header_data
from .file_info import FileInfoEnum


class FileMissionID(FileInfoEnum):
    EARTHCARE = "ECA"
