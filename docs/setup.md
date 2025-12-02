# Setup

## Installation

Set up a Python 3.11+ environment with `pip` available, then install the latest version from [PyPI](https://pypi.org/project/earthcarekit/):

```shell
pip install earthcarekit

# Check installed version
ecdownload -V

# Update to the latest release whenever needed
pip install earthcarekit --upgrade

# Note for conda users: To avoid mixing conda and system packages, use instead
python -m pip install earthcarekit [--upgrade]
```

<details>
<summary><strong>Advanced:</strong> Install Latest Pre-Release from GitHub.</summary>

```shell
pip install -U git+https://github.com/TROPOS-RSD/earthcarekit.git

# Or, install manually from a local clone
pip install .
```
</details>

## Configuration

Set up a configuration file to define storage paths and access to data platforms. ESA products require an ESA account. Applied via Python, the settings are saved at ~/.config/earthcarekit/default_config.toml.

Before using the package, you need to set up a configuration file to define storage paths and download credentials.
Downloading EarthCARE products requires an ESA account.
You can create one at [OADS](https://ec-pdgs-dissemination2.eo.esa.int/oads/access/collection) or [MAAP](https://portal.maap.eo.esa.int/earthcare/)

Once applied via Python, your settings are saved to your home directory at `~/.config/earthcarekit/default_config.toml`.

!!! warning
    As of August 2025, data dissemination is transitioning from OADS to MAAP.
    OADS is still recommended for now, but will be phased out by the end of 2025.

<details>
<summary><strong>Example:</strong> See an example configuration file.</summary>

```toml title="example_config.toml"
[local]
# Set a path to your root EarthCARE data directory,
# where local EarthCARE product files will be searched and downloaded to.
data_directory = ""

# Set a path to your root image directory,
# where saved plots will be put.
image_directory = ""

# Optionally, customize the sub-folder structure used in your data directory
[local.data_directory_structure]
subdir_template = "{level}/{file_type}/{year}/{month}/{day}/{baseline}"
subdir_name_auxiliary_files = "auxiliary_files"
subdir_name_orbit_files = "orbit_files"
subdir_name_level0 = "level0"
subdir_name_level1b = "level1b"
subdir_name_level1c = "level1c"
subdir_name_level2a = "level2a"
subdir_name_level2b = "level2b"

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
# (see <https://portal.maap.eo.esa.int/ini/services/auth/token/>)
maap_token = ""

# Using MAAP you can speed up the download by only downloading the .h5-file excluding the related header file .HDR.
maap_include_header_file = false

# If you've choosen "oads", give your OADS credencials here:
# (see <https://ec-pdgs-dissemination1.eo.esa.int> and <https://ec-pdgs-dissemination2.eo.esa.int>)
oads_username = "my_username"
oads_password = """my_password"""
```
</details>

### Configuration via the Python Interpreter

1. Open the Python interpreter and generate an example configuration file in your current directory:

    ```shell
    $ python
    >>> import earthcarekit as eck
    >>> eck.create_example_config()
    ```

2. Edit the generated file.
   
    Follow the instructions in the inline comments of the exsample file to customize your settings.
    You may rename and save your file to any location.

3. Go back to the Python Interpreter and apply your configuration file as default:

    ```shell
    >>> eck.set_config(path_to_file)
    >>> exit()
    ```

You can later view or manually edit the saved configuration at `~/.config/earthcarekit/default_config.toml`. To update your settings, you can also simply repeat the steps above.
