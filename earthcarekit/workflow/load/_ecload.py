from typing import Literal, cast, overload

from xarray import Dataset

from ...typing import PathLike
from ...utils.time import TimestampLike
from ._load_product import _load_product


@overload
def ecload(
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
) -> Dataset: ...
@overload
def ecload(
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
def ecload(
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
) -> Dataset | str:
    """Locate, download (if needed), and open an EarthCARE product as a ``xarray.Dataset``.

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
        [`eclazy()`][earthcarekit.eclazy]: Opens file as [`LazyDataset`][earthcarekit.LazyDataset].

    Examples:
        These examples all yield the same dataset:

        >>> ds = eck.ecload("ATL_EBD_2A", "2024-09-02 21:04:37")
        >>> ds = eck.ecload("ATL_EBD_2A", "01508B")
        >>> ds = eck.ecload("A-EBD", "01508B")
        >>> ds = eck.ecload("aebd", "01508B")

        You may specifify the desired baseline of a product like this:

        >>> ds = eck.ecload("ATL_EBD_2A", "01508B", "BA")

        Or using the colon syntax, e.g.:

        >>> ds = eck.ecload("ATL_EBD_2A:BA", "01508B")
        >>> ds = eck.ecload("aebd:ba", "01508B")
    """
    return cast(
        Dataset | str,
        _load_product(
            is_lazy=False,
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
