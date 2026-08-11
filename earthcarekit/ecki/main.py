import argparse

from . import commands
from .commands import common


def main():
    parser = argparse.ArgumentParser(
        prog="ecki",
        description="EarthCareKit Interface (ecki): A command-line tool to access features of the earthcarekit package.",
    )

    subparsers = parser.add_subparsers(dest="command")

    commands.register(subparsers)

    common.args.version.add(parser)

    args = parser.parse_args()

    common.args.version.run(args)

    if args.command is None:
        parser.error("a subcommand is required")

    args.func(args)


if __name__ == "__main__":
    main()
