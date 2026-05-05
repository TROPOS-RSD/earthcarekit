"""
**earthcarekit.utils.dict**

Dictionary utilities.

## Notes

This module does not depend on other internal modules.

---
"""

from typing import TypeVar

A = TypeVar("A")
B = TypeVar("B")


def remove_keys_from_dict(d: dict[A, B], keys: list[A]) -> dict[A, B]:
    """Return new dictionary with selected keys removed."""
    d = d.copy()
    for k in keys:
        if k in d:
            del d[k]
    return d


def invert_dict(d: dict[A, B]) -> dict[B, A]:
    """Return new dictionary with keys and values swapped (assumes all unique values)."""
    return {v: k for k, v in d.items()}


def invert_dict_nonunique(d: dict[A, B]) -> dict[B, list[A]]:
    """Return new dictionary mapping from values to lists of keys that map to it."""
    inv_d: dict[B, list[A]] = {}
    for k, v in d.items():
        inv_d.setdefault(v, []).append(k)
    return inv_d
