import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from xml.etree.ElementTree import Element

import pandas as pd


@dataclass
class HDRFixedHeader:
    file_name: str | None
    file_description: str | None
    notes: str | None
    mission: str | None
    file_class: str | None
    file_type: str | None
    validity_start: pd.Timestamp | None
    validity_stop: pd.Timestamp | None
    file_version: str | None
    system: str | None
    creator: str | None
    creator_version: str | None
    creation_date: str | None


def _safe_get_text(root: Element, path: str) -> str | None:
    element = root.find(path)
    if isinstance(element, Element):
        return element.text
    else:
        return None


def read_hdr_fixed_header(filepath: str) -> HDRFixedHeader:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"HDR file not found: {filepath}")

    tree = ET.parse(filepath)
    root = tree.getroot()

    validity_start_string = _safe_get_text(
        root, "Fixed_Header/Validity_Period/Validity_Start"
    )
    if isinstance(validity_start_string, str):
        validity_start = pd.Timestamp(validity_start_string.replace("UTC=", ""))
    else:
        validity_start = None

    validity_stop_string = _safe_get_text(
        root, "Fixed_Header/Validity_Period/Validity_Stop"
    )
    if isinstance(validity_stop_string, str):
        validity_stop = pd.Timestamp(validity_stop_string.replace("UTC=", ""))
    else:
        validity_stop = None

    fixed_header_data = HDRFixedHeader(
        file_name=_safe_get_text(root, "Fixed_Header/File_Name"),
        file_description=_safe_get_text(root, "Fixed_Header/File_Description"),
        notes=_safe_get_text(root, "Fixed_Header/Notes"),
        mission=_safe_get_text(root, "Fixed_Header/Mission"),
        file_class=_safe_get_text(root, "Fixed_Header/File_Class"),
        file_type=_safe_get_text(root, "Fixed_Header/File_Type"),
        validity_start=validity_start,
        validity_stop=validity_stop,
        file_version=_safe_get_text(root, "Fixed_Header/File_Version"),
        system=_safe_get_text(root, "Fixed_Header/Source/System"),
        creator=_safe_get_text(root, "Fixed_Header/Source/Creator"),
        creator_version=_safe_get_text(root, "Fixed_Header/Source/Creator_Version"),
        creation_date=_safe_get_text(root, "Fixed_Header/Source/Creation_Date"),
    )
    return fixed_header_data
