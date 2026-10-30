import warnings
from dataclasses import dataclass
from enum import StrEnum
from typing import Any, Literal, TypeAlias, cast

import numpy as np
from numpy.typing import ArrayLike, NDArray
from xarray import Dataset

from ..utils.numpy import rolling_mean_2d
from ..utils.sentinels import UNSET, Unset, is_set


class RatioType(StrEnum):
    PDR = "PDR"
    BSR = "BSR"
    BSR_M1 = "BSR_M1"

    @property
    def var_name(self) -> str:
        return {
            self.PDR: "depol_ratio",
            self.BSR: "bsc_ratio",
            self.BSR_M1: "bsc_ratio_minus_one",
        }[self]

    @property
    def long_name(self) -> str:
        return {
            self.PDR: "Part. depol. ratio",
            self.BSR: "Bsc. ratio",
            self.BSR_M1: r"Bsc. ratio $-1$",
        }[self]

    @property
    def short_name(self) -> str:
        return {
            self.PDR: "PDR",
            self.BSR: "BSR",
            self.BSR_M1: "BSR-1",
        }[self]

    @property
    def description(self) -> str:
        return {
            self.PDR: "Computed with: xpol / cpol",
            self.BSR: "Computed with: (cpol + xpol + ray) / ray",
            self.BSR_M1: "Computed with: (cpol + xpol) / ray",
        }[self]

    @property
    def units(self) -> str:
        return ""

    @property
    def attrs(self) -> dict[str, str]:
        return {
            "long_name": self.long_name,
            "short_name": self.short_name,
            "units": self.units,
            "earthcarekit": self.description,
        }

    @classmethod
    def from_input(cls, value: Any) -> "RatioType":
        if isinstance(value, RatioType):
            return value
        elif isinstance(value, str):
            if value.lower() in ("pdr", "x/c", "depol_ratio"):
                return cls.PDR
            elif value.lower() in ("bsr", "(c+x+r)/r", "bsc_ratio"):
                return cls.PDR
            elif value.lower() in ("bsr_m1", "bsrm1", "bsr-1", "(c+x)/r", "bsc_ratio_minus_one"):
                return cls.BSR_M1
        raise ValueError(f"invalid ratio type: '{value}'")


def _get_cleaned_var_names() -> dict[Literal["cpol", "xpol", "ray"], str]:
    return {
        "cpol": "cpol_cleaned_for_ratio_calculation",
        "xpol": "xpol_cleaned_for_ratio_calculation",
        "ray": "ray_cleaned_for_ratio_calculation",
    }


def _get_cleaned_attrs(
    rolling_w: int, tol: float, elevation_margin: float, bsr_thresh: float | Unset
) -> dict[Literal["cpol", "xpol", "ray"], dict[str, str]]:
    if is_set(bsr_thresh):
        info = f"Added by earthcarekit: Rolling mean applied (w={rolling_w}), values below BSR threshold (BSR>{bsr_thresh:.2f}) and first {elevation_margin}m above elevation height set to NaN"
    else:
        info = f"Added by earthcarekit: Rolling mean applied (w={rolling_w}), near-zero values (tol={tol}) and first {elevation_margin}m above elevation height set to NaN"
    return {
        "cpol": {
            "label": "Co-polar atten. part. bsc.",
            "units": "m$^{-1}$ sr$^{-1}$",
            "earthcarekit": info,
        },
        "xpol": {
            "label": "Cross-polar atten. part. bsc.",
            "units": "m$^{-1}$ sr$^{-1}$",
            "earthcarekit": info,
        },
        "ray": {
            "label": "Ray. atten. bsc.",
            "units": "m$^{-1}$ sr$^{-1}$",
            "earthcarekit": info,
        },
    }


RatioTypeLike: TypeAlias = (
    Literal["PDR", "BSR", "BSR-1"] | Literal["x/c", "(c+x+r)/r", "(c+x)/r"] | RatioType | str
)


def nan_mean(a: ArrayLike, axis: int | None = None) -> NDArray | float:
    """Compute the mean while ignoring NaNs."""
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        a = np.asarray(a)
        return np.nanmean(a, axis=axis)


