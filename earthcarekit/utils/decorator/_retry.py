import time
from functools import wraps
from typing import Callable, ParamSpec, TypeAlias, TypeVar

P = ParamSpec("P")
T = TypeVar("T")
ExceptionLike: TypeAlias = type[BaseException] | tuple[type[BaseException], ...]


def retry(
    n: int = 3,
    delay: float = 2.0,
    exception: ExceptionLike | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator factory that retries a wrapped function a specified number of times.

    Args:
        n (int, optional): Maximum number of retries. Defaults to 3.
        delay (float, optional): Seconds between retries. Defaults to 2.0.

    Returns:
        Callable[[Callable[P, T]], Callable[P, T]]: The retry-decorator.
    """

    _exception: ExceptionLike = exception or Exception
    print(_exception)

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for attempt in range(1, n + 1):
                try:
                    return func(*args, **kwargs)
                except _exception as e:
                    if attempt == n:
                        raise RuntimeError(f"Failed after {n} retries") from e
                    time.sleep(delay)

            raise ValueError(f"Invalid number of retires ({n}); expects `n` > 0")

        return wrapper

    return decorator
