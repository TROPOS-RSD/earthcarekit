import os
import re
import warnings
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd
import xarray as xr
from numpy.typing import NDArray

from .agency import FileAgency
from .latency import FileLatency
from .mission_id import FileMissionID
from .type import FileType


@dataclass
class ProductInfo:
    """Class storing all info gathered from a EarthCARE product's file path."""

    mission_id: FileMissionID
    agency: FileAgency
    latency: FileLatency
    baseline: str
    file_type: FileType
    start_sensing_time: pd.Timestamp
    start_processing_time: pd.Timestamp
    orbit_number: int
    frame_id: str
    orbit_and_frame: str
    name: str
    filepath: str
    hdr_filepath: str

    def to_dict(self) -> dict:
        """Returns data stored in `ProductInfo` as a `dict`."""
        return asdict(self)

    def to_dataframe(self) -> "ProductDataFrame":
        return ProductDataFrame([self])


def _is_url(string: str) -> bool:
    import urllib.parse as urlp

    parsed = urlp.urlparse(string)
    return parsed.scheme in ("http", "https", "ftp") and parsed.netloc != ""


def _get_path_from_url(url: str) -> str:
    import urllib.parse as urlp

    parsed = urlp.urlparse(url)
    return parsed.path


def get_product_info(
    filepath: str,
    warn: bool = False,
    must_exist: bool = True,
) -> ProductInfo:
    """Gather all info contained in the EarthCARE product's file path."""
    if _is_url(filepath):
        filepath = _get_path_from_url(filepath)
        must_exist = False

    filepath = os.path.abspath(filepath)

    if must_exist and not os.path.exists(filepath):
        raise FileNotFoundError(f"File does not exist: {filepath}")

    if must_exist:
        pattern = re.compile(
            r".*ECA_[EJ][XNO][A-Z]{2}_..._..._.._\d{8}T\d{6}Z_\d{8}T\d{6}Z_\d{5}[ABCDEFGH]\.h5"
        )
    else:
        pattern = re.compile(
            r".*ECA_[EJ][XNO][A-Z]{2}_..._..._.._\d{8}T\d{6}Z_\d{8}T\d{6}Z_\d{5}[ABCDEFGH].*"
        )
    is_match = bool(pattern.fullmatch(filepath))

    if not is_match:
        raise ValueError(f"EarthCARE product has invalid file name: {filepath}")

    hdr_filepath = filepath.rstrip(".h5") + ".HDR"
    if not os.path.exists(hdr_filepath):
        if warn:
            msg = f"Missing product header file: {hdr_filepath}"
            warnings.warn(msg)
        hdr_filepath = ""

    filename = os.path.basename(filepath).rstrip(".h5")
    mission_id = FileMissionID.from_input(filename[0:3])
    agency = FileAgency.from_input(filename[4])
    latency = FileLatency.from_input(filename[5])
    baseline = filename[6:8]
    file_type = FileType.from_input(filename[9:19])
    start_sensing_time = pd.Timestamp(filename[20:35])
    start_processing_time = pd.Timestamp(filename[37:52])
    orbit_number = int(filename[54:59])
    frame_id = filename[59]
    orbit_and_frame = filename[54:60]

    info = ProductInfo(
        mission_id=mission_id,
        agency=agency,
        latency=latency,
        baseline=baseline,
        file_type=file_type,
        start_sensing_time=start_sensing_time,
        start_processing_time=start_processing_time,
        orbit_number=orbit_number,
        frame_id=frame_id,
        orbit_and_frame=orbit_and_frame,
        name=filename,
        filepath=filepath,
        hdr_filepath=hdr_filepath,
    )

    return info


def is_earthcare_product(filepath: str) -> bool:
    try:
        get_product_info(filepath, must_exist=False)
        return True
    except ValueError as e:
        return False


