import xarray as xr


def merge_datasets(
    ds1: xr.Dataset,
    ds2: xr.Dataset,
    keep_sec: bool = False,
) -> xr.Dataset:
    """Merges two datasets while keeping all global attributes from one dataset."""
    ds_merged = xr.merge([ds1, ds2])
    if keep_sec:
        ds_merged.attrs = ds2.attrs.copy()
        ds_merged.encoding = ds2.encoding.copy()
    else:
        ds_merged.attrs = ds1.attrs.copy()
        ds_merged.encoding = ds1.encoding.copy()
    return ds_merged
