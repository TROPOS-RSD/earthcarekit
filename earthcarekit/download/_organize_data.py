"""Ensures that all earthcare data folders are moved correctly in the subfolder structure given by earthcarekit"""

import os
import re
import shutil
from logging import Logger
from pathlib import Path

import pandas as pd

from ..utils.config import ECKConfig
from ..utils.time import time_to_string
from ._eo_product import get_local_product_dirpath


def delete_dir(
    dirpath: str,
    logger: Logger | None = None,
) -> None:
    """Delete a directory and all its contents."""
    if os.path.exists(dirpath):
        shutil.rmtree(dirpath)
        if logger:
            logger.info(f"Deleted directory: <{dirpath}>")
    elif logger:
        logger.info(f"Directory not found: <{dirpath}>")


def organize_data(
    config: ECKConfig,
    dry_run: bool = False,
    create_log_file: bool = False,
    logger: Logger | None = None,
) -> list[dict[str, str]]:
    root_directory = config.path_to_data

    pattern: str = (
        r"^ECA_[EJ][XNO][A-Z]{2}_.........._\d{8}T\d{6}Z_\d{8}T\d{6}Z_\d{5}[ABCDEFGH](\.h5|\.HDR)$"
    )
    time_now: str = time_to_string(pd.Timestamp.now(), format="%Y%m%dT%H%M%S")
    log_filepath: str = f"./organize_data_{time_now}.csv"

    moves_performed: list[dict[str, str]] = []

    for current_dir, subdirs, files in os.walk(root_directory, topdown=False):
        for file in files[:]:
            folder_path: Path = Path(os.path.join(current_dir, file))

            match = re.match(pattern, file)
            if match:
                product_folder = file.split(".")[0]

                target_base: Path = Path(
                    get_local_product_dirpath(
                        root_directory,
                        product_folder,
                        create_subdirs=True,
                        config=config,
                    )
                )
                target_dirpath: Path = Path(os.path.join(target_base, product_folder))
                target_path: Path = Path(
                    os.path.join(target_base, product_folder, file)
                )

                if folder_path == target_path:
                    continue

                move_info = {
                    "source": str(folder_path),
                    "target": str(target_path),
                    "status": "dry_run",
                    "error": "",
                }

                if dry_run:
                    if logger:
                        logger.info(
                            f"[DRY RUN] Would move: <{str(folder_path)}> -> <{str(target_path)}>"
                        )
                        moves_performed.append(move_info)
                else:
                    try:
                        target_dirpath.mkdir(parents=True, exist_ok=True)

                        shutil.move(str(folder_path), str(target_path))
                        if logger:
                            logger.info(
                                f"Moved: <{str(folder_path)}> -> <{str(target_path)}>"
                            )
                        move_info["status"] = "success"
                        moves_performed.append(move_info)

                        # subdirs.remove(subdir)
                    except Exception as e:
                        if logger:
                            logger.info(f"Error moving <{str(folder_path)}>: {e}")

                        if str(target_path) in str(folder_path):
                            delete_dir(str(folder_path), logger=logger)

                        move_info["status"] = "error"
                        move_info["error"] = str(e)
                        moves_performed.append(move_info)

        # Remove empty folders
        with os.scandir(current_dir) as entries:
            has_subdirs = any(entry.is_dir() for entry in entries)
            has_files = len(os.listdir(current_dir)) > 0
            if not has_files and not has_subdirs:
                os.rmdir(current_dir)
                if logger:
                    logger.info(
                        f"Removed empty folder: <{os.path.abspath(current_dir)}>"
                    )

    df = pd.DataFrame(moves_performed)
    if df.size > 0:
        if create_log_file:
            df.to_csv(log_filepath)
            if logger:
                logger.info(f"Saved log to <{os.path.abspath(log_filepath)}>")
    else:
        if logger:
            logger.info("No moves were performed")

    return moves_performed