def get_product_infos(
    filepaths: str | list[str] | NDArray | pd.DataFrame | xr.Dataset,
    **kwargs,
) -> "ProductDataFrame":
    """
    Extracts product metadata from EarthCARE product file paths (e.g. file_type, orbit_number, frame_id, baseline, ...).

    Args:
        filepaths:
            Input sources for EarthCARE product files. Can be one of
            - `str` -> A single file path.
            - `list[str]` or `numpy.ndarray` -> A list or array of file paths.
            - `pandas.DataFrame` -> Must contain a 'filepath' column.
            - `xarray.Dataset` -> Must have encoding with attribute 'source' (`str`) or 'sources' (`list[str]`).
        **kwargs: Additional arguments passed to `get_product_info()`.

    Returns:
        ProductDataFrame: A dataframe containing extracted product information.
    """
    _filepaths: list[str] | NDArray
    if isinstance(filepaths, (str, np.str_)):
        _filepaths = [str(filepaths)]
    elif isinstance(filepaths, xr.Dataset):
        ds: xr.Dataset = filepaths
        if not hasattr(ds, "encoding"):
            raise ValueError(f"Dataset missing encoding attribute.")
        elif "source" in ds.encoding:
            _filepaths = [ds.encoding["source"]]
        elif "sources" in ds.encoding:
            _filepaths = ds.encoding["sources"]
        else:
            raise ValueError(f"Dataset encoding does not contain source or sources.")
    elif isinstance(filepaths, pd.DataFrame):
        df: pd.DataFrame = filepaths
        if "filepath" in df:
            _filepaths = df["filepath"].to_numpy()
        else:
            raise ValueError(
                f"""Given dataframe does not contain a column of file paths. A valid file path column name is "filepath"."""
            )
    else:
        _filepaths = filepaths

    infos = []
    for filepath in _filepaths:
        try:
            infos.append(get_product_info(filepath, **kwargs).to_dict())
        except ValueError as e:
            continue
    return ProductDataFrame(infos)


class ProductDataFrame(pd.DataFrame):
    required_columns = [
        "mission_id",
        "agency",
        "latency",
        "baseline",
        "file_type",
        "start_sensing_time",
        "start_processing_time",
        "orbit_number",
        "frame_id",
        "orbit_and_frame",
        "name",
        "filepath",
        "hdr_filepath",
    ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not self.empty:
            missing = set(self.required_columns) - set(self.columns)
            if missing:
                raise ValueError(f"Missing required columns: {missing}")
        else:
            # Ensure the required columns exist
            for col in self.required_columns:
                if col not in self.columns:
                    self[col] = pd.Series(dtype="object")

    # Ensure that all pandas.DataFrame methods retrun the new ProductDataFrame type
    @property
    def _constructor(self):
        return ProductDataFrame

    @property
    def filepath(self) -> NDArray:
        return np.array(self["filepath"].values)

    @property
    def hdr_filepath(self) -> NDArray:
        return np.array(self["hdr_filepath"].values)

    @property
    def mission_id(self) -> NDArray:
        return np.array(self["mission_id"].values)

    @property
    def agency(self) -> NDArray:
        return np.array(self["agency"].values)

    @property
    def latency(self) -> NDArray:
        return np.array(self["latency"].values)

    @property
    def baseline(self) -> NDArray:
        return np.array(self["baseline"].values)

    @property
    def file_type(self) -> NDArray:
        return np.array(self["file_type"].values)

    @property
    def start_sensing_time(self) -> NDArray:
        return np.array(self["start_sensing_time"].values)

    @property
    def start_processing_time(self) -> NDArray:
        return np.array(self["start_processing_time"].values)

    @property
    def orbit_number(self) -> NDArray:
        return np.array(self["orbit_number"].values)

    @property
    def frame_id(self) -> NDArray:
        return np.array(self["frame_id"].values)

    @property
    def orbit_and_frame(self) -> NDArray:
        return np.array(self["orbit_and_frame"].values)

    @property
    def name(self) -> NDArray:
        return np.array(self["name"].values)

    def filter_latest(self) -> "ProductDataFrame":
        """
        Retruns filtered `ProductDataFrame` containing only the latest files for each group of file type,
        orbit numer and frame IDs (based on latest `start_processing_time`).
        """
        return ProductDataFrame(
            self.sort_values("start_processing_time")
            .groupby(["orbit_and_frame", "file_type"])
            .tail(1)
        )

    def filter_baseline(self, *baselines: str | list[str]) -> "ProductDataFrame":
        """Retruns filtered `ProductDataFrame` containing only the selected baseline(s)."""
        return self[self["baseline"].isin(np.array(baselines).flatten())]

    @classmethod
    def from_files(cls, filepaths: list[str]) -> "ProductDataFrame":
        return cls([get_product_info(fp).to_dict() for fp in filepaths])
