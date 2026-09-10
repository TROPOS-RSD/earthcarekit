from functools import wraps
from typing import Callable, ParamSpec, TypeVar, cast

P = ParamSpec("P")
T = TypeVar("T")


def requires(*dependencies: str) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Declares methods that must run before the decorated method.

    Args:
        *dependencies: Names of methods that must be run before the decorated method.

    Returns:
        A decorator that resolves the declared dependencies before the decorated method.

    Raises:
        AttributeError: If a declared dependency does not exist on the instance.
    """

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(self, *args: P.args, **kwargs: P.kwargs) -> T:
            for dependency in dependencies:
                getattr(self, dependency)()

            return func(self, *args, **kwargs)

        return cast(Callable[P, T], wrapper)

    return decorator
