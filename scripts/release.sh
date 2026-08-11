#!/bin/bash
#
# Release helper script.
#
# This script validates the version, prompts for release notes,
# updates project files, and asks for confirmation before committing,
# tagging and pushing to the remote repository.
#
# Usage:
#   $ bash scripts/release.sh 0.1.0
#

set -euo pipefail

# Globals
VERSION="$1"

NOTES=""

NOTES_FILE="docs/releases/$VERSION.md"
PYPROJECT_FILE="pyproject.toml"
INIT_FILE="earthcarekit/__init__.py"
MKDOCS_FILE="mkdocs.yml"
DOCS_INDEX_FILE="docs/index.md"
DOCS_RELEASES_FILE="docs/releases/SUMMARY.md"
ZENODO_FILE=".zenodo.json"

if LAST_TAG=$(git describe --tags --abbrev=0 2>/dev/null); then
    RANGE="${LAST_TAG}..HEAD"
else
    RANGE="HEAD"
fi

COMMITS=$(git log "$RANGE" --no-merges --format=%s)
MERGES=$(git log "$RANGE" --merges --format=%s)

# Functions
confirm() {
    local question
    question=$1

    read -rp "==> $question [y/N] " answer

    [[ "$answer" =~ ^[yY]$ ]]
}

check_new_version() {
    git fetch

    local v1="$VERSION"
    local v2=$(
        git tag \
            | grep -E '^v?[0-9]+\.[0-9]+\.[0-9]+$' \
            | sed 's/^v//' \
            | sort -V \
            | tail -n1
    )
    local v3=$(printf '%s\n%s\n' "$v1" "$v2" | sort -V | tail -n1)

    if [[ "$v1" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "Version format is valid."
    else
        echo "ERROR: Version is not valid! Must use format: NUM.NUM.NUM (e.g., 1.0.0)"
        exit 0
    fi

    if [[ "$v1" != "$v2" && "$v1" = "$v3" ]]; then
        echo "New version is greater than the current version: $v1 > $v2"
    else
        echo "ERROR: New version must be greater than current version! ($v1 <= $v2)"
        exit 0
    fi
}

add_body() {
    local editor
    local tmp
    local body

    read -rp "==> Press Enter to add release notes "

    editor=$(git var GIT_EDITOR)

    tmp=$(mktemp)
    trap 'rm -f "tmp"' EXIT

    "$editor" "$tmp"

    body=$(<"$tmp")

    if [[ -n "$body" ]]; then
        NOTES+=$'\n'
        NOTES+="$body"
        NOTES+=$'\n'
    else
        echo "ERROR: Release notes are required but were not provided."
        exit 1
    fi
}

add_breaking_changes() {
    local entries
    entries=$(
        printf '%s\n' "$COMMITS" \
        | grep -E "^(feat|fix|docs|refactor|style|build|ci|chore|perf|test)(\([^)]+\))?!:" \
        | sed -E "s/^[^:]+: /- /" \
        | sed -E "s/^- ([a-z])/- \u\1/" \
        || true
    )

    if [[ -n "$entries" ]]; then
        NOTES+=$'\n'"### Breaking Changes"$'\n'
        NOTES+="$entries"$'\n'
    fi
}

add_section() {
    local heading="$1"
    local pattern="$2"

    local entries
    entries=$(
        printf '%s\n' "$COMMITS" \
        | grep -E "^${pattern}(\([^)]+\))?:" \
        | sed -E "s/^[^:]+: /- /" \
        | sed -E "s/^- ([a-z])/- \u\1/" \
        || true
    )

    if [[ -n "$entries" ]]; then
        NOTES+=$'\n'"### ${heading}"$'\n'
        NOTES+="$entries"$'\n'
    fi
}

add_other_changes() {
    local entries
    entries=$(
        printf '%s\n' "$COMMITS" \
        | grep -Ev "^(feat|fix|docs|refactor|style|build|ci|chore|perf|test)(\(.+\))?!?:" \
        || true
    )

    if [[ -n "$entries" ]]; then
        NOTES+=$'\n'"### Other Changes"$'\n'
        while IFS= read -r line; do
            NOTES+="- $line"$'\n'
        done <<< "$entries"
    fi
}

add_merges() {
    local entries
    entries=$(printf '%s\n' "$MERGES")
    if [[ -n "$entries" ]]; then
        NOTES+=$'\n'"### Merges"$'\n'
        while IFS= read -r line; do
            NOTES+="- $line"$'\n'
        done <<< "$entries"
    fi
}

generate_notes() {
    NOTES+="# earthcarekit $VERSION "$(date +"(%B %-d, %Y)")$'\n'
    add_body
    if [[ -n "$COMMITS" ]]; then
        NOTES+=$'\n'"## Changelog"$'\n'
        add_breaking_changes
        add_section "New Features" "feat"
        add_section "Bug Fixes" "fix"
        add_section "Maintenance" "refactor|style|build|ci|chore"
        add_section "Documentation" "docs"
        add_section "Performance" "perf"
        add_section "Tests" "test"
        add_other_changes
        add_merges
    fi
}

print_notes() {
    echo "--------------------------------------------------------------------"
    echo "Generated release note file:"
    echo "--------------------------------------------------------------------"
    echo "$NOTES"
    echo "--------------------------------------------------------------------"
}

update_docs_releases() {
    local filepath
    local version
    local items
    local text

    items=$(
        find docs/releases -maxdepth 1 -type f -name "*.md" \
            | grep -E '/[0-9]+\.[0-9]+\.[0-9]+\.md$' \
            | sort -Vr \
            | while read -r filepath; do
                version=$(basename "$filepath" .md)
                echo "- [$version]($version.md)"
            done
    )

    text="# Navigation"$'\n\n'
    text+="$items"
    echo "$text" > docs/releases/SUMMARY.md
}

save_notes() {
    printf '%s' "$NOTES" > "$NOTES_FILE"
}

bump_version() {
    python scripts/version_helper.py "$VERSION"
}

confirm_git_commands() {
    if confirm "Commit?"; then
        git add "$NOTES_FILE" "$DOCS_RELEASES_FILE" "$PYPROJECT_FILE" "$INIT_FILE" "$MKDOCS_FILE" "$DOCS_INDEX_FILE" "$ZENODO_FILE"

        if git diff --cached --quiet; then
            echo "No version changes to commit."
            return 0
        fi

        git commit -m "chore: prepare $VERSION release"
    else
        exit 0
    fi

    if confirm "Push?"; then
        git push origin HEAD
    else
        exit 0
    fi

    if confirm "Create tag $VERSION?"; then
        git tag -a "$VERSION" -m "Release $VERSION"
    else
        exit 0
    fi

    if confirm "Push tag $VERSION?"; then
        git push origin "$VERSION"
    else
        exit 0
    fi
}

# Main program
check_new_version
generate_notes
print_notes

if confirm "Save these release notes?"; then
    save_notes
else
    exit 0
fi

if confirm "Bump version to $VERSION?"; then
    bump_version
else
    exit 0
fi

if confirm "Update releases in documentation?"; then
    update_docs_releases
else
    exit 0
fi

confirm_git_commands
