import os
from logging import Logger
from zipfile import BadZipFile, ZipFile

from ..utils._cli import console_exclusive_info, get_counter_message


def unzip_file(
    filepath: str,
    delete: bool = False,
    delete_on_error: bool = False,
    counter: int | None = None,
    total_count: int | None = None,
    logger: Logger | None = None,
) -> bool:
    """
    Extracts file and optionally deletes the original ZIP file upon success or error.

    Args:
        filepath (str): The path to the ZIP file to be extracted.
        delete (bool, optional): If True, the original ZIP file is deleted after extraction. Defaults to False.
        delete_on_error (bool, optional): If True, the ZIP file is deleted if an error occurs during extraction. Defaults to False.
        counter (int or None, optional): A counter to track progress during extraction. Defaults to None.
        total_count (int or None, optional): The total number of files to extract, used for progress tracking. Defaults to None.
        logger (Logger or None, optional): A logger instance to log progress and errors. Defaults to None.

    Returns:
        bool: True if the extraction was successful, False otherwise.
    """
    count_msg, _ = get_counter_message(counter=counter, total_count=total_count)

    if not os.path.exists(filepath):
        if logger:
            logger.info(f" {count_msg} File not found: <{filepath}>")
        return False

    if logger:
        console_exclusive_info(f" {count_msg} Extracting...", end="\r")
    new_filepath = os.path.join(
        os.path.dirname(filepath), os.path.basename(filepath).split(".")[0]
    )
    try:
        with ZipFile(filepath, "r") as zip_file:
            zip_file.extractall(path=new_filepath)
    except BadZipFile as e:
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
            logger.info(
                f" {count_msg} File extracted and ZIP-file deleted. (see <{new_filepath}>)"
            )
    else:
        if logger:
            logger.info(f" {count_msg} File extracted. (see <{new_filepath}>)")

    return True
