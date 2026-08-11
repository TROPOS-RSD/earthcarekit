import argparse
import os
import zipfile as zf
from pathlib import Path

from ...utils._cli.ui import confirm, console_print
from ...utils._cli.ui.counter import format_counter
from ...utils.parse.filename import FILE_INFO_REGEX
from ...utils.path import search_files_by_regex
from . import common


def add_arguments(parser: argparse.ArgumentParser) -> None:
    common.args.version.add(parser)
    common.args.directory.add(parser)
    common.args.keep_paths.add(parser)
    common.args.delete_originals.add(parser)


def run(args: argparse.Namespace) -> None:
    common.args.version.run(args)
    directory: Path = common.args.directory.run(args)
    is_keep_paths: bool = common.args.keep_paths.run(args)
    is_delete_originals: bool = common.args.delete_originals.run(args)

    files: list[Path] = [
        Path(f)
        for f in search_files_by_regex(
            root=directory,
            pattern=rf"{FILE_INFO_REGEX}\.(zip|ZIP)",
        )
    ]

    common.log.zip_files(files)

    is_unzip: bool = confirm(
        msg=f"==> Proceed extracting {len(files)} archives ?",
        default=False,
    )

    if is_unzip:
        tot = len(files)
        _n_unzipped: int = 0
        _n_deleted: int = 0
        for i, file in enumerate(files):
            console_print(f"*{format_counter(i + 1, tot)[0]} Extracting {file.name}...", end="\r")

            dirpath = (file.parent if is_keep_paths else directory) / file.stem

            with zf.ZipFile(file, "r") as archive:
                archive.extractall(path=dirpath)
            _n_unzipped += 1
            console_print(f"*{format_counter(i + 1, tot)[0]} Extracted '{dirpath}'")

            if is_delete_originals:
                os.remove(file)
                _n_deleted += 1
                console_print(f" {format_counter(i + 1, tot)[0]} Deleted '{file}'")

        console_print(f"==> Extracted {_n_unzipped} archives.")
        if is_delete_originals:
            console_print(f"==> Deleted {_n_deleted} archives.")
