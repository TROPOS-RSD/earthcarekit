from urllib.parse import urlparse


def is_url(string: str) -> bool:
    """Check whether a string appears to be a valid URL."""
    try:
        parsed = urlparse(string)
        return parsed.scheme in ("http", "https", "ftp") and parsed.netloc != ""
    except Exception:
        return False
