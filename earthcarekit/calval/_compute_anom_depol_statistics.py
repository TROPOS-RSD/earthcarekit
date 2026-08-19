from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
import xarray as xr

from ..data.profile import Profile
from ..plot.figure import ProfileFigure
from ..read.product.level1.atl_nom_1b import add_depol_ratio
from ..typing import DistanceRangeLike, validate_numeric_range


@dataclass(frozen=True)
class _ANOMDepolCalculationResults:
    ds: xr.Dataset
    selection_height_range: tuple[float, float]
    dpol_mean: float
    dpol_std: float
    cpol_mean: float
    cpol_std_t: float
    cpol_std_z: float
    cpol_std: float
    xpol_mean: float
    xpol_std_t: float
    xpol_std_z: float
    xpol_std: float
    error: float
    error_t: float
    error_z: float

    @property
    def stats(self) -> pd.DataFrame:
        return pd.DataFrame(
            dict(
                hmin=[self.selection_height_range[0]],
                hmax=[self.selection_height_range[1]],
                dpol_mean=[self.dpol_mean],
                dpol_std=[self.dpol_std],
                error_t=[self.error_t],
                error_z=[self.error_z],
                error=[self.error],
                cpol_mean=[self.cpol_mean],
                cpol_std_t=[self.cpol_std_t],
                cpol_std_z=[self.cpol_std_z],
                cpol_std=[self.cpol_std],
                xpol_mean=[self.xpol_mean],
                xpol_std_t=[self.xpol_std_t],
                xpol_std_z=[self.xpol_std_z],
                xpol_std=[self.xpol_std],
            )
        )

    def print(self) -> None:
        print("===========================================")
        print(" Statistics: A-NOM depol ratio calculation")
        print("===========================================")
        print(
            f" Height range = {self.selection_height_range[0]} to {self.selection_height_range[1]} meters"
        )
        print(f" mean(depol)  = {self.dpol_mean:.4f}")
        print(f" std(depol)   = {self.dpol_std:.4f}")
        print("-------------------------------------------")
        print(f" error_t      = {self.error_t:.4f}")
        print(f" error_z      = {self.error_z:.4f}")
        print(f" error        = {self.error:.4f}")
        print("-------------------------------------------")
        print(f" mean(cpol)   = {self.cpol_mean:.4e}")
        print(f" std_t(cpol)  = {self.cpol_std_t:.4e}")
        print(f" std_z(cpol)  = {self.cpol_std_z:.4e}")
        print(f" std(cpol)    = {self.cpol_std:.4e}")
        print("-------------------------------------------")
        print(f" mean(xpol)   = {self.xpol_mean:.4e}")
        print(f" std_t(xpol)  = {self.xpol_std_t:.4e}")
        print(f" std_z(xpol)  = {self.xpol_std_z:.4e}")
        print(f" std(xpol)    = {self.xpol_std:.4e}")
        print("===========================================")

    def plot(
        self,
        profile_figure_kwargs: dict[str, Any] = dict(),
        **kwargs,
    ) -> ProfileFigure:
        if "value_range" not in kwargs:
            kwargs["value_range"] = (0, 0.6)
        return ProfileFigure(**profile_figure_kwargs).ecplot(
            ds=self.ds,
            var="depol_ratio_from_means",
            selection_height_range=self.selection_height_range,
            **kwargs,
        )


