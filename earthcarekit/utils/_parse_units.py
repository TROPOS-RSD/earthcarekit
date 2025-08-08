import re


def parse_units(units: str) -> str:

    pattern = re.compile(
        r"(?i)^((mm|msr)(\^?-1)\s*(m|sr)(\^?-1)|(m|sr)(\^?-1)\s*(mm|msr)(\^?-1))$"
    )
    match = pattern.match(units)
    if match:
        return "Mm-1 sr-1"

    pattern = re.compile(r"(?i)^((m)(\^?-1)\s*(sr)(\^?-1)|(sr)(\^?-1)\s*(m)(\^?-1))$")
    match = pattern.match(units)
    if match:
        return "m-1 sr-1"

    pattern = re.compile(r"(?i)^mm(\^?-1)$")
    match = pattern.match(units)
    if match:
        return "Mm-1"

    pattern = re.compile(r"(?i)^m(\^?-1)$")
    match = pattern.match(units)
    if match:
        return "m-1"

    pattern = re.compile(r"(?i)^msr(\^?-1)$")
    match = pattern.match(units)
    if match:
        return "Msr-1"

    pattern = re.compile(r"(?i)^sr(\^?-1)$")
    match = pattern.match(units)
    if match:
        return "sr-1"

    return units.strip()
