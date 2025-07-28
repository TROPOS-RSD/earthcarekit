import os
from logging import Logger


def _parse_dirpath(
    dirpath: str | None,
    logger: Logger | None = None,
) -> str | None:
    if not isinstance(dirpath, str):
        return None

    dirpath = os.path.abspath(dirpath)

    if not os.path.exists(dirpath):
        raise FileNotFoundError(f"No directory found at <{dirpath}>.")

    return dirpath


def parse_path_to_data(
    path_to_data: str | None,
    logger: Logger | None = None,
) -> str | None:
    try:
        return _parse_dirpath(dirpath=path_to_data, logger=logger)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"No directory found at path_to_data: <{path_to_data}>."
        )


def parse_path_to_imgs(
    path_to_imgs: str | None,
    logger: Logger | None = None,
) -> str | None:
    try:
        return _parse_dirpath(dirpath=path_to_imgs, logger=logger)
    except FileNotFoundError as e:
        raise FileNotFoundError(
            f"No directory found at path_to_imgs: <{path_to_imgs}>."
        )
