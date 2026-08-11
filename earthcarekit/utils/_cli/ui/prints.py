import sys


def stdout_print(*values: object, sep: str = " ", end: str = "\n", flush: bool = True) -> None:
    """A print-like function using sys.stdout.write() to work with consolce and notebook outputs."""
    text = sep.join(str(v) for v in values) + end
    sys.stdout.write(text)
    if flush:
        sys.stdout.flush()


def console_print(*values: object, end: str = "\n") -> None:
    """Wrapper for print function (forcibly flush the stream) and without logging"""
    stdout_print(*values, end=end, flush=True)
