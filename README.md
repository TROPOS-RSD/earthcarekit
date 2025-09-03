<picture align="center">
  <source media="(prefers-color-scheme: dark)" srcset="./docs/images/logos/earthcarekit-logo-lightblue.png">
  <img alt="logo" src="./docs/images/logos/earthcarekit-logo-blue.png">
</picture>

---

[![GitHub License](https://img.shields.io/github/license/TROPOS-RSD/earthcarekit?label=license&color=green)](https://github.com/TROPOS-RSD/earthcarekit/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-online-brightgreen)](https://tropos-rsd.github.io/earthcarekit/)
[![GitHub Tag](https://img.shields.io/github/v/tag/TROPOS-RSD/earthcarekit?label=latest&color=blue&logo=github)](https://github.com/TROPOS-RSD/earthcarekit/tags)
[![PyPI - Latest Version](https://img.shields.io/pypi/v/earthcarekit?label=latest%20on%20PyPI&color=blue)](https://pypi.org/project/earthcarekit/)
[![GitHub commits since latest](https://img.shields.io/github/commits-since/TROPOS-RSD/earthcarekit/latest.svg?color=blue)](https://github.com/TROPOS-RSD/earthcarekit/commits/main)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.16813294.svg)](https://doi.org/10.5281/zenodo.16813294)

A Python package to simplify working with EarthCARE satellite data.

> ⚠️ **Project Status: In Development**
> 
> This project is still under active development.
> It is **not yet feature-complete**, and parts of the **user documentation are missing or incomplete**.
> Use at your own risk and expect breaking changes.
> Feedback and contributions are welcome!

- **Documentation:** https://tropos-rsd.github.io/earthcarekit/
- **Source code:** https://github.com/TROPOS-RSD/earthcarekit
- **Examples:** https://github.com/TROPOS-RSD/earthcarekit/tree/main/examples/notebooks
- **Feature requests and bug reports:** https://github.com/TROPOS-RSD/earthcarekit/issues

## What is `earthcarekit`?

**`earthcarekit`** is an open-source Python package that provides comprehensive and flexible tools for downloading, reading, analysing and visualizing data from [ESA](https://earth.esa.int/eogateway/missions/earthcare) (European Space Ageny) and [JAXA](https://www.eorc.jaxa.jp/EARTHCARE/index.html)'s (Japan Aerospace Exploration Agency) joint satellite mission EarthCARE (Earth Cloud, Aerosol and Radiation Explorer, [Wehr et al., 2023](https://doi.org/10.5194/amt-16-3581-2023)). The goal of this software is to support the diverse calibration/validation (cal/val) and scientific efforts related to the mission and provide easy-to-use functions for new EarthCARE data users.

You can find more info about the package, setup, and usage in the [documentation](https://tropos-rsd.github.io/earthcarekit/).

## Contact

The package is developed and maintained by [Leonard König](https://orcid.org/0009-0004-3095-3969) at Leibniz Institute for Tropospheric Research ([TROPOS](https://www.tropos.de/en/)).
For questions, suggestions, or bug reports, please [create an issue](https://github.com/TROPOS-RSD/earthcarekit/issues) or reach out via [email](mailto:koenig@tropos.de).

## Acknowledgments

Colormap definitions for `calipso` and `chiljet2` were adapted from the exellent [ectools](https://bitbucket.org/smason/workspace/projects/EC) repository by Shannon Mason ([ECMWF](https://www.ecmwf.int/)).

## Citation

If you use this software in your work, please cite it.
We recommend citing the specific version you are using, which you can select on [Zenodo](https://doi.org/10.5281/zenodo.16813294).

Alternatively, if you want to cite version-independent use:

```bibtex
@software{koenig_2025_earthcarekit,
  author       = {König, Leonard and
                  Floutsi, Athena Augusta and
                  Haarig, Moritz and
                  Baars, Holger and
                  Wandinger, Ulla},
  title        = {earthcarekit: A Python package to simplify working
                   with EarthCARE satellite data
                  },
  month        = aug,
  year         = 2025,
  publisher    = {Zenodo},
  doi          = {10.5281/zenodo.16813294},
  url          = {https://doi.org/10.5281/zenodo.16813294},
}
```

or in text:

> König, L., Floutsi, A. A., Haarig, M., Baars, H., & Wandinger, U. (2025). earthcarekit: A Python package to simplify working with EarthCARE satellite data. Zenodo. [https://doi.org/10.5281/zenodo.16813294](https://doi.org/10.5281/zenodo.16813294)

## License

This project is licensed under the MIT License (see [LICENSE](https://github.com/TROPOS-RSD/earthcarekit/blob/main/LICENSE) file or [https://opensource.org/license/mit](https://opensource.org/license/mit)). See also third-party licenses listed in the [documentation](https://tropos-rsd.github.io/earthcarekit/#third-party-licenses).

## References

- Wehr, T., Kubota, T., Tzeremes, G., Wallace, K., Nakatsuka, H., Ohno, Y., Koopman, R., Rusli, S., Kikuchi, M., Eisinger, M., Tanaka, T., Taga, M., Deghaye, P., Tomita, E., and Bernaerts, D.: The EarthCARE mission – science and system overview, Atmos. Meas. Tech., 16, 3581–3608, https://doi.org/10.5194/amt-16-3581-2023, 2023.