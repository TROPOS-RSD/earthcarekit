from typing import TYPE_CHECKING, Union, overload

import numpy as np
import xarray as xr

from ...xarray_utils import convert_scalar_var_to_str, merge_datasets
from .fill_values import _convert_all_fill_values_to_nan


@overload
def read_header_data(source: str) -> xr.Dataset: ...
@overload
def read_header_data(source: xr.Dataset) -> xr.Dataset: ...
def read_header_data(source: str | xr.Dataset) -> xr.Dataset:
    """Opens the product header groups of a EarthCARE file as a `xarray.Dataset`."""
    if isinstance(source, str):
        filepath = source
    elif isinstance(source, xr.Dataset):
        filepath = source.encoding.get("source", None)
        if filepath is None:
            raise ValueError(f"Dataset missing source attribute")
    else:
        raise TypeError("Expected 'str' or 'xarray.Dataset'")

    groups = xr.open_groups(filepath)
    header_groups = {n: g for n, g in groups.items() if "HeaderData" in n}

    # Rename duplicate vars

    all_vars = {}
    header_datasets = []
    for i, (group_name, ds) in enumerate(header_groups.items()):
        ds_new = ds.copy()
        for var in ds.data_vars:
            if var in all_vars:
                new_name = f"{group_name.split('/')[-1]}_{var}"
                ds_new = ds_new.rename({var: new_name})
            else:
                all_vars[var] = True
        header_datasets.append(ds_new)

    ds = xr.merge(header_datasets)

    ds = _convert_all_fill_values_to_nan(ds)

    # Convert timestamps to numpy datetime
    for var in [
        "Creation_Date",
        "Validity_Start",
        "Validity_Stop",
        "ANXTime",
        "frameStartTime",
        "frameStopTime",
        "processingStartTime",
        "processingStopTime",
        "sensingStartTime",
        "sensingStopTime",
        "stateVectorTime",
    ]:
        if var in ds:
            raw = ds[var].values
            formatted = np.char.replace(raw, "UTC=", "")
            ds[var].values = formatted.astype("datetime64[ns]")

    # Ensure that strings are correctly decoded
    for var in ["frameID"]:
        if var in ds:
            ds = convert_scalar_var_to_str(ds, var)

    # Remove dimensions of size == 1
    ds = ds.squeeze()

    return ds


def extract_basic_meta_data_from_header(ds: xr.Dataset) -> xr.Dataset:
    ds["filename"] = ds["File_Name"]
    ds["baseline"] = ds["File_Class"]
    baseline = str(np.str_(ds["File_Class"].values))
    if len(baseline) > 2:
        baseline = baseline[2:]
    ds["baseline"].values = np.array(baseline)

    ds["file_type"] = ds["File_Type"]
    ds["sensing_start_time"] = ds["sensingStartTime"]
    ds["processing_start_time"] = ds["processingStartTime"]
    ds["orbit_number"] = ds["orbitNumber"]
    ds["frame_id"] = ds["frameID"]

    ds["orbit_and_frame"] = ds["frameID"]
    orbit_and_frame = np.str_(ds["orbit_number"].values).zfill(5) + np.str_(
        ds["frame_id"].values
    )
    ds["orbit_and_frame"].values = np.array(orbit_and_frame)

    keep_vars = [
        "filename",
        "file_type",
        "frame_id",
        "orbit_number",
        "orbit_and_frame",
        "baseline",
        "sensing_start_time",
        "processing_start_time",
    ]
    return ds[keep_vars]


def add_header_and_meta_data(
    filepath: str, ds: xr.Dataset, header: bool, meta: bool
) -> xr.Dataset:
    ds_hdr: xr.Dataset | None = None
    if header:
        ds_hdr = read_header_data(filepath)
        ds = merge_datasets(ds_hdr, ds, keep_sec=True)

    if meta:
        if not isinstance(ds_hdr, xr.Dataset):
            ds_hdr = read_header_data(filepath)
        ds_meta = extract_basic_meta_data_from_header(ds_hdr)
        ds = merge_datasets(ds_meta, ds, keep_sec=True)
    return ds