def compute_anom_depol_statistics(
    ds_anom: xr.Dataset,
    selection_height_range: DistanceRangeLike,
    is_rayleigh_corrected: bool = False,
    rayleigh_correction_factor: float = 0.004,
    **kwargs,
) -> _ANOMDepolCalculationResults:
    """
    Calculate depolarization statistics and uncertainties within a height range.

    This function adds the depol. ratio (`DPOL`) calculated from co- (`CPOL`) and cross-polarized (`XPOL`)
    attenuated backscatter to the dataset (ATL_NOM_1B) and computes related statistics.
    Mean values and standard deviations are calculated for `CPOL`, `XPOL`, and `DPOL` within the selected
    height range. Variability is separated into vertical and temporal components. Errors of `DPOL` are derived
    using error propagation for the `XPOL`/`CPOL` ratio.

    Args:
        ds_anom: ATL_NOM_1B dataset with cross- and co-polar signals.
        selection_height_range: Height range for statistics.
        is_rayleight_corrected: If True, the mean cross-polar profile is corrected by substracting the
            mean rayleigh profile scaled by a correction factor. Defaults to False.
        rayleigh_correction_factor: The scaling factor used when `is_rayleight_corrected` is True.
            Defaults to 0.004.

    Returns:
        Results as a data container with

            - Mean and standard deviation of depolarization ratio.
            - Mean, vertical, temporal, and combined spreads for co- and cross-polar signals.
            - Propagated uncertainty of δ (total, vertical, temporal).
            - Input dataset with depolarization ratio added.

    Examples:
        >>> import earthcarekit as eck
        >>> ds = eck.ecload("ATL_NOM_1B", "01508B", download=True)
        >>> ds = eck.filter_radius(ds, radius_km=100, site="dushanbe")
        >>> results = eck.perform_anom_depol_statistics(
        ...     ds_anom=ds,
        ...     selection_height_range=(1000, 4000),
        ... )
        >>> results.print()
        >>> # results.stats.to_csv("./stats.csv")  # Optionally, save as CSV table
        ===========================================
        Statistics: A-NOM depol ratio calculation
        ===========================================
        Height range = 1000.0 to 4000.0 meters
        mean(depol)  = 0.2270
        std(depol)   = 0.0367
        -------------------------------------------
        error_t      = 0.0551
        error_z      = 0.0542
        error        = 0.1093
        -------------------------------------------
        mean(cpol)   = 4.6728e-07
        std_t(cpol)  = 4.6008e-08
        std_z(cpol)  = 5.0832e-08
        std(cpol)    = 9.6840e-08
        -------------------------------------------
        mean(xpol)   = 1.0639e-07
        std_t(xpol)  = 2.3535e-08
        std_z(xpol)  = 2.2550e-08
        std(xpol)    = 4.6085e-08
        ===========================================

        >>> fig = results.plot(height_range=(0, 10e3))

        <img src="https://raw.githubusercontent.com/TROPOS-RSD/earthcarekit-docs-assets/refs/heads/main/assets/images/api/compute_anom_depol_statistics.png" alt="missing image" height="330">
    """

    selection_height_range = validate_numeric_range(selection_height_range)

    ds_anom = add_depol_ratio(ds_anom, **kwargs)

    cpol_p: Profile = Profile.from_dataset(ds_anom, var="cpol_cleaned_for_ratio_calculation")
    xpol_p: Profile = Profile.from_dataset(ds_anom, var="xpol_cleaned_for_ratio_calculation")
    ray_p: Profile = Profile.from_dataset(ds_anom, var="ray_cleaned_for_ratio_calculation")
    cpol_mean_p: Profile = cpol_p.mean()
    xpol_mean_p: Profile = xpol_p.mean()
    ray_mean_p: Profile = ray_p.mean()

    if is_rayleigh_corrected:
        xpol_mean_p = xpol_mean_p - (ray_mean_p * rayleigh_correction_factor)

    dpol_mean_p: Profile = xpol_mean_p / cpol_mean_p
    cpol_std_p: Profile = cpol_p.std()
    xpol_std_p: Profile = xpol_p.std()

    cpol_stats = cpol_p.stats(selection_height_range)
    if is_rayleigh_corrected:
        xpol_p_corr = xpol_p - (ray_p * rayleigh_correction_factor)
        xpol_stats = xpol_p_corr.stats(selection_height_range)
    else:
        xpol_stats = xpol_p.stats(selection_height_range)
    dpol_stats = dpol_mean_p.stats(selection_height_range)

    dpol_mean: float = dpol_stats.mean
    dpol_std: float = dpol_stats.std
    cpol_mean: float = cpol_stats.mean
    xpol_mean: float = xpol_stats.mean
    cpol_std_t: float = cpol_std_p.stats(selection_height_range).std
    xpol_std_t: float = xpol_std_p.stats(selection_height_range).std
    cpol_std_z: float = cpol_stats.std
    xpol_std_z: float = xpol_stats.std
    cpol_std: float = cpol_std_t + cpol_std_z
    xpol_std: float = xpol_std_t + xpol_std_z

    def calc_error(xsd, csd):
        return np.sqrt((xsd / cpol_mean) ** 2 + (((xpol_mean / (cpol_mean**2)) * csd) ** 2))

    error = calc_error(xpol_std, cpol_std)
    error_z = calc_error(xpol_std_z, cpol_std_z)
    error_t = calc_error(xpol_std_t, cpol_std_t)

    return _ANOMDepolCalculationResults(
        ds=ds_anom.copy(),
        selection_height_range=selection_height_range,
        dpol_mean=dpol_mean,
        dpol_std=dpol_std,
        cpol_mean=cpol_mean,
        cpol_std_t=cpol_std_t,
        cpol_std_z=cpol_std_z,
        cpol_std=cpol_std,
        xpol_mean=xpol_mean,
        xpol_std_t=xpol_std_t,
        xpol_std_z=xpol_std_z,
        xpol_std=xpol_std,
        error=error,
        error_t=error_t,
        error_z=error_z,
    )
