import logging
from typing import Final

LOG_FORMAT_USER: Final[str] = "[%(levelname)s] - %(message)s"
LOG_FORMAT_DEV: Final[str] = (
    "%(asctime)s [%(levelname).1s] %(name)s.%(funcName)s:%(lineno)d - %(message)s"
)
LOG_FORMAT_JSON: Final[str] = (
    '{ "time": "%(asctime)s", "level": "%(levelname).1s", "module": "%(name)s", "message": "%(message)s" }'
)
LOG_FORMAT_LINE: Final[str] = (
    "%(asctime)s [%(levelname).1s] %(pathname)s:%(lineno)d - %(message)s"
)


def _setup_logging(
    level: int | str = logging.INFO, format: str = LOG_FORMAT_USER
) -> None:
    logging.getLogger("matplotlib").setLevel(logging.ERROR)
    logging.basicConfig(level=level, format=format)
