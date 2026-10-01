#!/usr/bin/env python3
"""Run Biome on the staged files of a project that uses Biome.

Issue 230. Ripple was cleaned to zero Biome errors and style errors came back
within days, because nothing checked style before a commit and there is no
hosted CI. This check closes that gap at commit time.

- A repository with no biome.json or biome.jsonc at its root is skipped.
- A project with no installed Biome binary reports UNAVAILABLE and passes.
- Only staged added, copied, modified, or renamed files are checked, so older
  errors in untouched files never block an unrelated commit.

Biome reads the working-tree copy of each staged file. The binary defaults to
the project's node_modules/.bin/biome; AGENT_OS_BIOME_BIN overrides it.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys

PREFIX = "biome-staged-check:"
CONFIG_NAMES = ("biome.json", "biome.jsonc")
TIMEOUT_SECONDS = 180


def git(*args: str) -> str:
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, check=False
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {args[0]} failed: {result.stderr.strip()}")
    return result.stdout


def staged_files() -> list[str]:
    out = git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z")
    return [path for path in out.split("\0") if path]


def biome_binary(root: Path) -> Path | None:
    override = os.environ.get("AGENT_OS_BIOME_BIN")
    candidate = Path(override) if override else root / "node_modules" / ".bin" / "biome"
    return candidate if candidate.is_file() and os.access(candidate, os.X_OK) else None


def main() -> int:
    try:
        root = Path(git("rev-parse", "--show-toplevel").strip())
    except RuntimeError:
        print(f"{PREFIX} UNAVAILABLE not a git work tree")
        return 0

    if not any((root / name).is_file() for name in CONFIG_NAMES):
        print(f"{PREFIX} skipped, no biome.json in this project")
        return 0

    binary = biome_binary(root)
    if binary is None:
        print(f"{PREFIX} UNAVAILABLE biome.json exists but Biome is not installed; run npm install")
        return 0

    try:
        files = staged_files()
    except RuntimeError as exc:
        print(f"{PREFIX} {exc}", file=sys.stderr)
        return 1
    if not files:
        print(f"{PREFIX} no staged files to check")
        return 0

    try:
        result = subprocess.run(
            [
                str(binary),
                "check",
                "--no-errors-on-unmatched",
                "--files-ignore-unknown=true",
                "--",
                *files,
            ],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=TIMEOUT_SECONDS,
            check=False,
        )
    except subprocess.TimeoutExpired:
        print(f"{PREFIX} Biome did not finish within {TIMEOUT_SECONDS}s", file=sys.stderr)
        return 1

    if result.returncode == 0:
        print(f"{PREFIX} {len(files)} staged file(s) pass Biome")
        return 0

    sys.stderr.write(result.stdout)
    sys.stderr.write(result.stderr)
    print(
        f"{PREFIX} Biome found errors in staged files. Fix them, for example with "
        "`npx biome check --write <file>`, then stage the result again.",
        file=sys.stderr,
    )
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
