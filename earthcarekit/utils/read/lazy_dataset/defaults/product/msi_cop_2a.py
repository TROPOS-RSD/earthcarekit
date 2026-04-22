import numpy as np
from numpy.typing import NDArray

from ....product.file_info.type import FileType
from ..._lazy_variable import LazyVariable
from ..._typing import NonEmptyTuple, _LazyDataset
from .. import ProductDefaults, register
from ._msi import (
    _generate_across_track_distance,
    _generate_from_track_distance,
    _tranform_swath_latitude,
    _tranform_swath_longitude,
)


def _get_isccp_cloud_type(
    cot: NDArray,
    cth: NDArray,
) -> NDArray:
    cu = np.where((cth >= 100) & (cth < 3200) & (cot >= 0.01) & (cot < 3.6))
    ac = np.where((cth >= 3200) & (cth < 6500) & (cot >= 0.01) & (cot < 3.6))
    ci = np.where((cth >= 6500) & (cth < 19300) & (cot >= 0.01) & (cot < 3.6))
    sc = np.where((cth >= 100) & (cth < 3200) & (cot >= 3.6) & (cot < 23))
    asc = np.where((cth >= 3200) & (cth < 6500) & (cot >= 3.6) & (cot < 23))
    cs = np.where((cth >= 6500) & (cth < 19300) & (cot >= 3.6) & (cot < 23))
    st = np.where((cth >= 100) & (cth < 3200) & (cot >= 23))
    ns = np.where((cth >= 3200) & (cth < 6500) & (cot >= 23))
    cb = np.where((cth >= 6500) & (cth < 19300) & (cot >= 23))
    clear = np.where((cot < 0.01) & (cot >= 0))

    cloud_type = np.empty(shape=cot.shape, dtype=int)
    cloud_type[:, :] = -127

    cloud_type[cu] = 1
    cloud_type[ac] = 2
    cloud_type[ci] = 3
    cloud_type[sc] = 4
    cloud_type[asc] = 5
    cloud_type[cs] = 6
    cloud_type[st] = 7
    cloud_type[ns] = 8
    cloud_type[cb] = 9
    cloud_type[clear] = 0

    return cloud_type


def _generate_isccp_cloud_type(
    lds: _LazyDataset[LazyVariable],
) -> NonEmptyTuple[LazyVariable]:
    cot_lvar = lds["cloud_optical_thickness"]

    cloud_type = _get_isccp_cloud_type(
        cot=cot_lvar.values,
        cth=lds["cloud_top_height"].values,
    )

    return (
        LazyVariable(
            varname="isccp_cloud_type",
            dims=cot_lvar.dims,
            attrs={
                "long_name": "ISCCP cloud type calculated from M-COP",
                "units": "",
                "definition": "0: Clear, 1: Cumulus, 2: Altocumulus, 3: Cirrus, 4: Stratocumulus, 5: Altostratus, 6: Cirrostratus, 7: Stratus, 8: Nimbostratus, 9: Deep convection, -127: Not determined",
                "earthcarekit": "Added by earthcarekit",
            },
            values=cloud_type,
            _dataset=lds,
        ),
    )


register(
    file_type=FileType.MSI_COP_2A.value,
    defaults=ProductDefaults(
        lat_var="latitude",
        lon_var="longitude",
        time_var="time",
        elevation_var="surface_elevation",
        land_flag_var="land_flag",
        geoid_offset_var="geoid_offset",
        generators={
            "across_track_distance": _generate_across_track_distance,
            "from_track_distance": _generate_from_track_distance,
            "isccp_cloud_type": _generate_isccp_cloud_type,
        },
        optional_generators={},
        transforms={
            "latitude": _tranform_swath_latitude,
            "longitude": _tranform_swath_longitude,
        },
        height_vars={"surface_elevation"},
    ),
)
