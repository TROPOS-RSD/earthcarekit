import logging
import os
import sys
import time
from logging import Logger
from typing import Literal

import numpy as np
import pandas as pd

from ..path import ensure_dir


class UnlabledInfoLoggingFormatter(logging.Formatter):
    """Logging formatter that omits level name for INFO messages."""

    def format(self, record):
        if record.levelname == "INFO":
            return record.getMessage()
        return f"[{record.levelname}] {record.getMessage()}"


def create_logger(
    logger_name: str,
    log_to_file: bool,
    debug: bool = False,
) -> Logger:
    """Creates logger with special handlers for console and optionally log files."""
    logger = logging.getLogger(logger_name)
    logger.propagate = False
    logger.handlers.clear()

    logger.setLevel(logging.DEBUG)

    # console logs
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(UnlabledInfoLoggingFormatter())
    if debug:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)
    logger.addHandler(console_handler)
    # file logs (optional)
    if log_to_file:
        ensure_dir("logs")

        log_filename = (
            f"logs/ecdownload_{time.strftime('%Y%m%dT%H%M%S', time.localtime(time.time()))}.log"
        )
        # Ensure that a new log is created instead of appending to an existing log
        new_log_filename = log_filename
        i = 2
        while os.path.exists(new_log_filename):
            new_log_filename = log_filename.replace(
                ".log",
                f"_{i}.log",
            )
            i = i + 1

        file_handler = logging.FileHandler(new_log_filename, mode="a")
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    return logger


def log_textbox(
    text: str,
    logger: Logger | None,
    is_mayor: bool = False,
    line_length: int = 70,
    align: str | Literal["left", "center", "right"] | None = None,
    show_time: bool = False,
) -> None:
    if not isinstance(logger, Logger):
        return None

    if isinstance(align, str) and align not in ["left", "center", "right"]:
        raise ValueError(f'invalid value "{align}" for align, expected "left", "center" or "right"')
    elif align is not None:
        raise TypeError(f"invalid type '{type(align).__name__}' for align, expected 'str' or None")
    else:
        if is_mayor:
            align = "center"
        else:
            align = "left"

    top_left = "#" if is_mayor else "+"
    top_right = "#" if is_mayor else "+"
    bottom_right = "#" if is_mayor else "+"
    bottom_left = "#" if is_mayor else "+"
    vertical = "#" if is_mayor else "|"
    horizontal = "=" if is_mayor else "-"

    lines = text.split("\n")

    logger.info(top_left + horizontal * line_length + top_right)

    time_str: str = ""
    if show_time:
        time_str = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S") + " "

    for line in lines:
        if line == "---":
            logger.info(top_left + "-" * line_length + top_right)
            continue
        elif line == "===":
            logger.info(top_left + "-" * line_length + top_right)
            continue

        if align == "left":
            pad_left = 1
            pad_right = line_length - len(line) - 1
        elif align == "center":
            half_pad = (line_length - len(line)) / 2
            pad_left = int(np.floor(half_pad))
            pad_right = int(np.ceil(half_pad))
            # Only show time in left alignment
            time_str = ""
        else:
            pad_left = line_length - len(line) - 1
            pad_right = 1
            # Only show time in left alignment
            time_str = ""

        pad_right = max(0, pad_right - len(time_str))

        logger.info(vertical + " " * pad_left + line + " " * pad_right + time_str + vertical)
        # Only show time in first line
        time_str = ""

    logger.info(bottom_left + horizontal * line_length + bottom_right)
