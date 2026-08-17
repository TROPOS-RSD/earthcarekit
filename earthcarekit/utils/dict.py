"""
**earthcarekit.utils.dict**

Dictionary utilities.

## Notes

This module does not depend on other internal modules.

---
"""

from typing import Sequence, TypeVar, overload

from .sentinels import MISSING, Missing

A = TypeVar("A")
B = TypeVar("B")
C = TypeVar("C")


def remove_keys(d: dict[A, B], keys: Sequence[A]) -> dict[A, B]:
    """Return new dictionary with selected keys removed."""
    d = d.copy()
    for k in keys:
        if k in d:
            del d[k]
    return d


def invert(d: dict[A, B]) -> dict[B, A]:
    """Return new dictionary with keys and values swapped (assumes all unique values)."""
    return {v: k for k, v in d.items()}


def invert_nonunique(d: dict[A, B]) -> dict[B, list[A]]:
    """Return new dictionary mapping from values to lists of keys that map to it."""
    inv_d: dict[B, list[A]] = {}
    for k, v in d.items():
        inv_d.setdefault(v, []).append(k)
    return inv_d


def update_if_not_none(d: dict[A, B], updates: dict[A, B]) -> None:
    """Update a dictionary for keys whose values are not None."""
    d.update({k: v for k, v in updates.items() if v is not None})


@overload
def get_first(d: dict[A, B], keys: Sequence[A], default: None = None) -> B | None: ...
@overload
def get_first(d: dict[A, B], keys: Sequence[A], default: B) -> B: ...
@overload
def get_first(d: dict[A, B], keys: Sequence[A], default: C) -> B | C: ...
def get_first(d: dict[A, B], keys: Sequence[A], default: B | C | None = None) -> B | C | None:
    """Return the value for the first key present in the dictionary, else default."""
    for key in keys:
        value = d.get(key, MISSING)
        if not isinstance(value, Missing):
            return value
    return default


def get_first_label(
    d: dict[str, str],
    keys: Sequence[str] = ("label", "long_name", "name"),
    default: str | None = None,
) -> str | None:
    return get_first(d, keys, default)


def get_first_units(
    d: dict[str, str], keys: Sequence[str] = ("units", "unit"), default: str | None = None
) -> str | None:
    return get_first(d, keys, default)


_DEPRECATED = {
    "remove_keys_from_dict": remove_keys,
    "invert_dict": invert,
    "invert_dict_nonunique": invert_nonunique,
}


def __getattr__(name):
    import warnings

    if name in _DEPRECATED:
        warnings.warn(
            f"'{name}' is deprecated; use '{_DEPRECATED[name].__name__}' instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        return _DEPRECATED[name]

    raise AttributeError(name)
