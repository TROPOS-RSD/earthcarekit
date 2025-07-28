from dataclasses import dataclass
from enum import StrEnum


class FileInfoEnum(StrEnum):
    """Base class for file info enumerators."""

    @classmethod
    def from_input(cls, value: str):
        """Default implementation: Match input string to enum member (case insensitive)."""
        for member in cls:
            if member.value.lower() == value.lower():
                return member
            if member.name.lower() == value.lower():
                return member
        raise ValueError(
            f"Invalid value: {value}. Expected one of: {[m.value for m in cls]}"
        )

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))
