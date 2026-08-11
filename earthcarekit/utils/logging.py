"""
**earthcarekit.utils.logging**

Logging utilities.

## Notes

This module does not depend on other internal modules.

---
"""

import logging
from contextlib import contextmanager
from typing import Final

LOG_FORMAT_USER: Final[str] = "[%(levelname)s] - %(message)s"
"""Concise log format intended for end users."""

LOG_FORMAT_DEV: Final[str] = (
    "%(asctime)s [%(levelname).1s] %(name)s.%(funcName)s:%(lineno)d - %(message)s"
)
"""Detailed log format intended for development and debugging."""

LOG_FORMAT_JSON: Final[str] = (
    '{ "time": "%(asctime)s", "level": "%(levelname).1s", "module": "%(name)s", "message": "%(message)s" }'
)
"""JSON log format intended for structured log processing."""

LOG_FORMAT_LINE: Final[str] = "%(asctime)s [%(levelname).1s] %(pathname)s:%(lineno)d - %(message)s"
"""Detailed log format including source file and line number."""


def set(level: int | str = logging.INFO, format: str = LOG_FORMAT_USER) -> None:
    """Configure logging and supress versboe third-party output."""
    logging.getLogger("fsspec.caching").setLevel(logging.WARNING)
    logging.getLogger("matplotlib").setLevel(logging.ERROR)
    logging.basicConfig(level=level, format=format)


@contextmanager
def silence_logger(logger: logging.Logger, level=logging.CRITICAL):
    """Temporarily raise the logging level of a given logger.

    Example:
        ```python
        from earthcarekit.utils.logging import silence_logger

        logger = logging.getLogger()

        logger.info("This message is logged.")

        with silence_logger(logger):
            logger.info("This message is NOT logged!")

        logger.info("This message is logged again.")
        ```
    """
    prev_level = logger.level
    logger.setLevel(level)
    try:
        yield
    finally:
        logger.setLevel(prev_level)
