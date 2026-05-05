from collections.abc import Callable
from typing import Protocol, TypeAlias, TypeVar

from numpy.typing import NDArray

from ...profile import ProfileData

V = TypeVar("V", bound="_LazyVariable")
T = TypeVar("T")

NonEmptyTuple = tuple[T, *tuple[T, ...]]
_CommonVarTransformer: TypeAlias = Callable[[str, "_LazyDataset[V]", V], None]
_CommonVarTransformRegistry: TypeAlias = dict[str, _CommonVarTransformer]
_VarGenerator: TypeAlias = Callable[["_LazyDataset[V]"], NonEmptyTuple[V]]
_VarTransformer: TypeAlias = Callable[["_LazyDataset[V]", V], NonEmptyTuple[V]]


class _LazyVariable(Protocol):
    varname: str
    attrs: dict[str, str]
    values: NDArray

    def copy(self: V) -> V: ...


class _LazyDataset(Protocol[V]):
    def __getitem__(self, key: str) -> V: ...
    def _add_var(self, var: str, lvar: V) -> None: ...
    def _get_common_var(self, var: str) -> str | None: ...
    def get_profile(self, var: str) -> ProfileData: ...
    def contains_loaded(self, item: str) -> bool: ...
    @property
    def nadir_index(self) -> int | None: ...
