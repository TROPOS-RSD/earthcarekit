import logging
import os
from typing import Literal

from xarray import Dataset

from ...constants import (
    DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    DEFAULT_READ_EC_PRODUCT_HEADER,
    DEFAULT_READ_EC_PRODUCT_META,
    DEFAULT_READ_EC_PRODUCT_MODIFY,
)
from ...filter import filter_frame
from ...utils import get_file_info_from_str
from ..header import add_header_and_meta_data
from ..info import FileType
from ..lazy import LazyDataset
from .auxiliary import read_product_xjsg, read_product_xmet
from .level1 import read_product_anom, read_product_cnom, read_product_mrgr
from .level2a import (
    read_product_aaer,
    read_product_aald,
    read_product_acla,
    read_product_acth,
    read_product_aebd,
    read_product_afm,
    read_product_aice,
    read_product_atc,
    read_product_ccd,
    read_product_ccld,
    read_product_cclp,
    read_product_ceco,
    read_product_cfmr,
    read_product_ctc,
    read_product_maot,
    read_product_mcm,
    read_product_mcop,
)
from .level2b import read_product_acmcap, read_product_actc, read_product_amacd, read_product_amcth


def _read_auxiliary_product(
    filepath: str,
    file_type: FileType,
    modify: bool,
    header: bool,
    meta: bool,
    ensure_nans: bool,
    **kwargs,
) -> Dataset | None:
    args: list = [filepath, modify, header, meta, ensure_nans]
    match file_type:
        case FileType.AUX_MET_1D:
            return read_product_xmet(*args, **kwargs)
        case FileType.AUX_JSG_1D:
            return read_product_xjsg(*args, **kwargs)
        case _:
            return None


def _read_level1_product(
    filepath: str,
    file_type: FileType,
    modify: bool,
    header: bool,
    meta: bool,
    ensure_nans: bool,
    **kwargs,
) -> Dataset | None:
    args: list = [filepath, modify, header, meta, ensure_nans]
    match file_type:
        case FileType.ATL_NOM_1B:
            return read_product_anom(*args, **kwargs)
        case FileType.MSI_RGR_1C:
            return read_product_mrgr(*args, **kwargs)
        case FileType.CPR_NOM_1B:
            return read_product_cnom(*args, **kwargs)
        case _:
            return None


def _read_level2a_product(
    filepath: str,
    file_type: FileType,
    modify: bool,
    header: bool,
    meta: bool,
    ensure_nans: bool,
    **kwargs,
) -> Dataset | None:
    args: list = [filepath, modify, header, meta, ensure_nans]
    match file_type:
        case FileType.ATL_AER_2A:
            return read_product_aaer(*args, **kwargs)
        case FileType.ATL_EBD_2A:
            return read_product_aebd(*args, **kwargs)
        case FileType.ATL_TC__2A:
            return read_product_atc(*args, **kwargs)
        case FileType.ATL_CLA_2A:
            return read_product_acla(*args, **kwargs)
        case FileType.ATL_CTH_2A:
            return read_product_acth(*args, **kwargs)
        case FileType.ATL_ALD_2A:
            return read_product_aald(*args, **kwargs)
        case FileType.ATL_ICE_2A:
            return read_product_aice(*args, **kwargs)
        case FileType.ATL_FM__2A:
            return read_product_afm(*args, **kwargs)
        case FileType.MSI_AOT_2A:
            return read_product_maot(*args, **kwargs)
        case FileType.MSI_CM__2A:
            return read_product_mcm(*args, **kwargs)
        case FileType.MSI_COP_2A:
            return read_product_mcop(*args, **kwargs)
        case FileType.CPR_TC__2A:
            return read_product_ctc(*args, **kwargs)
        case FileType.CPR_CLD_2A:
            return read_product_ccld(*args, **kwargs)
        case FileType.CPR_FMR_2A:
            return read_product_cfmr(*args, **kwargs)
        case FileType.CPR_CD__2A:
            return read_product_ccd(*args, **kwargs)
        case FileType.CPR_CLP_2A:
            return read_product_cclp(*args, **kwargs)
        case FileType.CPR_ECO_2A:
            return read_product_ceco(*args, **kwargs)
        case _:
            return None


def _read_level2b_product(
    filepath: str,
    file_type: FileType,
    modify: bool,
    header: bool,
    meta: bool,
    ensure_nans: bool,
    **kwargs,
) -> Dataset | None:
    args: list = [filepath, modify, header, meta, ensure_nans]
    match file_type:
        case FileType.AM__ACD_2B:
            return read_product_amacd(*args, **kwargs)
        case FileType.AM__CTH_2B:
            return read_product_amcth(*args, **kwargs)
        case FileType.AC__TC__2B:
            return read_product_actc(*args, **kwargs)
        case FileType.ACM_CAP_2B:
            return read_product_acmcap(*args, **kwargs)
        case _:
            return None