def calc_pdr(cpol: ArrayLike, xpol: ArrayLike) -> NDArray:
    """Computes particle depolarization ratio (PDR) from aerosol backscatter.

    Args:
        cpol: Aerosol co-polarized backscatter.
        xpol: Aerosol cross-polarized backscatter.

    Returns:
        PDR array; zero-division bins masked as NaN.
    """
    return np.asarray(xpol) / np.where(cpol == 0.0, np.nan, cpol)


def calc_bsr(cpol: ArrayLike, xpol: ArrayLike, ray: ArrayLike) -> NDArray:
    """Computes backscatter ratio (BSR) from aerosol and molecular backscatter.

    Args:
        cpol: Aerosol co-polarized backscatter.
        xpol: Aerosol cross-polarized backscatter.
        ray: Rayleigh (molecular) backscatter.

    Returns:
        BSR array; zero-division bins masked as NaN.
    """
    bsc_aer = np.asarray(cpol) + np.asarray(xpol)
    bsc_mol = np.where(ray == 0.0, np.nan, ray)
    return (bsc_aer + bsc_mol) / bsc_mol


def calc_bsr_m1(cpol: ArrayLike, xpol: ArrayLike, ray: ArrayLike) -> NDArray:
    """Computes backscatter ratio minus one (BSR-1) from aerosol and molecular backscatter.

    Args:
        cpol: Aerosol co-polarized backscatter.
        xpol: Aerosol cross-polarized backscatter.
        ray: Rayleigh (molecular) backscatter.

    Returns:
        BSR-1 array; zero-division bins masked as NaN.
    """
    bsc_aer = np.asarray(cpol) + np.asarray(xpol)
    bsc_mol = np.where(ray == 0.0, np.nan, ray)
    return bsc_aer / bsc_mol


def calc_sr(
    ratio_type: RatioTypeLike,
    cpol: ArrayLike,
    xpol: ArrayLike,
    ray: ArrayLike | Unset = UNSET,
) -> NDArray:
    """Computes a scattering ratio (PDR, BSR, or BSR-1) from aerosol and molecular backscatter.

    Args:
        ratio_type: Target ratio type (PDR, BSR, or BSR-1).
        cpol: Aerosol co-polarized backscatter.
        xpol: Aerosol cross-polarized backscatter.
        ray: Rayleigh (molecular) backscatter; required for BSR and BSR-1.

    Returns:
        Scattering ratio array; zero-division bins masked as NaN.
    """
    ratio_type = RatioType.from_input(ratio_type)
    if ratio_type is RatioType.PDR:
        return calc_pdr(cpol, xpol)
    if not is_set(ray):
        raise TypeError(f"missing required argument 'ray' to calculate '{ratio_type.var_name}'")
    if ratio_type is RatioType.BSR:
        return calc_bsr(cpol, xpol, cast(ArrayLike, ray))
    return calc_bsr_m1(cpol, xpol, cast(ArrayLike, ray))


def _get_near_zero_mask(
    ratio_type: RatioType, cpol: NDArray, ray: NDArray, tol: float
) -> NDArray[np.bool_]:
    if ratio_type == RatioType.PDR:
        return np.isclose(cpol, 0, atol=tol)
    return np.isclose(ray, 0, atol=tol)


@dataclass(frozen=True)
class ScattRatioResult:
    """Container for scattering ratio calculation results.

    Attributes:
        ratio: Computed scattering ratio array.
        ratio_mean: Mean of the scattering ratio profile.
        cpol_cleaned: Cleaned co-polarized backscatter signal.
        xpol_cleaned: Cleaned cross-polarized backscatter signal.
        ray_cleaned: Cleaned Rayleigh (molecular) backscatter signal.
    """

    ratio_type: RatioType
    ratio: NDArray
    ratio_mean: NDArray
    cleaned: dict[Literal["cpol", "xpol", "ray"], NDArray]

    def __array__(self, dtype=None, copy=None):
        if copy is False:
            return np.asarray(self.ratio, dtype=dtype)
        return np.asarray(self.ratio, dtype=dtype, copy=copy)

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        inputs = tuple(np.asarray(x) if isinstance(x, ScattRatioResult) else x for x in inputs)
        kwargs = {
            k: np.asarray(v) if isinstance(v, ScattRatioResult) else v for k, v in kwargs.items()
        }
        return getattr(ufunc, method)(*inputs, **kwargs)


