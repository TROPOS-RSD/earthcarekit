def validate_baseline(baseline: str) -> str:
    if not isinstance(baseline, str):
        raise TypeError(f"Wrong type for baseline given ({type(baseline)}): {baseline}")

    if baseline == "latest":
        return ".."

    if len(baseline) != 2 or not baseline.isalpha():
        raise ValueError(f"Invalid product baseline: '{baseline}'")

    return baseline.upper()
