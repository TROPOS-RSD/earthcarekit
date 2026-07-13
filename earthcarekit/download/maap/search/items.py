from typing import TypeAlias

import numpy as np
from numpy.typing import NDArray
from pystac import Asset, Item

from ....read.info import ProductDataFrame, get_product_infos
from ....utils.parse import get_file_info_from_str
from ..._eo_product import EOProduct

StartLat: TypeAlias = float
StartLon: TypeAlias = float
EndLat: TypeAlias = float
EndLon: TypeAlias = float


def get_href(item: Item, key: str) -> str | None:
    asset = item.assets.get(key)
    return None if not isinstance(asset, Asset) else asset.href


def get_url_archive(item: Item) -> str:
    return get_href(item, "product") or "missing"


def get_url_h5(item: Item) -> str | None:
    return get_href(item, "enclosure_h5")


def get_url_hdr(item: Item) -> str | None:
    return get_href(item, "enclosure_hdr")


def get_url_quicklook(item: Item) -> str | None:
    return get_href(item, "quicklook_jpeg")


def get_size(item: Item, keys: list[str] = ["enclosure_h5", "enclosure_hdr"]) -> int:
    size = 0
    for name in ["enclosure_h5", "enclosure_hdr"]:
        asset = item.assets.get(name)
        if isinstance(asset, Asset):
            size += asset.to_dict().get("file:size", 0)
    return size


def get_start_end_coords(item: Item) -> tuple[StartLat, StartLon, EndLat, EndLon]:
    geometry = item.geometry or {}
    fallback: list = [[np.nan, np.nan], [np.nan, np.nan]]
    coords: NDArray[np.float64] = np.array(geometry.get("coordinates", fallback), dtype=np.float64)
    if coords.ndim == 2 and coords.shape[0] >= 2 and coords.shape[1] == 2:
        start_lat = coords[0, 1]
        start_lon = coords[0, 0]
        end_lat = coords[-1, 1]
        end_lon = coords[-1, 0]
    else:
        orbit_state = str(item.properties.get("sat:orbit_state", "")).lower()
        fallback = [np.nan, np.nan, np.nan, np.nan]
        bbox: NDArray[np.float64] = np.array(item.bbox or fallback, dtype=np.float64)
        if orbit_state == "descending":
            start_lat = bbox[3]
            start_lon = bbox[2]
            end_lat = bbox[1]
            end_lon = bbox[0]
        else:
            start_lat = bbox[1]
            start_lon = bbox[0]
            end_lat = bbox[3]
            end_lon = bbox[2]
    return (float(start_lat), float(start_lon), float(end_lat), float(end_lon))


def get_unique_items(items: list[Item]) -> list[Item]:
    seen: set[str] = set()
    result: list[Item] = []
    for item in items:
        if item.id not in seen:
            seen.add(item.id)
            result.append(item)
    return result


def get_sorted_items(items: list[Item], reverse: bool = False) -> list[Item]:
    return sorted(items, key=lambda item: item.id, reverse=reverse)


def items_to_product_dataframe(items: list[Item]) -> ProductDataFrame:
    pdf = get_product_infos([item.id for item in items], must_exist=False)
    coords = [get_start_end_coords(item) for item in items]
    pdf["start_latitude"] = np.array([coord[0] for coord in coords])
    pdf["start_longitude"] = np.array([coord[1] for coord in coords])
    pdf["end_latitude"] = np.array([coord[2] for coord in coords])
    pdf["end_longitude"] = np.array([coord[3] for coord in coords])
    pdf["url_download_h5"] = np.array([get_url_h5(item) for item in items], dtype=str)
    pdf["url_download_hdr"] = np.array([get_url_hdr(item) for item in items], dtype=str)
    pdf["url_quicklook"] = np.array([get_url_quicklook(item) for item in items], dtype=str)
    return pdf


def item_to_eo_product(
    items: list[Item],
    download_only_h5: bool = False,
    download_only_hdr: bool = False,
) -> list[EOProduct]:
    eo_products = []

    for item in items:
        start_lat, start_lon, end_lat, end_lon = get_start_end_coords(item)
        info = get_file_info_from_str(item.id)
        if download_only_h5:
            size = get_size(item, keys=["enclosure_h5"])
        elif download_only_hdr:
            size = get_size(item, keys=["enclosure_hdr"])
        else:
            size = get_size(item)
        eop = EOProduct(
            name=info["filename"],
            orbit_and_frame=info["orbit_and_frame"],
            file_type=info["file_type"],
            version=info["baseline"],
            start_processing_time=info["start_processing_time"],
            url_download=get_url_archive(item),
            url_quicklook=get_url_quicklook(item),
            size=size,
            url_download_h5=get_url_h5(item),
            url_download_hdr=get_url_hdr(item),
            start_latitude=start_lat,
            start_longitude=start_lon,
            end_latitude=end_lat,
            end_longitude=end_lon,
        )
        eo_products.append(eop)
    return eo_products
