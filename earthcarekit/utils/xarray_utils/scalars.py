import xarray as xr


def convert_scalar_var_to_str(ds: xr.Dataset, var: str) -> xr.Dataset:
    """Converts a given scalar variable inside a `xarray.Dataset` to string."""
    val = ds[var].item()
    if isinstance(val, bytes):
        val = val.decode("utf-8")
    else:
        val = str(val)
    ds[var] = xr.DataArray(val)
    return ds
