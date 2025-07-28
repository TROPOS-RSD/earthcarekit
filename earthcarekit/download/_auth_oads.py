import json
import urllib.parse as urlp
from logging import Logger

import requests
from lxml import html
from requests.cookies import RequestsCookieJar

from ._constants import URL_AUTHENTIFICATION
from ._exceptions import BadResponseError
from ._request import request_get, request_post


def _get_oads_login_url(server: str) -> str:
    return f"https://{server}/oads/access/login"


def get_oads_authentification_cookies(
    dissemination_server: str,
    username: str,
    password: str,
    logger: Logger | None = None,
) -> RequestsCookieJar:
    proxies: dict = {}

    # Requesting access to the dissemination server
    url_login = _get_oads_login_url(dissemination_server)
    response_login = request_get(url=url_login, logger=logger, proxies=proxies)
    cookies_login = response_login.cookies
    for r in response_login.history:
        cookies_login = requests.cookies.merge_cookies(cookies_login, r.cookies)

    tree_login = html.fromstring(response_login.content)
    _path = ".//input[@name = 'sessionDataKey']"
    session_data_key = tree_login.findall(_path)[0].attrib["value"]

    post_data = {
        "tocommonauth": "true",
        "username": username,
        "password": password,
        "sessionDataKey": session_data_key,
    }

    # Sending login request to the authentication platform
    url_auth = URL_AUTHENTIFICATION
    response_auth = request_post(
        url=url_auth,
        data=post_data,
        cookies=cookies_login,
        proxies=proxies,
    )
    tree_auth = html.fromstring(response_auth.content)

    # Extracting the variables needed to redirect from a successful authentication
    try:
        _path_relay_state = ".//input[@name='RelayState']"
        relay_state = tree_auth.findall(_path_relay_state)[0].attrib["value"]

        _path_saml_response = ".//input[@name='SAMLResponse']"
        saml_response = tree_auth.findall(_path_saml_response)[0].attrib["value"]
    except IndexError as e:
        exception_msg = "OADS did not responde as expected. Check your configuration file for valid a username and password."
        if logger:
            logger.exception(exception_msg)
        raise BadResponseError(exception_msg)

    # Defining the SAML redirection request
    post_data_saml = {
        "RelayState": relay_state,
        "SAMLResponse": saml_response,
    }
    url_saml = tree_auth.findall(".//form[@method='post']")[0].attrib["action"]
    response_saml = request_post(
        url=url_saml,
        data=post_data_saml,
        proxies=proxies,
        logger=logger,
    )
    cookies_saml = response_saml.cookies
    for r in response_saml.history:
        cookies_saml = requests.cookies.merge_cookies(cookies_saml, r.cookies)

    return cookies_saml
