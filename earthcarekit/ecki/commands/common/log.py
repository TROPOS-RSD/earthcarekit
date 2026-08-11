from pathlib import Path

from ....utils._cli.ui import console_print
from ....utils._cli.ui.counter import format_counter


def file_pairs(file_pairs: dict[str, list[Path]], nmax: int = 100) -> None:
    tot = len(file_pairs)
    for i, (stem, _files) in enumerate(file_pairs.items()):
        if i == nmax:
            console_print(f"... {tot - nmax} more file pairs.")
            break

        console_print(f"{format_counter(i + 1, tot)[0]} {stem}")
        for j, f in enumerate(_files):
            if j == 1:
                console_print(f"  └─ '{f}'")
            else:
                console_print(f"  ├─ '{f}'")


def zip_files(files: list[Path], nmax: int = 100) -> None:
    tot = len(files)
    for i, file in enumerate(files):
        if i == nmax:
            console_print(f"... {tot - nmax} more files.")
            break

        console_print(f"{format_counter(i + 1, tot)[0]} '{file}'")
