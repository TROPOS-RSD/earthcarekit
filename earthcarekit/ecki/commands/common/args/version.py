import sys
from argparse import ArgumentParser, Namespace

from ..... import __version__
from .....utils._cli.ui import console_print


def add(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-V",
        "--version",
        action="store_true",
        help="show the package version and exit",
    )


def run(args: Namespace) -> None:
    if args.version:
        console_print(f"earthcarekit {__version__}")
        sys.exit(0)
