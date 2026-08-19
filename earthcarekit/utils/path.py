"""
**earthcarekit.utils.path**

Filesystem path utilities.

## Notes

This module does not depend on other internal modules.

---
"""

import os
import re
from pathlib import Path

from ..typing import PathLike


def extend_filepath(filepath: PathLike, suffix: str) -> str:
    """Appends a suffix to the filename before its extension.

    Args:
        filepath: Absolute file path.
        suffix: String to append to the filename.

    Returns:
        New file path with the suffix added.
    """

    p = Path(os.path.abspath(str(filepath)))
    return str(p.with_name(f"{p.stem}{suffix}{p.suffix}"))


def search_files_by_regex(root: PathLike, pattern: str) -> list[str]:
    """Recursively searches for files matching a regex pattern.

    Args:
        root: Root directory to search.
        pattern: Regular expression pattern to match filenames.

    Returns:
        Absolute paths to matching files.

    Raises:
        FileNotFoundError: If `root` does not exist.
        re.error: If `pattern` is invalid.
    """
    root = str(root)
    if not os.path.exists(root):
        raise FileNotFoundError(
            f"{search_files_by_regex.__name__}() Root directory does not exist: {root}"
        )

    filepaths = []
    for dirpath, _, filenames in os.walk(root):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if re.search(pattern, filename):
                filepaths.append(filepath)
    return filepaths


def ensure_dir(path: PathLike) -> None:
    """Create directory if not existing"""
    _path = Path(path)
    if not os.path.exists(_path):
        os.mkdir(_path)


def ensure_file(path: PathLike) -> None:
    """Create file if not existing"""
    _path = Path(path)
    _path.parent.mkdir(parents=True, exist_ok=True)
    _path.touch(exist_ok=True)
