import os
import warnings
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path
from typing import Any, Final, Literal

from .. import __title__

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib  # type: ignore

import tomli_w

DEAULT_CONFIG_FILENAME: Final[str] = "default_config.toml"
DEFAULT_CONFIG_TEXT: Final[
    str
] = '''[local]
# Set a path to your root EarthCARE data directory,
# where local EarthCARE product files will be searched and downloaded to.
data_directory = ""

# Set a path to your root image directory,
# where saved plots will be put.
image_directory = ""

[download]
# You have 2 options to set your data access rights:
# 1. (recommended) Choose one: "commissioning", "calval" or "open", e.g.:
#         collections = "calval"
# 2. List individual collections, e.g.:
#         collections = [
#             "EarthCAREL1InstChecked",
#             "EarthCAREL2InstChecked",
#             ...
#         ]
collections = "open"

# Set your data dissemination service that will be used for remote data search and download.
# Choose one: "oads" or "maap"
platform = "oads"

# If you've choosen "maap", generate a data access token on EarthCARE MAAP and put it here:
# (see <https://portal.maap.eo.esa.int/earthcare/>)
maap_token = ""

# If you've choosen "oads", give your OADS credencials here:
# (see <https://ec-pdgs-dissemination1.eo.esa.int> and <https://ec-pdgs-dissemination2.eo.esa.int>)
oads_username = "my_username"
oads_password = """my_password"""
'''
DEFAULT_CONFIG_SETUP_INSTRUCTIONS: Final[str] = (
    "\n\tPlease create a custom configuration file (TOML).\n"
    "\tTo do this you can follow these steps:\n\n"
    "\t1. Generate a template configuration file by running in your Python code:\n"
    "\t       >>> import earthcarekit as eck\n"
    "\t       >>> eck.create_example_config(path_to_file_or_dir)\n\n"
    "\t2. Edit the fields the generated file using a text editor.\n\n"
    "\t3. Finally to run in your Python code:\n"
    "\t       >>> eck.set_config(path_to_file)\n\n"
    "\tThis will generate a file in your users home directory (see <~/.config/default_config.toml)>\n"
    f"\twhich will be used as the default configuration of '{__title__}'.\n"
)


class DisseminationCollection(StrEnum):
    """Enum for OADS data collection names."""

    EarthCAREL0L1Products = "EarthCAREL0L1Products"
    EarthCAREL1InstChecked = "EarthCAREL1InstChecked"
    EarthCAREL1Validated = "EarthCAREL1Validated"
    EarthCAREL2Products = "EarthCAREL2Products"
    EarthCAREL2InstChecked = "EarthCAREL2InstChecked"
    EarthCAREL2Validated = "EarthCAREL2Validated"
    JAXAL2Products = "JAXAL2Products"
    JAXAL2InstChecked = "JAXAL2InstChecked"
    JAXAL2Validated = "JAXAL2Validated"
    EarthCAREAuxiliary = "EarthCAREAuxiliary"
    EarthCAREXMETL1DProducts10 = "EarthCAREXMETL1DProducts10"
    EarthCAREOrbitData = "EarthCAREOrbitData"

    def to_maap(self) -> str:
        return f"{self.value}_MAAP"


@dataclass
class ECKConfig:
    """Class storing earthcarekit configurations."""

    filepath: str = field(default_factory=str)
    path_to_data: str = field(default_factory=str)
    path_to_images: str = field(default_factory=str)
    oads_username: str = field(default_factory=str)
    oads_password: str = field(default_factory=str)
    collections: list[DisseminationCollection] = field(
        default_factory=lambda: [
            DisseminationCollection.EarthCAREL1Validated,
            DisseminationCollection.EarthCAREL2Validated,
            DisseminationCollection.JAXAL2Validated,
            DisseminationCollection.EarthCAREOrbitData,
        ]
    )
    maap_token: str = field(default_factory=str)
    download_backend: str = "oads"
    user_type: str = "none"

    def __repr__(self):
        data = [
            f"filepath='{self.filepath}'",
            f"path_to_data='{self.path_to_data}'",
            f"path_to_images='{self.path_to_images}'",
            f"oads_username='{self.oads_username}'",
            f"oads_password='***'",
            f"collections='{self.collections}'",
            f"maap_token='{self.maap_token}'",
        ]
        return f"{ECKConfig.__name__}({', '.join(data)})"


def get_default_config_filepath() -> str:
    user_dir = os.path.expanduser("~")
    config_dir = os.path.join(user_dir, ".config", "earthcarekit")
    config_filepath = os.path.join(config_dir, DEAULT_CONFIG_FILENAME)
    return config_filepath


def ensure_filepath(filepath: str) -> None:
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.touch(exist_ok=True)


def get_collections_from_user_type_str(
    user_type_str: Literal["commissioning", "calval", "open", "none"],
) -> list[str]:
    colls_comm = [
        "EarthCAREL0L1Products",
        "EarthCAREL2Products",
        "JAXAL2Products",
    ]

    colls_calval = [
        "EarthCAREAuxiliary",
        "EarthCAREL1InstChecked",
        "EarthCAREL2InstChecked",
        "JAXAL2InstChecked",
    ]

    colls_public = [
        "EarthCAREL1Validated",
        "EarthCAREL2Validated",
        "JAXAL2Validated",
        "EarthCAREXMETL1DProducts10",
        "EarthCAREOrbitData",
    ]

    if user_type_str == "commissioning":
        return colls_comm + colls_calval + colls_public
    elif user_type_str == "calval":
        return colls_calval + colls_public
    elif user_type_str == "open":
        return colls_public
    elif user_type_str == "none":
        return []
    else:
        raise ValueError(
            f'invalid user_type_str "{user_type_str}". expected EarthCARE user types are: "commissioning", "calval", "open" or "none"'
        )


