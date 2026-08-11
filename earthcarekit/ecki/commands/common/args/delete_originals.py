from argparse import ArgumentParser, Namespace
from typing import cast


def add(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--delete_originals",
        "--delete-originals",
        action="store_true",
        help="Delete the original files after zipping or extracting.",
    )


def run(args: Namespace) -> bool:
    return cast(bool, args.delete_originals)
