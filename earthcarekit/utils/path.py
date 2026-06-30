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
    """Recursively searches for files in a directory that match a given regex pattern.

    Args:
        root (str): The root directory to start the search from.
        pattern (str): A regular expression pattern to match file names against.

    Return:
        list[str]: A list of absolute file paths that point to files with matching names.

    Raises:
        FileNotFoundError: If the root directory does not exist.
        re.error: If the given pattern is not a valid regular expression.
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
