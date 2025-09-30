import numpy as np
import xarray as xr

from ...utils import filter_time
from ...utils.constants import TIME_VAR
from ...utils.read.product import update_rgb_of_mrgr
from ...utils.time import TimeRangeLike


def ensure_updated_msi_rgb_if_required(
    ds: xr.Dataset,
    var: str,
    time_range: TimeRangeLike | None,
    time_var: str = TIME_VAR,
) -> xr.Dataset:
    if var == "rgb" and "swir1" in ds and "nir" in ds and "vis" in ds:
        ds_filtered = filter_time(ds, time_range)
        ds_filtered = update_rgb_of_mrgr(ds_filtered)
        t1 = ds[time_var].values
        t2 = ds_filtered[time_var].values
        mask = np.logical_and(t1 >= t2[0], t1 <= t2[-1])
        ds[var].values[:, mask] = ds_filtered[var].values
        ds[var].values[:, mask] = ds_filtered[var].values
    return ds
