from typing import Literal, cast, overload

from ...read import LazyDataset
from ...typing import PathLike
from ...utils.time import TimestampLike
from ._load_product import _load_product


@overload
def eclazy(
    type_or_path: str | PathLike,
    frame_or_time: str | TimestampLike | None = None,
    baseline: str | None = None,
    *,
    path_to_data: str | None = None,
    search_mode: Literal["exhaustive", "fast"] = "exhaustive",
    download: bool = False,
    verbose: bool = False,
    return_path: Literal[False] = ...,
    **kwargs,
) -> LazyDataset: ...
@overload
def eclazy(
    type_or_path: str | PathLike,
    frame_or_time: str | TimestampLike | None = None,
    baseline: str | None = None,
    *,
    path_to_data: str | None = None,
    search_mode: Literal["exhaustive", "fast"] = "exhaustive",
    download: bool = False,
    verbose: bool = False,
    return_path: Literal[True] = ...,
    **kwargs,
) -> str: ...
def eclazy(
    type_or_path: str | PathLike,
    frame_or_time: str | TimestampLike | None = None,
    baseline: str | None = None,
    *,
    path_to_data: str | None = None,
    search_mode: Literal["exhaustive", "fast"] = "exhaustive",
    download: bool = False,
    verbose: bool = False,
    return_path: bool = False,
    **kwargs,
) -> LazyDataset | str:
    """Locate, download (if needed), and open an EarthCARE product as a ``LazyDataset``.

    Args:
        type_or_path:
            Product name (e.g., "ATL_EBD_2A", "ATL_EBD_2A:BA") or file path.
            If path, loads directly.
        frame_or_time:
            Orbit frame (e.g., "01234B") or timestamp (e.g., "2024-09-02 21:04:37").
            Required when ``type_or_path`` is a product name.
        baseline: Two-letter processor baseline. Ignored if already in ``type_or_path``.
        path_to_data: Root search directory; defaults to config value if None.
        search_mode:
            Search strategy: "exhaustive" (recursive scan) or "fast" (expected paths only).
            Defaults to "exhaustive".
        download: Download missing files if True; raise ``ValueError`` otherwise.
        verbose: Print logs to console if True.
        return_path: If True, return the file path instead of loading the dataset.

    Returns:
        The opened EarthCARE product (default) or file path (str) if ``return_path`` is True.

    See Also:
        [`ecload()`][earthcarekit.ecload]: Opens file as [`xarray.Dataset`](https://docs.xarray.dev/en/stable/generated/xarray.Dataset.html).

    Examples:
        >>> with eck.eclazy("ATL_EBD_2A", "01508B") as lds:
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
            download=download,
            verbose=verbose,
            return_path=return_path,
            **kwargs,
        ),
    )
