import re
import textwrap
from typing import Literal, TypeAlias

from ...utils.debug import get_calling_function_name

AxisInput: TypeAlias = Literal["x", "y", 0, 1]


def validate_axis_input(axis: AxisInput) -> Literal["x", "y"]:
    _axis: Literal["x", "y"]
    if axis in [0, "0", "x"]:
        _axis = "x"
    elif axis in [1, "1", "y"]:
        _axis = "y"
    else:
        raise ValueError(
            f"{get_calling_function_name(2)}() Invalid values given for `axis`: '{axis}' (expecting 'x', 'y' or respectively 0, 1)"
        )
    return _axis