def read_config(config_filepath: str | None = None) -> ECKConfig:
    """Reads and return earthcare-kit configurations."""
    if isinstance(config_filepath, str):
        config_filepath = os.path.abspath(config_filepath)
    elif config_filepath is None:
        config_filepath = get_default_config_filepath()
    else:
        raise TypeError(
            f"got invalid type for `path_to_config` ('{type(config_filepath).__name__}'), expected type 'str'"
        )

    if os.path.exists(config_filepath):
        with open(config_filepath, "rb") as f:
            config = tomllib.load(f)
            try:
                if "Local_file_system" in config:
                    data_dirpath = config["Local_file_system"]["data_directory"]
                    image_dirpath = config["Local_file_system"]["image_directory"]
                else:
                    data_dirpath = config["local"]["data_directory"]
                    image_dirpath = config["local"]["image_directory"]

                download_backend: str
                user_type: Literal["commissioning", "calval", "open", "none"] = "none"
                collections: str | list[str] | None
                if "OADS_credentials" in config:
                    oads_username = config.get("OADS_credentials", dict).get(
                        "username", ""
                    )
                    oads_password = config.get("OADS_credentials", dict).get(
                        "password", ""
                    )
                    collections = config.get("OADS_credentials", dict).get(
                        "collections", None
                    )
                    download_backend = config.get("OADS_credentials", dict).get(
                        "platform", "oads"
                    )
                    maap_token = config.get("OADS_credentials", dict).get(
                        "maap_token", ""
                    )
                else:
                    oads_username = config.get("download", dict).get(
                        "oads_username", ""
                    )
                    oads_password = config.get("download", dict).get(
                        "oads_password", ""
                    )
                    collections = config.get("download", dict).get("collections", None)
                    download_backend = config.get("download", dict).get(
                        "platform", "oads"
                    )
                    maap_token = config.get("download", dict).get("maap_token", "")

                if isinstance(collections, str):
                    if collections.lower() == "commissioning":
                        user_type = "commissioning"
                        collections = get_collections_from_user_type_str(user_type)
                    elif collections.lower() == "calval":
                        user_type = "calval"
                        collections = get_collections_from_user_type_str(user_type)
                    elif collections.lower() == "open":
                        user_type = "open"
                        collections = get_collections_from_user_type_str(user_type)

                _collections: list[DisseminationCollection] = []
                if isinstance(collections, list):
                    _collections = [DisseminationCollection(c) for c in collections]

                eckit_config = ECKConfig(
                    filepath=config_filepath,
                    path_to_data=data_dirpath,
                    path_to_images=image_dirpath,
                    oads_username=oads_username,
                    oads_password=oads_password,
                    collections=_collections,
                    maap_token=maap_token,
                    download_backend=download_backend.lower(),
                    user_type=user_type,
                )
                return eckit_config
            except AttributeError as e:
                raise AttributeError(f"Invalid config file is missing variable: {e}")

    raise FileNotFoundError(
        f"Missing config.toml file ({config_filepath})\n"
        f"{DEFAULT_CONFIG_SETUP_INSTRUCTIONS}"
    )


def set_config(c: str | ECKConfig, verbose: bool = True) -> None:
    _config: ECKConfig
    if isinstance(c, str):
        _config = read_config(c)
    elif isinstance(c, ECKConfig):
        _config = c
    else:
        raise TypeError(
            f"Invalid config! Either give a path to a eckit config TOML file or pass a instance of the class '{ECKConfig.__name__}'"
        )

    config = {
        "local": {
            "data_directory": _config.path_to_data,
            "image_directory": _config.path_to_images,
        },
        "download": {
            "collections": [str(oads_c) for oads_c in _config.collections],
            "platform": _config.download_backend,
            "maap_token": _config.maap_token,
            "oads_username": _config.oads_username,
            "oads_password": _config.oads_password,
        },
    }

    config_filepath = get_default_config_filepath()
    ensure_filepath(config_filepath)

    with open(config_filepath, "wb") as f:
        tomli_w.dump(config, f)

    if verbose:
        print(f"Default configuration file set at <{config_filepath}>")


def create_example_config(target_dirpath: str = ".", verbose: bool = True) -> None:
    filename: str
    dirpath: str = os.path.abspath(target_dirpath)
    if not os.path.isdir(dirpath):
        filename = os.path.basename(dirpath)
        dirpath = os.path.dirname(dirpath)
    else:
        filename = "example_config.toml"

    filepath: str = os.path.join(dirpath, filename)

    config_str = DEFAULT_CONFIG_TEXT

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(config_str)

    if verbose:
        print(f"Example configuration file created at <{filepath}>")


def _warn_user_if_not_default_config_exists() -> None:
    if not os.path.exists(get_default_config_filepath()):
        msg: str = (
            f"Configuration of '{__title__}' is incomplete.\n"
            f"{DEFAULT_CONFIG_SETUP_INSTRUCTIONS}"
        )
        warnings.warn(message=msg)
