"""
Tests that validate the package can be imported without missing symbols.

This is especially useful when refactoring exports (e.g. Ruff-driven import cleanup),
because many modules rely on re-exported types/exceptions.
"""

from __future__ import annotations

import importlib
import pkgutil
from typing import List, Tuple


def test_import_all_earthcarekit_modules() -> None:
    """Import every module under ``earthcarekit.*``.

    Fails if any module raises during import (ImportError, NameError, etc.).
    """

    import earthcarekit as eck

    failures: List[Tuple[str, str]] = []
    for mod in pkgutil.walk_packages(eck.__path__, eck.__name__ + "."):
        name = mod.name
        try:
            importlib.import_module(name)
        except Exception as exc:  # noqa: BLE001 (error reporting for test)
            failures.append((name, f"{type(exc).__name__}: {exc}"))

    if failures:
        # Keep the message readable in CI.
        max_show = 25
        shown = failures[:max_show]
        msg = "\n".join([f"- {name}: {err}" for name, err in shown])
        extra = (
            ""
            if len(failures) <= max_show
            else f"\n... and {len(failures) - max_show} more failures"
        )
        raise AssertionError(f"Import failures ({len(failures)}):\n{msg}{extra}")