def calc_scatt_ratio(
    ratio_type: RatioTypeLike,
    cpol: ArrayLike,
    xpol: ArrayLike,
    ray: ArrayLike,
    elevation: ArrayLike | Unset = UNSET,
    height: ArrayLike | Unset = UNSET,
    bsr_thresh: float | Unset = UNSET,
    smooth: bool = True,
    rolling_w: int = 20,
    mask_zero: bool = True,
    tol: float = 2e-7,
    elevation_margin: float = 300,
) -> ScattRatioResult:
    """Computes a scattering ratio with signal cleaning and temporal averaging.

    Supported ratios:
        - PDR: Particle Depolarization Ratio (`xpol / cpol`).
        - BSR: Backscatter Ratio (`(cpol + xpol + ray) / ray`).
        - BSR-1: Aerosol-to-Molecular Backscatter Ratio (`(cpol + xpol) / ray`).

    Args:
        ratio_type: Target ratio type (PDR, BSR, or BSR-1).
        cpol: Aerosol co-polarized backscatter.
        xpol: Aerosol cross-polarized backscatter.
        ray: Rayleigh (molecular) backscatter.
        elevation: Surface elevation; masks bins above threshold if provided.
        height: Vertical coordinate array; used with `elevation` for surface masking.
        bsr_thresh: BSR threshold for signal cleaning; if provided, used over near-zero masking.
        smooth: If True, apply along-track rolling mean smoothing.
        rolling_w: Window size for the rolling mean smoothing.
        mask_zero: If True, mask near-zero division bins; ignored if `bsr_thresh` is set.
        tol: Threshold for masking near-zero division bins.
        elevation_margin: Vertical margin above surface to mask in meters.

    Returns:
        `ScattRatioResult` with ratio array, cleaned signals, and mean profile.
    """
    ratio_type = RatioType.from_input(ratio_type)
    cpol = np.asarray(cpol)
    xpol = np.asarray(xpol)
    ray = np.asarray(ray)

    # Mask surface bins
    if is_set(elevation) and is_set(height):
        elevation = np.asarray(elevation)
        height = np.asarray(height)
        elevation = elevation[:, np.newaxis] + elevation_margin
        mask = height < elevation
        cpol = np.where(mask, np.nan, cpol)
        xpol = np.where(mask, np.nan, xpol)
        ray = np.where(mask, np.nan, ray)

    # Smooth signals using moving average
    if smooth:
        cpol = rolling_mean_2d(cpol, rolling_w, axis=0)
        xpol = rolling_mean_2d(xpol, rolling_w, axis=0)
        ray = rolling_mean_2d(ray, rolling_w, axis=0)

    # Clean signals using threshold
    if is_set(bsr_thresh):
        mask = calc_bsr(cpol, xpol, ray) < bsr_thresh
    elif mask_zero:
        mask = _get_near_zero_mask(ratio_type, cpol, ray, tol)
    else:
        mask = np.full(cpol.shape, False, dtype=np.bool_)
    cpol = np.where(mask, np.nan, cpol)
    xpol = np.where(mask, np.nan, xpol)
    ray = np.where(mask, np.nan, ray)

    # Calculate scattering ratio
    ratio = calc_sr(ratio_type, cpol, xpol, ray)
    ratio_mean = calc_sr(
        ratio_type=ratio_type,
        cpol=nan_mean(cpol, axis=0),
        xpol=nan_mean(xpol, axis=0),
        ray=nan_mean(ray, axis=0),
    )

    return ScattRatioResult(
        ratio_type=ratio_type,
        ratio=ratio,
        ratio_mean=ratio_mean,
        cleaned={"cpol": cpol, "xpol": xpol, "ray": ray},
    )


