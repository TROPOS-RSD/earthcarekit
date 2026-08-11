from argparse import ArgumentParser, Namespace
from typing import cast


def add(parser: ArgumentParser) -> None:
    parser.add_argument(
        "--keep_paths",
        "--keep-paths",
        action="store_true",
        help="Preserve the original file paths when zipping or extracting.",
    )


def run(args: Namespace) -> bool:
    return cast(bool, args.keep_paths)
