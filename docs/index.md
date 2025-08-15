[![GitHub License](https://img.shields.io/github/license/TROPOS-RSD/earthcarekit?label=license&color=green)](https://github.com/TROPOS-RSD/earthcarekit/blob/main/LICENSE)
[![PyPI - Latest Version](https://img.shields.io/pypi/v/earthcarekit?label=latest&color=blue)](https://pypi.org/project/earthcarekit/)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16813765.svg)](https://doi.org/10.5281/zenodo.16813765)

A Python package to simplify working with EarthCARE satellite data.

!!! caution
    **Project Status: In Development**

    This project is still under active development.
    It is **not yet feature-complete**, and parts of the **user documentation are missing or incomplete**.
    Use at your own risk and expect breaking changes.
    Feedback and contributions are welcome!


## Key Features

- ⬇️ **Download** - Access EarthCARE data via the command line or your Python scripts.
- 🔍 **Search & Read** - Search your local EarthCARE products and open them as `xarray.Dataset` objects with unified dimension names.
- ⚙️ **Process** - Make use of a comprehensive set of functions, including filtering by time or geographic location, extracting vertical profile statistics, rebinning, along-track interpolation from X-MET files, and merging consecutive EarthCARE datasets, and more.
- 📊 **Visualize** - Create quicklooks and plot vertical and across-track time series using a set of `matplotlib`/`cartopy`-based figure objects - while allowing customization.
- 💻 **Command-Line Interface Tools:**
    - [`ecdownload`](./ecdownload.md) - Search, select, and download EarthCARE data from a terminal.
    - [`ecquicklook`](./ecquicklook.md) - Create fast preview visualisations of EarthCARE datasets from a terminal.

## License

This project is licensed under the MIT License (see [LICENSE](https://github.com/TROPOS-RSD/earthcarekit/blob/main/LICENSE) file or [https://opensource.org/license/mit](https://opensource.org/license/mit)).

#### Third-Party Licenses

This project relies on several open-source packages. Their licenses include:
- MIT License: [`plotly`](https://dash.plotly.com/), [`cmcrameri`](https://github.com/callumrollo/cmcrameri), [`vedo`](https://vedo.embl.es/), [`netcdf4`](https://unidata.github.io/netcdf4-python/), [`tomli-w`](https://github.com/hukkin/tomli-w)
- BSD License: [`numpy`](https://numpy.org/), [`pandas`](https://pandas.pydata.org/), [`scipy`](https://scipy.org/), [`seaborn`](https://seaborn.pydata.org/), [`owslib`](https://github.com/geopython/OWSLib), [`jupyterlab`](https://jupyter.org/), [`h5netcdf`](https://h5netcdf.org/index.html)
- Apache 2.0 License: [`xarray`](https://xarray.dev/)
- LGPL License: [`cartopy`](https://scitools.org.uk/cartopy/docs/latest/)
- PSF License: [`matplotlib`](https://matplotlib.org/)

Please refer to each project's repository for detailed license information.

## Contact

Developed and maintained by [Leonard König](https://orcid.org/0009-0004-3095-3969) ([TROPOS](https://www.tropos.de/en/)).
For questions, suggestions, or bug reports, please create an issue or reach out via email: koenig@tropos.de

## Citation

If you use this software in your work, please cite it.
We recommend citing the specific version you are using, which you can find on [Zenodo](https://doi.org/10.5281/zenodo.16813765).

## Acknowledgments

Colormap definitions for `calipso` and `chiljet2` were adapted from the exellent [ectools](https://bitbucket.org/smason/workspace/projects/EC) repository by Shannon Mason (ECMWF).
