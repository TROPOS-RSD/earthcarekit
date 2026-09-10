from functools import wraps
from typing import Callable, Protocol, TypeVar


class _ProcessorProtocol(Protocol):
    _executed_steps: set[str]


P = TypeVar("P", bound=_ProcessorProtocol)


def executed(func: Callable[[P], P]) -> Callable[[P], P]:
    """Execute the decorated method at most once.

    The instance must track already executed methods in an attribute called `_executed_steps: set[str]`.
    """

    @wraps(func)
    def wrapper(self: P) -> P:
        name = func.__name__

        if name in self._executed_steps:
            return self

        func(self)

        self._executed_steps.add(name)

        return self

    return wrapper
