import re
import textwrap

import numpy as np


def format_float(f: float | int) -> str:
    """
    Format a float or integer to a string with one decimal place.

    Raises `TypeError` for invalid input type.
    """
    if isinstance(f, (float, int)):
        return "{:.1f}".format(f)
    raise TypeError(
        f"Given value `f` hat wrong type '{type(f).__name__}', expecting 'float' or 'int'"
    )


def wrap_label(label: str, width: int = 40) -> str:
    """
    Wrap a label string to a specified width, preserving units (in square brackets) and extra information.

    Args:
        label (str): The label string, optionally including units in square brackets.
        width (int, optional): Maximum width for each line. Defaults to 40.

    Returns:
        str: The wrapped label string.
    """

    def _len(x) -> int:
        if isinstance(x, str):
            tmp_x = x
            tmp_x = tmp_x.replace("$", "")
            tmp_x = tmp_x.replace("\mathrm", "")
            tmp_x = tmp_x.replace("\AA", "A")
            tmp_x = tmp_x.replace("{", "")
            tmp_x = tmp_x.replace("}", "")
            tmp_x = tmp_x.replace("\circ", "c")
            tmp_x = tmp_x.replace("\text", "")
            tmp_x = tmp_x.replace("^", "")
            tmp_x = tmp_x.replace("_", "")
            return len(tmp_x)
        return len(x)

    _ini_half_width = width / 2
    wrapped_label = label
    match = re.match(r"([^\[]+)(\[[^\]]+\])?(.*)", label)
    if match:
        var_name = match.group(1).strip()
        units = match.group(2) or ""
        extra = match.group(3).strip()

        _width = width
        while _len(var_name) % _width < _width / 2 and _width > _ini_half_width:
            _width -= 1

        wrapped_var_name = textwrap.fill(var_name, width=_width)
        current = _len(wrapped_var_name) % width

        if _len(var_name) + _len(units) + _len(extra) <= width:
            wrapped_label = f"{var_name} {units} {extra}".strip()
        elif current + _len(units) + _len(extra) <= width:
            wrapped_label = f"{wrapped_var_name} {units} {extra}".strip()
        else:
            wrapped_label = f"{wrapped_var_name}\n{units} {extra}".strip()
    else:
        while _len(label) % width < width / 2 and width > _ini_half_width:
            width -= 1

        wrapped_label = textwrap.fill(label, width=width)
    return wrapped_label
