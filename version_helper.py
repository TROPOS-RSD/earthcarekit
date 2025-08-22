"""Helper script for replacing version and date strings in all relevant files of the package."""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path

import requests


def replace_in_file(
    path: str,
    pattern: str,
    repl: str,
) -> None:
    text = Path(path).read_text()

    m = re.search(pattern, text)
    original_value = "NOT_FOUND" if m is None else m.group()

    m = re.search(pattern, repl)
    new_value = "NOT_FOUND" if m is None else m.group()

    new_text = re.sub(pattern, repl, text, flags=re.M)
    Path(path).write_text(new_text)
    print(f"Updated <{path}>: {original_value} -> {new_value}")


def validate_input(new_version: str) -> None:
    pattern = r"^[0-9]+.[0-9]+.[0-9]+(?:(?:a|b|rc)[0-9]+)?$"
    if not re.compile(pattern).match(new_version):
        raise ValueError(f"ERROR! Input {new_version} is not a valid version string.")

    try:

        response = requests.get(
            "https://api.github.com/repos/TROPOS-RSD/earthcarekit/releases"
        )
        github_releases = [r.get("tag_name") for r in json.loads(response.text)]

        response = requests.get(
            "https://api.github.com/repos/TROPOS-RSD/earthcarekit/releases/latest"
        )
        latest_version = json.loads(response.text).get("tag_name")

        print(f"Current latest on GitHub: {latest_version}")
        if new_version in github_releases:
            raise ValueError(
                f"ERROR! Input {new_version} is already a used release tag on GitHub."
            )
    except (requests.exceptions.HTTPError, AttributeError) as e:
        if isinstance(e, AttributeError):
            print(
                f"WARNING! Unable to check GitHub releases: GitHub API limit exceeded"
            )
        else:
            status_code = e.response.status_code
            print(f"WARNING! Unable to check GitHub releases: HTTPError {status_code}")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="version_helper",
        description=f"Updates the version in all relevant places/files of earthcarekit.",
    )
    parser.add_argument(
        "new_version",
        type=str,
        help="A new version tag, e.g., 0.1.0",
    )

    args = parser.parse_args()
    new_version = args.new_version
    validate_input(new_version)

    new_date = datetime.now().date().strftime("%Y-%m-%d")

    # earthcarekit/__init__.py
    replace_in_file(
        "earthcarekit/__init__.py",
        r'__version__\s*=\s*["\'].*?["\']',
        f'__version__ = "{new_version}"',
    )
    replace_in_file(
        "earthcarekit/__init__.py",
        r'__date__\s*=\s*["\'].*?["\']',
        f'__date__ = "{new_date}"',
    )

    # pyproject.toml
    replace_in_file(
        "pyproject.toml",
        r'version\s*=\s*".*?"',
        f'version = "{new_version}"',
    )

    # .zenodo.json
    replace_in_file(
        ".zenodo.json",
        r'"version"\s*:\s*".*?"',
        f'"version": "{new_version}"',
    )
    replace_in_file(
        ".zenodo.json",
        r'"identifier"\s*:\s*"https://github.com/TROPOS-RSD/earthcarekit/tree/.*?"',
        f'"identifier": "https://github.com/TROPOS-RSD/earthcarekit/tree/{new_version}"',
    )

    # mkdocs.yml
    replace_in_file(
        "mkdocs.yml",
        r"site_name: earthcarekit\s*.*?\s*documentation",
        f"site_name: earthcarekit {new_version} documentation",
    )
    replace_in_file(
        "mkdocs.yml",
        r'version\s*:\s*".*?"',
        f'version: "{new_version}"',
    )

    print(f"Updated version to {new_version} in all files.")


if __name__ == "__main__":
    main()
    main()
