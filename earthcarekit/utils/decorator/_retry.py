import time
from functools import wraps
from logging import Logger
from random import random
from typing import Callable, ParamSpec, TypeAlias, TypeVar

P = ParamSpec("P")
T = TypeVar("T")
ExceptionLike: TypeAlias = type[BaseException] | tuple[type[BaseException], ...]


def retry(
    n: int = 3,
    delay: float | None = None,
    backoff: float | None = None,
    jitter: float | None = None,
    logger: Logger | None = None,
    exception: ExceptionLike | None = None,
    prefix: str | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator factory that retries a wrapped function a specified number of times.

    Args:
        n (int, optional):
            Maximum number of retries. Defaults to 3.
        delay (float | None, optional):
            Seconds between retries. Defaults to None.
        backoff (float | None, optional):
            Exponential backoff factor added to the delay. If provided, the delay before each
            retry is computed as `delay + backoff ** (attempt -1)`. Defaults to None.
        jitter (float | None, optional):
            Additional random time, in seconds, added to the delay. Defaults to None.

    Returns:
        Callable[[Callable[P, T]], Callable[P, T]]: The retry-decorator.

    Raises:
        RuntimeError: If all retries failed.
    """
    _exception: ExceptionLike = exception or Exception

    if delay is None and backoff is None and jitter is None:
        delay = 2.0

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            _prefix: str = prefix if isinstance(prefix, str) else f"{func.__name__=}() "

            for attempt in range(1, n + 1):
                try:
                    return func(*args, **kwargs)
                except _exception as e:
                    if attempt == n:
                        if logger:
                            logger.error(f"{_prefix}Failed {n} times")
                        raise RuntimeError(f"Failed after {n} tries") from e

                    _sleep_time = max(delay or 0.0, 0.0)
                    if jitter is not None:
                        _sleep_time += max(jitter, 0.0) * random()
                    if backoff is not None:
                        _sleep_time += max(backoff, 1.0) ** (attempt - 1)

                    if logger:
                        logger.info(
                            f"{_prefix}Try {attempt} failed ({type(e).__name__}: {e}); retry in {_sleep_time:.3f} seconds ..."
                        )
                        logger.debug(f"{_prefix}An exception was raised -> {type(e).__name__}: {e}")

                    time.sleep(_sleep_time)

            raise ValueError(f"Invalid number of retires ({n}); expects `n` > 0")

        return wrapper

    return decorator
