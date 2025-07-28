import os
from pathlib import Path


def extend_filepath(filepath: str, suffix: str) -> str:
    """Appends a suffix to the filename before its extension.

    Args:
        filepath: Absolute file path.
        suffix: String to append to the filename.

    Returns:
        New file path with the suffix added.
    """

    p = Path(os.path.abspath(filepath))
    return str(p.with_name(f"{p.stem}{suffix}{p.suffix}"))
