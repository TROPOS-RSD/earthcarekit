import os
import shutil
from logging import Logger
from pathlib import Path
from zipfile import BadZipFile, ZipFile

from ..utils._cli.ui import console_print, format_counter


def remove_redundant_folder(dirpath: str | Path, verbose: bool = False) -> None:
    dirpath = Path(dirpath)
    redundant_subdirpath = dirpath / dirpath.name

    if redundant_subdirpath.is_dir():
        if verbose:
            print(f"Found redundant folder: {redundant_subdirpath}")

        for item in redundant_subdirpath.iterdir():
            target = dirpath / item.name
            if verbose:
                print(f"Moving {item} -> {target}")
            shutil.move(str(item), str(target))

        redundant_subdirpath.rmdir()
        if verbose:
            print(f"Removed redundant folder: {redundant_subdirpath}")

    else:
        if verbose:
            print(f"No redundant folder found in {dirpath}")


def unzip_file(
    filepath: str,
    delete: bool = False,
    delete_on_error: bool = False,
    counter: int | None = None,
    total_count: int | None = None,
    logger: Logger | None = None,
) -> bool:
    """Extracts a ZIP file and optionally deletes it upon success or error.

    Args:
        filepath: Path to the ZIP file.
        delete: Delete ZIP file after successful extraction if True.
        delete_on_error: Delete ZIP file on error if True.
        counter: Progress counter for logging.
        total_count: Total files for progress tracking.
        logger: Logger for progress/error messages.

    Returns:
        True if extraction succeeded, False otherwise.
    """
    count_msg, _ = format_counter(current=counter, total=total_count)

    if not os.path.exists(filepath):
        if logger:
            logger.info(f" {count_msg} File not found: <{filepath}>")
        return False

    if logger:
        console_print(f" {count_msg} Extracting...", end="\r")
    new_filepath = os.path.join(os.path.dirname(filepath), os.path.basename(filepath).split(".")[0])

    try:
        with ZipFile(filepath, "r") as zip_file:
            zip_file.extractall(path=new_filepath)
        remove_redundant_folder(new_filepath)
    except BadZipFile:
        if delete_on_error:
            os.remove(filepath)
            if logger:
                logger.info(f" {count_msg} Unzip failed! ZIP-file was deleted.")
        else:
            if logger:
                logger.info(f" {count_msg} Unzip failed! <{filepath}>")
        return False

    if delete:
        os.remove(filepath)
        if logger:
            logger.info(f" {count_msg} File extracted and ZIP-file deleted. (see <{new_filepath}>)")
    else:
        if logger:
            logger.info(f" {count_msg} File extracted. (see <{new_filepath}>)")

    return True
