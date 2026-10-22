import re


def parse_degrees(units: str, name: str, use_latex: bool = False) -> str | None:
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


def parse_m_inv_sr_inv(units: str, use_latex: bool = True) -> str | None:
    options = [
        r"m\^?-1\s*sr\^?-1",
        r"sr\^?-1\s*m\^?-1",
        r"/m\s*/sr",
        r"/sr\s*/m",
    ]
    regex = "(?i)^" + "|".join(options) + "$"
    pattern = re.compile(regex)
    if pattern.match(units):
        return "m$^{-1}$ sr$^{-1}$" if use_latex else "m-1 sr-1"
    return None


def parse_mega_m_inv_sr_inv(units: str, use_latex: bool = True) -> str | None:
    options = [
        r"mm\^?-1\s*sr\^?-1",
        r"sr\^?-1\s*mm\^?-1",
        r"m\^?-1\s*msr\^?-1",
        r"msr\^?-1\s*m\^?-1",
        r"/mm\s*/sr",
        r"/sr\s*/mm",
        r"/m\s*/msr",
        r"/msr\s*/m",
    ]
    regex = "(?i)^" + "|".join(options) + "$"
    pattern = re.compile(regex)
    if pattern.match(units):
        return "Mm$^{-1}$ sr$^{-1}$" if use_latex else "Mm-1 sr-1"
    return None


def parse_x_inv(x: str, units: str, use_latex: bool = True) -> str | None:
    options = [r"x\^?-1", r"/x"]
    regex = "(?i)^" + "|".join(options) + "$"
    regex = regex.replace("x", x)
    pattern = re.compile(regex)
    if pattern.match(units):
        return "x$^{-1}$".replace("x", x) if use_latex else "x-1".replace("x", x)
    return None


def parse_mega_x_inv(x: str, units: str, use_latex: bool = True) -> str | None:
    options = [r"Mx\^?-1", r"/Mx"]
    regex = "^" + "|".join(options) + "$"
    regex = regex.replace("x", x)
    pattern = re.compile(regex)
    if pattern.match(units):
        return "Mx$^{-1}$".replace("x", x) if use_latex else "Mx-1".replace("x", x)
    return None


def parse_dbz(units: str) -> str | None:
    pattern = re.compile(r"(?i)^dbz$")
    if pattern.match(units):
        return "dBZ"
    return None


def parse_micro_m(units: str, use_latex: bool = True) -> str | None:
    pattern = re.compile(r"(?i)^(µ|u|micro)\s*(m|meter)$")
    if pattern.match(units):
        return "µm" if use_latex else "um"
    return None


def parse_latex_pow(units: str) -> str:
    units = re.sub(r"\$\^\{[-−]([0-9]+)\}\$", r"-\1", units)
    return re.sub(r"\$\^\{([0-9]+)\}\$", r"\1", units)


def parse_pow_to_latex(units: str) -> str:
    units = re.sub(r"(?<!\$\^\{)\^?\s*[-−]([0-9]+)", r"$^{-\1}$", units)
    return re.sub(r"(?<!\$\^\{)(?<!-)(?<![0-9])\^?\s*([0-9]+)", r"$^{\1}$", units)


def parse_units(units: str, use_latex: bool = True) -> str:
    units = units.strip()
    units = parse_latex_pow(units)  # ensure non-latex power formatting

    if s := parse_m_inv_sr_inv(units, use_latex):
        return s  # m-1 sr-1

    if s := parse_mega_m_inv_sr_inv(units, use_latex):
        return s  # Mm-1 sr-1

    if s := parse_x_inv("m", units, use_latex):
        return s  # m-1

    if s := parse_mega_x_inv("m", units, use_latex):
        return s  # Mm-1

    if s := parse_x_inv("sr", units, use_latex):
        return s  # sr-1

    if s := parse_mega_x_inv("sr", units, use_latex):
        return s  # Msr-1

    if s := parse_dbz(units):
        return s  # dBZ

    if s := parse_micro_m(units, use_latex):
        return s  # um

    if s := parse_degrees(units, "celsius", use_latex):
        return s

    if s := parse_degrees(units, "fahrenheit", use_latex):
        return s

    if s := parse_degrees(units, "north", use_latex):
        return s

    if s := parse_degrees(units, "east", use_latex):
        return s

    if s := parse_degrees(units, "south", use_latex):
        return s

    if s := parse_degrees(units, "west", use_latex):
        return s

    if use_latex:
        return parse_pow_to_latex(units)

    return units
