def remove_keys_from_dict(d: dict, keys: list) -> dict:
    """Return new dictionary with selected keys removed."""
    d = d.copy()
    for k in keys:
        if k in d:
            del d[k]
    return d
