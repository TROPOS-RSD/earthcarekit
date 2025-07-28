import json
import urllib.parse as urlp
from logging import Logger

import requests


def _encode_url(url: str | bytes) -> str | bytes:
    """Encode the URL, including its query string."""
    if isinstance(url, bytes):
        return url

    split_parsed_url = urlp.urlsplit(url)
    encoded_query = urlp.quote(split_parsed_url.query, safe="=&,/:")  # Keep separators
    return urlp.urlunsplit(
        (
            split_parsed_url.scheme,
            split_parsed_url.netloc,
            split_parsed_url.path,
            encoded_query,
            split_parsed_url.fragment,
        )
    )


def validate_request_response(
    response: requests.models.Response,
    logger: Logger | None = None,
) -> None:
    """Raises HTTPError if one occurred and logs it."""
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        if logger:
            logger.exception(e)
        raise


def _load_response_json(response: requests.Response) -> dict:
    """Reads a request response in JSON format."""
    return json.loads(response.text)


def request_get(
    url: str | bytes,
    logger: Logger | None = None,
    **kwargs,
) -> requests.Response:
    """Sends a GET request, validates it's response and returns it."""
    url = _encode_url(url=url)
    if logger:
        logger.debug(f"Send GET request: {str(url)}")
    response = requests.get(url, **kwargs)
    validate_request_response(response=response, logger=logger)
    return response


def get_request_json(url: str, logger: Logger | None = None, **kwargs) -> dict:
    response = request_get(url=url, logger=logger, **kwargs)
    data = _load_response_json(response)
    return data


def request_post(
    url: str | bytes,
    logger: Logger | None = None,
    **kwargs,
) -> requests.Response:
    """Sends a POST request, validates it's response and returns it."""
    url = _encode_url(url=url)
    if logger:
        logger.debug(f"Send POST request: {str(url)}")
    response = requests.post(url, **kwargs)
    validate_request_response(response=response, logger=logger)
    return response
