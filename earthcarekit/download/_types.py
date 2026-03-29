from enum import StrEnum

from ._constants import URL_MAAP, URL_OADS


class UserType(StrEnum):
    COMMISSIONING = "commissioning"
    CALVAL = "calval"
    OPEN = "public"


class Entrypoint(StrEnum):
    MAAP = URL_MAAP
    OADS = URL_OADS
