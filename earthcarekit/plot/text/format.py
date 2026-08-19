import re
import textwrap

import xarray as xr

from ...utils import dict as dict_utils
from ...utils._parse_units import parse_units


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
    """Wraps a label string to a specified width, preserving units and extra info.

    Args:
        label: Label string, optionally with units in square brackets.
        width: Maximum line width; defaults to 40.

    Returns:
        The wrapped label string.
    """

    def _len(x) -> int:
        if isinstance(x, str):
            tmp_x = x
            tmp_x = tmp_x.replace("$", "")
            tmp_x = tmp_x.replace("\\mathrm", "")
            tmp_x = tmp_x.replace("\\AA", "A")
            tmp_x = tmp_x.replace("{", "")
            tmp_x = tmp_x.replace("}", "")
            tmp_x = tmp_x.replace("\\circ", "c")
            tmp_x = tmp_x.replace("\\text", "")
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


def format_var_label(
    name: str | None = None,
    units: str | None = None,
    da: xr.DataArray | None = None,
    label_len: int | None = 40,
) -> str:
    """Formats and wraps a label with optional units.

    Args:
        name: Base name of the label.
        units: Units to append; auto-extracted from `da` if None.
        da: DataArray to extract label/units from; overrides `name`/`units` if given.
        label_len: Maximum line length; defaults to 40.

    Returns:
        The formatted and wrapped label string.
    """

    if label_len is None:
        label_len = 40

    label: str

    if isinstance(da, xr.DataArray):
        if name is None:
            name = dict_utils.get_first_label(da.attrs) or "Values"
        if units is None:
            units = dict_utils.get_first_units(da.attrs) or "-"

    if name is None:
        name = ""
    elif not isinstance(name, str):
        raise TypeError(
            f"Invalid type '{type(name).__name__}' for variable name: {name}. Expected type 'str'."
        )

    label = name

    if isinstance(units, str):
        if units in "":
            pass
        elif units.lower() not in ["-", "none", "1"]:
            label = f"{name} [{parse_units(units, use_latex=True)}]"

    label = wrap_label(label, label_len)

    return label
