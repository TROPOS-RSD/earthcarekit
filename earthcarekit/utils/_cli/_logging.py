import logging
import os
import time
from datetime import datetime
from logging import Logger
from typing import Literal
import sys
import numpy as np
import pandas as pd


class UnlabledInfoLoggingFormatter(logging.Formatter):
    """Logging formatter that omits level name for INFO messages."""

    def format(self, record):
        if record.levelname == "INFO":
            return record.getMessage()
        return f"[{record.levelname}] {record.getMessage()}"


def ensure_directory(dirpath: str) -> None:
    """Creates directory if not existing"""
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)


def create_logger(logger_name: str, log_to_file: bool, debug: bool = False) -> Logger:
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
        ensure_directory("logs")

        log_filename = f"logs/ecdownload_{time.strftime('%Y%m%dT%H%M%S', time.localtime(time.time()))}.log"
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


def get_counter_message(
    counter: int | None = None, total_count: int | None = None
) -> tuple[str, int]:
    """Creates a formatted counter displaying current and total count (e.g. like this [ 7/10])."""
    max_count_digits = len(str(total_count))
    count_msg = ""
    if counter is not None and total_count is not None:
        count_msg += (
            "["
            + str(counter).rjust(max_count_digits)
            + "/"
            + str(total_count).rjust(max_count_digits)
            + "]"
        )
    elif counter is not None:
        count_msg += "[" + str(counter).rjust(max_count_digits) + "]"
    return count_msg, max_count_digits

def print_stdout(*values: object, sep: str = " ", end: str = "\n", flush: bool = True) -> None:
    """A print-like function using sys.stdout.write() to work with consolce and notebook outputs."""
    text = sep.join(str(v) for v in values) + end
    sys.stdout.write(text)
    if flush:
        sys.stdout.flush()

def console_exclusive_info(*values: object, end: str | None = "\n") -> None:
    """Wrapper for print function (forcibly flush the stream) and without logging"""
    print_stdout(*values, end=end, flush=True)


def log_textbox(
    text: str,
    logger: Logger,
    is_mayor: bool = False,
    line_length: int = 70,
    align: str | Literal["left", "center", "right"] | None = None,
    show_time: bool = False,
) -> None:
    if isinstance(align, str) and align not in ["left", "center", "right"]:
        raise ValueError(
            f'invalid value "{align}" for align, expected "left", "center" or "right"'
        )
    elif align is not None:
        raise TypeError(
            f"invalid type '{type(align).__name__}' for align, expected 'str' or None"
        )
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

    for l in lines:
        if l == "---":
            logger.info(top_left + "-" * line_length + top_right)
            continue
        elif l == "===":
            logger.info(top_left + "-" * line_length + top_right)
            continue

        if align == "left":
            pad_left = 1
            pad_right = line_length - len(l) - 1
        elif align == "center":
            half_pad = (line_length - len(l)) / 2
            pad_left = int(np.floor(half_pad))
            pad_right = int(np.ceil(half_pad))
            # Only show time in left alignment
            time_str = ""
        else:
            pad_left = line_length - len(l) - 1
            pad_right = 1
            # Only show time in left alignment
            time_str = ""

        pad_right = max(0, pad_right - len(time_str))

        logger.info(
            vertical + " " * pad_left + l + " " * pad_right + time_str + vertical
        )
        # Only show time in first line
        time_str = ""

    logger.info(bottom_left + horizontal * line_length + bottom_right)
