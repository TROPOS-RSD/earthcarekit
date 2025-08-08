import warnings
from typing import Callable, Sequence

import numpy as np
import pandas as pd
import xarray as xr
from xarray import Dataset

from ...constants import ALONG_TRACK_DIM, TRACK_LON_VAR
from ...xarray_utils import concat_datasets
from ._generic import read_product
from .file_info import ProductDataFrame


def circular_mean_np(
    data: np.ndarray, axis: int = -1, degrees: bool = True
) -> np.ndarray:
    if degrees:
        data = np.deg2rad(data)
    sin_mean = np.mean(np.sin(data), axis=axis)
    cos_mean = np.mean(np.cos(data), axis=axis)
    angle = np.arctan2(sin_mean, cos_mean)
    return np.rad2deg(angle) if degrees else angle


def read_products(
    filepaths: Sequence[str] | pd.DataFrame,
    zoom_at: float | None = None,
    along_track_dim: str = ALONG_TRACK_DIM,
    func: Callable | None = None,
    func_inputs: Sequence[dict] | None = None,
    max_num_files: int = 8,
    coarsen: bool = True,
) -> Dataset:
    """Read and concatenate a sequence of EarthCARE frames into a single xarray Dataset.

    Optionally applies a processing function to each frame and zooms in on a specific region
    (defined by `zoom_at`). Handles coarse averaging when not zooming.

    Args:
        filepaths (Sequence[str] or pandas.DataFrame): EarthCARE product file paths as a list or a DataFrame
            with metadata including `filepath`, `orbit_number`, and `frame_id`.
        zoom_at (float, optional): If set, selects only a zoomed-in portion of the frames
            around this fractional index. Defaults to None.
        along_track_dim (str): Name of the dimension to concatenate along. Defaults to ALONG_TRACK_DIM.
        func (Callable, optional): Function to apply to each frame after loading. Defaults to None.
        func_inputs (Sequence[dict], optional): Optional per-frame arguments to pass to `func`. Defaults to None.
        max_num_files (int, optional): Max. number of files that are allowed to be loaded at once. A `ValueError` is raised if above. Defaults to 8 (e.g., full orbit).
        coarsen (bool): If Ture, read data sets are coarened depending on the number given of files. Only aplicable when not zooming. Defaults to Ture.

    Returns:
        Dataset: Concatenated dataset with all frames along `along_track_dim`.
    """
    if isinstance(filepaths, str):
        filepaths = [filepaths]
    elif isinstance(filepaths, pd.DataFrame):
        df = filepaths.sort_values(by="filepath")
        filepaths = df["filepath"].tolist()
    else:
        df = ProductDataFrame.from_files(list(filepaths)).sort_values(by="filepath")
        filepaths = df["filepath"].tolist()

    if len(filepaths) == 0:
        raise ValueError(f"Given sequence of product files paths is empty")
    elif len(filepaths) == 1:
        warnings.warn(f"Can not concatenate frames since only one file path was given")
        return read_product(filepaths[0])
    elif len(filepaths) > max_num_files:
        raise ValueError(
            f"Too many files provided: {len(filepaths)} (currently maximum allowed is {max_num_files}). "
            "Please reduce the number of files or increase the allowed amount by setting the argument max_num_files."
        )
    elif len(filepaths) > 8:
        warnings.warn(
            f"You provided {len(filepaths)} files, which is more than one full orbit (8 files). "
            "Processing might take longer than usual."
        )

    # # Construct filename suffix from orbit/frame numbers
    # orbit_start = str(df["orbit_number"].iloc[0]).zfill(5)
    # orbit_end = str(df["orbit_number"].iloc[-1]).zfill(5)
    # frame_start = df["frame_id"].iloc[0]
    # frame_end = df["frame_id"].iloc[-1]

    # if orbit_start == orbit_end:
    #     oaf_string = (
    #         f"{orbit_start}{frame_start}"
    #         if frame_start == frame_end
    #         else f"{orbit_start}{frame_start}-{frame_end}"
    #     )
    # else:
    #     oaf_string = f"{orbit_start}{frame_start}-{orbit_end}{frame_end}"

    def apply_func(ds: Dataset, i: int) -> Dataset:
        """Apply a processing function to a dataset if specified."""
        if func is None:
            return ds
        if func_inputs is None:
            return func(ds)
        if i < len(func_inputs):
            return func(ds, **func_inputs[i])
        raise IndexError("Too few function inputs provided")

    num_files = len(filepaths)
    ds: xr.Dataset | None = None

    if zoom_at is not None:
        # Zoomed read: select portions of two adjacent frames
        frame_indices = np.unique([int(np.floor(zoom_at)), int(np.ceil(zoom_at))])
        offset = zoom_at - frame_indices[0]
        filepaths = [filepaths[i] for i in frame_indices]

        for i, filepath in enumerate(filepaths):
            with read_product(filepath) as frame_ds:
                frame_ds = apply_func(frame_ds, frame_indices[i])

                # Preserve original dtypes
                original_dtypes = {v: frame_ds[v].dtype for v in frame_ds.variables}

                # Select relevant portion of the frame
                n = len(frame_ds[along_track_dim])
                sel_slice = (
                    slice(int(np.floor(n * offset)), n)
                    if i == 0
                    else slice(0, int(np.ceil(n * offset)))
                )
                frame_ds = frame_ds.sel({along_track_dim: sel_slice})

                # Restore dtypes
                for v, dtype in original_dtypes.items():
                    frame_ds[v] = frame_ds[v].astype(dtype)

                ds = (
                    frame_ds.copy()
                    if ds is None
                    else concat_datasets(
                        ds.copy(), frame_ds.copy(), dim=along_track_dim
                    )
                )

    else:
        # Full read and coarsen each frame
        for i, filepath in enumerate(filepaths):
            with read_product(filepath) as frame_ds:
                frame_ds = apply_func(frame_ds, i)

                if coarsen:
                    original_dtypes = {v: frame_ds[v].dtype for v in frame_ds.variables}

                    coarsen_dims = {along_track_dim: num_files}

                    # Circular mean for longitude
                    lon_coarse = (
                        frame_ds["longitude"]
                        .coarsen(coarsen_dims, boundary="trim")
                        .reduce(circular_mean_np)
                    )

                    # Regular mean for the rest
                    rest = (
                        frame_ds.drop_vars("longitude")
                        .coarsen(coarsen_dims, boundary="trim")
                        .mean()  # type: ignore
                    )

                    # Merge results
                    frame_ds = xr.merge([lon_coarse, rest])

                    for v, dtype in original_dtypes.items():
                        frame_ds[v] = frame_ds[v].astype(dtype)

                ds = (
                    frame_ds
                    if ds is None
                    else concat_datasets(ds, frame_ds, dim=along_track_dim)
                )

    # Set output file sources
    if isinstance(ds, Dataset):
        ds.encoding["sources"] = list(filepaths)
        return ds
    else:
        raise RuntimeError(f"Bad implementation")
