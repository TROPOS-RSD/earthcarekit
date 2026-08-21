import xarray as xr

from ...constants import TIME_VAR
from ...read.product import update_rgb
from ...utils.time import TimeRangeLike


def ensure_updated_msi_rgb_if_required(
    ds: xr.Dataset,
    var: str,
    time_range: TimeRangeLike | None,
    time_var: str = TIME_VAR,
) -> xr.Dataset:
    if var == "rgb" and all(var in ds for var in ("swir1", "nir", "vis")):
        return update_rgb(ds, time_range=time_range, time_var=time_var)
    return ds
