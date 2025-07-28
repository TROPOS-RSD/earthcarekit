import os
import re


def search_files_by_regex(root_dirpath: str, regex_pattern: str) -> list[str]:
    """
    Recursively searches for files in a directory that match a given regex pattern.

    Args:
        root_dirpath (str): The root directory to start the search from.
        regex_pattern (str): A regular expression pattern to match file names against.

    Return:
        list[str]: A list of absolute file paths that point to files with matching names.

    Raises:
        FileNotFoundError: If the root directory does not exist.
        re.error: If the given pattern is not a valid regular expression.
    """
    if not os.path.exists(root_dirpath):
        raise FileNotFoundError(
            f"{search_files_by_regex.__name__}() Root directory does not exist: {root_dirpath}"
        )

    filepaths = []
    for dirpath, _, filenames in os.walk(root_dirpath):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if re.search(regex_pattern, filename):
                filepaths.append(filepath)
    return filepaths