def _add_scatt_ratio_results_to_dataset(
    ds: Dataset,
    res: ScattRatioResult,
    rolling_w: int,
    tol: float,
    elevation_margin: float,
    bsr_thresh: float | Unset,
    height_var: str = "height",
) -> Dataset:
    dims = ds[height_var].dims
    rt = res.ratio_type
    var = rt.var_name
    var_from_means = f"{var}_from_means"
    ds[var] = (dims, res.ratio)
    ds[var_from_means] = (dims[1], res.ratio_mean)

    for v in (var, var_from_means):
        ds[v] = ds[v].assign_attrs(rt.attrs)

    cleaned_var_names = _get_cleaned_var_names()
    cleaned_var_attrs = _get_cleaned_attrs(rolling_w, tol, elevation_margin, bsr_thresh)
    for key, values in res.cleaned.items():
        var = cleaned_var_names[key]
        attrs = cleaned_var_attrs[key]
        ds[var] = (dims, values)
        ds[var] = ds[var].assign_attrs(attrs)

    return ds


def add_scatt_ratio(
    ds: Dataset,
    ratio_type: RatioTypeLike,
    smooth: bool = True,
    rolling_w: int = 20,
    bsr_thresh: float | Unset = UNSET,
    mask_zero: bool = True,
    tol: float = 2e-7,
    elevation_margin: int = 300,
    cpol_var: str = "mie_attenuated_backscatter",
    xpol_var: str = "crosspolar_attenuated_backscatter",
    ray_var: str = "rayleigh_attenuated_backscatter",
    elevation_var: str = "elevation",
    height_var: str = "height",
    **kwargs,
) -> Dataset:
    """Computes scattering ratio from attenuated backscatter signals.

    Applies surface masking, rolling mean smoothing, and near-zero tolerance handling.

    Supported ratios:
        - PDR: Particle Depolarization Ratio (`xpol / cpol`).
        - BSR: Backscatter Ratio (`(cpol + xpol + ray) / ray`).
        - BSR-1: Aerosol-to-Molecular Backscatter Ratio (`(cpol + xpol) / ray`).

    Args:
        ds: Dataset with cross-, co-polar and rayleigh attenuated backscatter (e.g., A-NOM).
        ratio_type: Target ratio type (PDR, BSR, or BSR-1).
        smooth: If True, apply along-track rolling mean smoothing.
        rolling_w: Window size for the rolling mean smoothing.
        bsr_thresh: BSR threshold for signal cleaning; if provided, used over near-zero masking.
        mask_zero: If True, mask near-zero division bins; ignored if `bsr_thresh` is set.
        tol: Threshold for masking near-zero division bins.
        elevation_margin: Vertical margin above surface to mask in meters.
        cpol_var: Co-polar variable name; defaults to "mie_attenuated_backscatter".
        xpol_var: Cross-polar variable name; defaults to "crosspolar_attenuated_backscatter".
        ray_var: Rayleigh variable name; defaults to "rayleigh_attenuated_backscatter".
        elevation_var: Elevation variable name.
        height_var: Height variable name.
    Returns:
        Dataset with scattering ratio, cleaned signals, and mean ratio profile added.
    """
    # Collect all common args for wrapped plot function call
    local_args = locals()

    # Handle deprecated arguments
    def _get_depr_arg(old_name: str, new_name: str) -> Any:
        if old_name in kwargs:
            msg = f"'{old_name}' is deprecated and will be removed in future versions; use '{new_name}' instead."
            warnings.warn(msg, FutureWarning, stacklevel=2)
            out = kwargs.get(old_name, local_args[new_name])
            del kwargs[old_name]
            return out
        return local_args[new_name]

    elevation_margin = _get_depr_arg("skip_height_above_elevation", "elevation_margin")
    tol = _get_depr_arg("near_zero_tolerance", "tol")

    res = calc_scatt_ratio(
        ratio_type=ratio_type,
        cpol=ds[cpol_var].values,
        xpol=ds[xpol_var].values,
        ray=ds[ray_var].values,
        elevation=ds[elevation_var].values,
        height=ds[height_var].values,
        bsr_thresh=bsr_thresh,
        smooth=smooth,
        rolling_w=rolling_w,
        mask_zero=mask_zero,
        tol=tol,
        elevation_margin=elevation_margin,
    )

    return _add_scatt_ratio_results_to_dataset(
        ds=ds,
        res=res,
        height_var=height_var,
        rolling_w=rolling_w,
        tol=tol,
        elevation_margin=elevation_margin,
        bsr_thresh=bsr_thresh,
    )


