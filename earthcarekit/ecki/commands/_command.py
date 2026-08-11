from argparse import ArgumentParser, Namespace, _SubParsersAction
from dataclasses import dataclass
from typing import Any, Callable, Self


@dataclass(frozen=True)
class Command:
    name: str
    help: str
    add_arguments: Callable[[ArgumentParser], None]
    run: Callable[[Namespace], Any]

    def register(self: Self, subparsers: _SubParsersAction) -> ArgumentParser:
        parser = subparsers.add_parser(name=self.name, help=self.help)
        parser.set_defaults(func=self.run)
        self.add_arguments(parser)
        return parser
