import logging
import re
from typing import Any, Literal, cast

from xarray import Dataset

from ..download import ecdownload
from ..read import LazyDataset, read_product, search_product
from ..read.info import FileType
from ..typing import PathLike
from ..utils.time import TimestampLike, time_to_string


def _load_product(
    is_lazy: bool,
    type_or_path: str | PathLike,
    frame_or_time: str | TimestampLike | None,
    baseline: str | None = None,
    path_to_data: str | None = None,
    mode: Literal["exhaustive", "fast"] = "exhaustive",
    verbose: bool = False,
    logger: logging.Logger | None = None,
    **kwargs,
) -> Dataset | LazyDataset:
    if verbose:
        logger = logger or logging.getLogger()

    _kwargs: dict[str, Any] = {"in_memory": True}
    _kwargs.update(kwargs)

    if isinstance(type_or_path, str) and len(type_or_path.split(":")[-1]) == 2:
        baseline = type_or_path.split(":")[-1]
        type_or_path = type_or_path[:-3]

    if isinstance(type_or_path, str) and len(type_or_path) <= 10:
        file_type = FileType.from_input(type_or_path).value

        if frame_or_time is None:
            raise ValueError("Missing 'frame_or_time' input")

        orbit_and_frame: str | None = None
        timestamp: str | None = None
        if isinstance(frame_or_time, str) and re.compile(r"^\d{1,5}[AaBbCcDdEeFfGgHh]$").match(
            frame_or_time
        ):
            orbit_and_frame = frame_or_time
        else:
            timestamp = time_to_string(frame_or_time)

        if logger:
            msg = f"Searching '{file_type}'"
            if orbit_and_frame is not None:
                msg = f"{msg} frame {orbit_and_frame}"
            if timestamp is not None:
                msg = f"{msg} at {timestamp}"
            logger.info(f"{msg} ...")

        df = search_product(
            path_to_data=path_to_data,
            file_type=file_type,
            orbit_and_frame=orbit_and_frame,
            timestamp=timestamp,
            baseline=baseline,
            mode=mode,
        ).filter_latest()

        if df.size == 0:
            if logger:
                logger.info("File not found locally. Starting download ...")
            ecdownload(
                path_to_data=path_to_data,
                file_type=file_type,
                orbit_and_frame=orbit_and_frame,
                timestamp=timestamp,
                baseline=baseline,
                verbose=verbose,
            )
            if logger:
                logger.info("Download complete. Searching file locally ...")
            df = search_product(
                path_to_data=path_to_data,
                file_type=file_type,
                orbit_and_frame=orbit_and_frame,
                timestamp=timestamp,
                baseline=baseline,
                mode=mode,
            ).filter_latest()

        if df.size == 0:
            raise ValueError(
                f"Can't find frame for inputs: {file_type=}, {orbit_and_frame=}, {baseline=}, "
            )

        fp = df.filepath[-1]
    else:
        fp = str(type_or_path)

    if logger:
        logger.info("Reading file ...")

    if is_lazy:
        return LazyDataset(fp, **_kwargs)
    return read_product(fp, **_kwargs)


