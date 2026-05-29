import warnings

import numpy as np
from numpy.typing import NDArray

from .....utils.numpy import rolling_mean_2d
from ....info.type import FileType
from ..._typing import _LazyDataset
from ..._variable import LazyVariable
from .. import ProductDefaults, register


def _create_ref_lvar(
    lds: _LazyDataset[LazyVariable], lvar: LazyVariable, values: NDArray
) -> LazyVariable:
    return LazyVariable(
        varname="plot_radarReflectivityFactor",
        dims=lvar.dims,
        attrs={
            "long_name": "Radar reflectivity",
            "units": "dBZ",
            "earthcarekit": "Added by earthcarekit: Intended for use in curtain plots only!",
        },
        values=values,
        _dataset=lds,
    )


def _create_dvel_lvar(
    lds: _LazyDataset[LazyVariable], lvar: LazyVariable, values: NDArray
) -> LazyVariable:
    return LazyVariable(
        varname="plot_dopplerVelocity",
        dims=lvar.dims,
        attrs={
            "long_name": "Doppler velocity",
            "units": "m/s",
            "earthcarekit": "Added by earthcarekit: Intended for use in curtain plots only!",
        },
        values=values,
        _dataset=lds,
    )


def _get_ref_values_and_mask(
    lvar_ref: LazyVariable,
) -> tuple[NDArray, NDArray]:
    values_ref = lvar_ref.values.copy()
    # Create plotting ready radar reflectivity and doppler velocity variables
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        values_ref = 10 * np.log10(values_ref)
    values_ref = rolling_mean_2d(values_ref, 3, axis=1)
    values_ref = rolling_mean_2d(values_ref, 10, axis=0)
    mask = values_ref < -27
    return values_ref, mask


def _get_dvel_values(
    lvar_dvel: LazyVariable,
) -> NDArray:
    values_dvel = lvar_dvel.values.copy()
    values_dvel = rolling_mean_2d(values_dvel, 3, axis=1)
    values_dvel = rolling_mean_2d(values_dvel, 10, axis=0)
    return values_dvel


def _generate_plot_radar_reflectivity(
    lds: _LazyDataset[LazyVariable],
) -> tuple[LazyVariable, LazyVariable]:
    lvar_ref = lds["radarReflectivityFactor"]
    values_ref, mask = _get_ref_values_and_mask(lvar_ref)

    lvar_dvel = lds["dopplerVelocity"]
    values_dvel = _get_dvel_values(lvar_dvel)

    values_ref[mask] = np.nan
    values_dvel[mask] = np.nan

    return (
        _create_ref_lvar(lds, lvar_ref, values_ref),
        _create_dvel_lvar(lds, lvar_dvel, values_dvel),
    )


def _generate_plot_doppler_velocity(
    lds: _LazyDataset[LazyVariable],
) -> tuple[LazyVariable, LazyVariable]:
    lvar_ref, lvar_dvel = _generate_plot_radar_reflectivity(lds)
    return lvar_dvel, lvar_ref


def _transform_doppler_velocity(
    lds: _LazyDataset[LazyVariable], lvar: LazyVariable
) -> tuple[LazyVariable, *tuple[LazyVariable, ...]]:
    # change the sign of the doppler velocity
    lvar.values = lvar.values * -1
    lvar.attrs["earthcare"] = "Sign convention changed: values inverted (+/-)"

    return (lvar,)


def _remove_nans_from_heights(
    lds: _LazyDataset[LazyVariable], lvar: LazyVariable
) -> tuple[LazyVariable, *tuple[LazyVariable, ...]]:
    with warnings.catch_warnings():  # ignore warings about all-nan values
        warnings.simplefilter("ignore", category=RuntimeWarning)
        lvar.values[np.isnan(lvar.values)] = np.nanmin(lvar.values)

    return (lvar,)


register(
    file_type=FileType.CPR_NOM_1B.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="profileTime",
        height_var="binHeight",
        elevation_var="surfaceElevation",
        land_flag_var="navigationLandWaterFlg",
        solar_elevation_angle_var="solarElevationAngle",
        generators={
            "plot_dopplerVelocity": _generate_plot_doppler_velocity,
            "plot_radarReflectivityFactor": _generate_plot_radar_reflectivity,
        },
        optional_generators={},
        transforms={
            "dopplerVelocity": _transform_doppler_velocity,
        },
        height_vars={
            "binHeight",
            "surfaceElevation",
        },
    ),
)
