import os
from typing import Final

TEMPORARY_DIRNAME: Final[str] = "tmp"


def get_tmp_dirpath() -> str:
    """Returns absoulute path to the folder where temporary files produces by `earthcare-kit` are stored."""
    script_filepath = os.path.abspath(__file__)
    script_dirpath = os.path.dirname(script_filepath)
    tmp_dirpath = os.path.abspath(
        os.path.join(script_dirpath, os.pardir, os.pardir, os.pardir, TEMPORARY_DIRNAME)
    )
    print(tmp_dirpath)
    return tmp_dirpath
