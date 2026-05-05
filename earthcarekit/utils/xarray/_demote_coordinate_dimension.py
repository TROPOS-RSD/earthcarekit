import xarray as xr


def demote_coords(
    ds: xr.Dataset,
    var: str,
    new_dim_name: str,
) -> xr.Dataset:
    """Converts a coordinate to a variable and renames the related dimension."""
    if var in ds.coords:
        values = ds.coords[var].values
        _tmp_var = "tmp_var____"
        ds = ds.assign({_tmp_var: (var, values)})
        ds[_tmp_var] = ds[_tmp_var].assign_attrs(ds[var].attrs)
        ds = ds.drop_vars([var])
        ds = ds.rename({var: new_dim_name})
        ds = ds.rename_vars({_tmp_var: var})
    return ds
