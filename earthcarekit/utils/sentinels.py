from typing import Final, Self


class _Unset:
    """Singleton sentinel for 'argument not passed'."""

    _instance: Self | None = None

    def __new__(cls) -> Self:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __repr__(self) -> str:
        return "UNSET"

    def __bool__(self) -> bool:
        return False

    def __reduce__(self):
        return (_Unset, ())


UNSET: Final[_Unset] = _Unset()
Unset = _Unset
