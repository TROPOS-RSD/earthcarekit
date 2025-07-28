import re

from ..utils._cli._parse import (
    parse_path_to_config,
    parse_path_to_data,
    parse_search_inputs,
    parse_selected_index,
)
from ._types import Entrypoint, UserType


def get_collection_names_available_to_user(
    user_type: UserType,
    entrypoint: Entrypoint,
) -> list[str]:
    colls_comm = [
        "EarthCAREL0L1Products",
        "EarthCAREL2Products",
        "JAXAL2Products",
    ]

    colls_calval = [
        "EarthCAREAuxiliary",
        "EarthCAREL1InstChecked",
        "EarthCAREL2InstChecked",
        "JAXAL2InstChecked",
    ]

    colls_public = [
        "EarthCAREL1Validated",
        "EarthCAREL2Validated",
        "JAXAL2Validated",
        "EarthCAREXMETL1DProducts10",
        "EarthCAREOrbitData",
    ]

    is_maap: bool = entrypoint == Entrypoint.MAAP
    is_oads: bool = not is_maap

    to_maap = lambda colls: [f"{c}_MAAP" for c in colls]
    if is_maap and is_oads:
        colls_comm = colls_comm + to_maap(colls_comm)
        colls_calval = colls_calval + to_maap(colls_calval)
        colls_public = colls_public + to_maap(colls_public)
    elif is_maap:
        colls_comm = to_maap(colls_comm)
        colls_calval = to_maap(colls_calval)
        colls_public = to_maap(colls_public)

    if user_type == UserType.COMMISSIONING:
        return colls_comm + colls_calval + colls_public
    elif user_type == UserType.CALVAL:
        return colls_calval + colls_public
    elif user_type == UserType.OPEN:
        return colls_public
    else:
        raise NotImplementedError()


def parse_user_type(user_type: str) -> UserType:
    if not isinstance(user_type, str):
        raise TypeError(
            f"invalid type '{type(user_type).__name__}' for user_type, expects 'str'"
        )

    user_type = re.sub(r"\W+", "", user_type.lower())
    user_type = user_type.replace("teams", "").replace("team", "").replace("user", "")
    if user_type == "commissioning":
        return UserType.COMMISSIONING
    elif user_type == "calval":
        return UserType.CALVAL
    elif user_type == "open":
        return UserType.OPEN
    else:
        raise ValueError(
            f'invalid input for user_type: "{user_type}". expected inputs are: "commissioning", "calval" or "open"'
        )
