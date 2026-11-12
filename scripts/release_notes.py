#!/usr/bin/env python3
"""Prints the release notes of the current version, taken from CHANGELOG.md.

Used by the CI on every run and by the Release workflow, so a missing changelog
entry or a tag that does not match the version is caught before the release day.

    python scripts/release_notes.py              # notes of time_balance/VERSION
    python scripts/release_notes.py --tag v0.6.0 # also checks the tag matches the version
"""

from __future__ import annotations

import argparse
import pathlib
import sys
from collections.abc import Sequence

ROOT = pathlib.Path(__file__).resolve().parent.parent


def read_version(root: pathlib.Path = ROOT) -> str:
    return (root / "time_balance" / "VERSION").read_text(encoding="utf-8").strip()


def extract_notes(changelog: str, version: str) -> str:
    """The lines under ``## [version]``, up to the next ``## `` heading."""
    notes: list[str] = []
    found = False
    for line in changelog.splitlines():
        if line.startswith(f"## [{version}]"):
            found = True
            continue
        if found and line.startswith("## "):
            break
        if found:
            notes.append(line)
    return "\n".join(notes).strip() + "\n" if "".join(notes).strip() else ""


def main(argv: Sequence[str] | None = None, root: pathlib.Path = ROOT) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--tag", help="the git tag being released, for example v0.6.0")
    args = parser.parse_args(argv)

    version = read_version(root)
    if args.tag is not None and args.tag != f"v{version}":
        print(f"Tag {args.tag} does not match time_balance/VERSION (v{version}).", file=sys.stderr)
        return 1
    notes = extract_notes((root / "CHANGELOG.md").read_text(encoding="utf-8"), version)
    if not notes:
        print(f"No section for {version} in CHANGELOG.md.", file=sys.stderr)
        return 1
    sys.stdout.write(notes)
    return 0


if __name__ == "__main__":
    sys.exit(main())
