import logging
import time
from functools import wraps
from typing import Callable, ParamSpec, TypeVar

P = ParamSpec("P")
T = TypeVar("T")


def log_time(
    show_args: bool = False,
    logger: logging.Logger | None = None,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Decorator factory that logs the execution time of a function.

    Args:
        show_args (bool, optional):
            If True, displays arguemnts given to the function in the log message.
            Defaults to False.
        logger (Logger, optional):
            A Logger instance. Defaults to None.

    Returns:
        Callable[[Callable[P, T]], Callable[P, T]]: The log_time-decorator.
    """

    logger = logger or logging.getLogger()

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            st = time.time()
            res = func(*args, **kwargs)
            t = time.time() - st

            if show_args and (len(args) or len(kwargs)):
                msg = f"\n{func.__name__}("
                arg_strs = [f"{a!r}" for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
                for a in arg_strs:
                    msg += f"\n\t{a},"
                msg += f"\n) took {t:.4f} sec"
                logger.info(msg)
            else:
                logger.info(f"{func.__name__}() took {t:.4f} sec")
            return res

        return wrapper

    return decorator
