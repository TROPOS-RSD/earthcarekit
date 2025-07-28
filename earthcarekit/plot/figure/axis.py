import re
import textwrap
from typing import Literal, TypeAlias

from ...utils.debug import get_calling_function_name

AxisInput: TypeAlias = Literal["x", "y", 0, 1]


def validate_axis_input(axis: AxisInput) -> Literal["x", "y"]:
    if isinstance(axis, int):
        axis = str(axis)
    elif not isinstance(axis, str):
        raise TypeError(
            f"{get_calling_function_name(2)}() for `axis` expected type '{str.__name__}' or '{int.__name__}' but got '{type(axis).__name__}' instead"
        )

    if axis == "0":
        axis = "x"
    elif axis == "1":
        axis = "y"

    if axis not in ["x", "y"]:
        raise ValueError(
            f"{get_calling_function_name(2)}() Invalid values given for `axis`: '{axis}' (expecting 'x', 'y' or respectively 0, 1)"
        )

    return axis


def wrap_label(label: str, width: int = 40) -> str:
    """Wrap a label string to a specified width, preserving units (in square brackets) and extra information.

    Args:
        label (str): The label string, optionally including units in square brackets.
        width (int, optional): Maximum width for each line. Defaults to 40.

    Returns:
        str: The wrapped label string.
    """
    wrapped_label = label
    match = re.match(r"([^\[]+)(\[[^\]]+\])?(.*)", label)
    if match:
        var_name = match.group(1).strip()
        units = match.group(2) or ""
        extra = match.group(3).strip()

        _width = width
        while len(var_name) % _width < _width / 2 and _width > 10:
            _width -= 1

        wrapped_var_name = textwrap.fill(var_name, width=_width)
        current = len(wrapped_var_name) % width

        if current + len(units) + len(extra) <= width:
            wrapped_label = f"{wrapped_var_name} {units} {extra}".strip()
        else:
            wrapped_label = f"{wrapped_var_name}\n{units} {extra}".strip()
    else:
        while len(label) % width < width / 2 and width > 10:
            width -= 1

        wrapped_label = textwrap.fill(label, width=width)
    return wrapped_label


def format_label(
    name: str, units: str | None = None, max_line_length: int | None = 40
) -> str:
    """Format a label with optional units and wrap it to a specified maximum line length.

    Args:
        name (str): The base name of the label.
        units (str | None, optional): The units to include in the label. Defaults to None.
        max_line_length (int | None, optional): The maximum length of each line. Defaults to 40.

    Returns:
        str: The formatted and wrapped label string.
    """
    if max_line_length is None:
        max_line_length = 40
    label = name
    if units is not None and (units != ""):
        label = f"{label} [{units}]"
    wrapped_label = wrap_label(label, max_line_length)
    return wrapped_label
