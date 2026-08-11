import argparse
import os
import zipfile as zf
from collections import defaultdict
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
            pattern=rf"{FILE_INFO_REGEX}\.(h5|HDR)",
        )
    ]

    console_print(f"==> Found {len(files)} EarthCARE files.")

    file_groups: dict[str, list[Path]] = defaultdict(list)
    for file in files:
        filepath = Path(file)
        file_groups[filepath.stem].append(filepath)

    console_print("==> Matching h5/HDR file pairs...")

    h5_hdr_file_pairs: dict[str, list[Path]] = defaultdict(list)
    for i, (stem, _files) in enumerate(file_groups.items()):
        exts = {f.suffix for f in _files}
        if len(_files) == 2 and len(exts) == 2:
            h5_hdr_file_pairs[stem] = _files

    common.log.file_pairs(h5_hdr_file_pairs)
    console_print(f"==> Matched {len(h5_hdr_file_pairs)} h5/HDR file pairs.")

    is_zip: bool = confirm(
        msg=f"==> Proceed zipping of {len(h5_hdr_file_pairs)} h5/HDR file pairs ?",
        default=False,
    )

    if is_zip:
        tot = len(h5_hdr_file_pairs)
        _n_zipped: int = 0
        _n_deleted: int = 0
        for i, (stem, _files) in enumerate(h5_hdr_file_pairs.items()):
            console_print(f"*{format_counter(i + 1, tot)[0]} Zipping {stem}...", end="\r")

            if is_keep_paths:
                if _files[0].parent.stem == stem:
                    zippath = _files[0].parent.parent / f"{stem}.ZIP"
                else:
                    zippath = _files[0].parent / f"{stem}.ZIP"
            else:
                zippath = directory / f"{stem}.ZIP"

            with zf.ZipFile(zippath, "w", compression=zf.ZIP_DEFLATED) as archive:
                for file in _files:
                    archive.write(file, file.name)
            _n_zipped += 1
            console_print(f"*{format_counter(i + 1, tot)[0]} Zipped '{zippath}'")

            if is_delete_originals:
                for file in _files:
                    os.remove(file)
                    _n_deleted += 1
                    console_print(f" {format_counter(i + 1, tot)[0]} Deleted '{file}'")
                    if file.parent.stem == file.stem and not os.listdir(file.parent):
                        os.rmdir(file.parent)
                        console_print(
                            f" {format_counter(i + 1, tot)[0]} Deleted empty folder '{file.parent}'"
                        )

        console_print(f"==> Zipped {_n_zipped} h5/HDR file pairs.")
        if is_delete_originals:
            console_print(f"==> Deleted {_n_deleted} h5/HDR files.")
