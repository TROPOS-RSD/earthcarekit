import re


def _parse_degrees_units(units: str, name: str, use_latex: bool = False) -> str | None:
    first_letter = name[0].upper()
    pattern = re.compile(
        rf"(?i)^(?:"
        rf"deg[_ ]?{first_letter}|"
        rf"degree[_ ]?{name}|"
        rf"{name}[_ ]?(?:deg|degrees)?|"
        rf"°\s*{first_letter}|"
        rf"\$\^\{{\\circ\}}\${first_letter}"
        rf")$",
        flags=re.UNICODE,
    )
    match = pattern.match(units)
    if match:
        if use_latex:
            return rf"$^{{\circ}}${first_letter}"
        return f"deg_{name.lower()}"
    return None


def parse_units(units: str, use_latex: bool = False) -> str:
    units = units.strip()

    pattern = re.compile(
        r"(?i)^((mm|msr)(\^?-1)\s*(m|sr)(\^?-1)|(m|sr)(\^?-1)\s*(mm|msr)(\^?-1))$"
    )
    match = pattern.match(units)
    if match:
        if use_latex:
            return "Mm$^{-1}$ sr$^{-1}$"
        return "Mm-1 sr-1"

    pattern = re.compile(r"(?i)^((m)(\^?-1)\s*(sr)(\^?-1)|(sr)(\^?-1)\s*(m)(\^?-1))$")
    match = pattern.match(units)
    if match:
        if use_latex:
            return "m$^{-1}$ sr$^{-1}$"
        return "m-1 sr-1"

    pattern = re.compile(r"(?i)^mm(\^?-1)$")
    match = pattern.match(units)
    if match:
        if use_latex:
            return "Mm$^{-1}$"
        return "Mm-1"

    pattern = re.compile(r"(?i)^m(\^?-1)$")
    match = pattern.match(units)
    if match:
        if use_latex:
            return "m$^{-1}$"
        return "m-1"

    pattern = re.compile(r"(?i)^msr(\^?-1)$")
    match = pattern.match(units)
    if match:
        if use_latex:
            return "Msr$^{-1}$"
        return "Msr-1"

    pattern = re.compile(r"(?i)^sr(\^?-1)$")
    match = pattern.match(units)
    if match:
        if use_latex:
            return "sr$^{-1}$"
        return "sr-1"

    pattern = re.compile(r"(?i)^dbz$")
    match = pattern.match(units)
    if match:
        return "dBZ"

    if s := _parse_degrees_units(units, "celsius", use_latex):
        return s

    if s := _parse_degrees_units(units, "fahrenheit", use_latex):
        return s

    if s := _parse_degrees_units(units, "north", use_latex):
        return s

    if s := _parse_degrees_units(units, "east", use_latex):
        return s

    if s := _parse_degrees_units(units, "south", use_latex):
        return s

    if s := _parse_degrees_units(units, "west", use_latex):
        return s

    if use_latex:
        units = re.sub(r"(?<!\$\^\{)\s*[-−]([0-9]+)", r"$^{-\1}$", units)
    else:
        units = re.sub(r"\$\^\{[-−]([0-9]+)\}\$", r"-\1", units)

    return units
