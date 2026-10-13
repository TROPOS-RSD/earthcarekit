"""
**earthcarekit.utils.filesystem**

Filesystem utilities.

## Notes

This module depends on other internal modules:

- [earthcarekit.utils.parse][]

---
"""

import os
from pathlib import Path
from typing import TypeAlias, cast

import pandas as pd

from ._config import ECKConfig, get_config
from .parse import get_file_info_from_str

PathLike: TypeAlias = Path | str


def resolve_subdir(file_type: str, config: ECKConfig | None = None) -> str:
    """Map a EarthCARE file type identifier to its corresponding storage subdirectory.

    Uses configuration values if provided, otherwise falls back to default
    directory names for auxiliary, orbit, and level 0-2B products.

    Args:
        file_type: Product type identifier (e.g., 'AUX_MET_1D', 'ATL_EBD_2A', etc.).
        config: Optional configuration object containing custom subdirectory names.

    Returns:
        Subdirectory name string.
    """
    if isinstance(config, ECKConfig):
        subdir_name_aux_files = config.subdir_name_auxiliary_files
        subdir_name_orb_files = config.subdir_name_orbit_files
        subdir_name_l0__files = config.subdir_name_level0
        subdir_name_l1b_files = config.subdir_name_level1b
        subdir_name_l1c_files = config.subdir_name_level1c
        subdir_name_l2a_files = config.subdir_name_level2a
        subdir_name_l2b_files = config.subdir_name_level2b
    else:
        subdir_name_aux_files = "auxiliary_files"
        subdir_name_orb_files = "orbit_files"
        subdir_name_l0__files = "level0"
        subdir_name_l1b_files = "level1b"
        subdir_name_l1c_files = "level1c"
        subdir_name_l2a_files = "level2a"
        subdir_name_l2b_files = "level2b"

    if file_type in ["AUX_JSG_1D", "AUX_MET_1D"]:
        sub_dirname = subdir_name_aux_files
    elif file_type in ["MPL_ORBSCT", "AUX_ORBPRE", "AUX_ORBRES"]:
        sub_dirname = subdir_name_orb_files
    elif "0" in file_type.lower():
        sub_dirname = subdir_name_l0__files
    elif "1b" in file_type.lower():
        sub_dirname = subdir_name_l1b_files
    elif "1c" in file_type.lower():
        sub_dirname = subdir_name_l1c_files
    elif "2a" in file_type.lower():
        sub_dirname = subdir_name_l2a_files
    elif "2b" in file_type.lower():
        sub_dirname = subdir_name_l2b_files
    return sub_dirname


def construct_filepath(
    file: PathLike,
    *,
    config: ECKConfig | None = None,
    path_to_data: PathLike | None = None,
    subdirs: bool = True,
) -> str:
    """Construct the absolute filesystem path where a file is expected to reside.

    Parses metadata from the filename (date, type, baseline) and applies the
    configured directory template. Enforces '.h5' extension in the result.

    Args:
        file: Input filename or path to parse.
        config: Optional configuration object.
        path_to_data: Optional override for the root data directory.
        subdirs: If True, organize into date/type subdirectories; else flat.

    Returns:
        Absolute path string including the '.h5' extension.
    """
    _config = get_config(config)
    if path_to_data is not None:
        _config.path_to_data = str(path_to_data)

    _info = get_file_info_from_str(file)
    _filename = _info["filename"]
    _file_type = cast(str, _info["file_type"])
    _baseline = cast(str, _info["baseline"])
    _subdir = resolve_subdir(_file_type, config)
    _date = pd.Timestamp(_info["start_sensing_time"]).date()

    if subdirs:
        _path = _config.subdir_template.format(
            **{
                "level": _subdir,
                "file_type": _file_type,
                "year": str(_date.year).zfill(4),
                "month": str(_date.month).zfill(2),
                "day": str(_date.day).zfill(2),
                "baseline": _baseline,
            }
        )
        _path = os.path.join(_config.path_to_data, _path, _filename)
    else:
        _path = os.path.join(_config.path_to_data, _filename)

    return os.path.abspath(os.path.join(_config.path_to_data, _path, _filename + ".h5"))