def ecload(
    type_or_path: str | PathLike,
    frame_or_time: str | TimestampLike | None = None,
    baseline: str | None = None,
    *,
    path_to_data: str | None = None,
    search_mode: Literal["exhaustive", "fast"] = "exhaustive",
    verbose: bool = False,
    **kwargs,
) -> Dataset:
    """Convenience function to locate, download (if needed), and load an EarthCARE product.

    Args:
        type_or_path (str | PathLike):
            File type name or file path of an EarthCARE product. If file path is given, the dataset
            set is read directly. If a file type is given (i.e., a product name like `ATL_NOM_1B`),
            the second positional argument `frame_or_time` is required. The required processor
            baseline version can also be specified with the colon-notation (e.g., `ATL_NOM_1B:BA`).
        frame_or_time (str | TimestampLike | None, optional):
            Either a orbit-frame string (e.g., "01234B") or a timestamp
            (e.g.,"2024-09-02 21:04:37"). Required if `type_or_path` is a file type string.
            Defaults to None.
        baseline (str | None, optional):
            Two-letter processor baseline. Defaults to None.
        path_to_data (str | None, optional):
            Root directory to search. Defaults to directory given in a configuration file.
            Defaults to None.
        search_mode (Literal[&quot;exhaustive&quot;, &quot;fast&quot;], optional):
            Search strategy controlling completeness vs performance; the "exhaustive" mode
            recursivly scans all files under the root_directory, while the "fast" mode searches
            files only at expected paths and may miss files outside the standard data folder
            structure defined during the configuration of `earthcarekit`. Defaults to "exhaustive".
        verbose (bool, optional):
            If True, prints logs to the console; otherwise, execution will be silent.
            Defaults to False.

    Returns:
        Dataset: The EarthCARE dataset.

    See Also:
        eclazy: Opens file as `earthcarekit.LazyDataset`

    Examples:

        >>> ds = eck.ecload("ATL_EBD_2A", "2024-09-02 21:04:37")
        >>> ds = eck.ecload("ATL_EBD_2A", "01508B")
        >>> ds = eck.ecload("ATL_EBD_2A", "01508B", "BA")
        >>> ds = eck.ecload("aebd:ba", "01508B")
    """
    return cast(
        Dataset,
        _load_product(
            is_lazy=False,
            type_or_path=type_or_path,
            frame_or_time=frame_or_time,
            baseline=baseline,
            path_to_data=path_to_data,
            mode=search_mode,
            verbose=verbose,
            **kwargs,
        ),
    )


def eclazy(
    type_or_path: str | PathLike,
    frame_or_time: str | TimestampLike | None = None,
    baseline: str | None = None,
    *,
    path_to_data: str | None = None,
    search_mode: Literal["exhaustive", "fast"] = "exhaustive",
    verbose: bool = False,
    **kwargs,
) -> LazyDataset:
    """Convenience function to locate, download (if needed), and load an EarthCARE product as a
    `LazyDataset` object (to get an `xarray.Dataset` use instead `earthcarekit.ecload()`).

    Args:
        type_or_path (str | PathLike):
            File type name or file path of an EarthCARE product. If file path is given, the dataset
            set is read directly. If a file type is given (i.e., a product name like `ATL_NOM_1B`),
            the second positional argument `frame_or_time` is required. The required processor
            baseline version can also be specified with the colon-notation (e.g., `ATL_NOM_1B:BA`).
        frame_or_time (str | TimestampLike | None, optional):
            Either a orbit-frame string (e.g., "01234B") or a timestamp
            (e.g.,"2024-09-02 21:04:37"). Required if `type_or_path` is a file type string.
            Defaults to None.
        baseline (str | None, optional):
            Two-letter processor baseline. Defaults to None.
        path_to_data (str | None, optional):
            Root directory to search. Defaults to directory given in a configuration file.
            Defaults to None.
        search_mode (Literal[&quot;exhaustive&quot;, &quot;fast&quot;], optional):
            Search strategy controlling completeness vs performance; the "exhaustive" mode
            recursivly scans all files under the root_directory, while the "fast" mode searches
            files only at expected paths and may miss files outside the standard data folder
            structure defined during the configuration of `earthcarekit`. Defaults to "exhaustive".
        verbose (bool, optional):
            If True, prints logs to the console; otherwise, execution will be silent.
            Defaults to False.

    Returns:
        LazyDataset: The EarthCARE dataset.

    See Also:
        ecload: Opens file as `xarray.Dataset`

    Examples:

        >>> with eck.eclazy("aebd", "01508B") as lds:
        >>>     for var in lds.variables:
        >>>         print(var)
    """
    return cast(
        LazyDataset,
        _load_product(
            is_lazy=True,
            type_or_path=type_or_path,
            frame_or_time=frame_or_time,
            baseline=baseline,
            path_to_data=path_to_data,
            mode=search_mode,
            verbose=verbose,
            **kwargs,
        ),
    )
