#!/usr/bin/env python3
"""Create .claude/settings.json from the tracked hook template.

`.claude/settings.json` is ignored by git, so a new machine gets the guard
scripts but no hook wiring. The tracked `.claude/settings.template.json` holds
the same hook entries with `${CLAUDE_PROJECT_DIR}` in place of a machine path.

Default is a dry run. `--apply` creates the file only when it is missing and
never overwrites an existing one. If the file exists, the hook commands are
compared and any difference is reported.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
VAR = "${CLAUDE_PROJECT_DIR}"
SCRIPT_REF = re.compile(r'"\$\{CLAUDE_PROJECT_DIR\}"/(\S+)')


def hook_commands(settings: dict) -> list[tuple[str, str, str]]:
    """Return (event, matcher, command) for every hook entry."""
    found: list[tuple[str, str, str]] = []
    for event, items in (settings.get("hooks") or {}).items():
        for item in items:
            for hook in item.get("hooks", []):
                found.append((event, item.get("matcher", ""), hook.get("command", "")))
    return found


def validate_template(template: dict, project_dir: Path) -> list[str]:
    problems: list[str] = []
    commands = hook_commands(template)
    if not commands:
        problems.append("template has no hook commands")
    for event, matcher, command in commands:
        if VAR not in command:
            problems.append(f"{event}/{matcher}: command does not use {VAR}")
        if "/Users/" in command or "/home/" in command:
            problems.append(f"{event}/{matcher}: command holds a machine path")
        match = SCRIPT_REF.search(command)
        if match and not (project_dir / match.group(1)).is_file():
            problems.append(f"{event}/{matcher}: missing script {match.group(1)}")
    return problems


def normalise(command: str, project_dir: Path) -> str:
    """Turn a machine-path command into its template form for comparison."""
    return command.replace(f'"{VAR}"', str(project_dir)).replace(VAR, str(project_dir))


def compare(template: dict, existing: dict, project_dir: Path) -> list[str]:
    wanted = {(e, m, normalise(c, project_dir)) for e, m, c in hook_commands(template)}
    have = {(e, m, normalise(c, project_dir)) for e, m, c in hook_commands(existing)}
    notes = [f"missing in existing file: {e}/{m}: {c}" for e, m, c in sorted(wanted - have)]
    notes += [f"extra in existing file: {e}/{m}: {c}" for e, m, c in sorted(have - wanted)]
    return notes


def run(project_dir: Path, apply: bool) -> int:
    template_path = project_dir / ".claude" / "settings.template.json"
    target = project_dir / ".claude" / "settings.json"
    if not template_path.is_file():
        print(f"ERROR: template not found: {template_path}", file=sys.stderr)
        return 1
    template = json.loads(template_path.read_text())
    problems = validate_template(template, project_dir)
    if problems:
        for problem in problems:
            print(f"ERROR: {problem}", file=sys.stderr)
        return 1
    if target.exists() or target.is_symlink():
        try:
            existing = json.loads(target.read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"ERROR: {target} exists but cannot be read as JSON ({exc}). It was not changed.", file=sys.stderr)
            return 1
        notes = compare(template, existing, project_dir)
        if not notes:
            print(f"OK: {target} already has the same hook commands. Nothing changed.")
            return 0
        for note in notes:
            print(f"DIFF: {note}")
        print(f"{target} exists and was not changed. Review the differences above.")
        return 1
    if not apply:
        print(f"DRY RUN: would create {target} from the template. Use --apply.")
        return 0
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        # Exclusive create: fails if the file appeared since the check above, so it can never overwrite.
        with target.open("x") as handle:
            handle.write(template_path.read_text())
    except FileExistsError:
        print(f"{target} appeared while the script was running and was not changed.", file=sys.stderr)
        return 1
    print(f"Created {target} from the template.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project-dir", type=Path, default=ROOT)
    parser.add_argument("--apply", action="store_true", help="create the file when missing")
    args = parser.parse_args(argv)
    return run(args.project_dir.resolve(), args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
