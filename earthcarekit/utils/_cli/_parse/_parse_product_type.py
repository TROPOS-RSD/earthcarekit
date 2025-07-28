import re
from logging import Logger

from ._exceptions import InvalidInputError
from ._types import ProductTypeVersion


def parse_product_type_and_version(
    input_string: str,
    logger: Logger | None = None,
    default_version: str = "latest",
) -> ProductTypeVersion:
    """Returns a tuple of formatted product name and baseline strings (allows short names as input, e.g. 'ANOM:AA' -> ('ATL_NOM_1B', 'AA'))."""
    product_name_input = (
        input_string.replace(" ", "").replace("-", "").replace("_", "").lower()
    )
    product_baseline = None
    tmp = product_name_input.split(":")
    if len(tmp) == 2:
        product_baseline = tmp[1].upper()
        if re.fullmatch("[A-Z]{2}", product_baseline) is None:
            exception_msg = f"Product version in '{input_string}' is not valid. Please specify the product version by giving the two-letter processor baseline after the colon (e.g. ':AC')."
            if logger:
                logger.exception(exception_msg)
            raise InvalidInputError(exception_msg)
        product_name_input = tmp[0]

    file_types = [
        # ATLID level 1b
        "ATL_NOM_1B",
        "ATL_DCC_1B",
        "ATL_CSC_1B",
        "ATL_FSC_1B",
        # MSI level 1b
        "MSI_NOM_1B",
        "MSI_BBS_1B",
        "MSI_SD1_1B",
        "MSI_SD2_1B",
        # BBR level 1b
        "BBR_NOM_1B",
        "BBR_SNG_1B",
        "BBR_SOL_1B",
        "BBR_LIN_1B",
        # CPR level 1b
        "CPR_NOM_1B",  # JAXA product
        # MSI level 1c
        "MSI_RGR_1C",
        # level 1d
        "AUX_MET_1D",
        "AUX_JSG_1D",
        # ATLID level 2a
        "ATL_FM__2A",
        "ATL_AER_2A",
        "ATL_ICE_2A",
        "ATL_TC__2A",
        "ATL_EBD_2A",
        "ATL_CTH_2A",
        "ATL_ALD_2A",
        "ATL_CLA_2A",  # JAXA product
        # MSI level 2a
        "MSI_CM__2A",
        "MSI_COP_2A",
        "MSI_AOT_2A",
        "MSI_CLP_2A",  # JAXA product
        # CPR level 2a
        "CPR_FMR_2A",
        "CPR_CD__2A",
        "CPR_TC__2A",
        "CPR_CLD_2A",
        "CPR_APC_2A",
        "CPR_ECO_2A",  # JAXA product
        "CPR_CLP_2A",  # JAXA product
        # ATLID-MSI level 2b
        "AM__MO__2B",
        "AM__CTH_2B",
        "AM__ACD_2B",
        # ATLID-CPR level 2b
        "AC__TC__2B",
        "AC__CLP_2B",  # JAXA product
        # BBR-MSI-(ATLID) level 2b
        "BM__RAD_2B",
        "BMA_FLX_2B",
        # ATLID-CPR-MSI level 2b
        "ACM_CAP_2B",
        "ACM_COM_2B",
        "ACM_RT__2B",
        "ACM_CLP_2B",  # JAXA product
        # ATLID-CPR-MSI-BBR
        "ALL_DF__2B",
        "ALL_3D__2B",
        "ALL_RAD_2B",  # JAXA product
        # Orbit data
        "MPL_ORBSCT",  # Orbit scenario file
        "AUX_ORBPRE",  # Predicted orbit file
        "AUX_ORBRES",  # Restituted/reconstructed orbit file
    ]

    short_names = []

    for file_type in file_types:
        long_name = file_type.replace("_", "").lower()
        medium_name = long_name[0:-2]
        short_name = medium_name
        string_replacements = [
            ("atl", "a"),
            ("msi", "m"),
            ("bbr", "b"),
            ("cpr", "c"),
            ("aux", "x"),
        ]
        for old_string, new_string in string_replacements:
            short_name = short_name.replace(old_string, new_string)

        expected_inputs = [long_name, medium_name, short_name]

        if "ALL_" == file_type[0:4]:
            alternative_long_name = "acmb" + long_name[3:]
            alternative_short_name = "acmb" + short_name[3:]
            expected_inputs.extend([alternative_long_name, alternative_short_name])

        if product_name_input.lower() in expected_inputs:
            if product_baseline is not None:
                return ProductTypeVersion(type=file_type, version=product_baseline)
            else:
                return ProductTypeVersion(type=file_type, version=default_version)

        short_names.append(short_name.upper())

    msg = ""
    msg2 = ""
    for i in range(len(file_types)):
        if i % 6 == 0:
            msg += "\n" + file_types[i]
            msg2 += "\n" + short_names[i]
        else:
            msg += "\t" + file_types[i]
            msg2 += "\t" + short_names[i]

    exception_msg = f'The user input "{input_string}" is either not a valid product name or not supported by this function.\n{msg}\n\nor use the respective short hands (additional non letter characters like - or _ are also allowed, e.g. A-NOM):\n{msg2}'
    if logger:
        logger.exception(exception_msg)
    raise InvalidInputError(exception_msg)
