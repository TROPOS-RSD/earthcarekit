import numpy as np
import xarray as xr


def _convert_all_fill_values_to_nan(ds: xr.Dataset) -> xr.Dataset:
    for v in ds.variables:
        if not hasattr(ds[v].encoding, "_FillValue"):
            if np.issubdtype(ds[v].values.dtype, np.floating):
                ds[v].values[ds[v].values >= 9.969209968386869e36] = np.nan
        if not hasattr(ds[v].encoding, "dtype"):
            _dtype = ds[v].encoding["dtype"]
            if np.issubdtype(_dtype, np.integer):
                if hasattr(ds[v].encoding, "_FillValue"):
                    fill_value = int(ds[v].encoding["_FillValue"])
                else:
                    fill_value = np.iinfo(_dtype).min
                ds[v].values[np.isnan(ds[v].values)] = fill_value
                ds[v] = ds[v].astype(_dtype)
    return ds
