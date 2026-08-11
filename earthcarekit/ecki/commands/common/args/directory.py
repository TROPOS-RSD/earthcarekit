from argparse import ArgumentParser, Namespace
from pathlib import Path


def add(parser: ArgumentParser) -> None:
    parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        default=Path.cwd(),
        help="Root directory (default: current working directory).",
    )


def run(args: Namespace) -> Path:
    return args.directory or Path.cwd()
