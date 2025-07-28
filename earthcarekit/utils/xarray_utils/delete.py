import xarray as xr


def remove_dims(ds: xr.Dataset, dims_to_remove: list[str]) -> xr.Dataset:
    """Drop a list of dimensions and all associated variables and coordinates from a given `xarray.dataset`."""
    vars_to_drop = [
        var
        for var in ds.variables
        if any(dim in ds[var].dims for dim in dims_to_remove)
    ]
    coords_to_drop = [
        coord
        for coord in ds.coords
        if any(dim in ds[coord].dims for dim in dims_to_remove)
    ]

    ds_dropped = ds.drop_vars(vars_to_drop + coords_to_drop, errors="ignore")

    for dim in dims_to_remove:
        if dim in ds_dropped.dims:
            ds_dropped = ds_dropped.drop_dims(dim)

    return ds_dropped
