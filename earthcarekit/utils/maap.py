"""
This file contains adaped code originally published by:

    © ESA, 2025 - European Space Agency Community License
    Author: Sakia Brose

The relevant section (function get_maap_access_token) has been modified by Leonard König, 2025.
See comments below for attribution.
"""

import requests

from ._config import ECKConfig, get_config


def _get_maap_access_token(offline_token: str) -> str:
    """Retrieves MAAP access token from generated offline token"""
    # The code of this function was adapted from ESA code by Saskia Brose (© ESA, 2025 - European Space Agency Community License)
    # By explicit permission of the author this code is licensed for use under Apache-2.0.
    # Original available at https://catalog.maap.eo.esa.int/doc/examples/ESAMAAP_ecdataaccess.html# (accessed 2025-12-08)
    # Changes: Minor variable renames
    client_id = "offline-token"
    client_secret = "p1eL7uonXs6MDxtGbgKdPVRAmnGxHpVE"
    url = "https://iam.maap.eo.esa.int/realms/esa-maap/protocol/openid-connect/token"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "grant_type": "refresh_token",
        "refresh_token": offline_token,
        "scope": "offline_access openid",
    }

    response = requests.post(url, data=data)
    response.raise_for_status()

    response_json = response.json()
    access_token = response_json.get("access_token")

    if not access_token:
        raise RuntimeError("Failed to retrieve access token from IAM response")

    return access_token


def get_maap_access_token(
    token: str | None = None,
    config: str | ECKConfig | None = None,
) -> str:
    """Retrieves MAAP access token from generated offline token

    Args:
        token (str | None):
            A temporary/offline ESA MAAP access token (to generate it visit:
            https://portal.maap.eo.esa.int/ini/services/auth/token/). Defaults to None.
        config (str | ECKConfig | None): A path to a config file (.toml) or None. If None, returns
            the default config. Defaults to None.

    Returns:
        str: Long-lasting ESA MAAP access token.
    """
    return _get_maap_access_token(token or get_config(config).maap_token)
