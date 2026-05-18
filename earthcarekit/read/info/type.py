import os
from typing import Literal, overload

import numpy as np
import xarray as xr

from ...constants import FILE_TYPE_SHORT_HAND
from ...utils import get_file_info_from_str
from ..header import read_header_data
from ._enum import FileInfoEnum
from ._type_alias import format_file_type_string


class FileType(FileInfoEnum):
    # Level 1
    ATL_NOM_1B = "ATL_NOM_1B"
    ATL_DCC_1B = "ATL_DCC_1B"
    ATL_CSC_1B = "ATL_CSC_1B"
    ATL_FSC_1B = "ATL_FSC_1B"
    MSI_NOM_1B = "MSI_NOM_1B"
    MSI_BBS_1B = "MSI_BBS_1B"
    MSI_SD1_1B = "MSI_SD1_1B"
    MSI_SD2_1B = "MSI_SD2_1B"
    MSI_RGR_1C = "MSI_RGR_1C"
    BBR_NOM_1B = "BBR_NOM_1B"
    BBR_SNG_1B = "BBR_SNG_1B"
    BBR_SOL_1B = "BBR_SOL_1B"
    BBR_LIN_1B = "BBR_LIN_1B"
    CPR_NOM_1B = "CPR_NOM_1B"  # JAXA product
    # Level 2a
    ATL_FM__2A = "ATL_FM__2A"
    ATL_AER_2A = "ATL_AER_2A"
    ATL_ICE_2A = "ATL_ICE_2A"
    ATL_TC__2A = "ATL_TC__2A"
    ATL_EBD_2A = "ATL_EBD_2A"
    ATL_CTH_2A = "ATL_CTH_2A"
    ATL_ALD_2A = "ATL_ALD_2A"
    MSI_CM__2A = "MSI_CM__2A"
    MSI_COP_2A = "MSI_COP_2A"
    MSI_AOT_2A = "MSI_AOT_2A"
    CPR_FMR_2A = "CPR_FMR_2A"
    CPR_CD__2A = "CPR_CD__2A"
    CPR_TC__2A = "CPR_TC__2A"
    CPR_CLD_2A = "CPR_CLD_2A"
    CPR_APC_2A = "CPR_APC_2A"
    ATL_CLA_2A = "ATL_CLA_2A"  # JAXA product
    MSI_CLP_2A = "MSI_CLP_2A"  # JAXA product
    CPR_ECO_2A = "CPR_ECO_2A"  # JAXA product
    CPR_CLP_2A = "CPR_CLP_2A"  # JAXA product
    # Level 2b
    AM__MO__2B = "AM__MO__2B"
    AM__CTH_2B = "AM__CTH_2B"
    AM__ACD_2B = "AM__ACD_2B"
    AC__TC__2B = "AC__TC__2B"
    BM__RAD_2B = "BM__RAD_2B"
    BMA_FLX_2B = "BMA_FLX_2B"
    ACM_CAP_2B = "ACM_CAP_2B"
    ACM_COM_2B = "ACM_COM_2B"
    ACM_RT__2B = "ACM_RT__2B"
    ALL_DF__2B = "ALL_DF__2B"
    ALL_3D__2B = "ALL_3D__2B"
    AC__CLP_2B = "AC__CLP_2B"  # JAXA product
    ACM_CLP_2B = "ACM_CLP_2B"  # JAXA product
    ALL_RAD_2B = "ALL_RAD_2B"  # JAXA product
    # Auxiliary data
    AUX_MET_1D = "AUX_MET_1D"
    AUX_JSG_1D = "AUX_JSG_1D"
    # Orbit data
    MPL_ORBSCT = "MPL_ORBSCT"
    AUX_ORBPRE = "AUX_ORBPRE"
    AUX_ORBRES = "AUX_ORBRES"

    @classmethod
    def from_input(cls, input: str | xr.Dataset) -> "FileType":
        """Infers the EarthCARE product type from a given file or dataset."""
        if isinstance(input, str):
            try:
                return cls[format_file_type_string(input)]
            except AttributeError:
                pass
            except KeyError:
                pass
            try:
                return cls(format_file_type_string(input))
            except ValueError:
                pass
            except KeyError:
                pass

        return get_file_type(input)

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))

    def to_shorthand(self, with_dash: bool = False):
        if with_dash:
            return FILE_TYPE_SHORT_HAND[self.value]
        else:
            return FILE_TYPE_SHORT_HAND[self.value].replace("-", "")

    def get_level(self) -> Literal["1B", "1C", "2A", "2B", "1D", "ORB"]:
        if self.value[-2:] in ["1B", "1C", "1D", "2A", "2B"]:
            return self.value[-2:]  # type: ignore
        elif self.value in [
            FileType.MPL_ORBSCT.value,
            FileType.AUX_ORBPRE.value,
            FileType.AUX_ORBRES.value,
        ]:
            return "ORB"
        raise NotImplementedError(f"missing implementation for {self}")


def _find_substring(target: str, substrings: list[str]) -> str:
    for sub in substrings:
        if sub in target:
            return sub
    raise ValueError(f"'{target}' does not contain a substring from '{substrings}'")


def _get_file_type_from_dataset(ds: xr.Dataset) -> FileType:
    try:
        file_type = str(ds.File_Type.values)
        return FileType(file_type)
    except (AttributeError, ValueError):
        pass

    try:
        file_type = str(ds.file_type.values)
        return FileType(file_type)
    except (AttributeError, ValueError):
        pass

    try:
        filename = os.path.basename(str(ds.filename.values)).rstrip(".h5")
        file_type = FileType.from_input(filename[9:19])
        return FileType(file_type)
    except (AttributeError, ValueError):
        pass

    try:
        filepaths = ds.encoding["sources"]
        filename = os.path.basename(filepaths[0])
        file_type = _find_substring(filename, FileType.list())
        return FileType(file_type)
    except (ValueError, KeyError):
        pass

    try:
        filepath = ds.encoding["source"]
        filename = os.path.basename(filepath)
        file_type = _find_substring(filename, FileType.list())
        return FileType(file_type)
    except (ValueError, KeyError) as e:
        raise ValueError(f"File name does not contain file type info. ({e})")


@overload
def get_file_type(product: str) -> FileType: ...
@overload
def get_file_type(product: xr.Dataset) -> FileType: ...
def get_file_type(product: str | xr.Dataset) -> FileType:
    if isinstance(product, str):
        try:
            return FileType.from_input(get_file_info_from_str(product)["file_type"])  # type: ignore
        except Exception:
            pass
        with read_header_data(product) as ds:
            file_type = _get_file_type_from_dataset(ds)
    elif isinstance(product, xr.Dataset):
        if "file_type" in product:
            ft = np.atleast_1d(product["file_type"].values)[0]
            if isinstance(ft, str):
                ft = FileType.from_input(ft)
                return ft
        file_type = _get_file_type_from_dataset(product)
    else:
        try:
            file_type = FileType.from_input(product.filepath)
        except Exception:
            raise NotImplementedError()
    return file_type
