# earthcarekit

[![GitHub License](https://img.shields.io/github/license/TROPOS-RSD/earthcarekit?label=license&color=green&style=flat-square&)](https://github.com/TROPOS-RSD/earthcarekit/blob/main/LICENSE)
[![GitHub Tag](https://img.shields.io/github/v/tag/TROPOS-RSD/earthcarekit?label=latest&color=blue&style=flat-square&logo=github)](https://github.com/TROPOS-RSD/earthcarekit/tags)
[![PyPI - Latest Version](https://img.shields.io/pypi/v/earthcarekit?label=latest%20on%20PyPI&color=blue&style=flat-square)](https://pypi.org/project/earthcarekit/)
[![GitHub commits since latest](https://img.shields.io/github/commits-since/TROPOS-RSD/earthcarekit/latest.svg?color=blue&style=flat-square)](https://github.com/TROPOS-RSD/earthcarekit/commits/main)

A Python package to simplify working with EarthCARE satellite data.

> ⚠️ **Project Status: In Development**
> 
> This project is still under active development.
> It is **not yet feature-complete**, and parts of the **user documentation are missing or incomplete**.
> Use at your own risk and expect breaking changes.
> Feedback and contributions are welcome!

## Key Features

- ⬇️ **Download** - Access EarthCARE data from ESA's dissemination platfroms [OADS](https://ec-pdgs-dissemination2.eo.esa.int/oads/access/collection) or [MAAP](https://portal.maap.eo.esa.int/earthcare/) via the command line or your Python scripts.
- 🔍 **Search & Read** - Search your local EarthCARE products and open them as `xarray.Dataset` objects with unified dimension names.
- ⚙️ **Process** - Filter data by time or geographic location, extract vertical profile statistics, rebin to common grids, interpolate along-track vertical cross sections from X-MET files and merge datasets from consecutive EarthCARE frames.
- 📊 **Visualize** - Create quicklooks and plot vertical and across-track time series using a set of preset `matplotlib`/`cartopy`-based figure objects - while allowing customization.
- 💻 **Command-line interface tools:**
  - [`ecdownload`](https://github.com/TROPOS-RSD/earthcarekit/blob/main/docs/ecdownload.md) - Search, select, and download EarthCARE data from a terminal.
  - [`ecquicklook`](https://github.com/TROPOS-RSD/earthcarekit/blob/main/docs/ecquicklook.md) - Create fast quicklooks of your local EarthCARE products from a terminal.

## Getting Started

### Step 1 - Installation

Set up a Python 3.11+ environment with `pip` available, then install the latest version from [PyPI](https://pypi.org/project/earthcarekit/):

```shell
pip install earthcarekit
```

> 💡 Note: To update the package to the latest version run:
> 
> ```shell
> pip install earthcarekit --upgrade
> ```
> 
> Check the installed version with:
> ```shell
> python -c "import earthcarekit; print(earthcarekit.__version__)"
> ```

Alternatively, install the latest development version from GitHub with:

```shell
pip install -U git+https://github.com/TROPOS-RSD/earthcarekit.git
```

Or, install manually from a local clone:

```shell
pip install .
```

### Step 2 - Configuration

An initial configuration step is required to specify default paths for storing data and created images, as well as to set up access to the supported data dissemination platforms for downloading.
This involves creating and editing a configuration file.
Once applied via Python code, your settings will be saved to `~/.config/earthcarekit/default_config.toml`.

Below, the configuration process is shown using the Python command line interpreter:

1. **Open the Python interpreter and generate an example configuration file in your current directory:**

    ```python
    $ python
    >>> import earthcarekit as eck
    >>> eck.create_example_config()
    ```

2. **Edit the generated file.**
   
   Follow the instructions in the inline comments of the exsample file to customize your settings. You may rename and save your file to any location.
3. **Go back to the Python Interpreter and apply your configuration file as default:**

    ```python
    >>> eck.set_config(path_to_file)
    >>> exit()
    ```

You can later view or manually edit the saved configuration at `~/.config/earthcarekit/default_config.toml`. To update your settings, you can also simply repeat the steps above.

## Tutorials

See usage examples:
- Jupyter notebooks: [examples/notebooks/](https://github.com/TROPOS-RSD/earthcarekit/tree/main/examples/notebooks)
- Documentation: [docs/tutorials.md](https://github.com/TROPOS-RSD/earthcarekit/blob/main/docs/tutorials.md).

## Author

Developed and maintained by [Leonard König](https://orcid.org/0009-0004-3095-3969) ([TROPOS](https://www.tropos.de/en/)).

## Contact

For questions, suggestions, or bug reports, please create an issue or reach out via email: koenig@tropos.de

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

### Third-Party Licenses

This project relies on several open-source packages. Their licenses include:
- MIT License: `plotly`, `cmcrameri`, `vedo`, `netcdf4`, `tomli-w`
- BSD License: `numpy`, `pandas`, `scipy`, `seaborn`, `owslib`, `jupyterlab`, `h5netcdf`
- Apache 2.0 License: `xarray`
- LGPL License: `cartopy`
- PSF License: `matplotlib`

Please refer to each project's repository for detailed license information.

## Acknowledgments

Colormap definitions for `calipso` and `chiljet2` were adapted from the exellent [ectools](https://bitbucket.org/smason/workspace/projects/EC) repository by Shannon Mason (ECMWF).