def _read_product(
    filepath: str,
    trim_to_frame: bool = True,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
    ensure_nans: bool = DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    **kwargs,
) -> Dataset:
    """Loads an EarthCARE product file as an `xarray.Dataset`.

    Args:
        filepath (str): Path to the product file.
        trim_to_frame (bool, optional): Whether to trim the dataset to latitude frame bounds. Defaults to True.
        modify (bool): If True, default modifications to the opened dataset will be applied
            (e.g., renaming dimension corresponding to height to "vertical"). Defaults to True.
        header (bool): If True, all header data will be included in the dataframe. Defaults to False.
        meta (bool): If True, select meta data from header (like orbit number and frame ID) will be included in the dataframe. Defaults to True.

    Returns:
        xarray.Dataset: Loaded (and optionally trimmed) dataset.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"No product found under path: {filepath}")

    file_type = FileType.from_input(filepath)

    args: list = [
        filepath,
        file_type,
        modify,
        False,  # header will be read later
        False,  # meta data will be read later
        ensure_nans,
    ]

    ds = _read_level1_product(*args, **kwargs)
    if not isinstance(ds, Dataset):
        ds = _read_level2a_product(*args, **kwargs)
    if not isinstance(ds, Dataset):
        ds = _read_level2b_product(*args, **kwargs)
    if not isinstance(ds, Dataset):
        ds = _read_auxiliary_product(*args, **kwargs)
    if not isinstance(ds, Dataset):
        raise NotImplementedError(f"Product '{file_type}' not yet supported.")

    if file_type == FileType.AUX_MET_1D:
        trim_to_frame = False

    if modify and trim_to_frame:
        ds = filter_frame(ds)

    ds = add_header_and_meta_data(filepath, ds, header, meta)

    return ds


def read_product(
    input: str | Dataset,
    trim_to_frame: bool = True,
    modify: bool = DEFAULT_READ_EC_PRODUCT_MODIFY,
    header: bool = DEFAULT_READ_EC_PRODUCT_HEADER,
    meta: bool = DEFAULT_READ_EC_PRODUCT_META,
    ensure_nans: bool = DEFAULT_READ_EC_PRODUCT_ENSURE_NANS,
    in_memory: bool = False,
    to_geoid: bool = False,
    origin: Literal["native", "derived"] | None = None,
    try_lazy: bool = True,
    **kwargs,
) -> Dataset:
    """Returns an `xarray.Dataset` from a Dataset or EarthCARE file path,
    optionally loaded into memory.

    Args:
        input (str or xarray.Dataset):
            Path to a EarthCARE file. If a `xarray.Dataset` is given it will be returned as is.
        trim_to_frame (bool, optional):
            Whether to trim the dataset to latitude frame bounds. Defaults to True.
        modify (bool, optional):
            If True, default modifications to the opened dataset will be applied
            (e.g., renaming dimension corresponding to height to "vertical"). Defaults to True.
        header (bool, optional):
            If True, all header data will be included in the dataframe. Defaults to False.
        meta (bool, optional):
            If True, select meta data from header (like orbit number and frame ID) will be included
            in the dataframe. Defaults to True.
        ensure_nans (bool, optional):
            If True, ensures that _FillValues are set to NaNs even  if encoding of _FillValues or
            dtype is missing. Be aware, if True increases reading time. Defaults to True.
        in_memory (bool, optional):
            If True, ensures the dataset is fully loaded into memory. Defaults to False.
        to_geoid (bool, optional):
            If True, converts variables representing height/altitude values from HAE (WGS84) to
            AMSL (EGM96) using the `geoid_offset` variable. Defaults to False.
        origin (Literal["native", "derived"] | None, optional):
            Product origin identifier.

            - `"native"`: file is an original EarthCARE product.
            - `"derived"`: file was generated from a native product through post-processing or \
                transformation (e.g., nadir cross-sections of `AUX_MET_1C`).
            - None: automatically detect the origin from the filename schema.

            Defaults to None.
        try_lazy (bool, optional):
            If True, first attemps to read using `LazyDataset`, which is typically the fastest
            option and supports streaming data access via MAAP. On failure, falls back to "legacy"
            `xarray` reader (i.e., slower and no data streaming support). Defaults to True.

    Returns:
        xarray.Dataset: The resulting dataset.

    Raises:
        TypeError: If input is not a Dataset or string.
    """
    ds: Dataset
    if isinstance(input, Dataset):
        ds = input
    elif isinstance(input, str):
        if try_lazy:
            try:
                file_type = get_file_info_from_str(input)["file_type"]
                is_supported = file_type in LazyDataset.get_supported_file_types()
            except ValueError:
                is_supported = False

            if (
                is_supported
                and modify is True
                and header is False
                and meta is True
                and ensure_nans is True
            ):
                return LazyDataset(
                    input,
                    in_memory=True,
                    trim_to_frame=trim_to_frame,
                    to_geoid=to_geoid,
                    origin=origin,
                ).to_xarray()

            if not is_supported:
                logging.getLogger().info(
                    "`LazyDataset` reader don't support file_type; fall back to `xarray`-based reader"
                )

        kwargs = dict(
            trim_to_frame=trim_to_frame,
            modify=modify,
            header=header,
            meta=meta,
            ensure_nans=ensure_nans,
            **kwargs,
        )
        if in_memory:
            with _read_product(filepath=input, **kwargs) as ds:
                ds = ds.load()
        else:
            ds = _read_product(filepath=input, **kwargs)
    else:
        raise TypeError(
            "Invalid input type! Expecting a opened EarthCARE dataset (xarray.Dataset) or a path to a EarthCARE product."
        )
    return ds
