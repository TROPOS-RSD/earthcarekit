import os
from logging import Logger

from ...config import ECKConfig, get_default_config_filepath, read_config


def parse_path_to_config(
    path_to_config: str | None,
    logger: Logger | None = None,
) -> ECKConfig:
    if not isinstance(path_to_config, str):
        path_to_config = get_default_config_filepath()

    if not os.path.exists(path_to_config):
        raise FileNotFoundError(f"No config file found at <{path_to_config}>.")

    config = read_config(path_to_config)

    return config
