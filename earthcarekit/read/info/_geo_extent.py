from typing import Final, TypeAlias

from lxml import etree

StartLatFloat: TypeAlias = float
StartLonFloat: TypeAlias = float
EndLatFloat: TypeAlias = float
EndLonFloat: TypeAlias = float

_START_LAT_ELEM: Final[str] = (
    ".//Variable_Header/MainProductHeader/frameStartCoordinates/GeographicCoordinates/geographicLatitude"
)
_START_LON_ELEM: Final[str] = (
    ".//Variable_Header/MainProductHeader/frameStartCoordinates/GeographicCoordinates/geographicLongitude"
)
_END_LAT_ELEM: Final[str] = (
    ".//Variable_Header/MainProductHeader/frameStopCoordinates/GeographicCoordinates/geographicLatitude"
)
_END_LON_ELEM: Final[str] = (
    ".//Variable_Header/MainProductHeader/frameStopCoordinates/GeographicCoordinates/geographicLongitude"
)


def read_geo_extent_from_hdr(
    filepath_hdr: str,
) -> tuple[StartLatFloat, StartLonFloat, EndLatFloat, EndLonFloat]:
    tree = etree.parse(filepath_hdr)
    return (
        float(tree.findtext(_START_LAT_ELEM)),  # type: ignore
        float(tree.findtext(_START_LON_ELEM)),  # type: ignore
        float(tree.findtext(_END_LAT_ELEM)),  # type: ignore
        float(tree.findtext(_END_LON_ELEM)),  # type: ignore
    )


def safe_read_geo_extent_from_hdr(
    filepath_hdr: str,
) -> tuple[StartLatFloat, StartLonFloat, EndLatFloat, EndLonFloat]:
    try:
        return read_geo_extent_from_hdr(filepath_hdr)
    except Exception:
        return (float("nan"), float("nan"), float("nan"), float("nan"))
