from ..utils._cli._parse._exceptions import InvalidInputError


class BadResponseError(Exception):
    """Raised when a remote response is invalid or cannot be parsed."""


__all__ = ["BadResponseError", "InvalidInputError"]
