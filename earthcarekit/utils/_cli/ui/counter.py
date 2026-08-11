def format_counter(
    current: int | None = None,
    total: int | None = None,
) -> tuple[str, int]:
    """Creates a formatted counter displaying current and total count (e.g. like this [ 7/10])."""
    digits = len(str(total))
    text = ""
    if current is not None and total is not None:
        text += "[" + str(current).rjust(digits) + "/" + str(total).rjust(digits) + "]"
    elif current is not None:
        text += "[" + str(current).rjust(digits) + "]"
    return text, digits
