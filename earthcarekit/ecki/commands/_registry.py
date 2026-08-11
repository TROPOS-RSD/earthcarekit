from argparse import _SubParsersAction

from . import unzip, zip
from ._command import Command


def get_commands() -> list[Command]:
    return [
        Command(
            name="zip",
            help="archive EarthCARE h5/HDR file pairs in a folder",
            add_arguments=zip.add_arguments,
            run=zip.run,
        ),
        Command(
            name="unzip",
            help="extract EarthCARE ZIP archives in a folder",
            add_arguments=unzip.add_arguments,
            run=unzip.run,
        ),
    ]


def register(subparsers: _SubParsersAction) -> None:
    for command in get_commands():
        command.register(subparsers)