def add_depol_ratio(
    ds: Dataset,
    smooth: bool = True,
    rolling_w: int = 20,
    bsr_thresh: float | Unset = UNSET,
    mask_zero: bool = True,
    tol: float = 2e-7,
    elevation_margin: int = 300,
    cpol_var: str = "mie_attenuated_backscatter",
    xpol_var: str = "crosspolar_attenuated_backscatter",
    ray_var: str = "rayleigh_attenuated_backscatter",
    elevation_var: str = "elevation",
    height_var: str = "height",
    **kwargs,
) -> Dataset:
    """Computes particle depolarization ratio (PDR = `xpol / cpol`) from attenuated backscatter signals.

    Applies surface masking, rolling mean smoothing, and near-zero tolerance handling.

    Args:
        ds: Dataset with cross-, co-polar and rayleigh attenuated backscatter (e.g., A-NOM).
        smooth: If True, apply along-track rolling mean smoothing.
        rolling_w: Window size for the rolling mean smoothing.
        bsr_thresh: BSR threshold for signal cleaning; if provided, used over near-zero masking.
        mask_zero: If True, mask near-zero division bins; ignored if `bsr_thresh` is set.
        tol: Threshold for masking near-zero division bins.
        elevation_margin: Vertical margin above surface to mask in meters.
        cpol_var: Co-polar variable name; defaults to "mie_attenuated_backscatter".
        xpol_var: Cross-polar variable name; defaults to "crosspolar_attenuated_backscatter".
        ray_var: Rayleigh variable name; defaults to "rayleigh_attenuated_backscatter".
        elevation_var: Elevation variable name.
        height_var: Height variable name.

    Returns:
        Dataset with particle depolarization ratio, cleaned signals, and mean ratio profile added.
    """
    # Collect all common args for wrapped plot function call
    local_args = locals()

    # Handle deprecated arguments
    def _get_depr_arg(old_name: str, new_name: str) -> Any:
        if old_name in kwargs:
            msg = f"'{old_name}' is deprecated and will be removed in future versions; use '{new_name}' instead."
            warnings.warn(msg, FutureWarning, stacklevel=2)
            out = kwargs.get(old_name, local_args[new_name])
            del kwargs[old_name]
            return out
        return local_args[new_name]

    elevation_margin = _get_depr_arg("skip_height_above_elevation", "elevation_margin")
    tol = _get_depr_arg("near_zero_tolerance", "tol")

    return add_scatt_ratio(
        ds=ds,
        ratio_type=RatioType.PDR,
        smooth=smooth,
        rolling_w=rolling_w,
        bsr_thresh=bsr_thresh,
        mask_zero=mask_zero,
        tol=tol,
        elevation_margin=elevation_margin,
        cpol_var=cpol_var,
        xpol_var=xpol_var,
        ray_var=ray_var,
        elevation_var=elevation_var,
        height_var=height_var,
    )


def get_depol_profile(
    ds: Dataset,
    cpol_cleaned_var: str = "cpol_cleaned_for_ratio_calculation",
    xpol_cleaned_var: str = "xpol_cleaned_for_ratio_calculation",
) -> NDArray:
    """Compute part. depol. ratio profile from cleaned co- and cross-polar backscatter mean profiles."""
    cpol = ds[cpol_cleaned_var].data
    xpol = ds[xpol_cleaned_var].data
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        mean_xpol_bsc = np.nanmean(xpol, axis=0)
        mean_mie_bsc = np.nanmean(cpol, axis=0)
    return mean_xpol_bsc / mean_mie_bsc
