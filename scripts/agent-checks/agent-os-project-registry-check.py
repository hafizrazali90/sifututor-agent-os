#!/usr/bin/env python3
"""Fail when the live Agent OS project registries drift (issue 103).

The workspace states the same fact in many places: which projects are active,
which Koda project tags are valid, and which project names the Claude and Codex
hooks route on. When one of those lists is edited and the others are not, agents
silently disagree about what exists.

This check enforces one rule across every *live* registry:

- `team-inbox` is retired. It must not appear as an active project or as a
  valid Koda project tag.
- The replacement and newly active projects must appear in every live
  registry, while registry-specific requirements cover lists with a narrower
  purpose such as Koda tags and the all-project guard sweep.
- Claude and Codex must route project intent through identical alias maps.

Historical records are deliberately out of scope. Past reports, migration
notes, backup-branch records, and archived-checkout fixtures keep saying
`team-inbox`, because that is what happened. Only the live lists below are
parsed, and inside markdown regions a line that explicitly marks the mention as
retired or archived is allowed.

Usage:
    agent-os-project-registry-check.py [--root PATH] [--json]

Exit codes: 0 all registries agree, 1 drift found, 2 a registry could not be
read or parsed.
"""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]

RETIRED_PROJECT = "team-inbox"
REQUIRED_PROJECTS = (
    "finch-inbox",
    "cx-call-capture-android",
    "sims-owner-analytics",
)

EXTRA_REQUIRED_BY_REGISTRY = {
    "scripts/agent-checks/agent-os-koda-fixture-runner.py:PROJECT_TAGS": ("kelas",),
    "scripts/agent-checks/agent-os-response-shape-runner.py:PROJECT_TAG_MARKERS": ("kelas",),
    "docs/agent-playbooks/save-session.md:all-project guard sweep": ("kelas",),
    "docs/agent-playbooks/save-session.md:koda project tag list": ("kelas",),
    "docs/agent-playbooks/agent-os-memory.md:project tag table": ("kelas",),
}

# A markdown line that carries one of these markers is a historical statement,
# not a live registry entry, so the retired name is allowed on it.
HISTORICAL_LINE_MARKERS = (
    "retired",
    "archived",
    "read-only history",
    "historical record",
)

# Python registries: file -> constant names holding the live project list.
# A dict constant contributes its canonical values; a list/tuple/set
# contributes its string members.
PYTHON_REGISTRIES = {
    ".claude/hooks/koda-context-injector.py": ("PROJECT_NAMES", "PROJECT_TAG_MAP"),
    "scripts/agent-checks/codex-lifecycle-hook.py": ("PROJECTS", "PROJECT_ALIASES"),
    "scripts/agent-checks/agent-os-koda-fixture-runner.py": ("PROJECT_TAGS",),
    "scripts/agent-checks/agent-os-response-shape-runner.py": ("PROJECT_TAG_MARKERS",),
    "scripts/agent-checks/agent-os-today-snapshot.py": ("PROJECTS",),
    "scripts/agent-checks/agent-os-adapter-readiness.py": ("REQUIRED_CLAUDE_PROJECTS",),
    "scripts/agent-checks/worktree-lifecycle.py": ("PROJECTS",),
}

# Bash registries: file -> array names.
BASH_REGISTRIES = {
    "scripts/agent-checks/workflow-doctor.sh": ("PROJECTS",),
}

# Markdown registries: file -> (region label, start marker, end markers).
# The region is the live table or list only; everything outside it is history.
# Several end markers are allowed so the region still resolves on a tree that
# predates the retirement note, and drift is reported as a finding rather than
# an unreadable-registry error.
MARKDOWN_REGISTRIES = {
    "AGENTS.md": (
        ("active project table", "Active projects:", ("Retired projects:", "`live/` contains production snapshots")),
    ),
    "docs/agent-playbooks/README.md": (
        ("project families table", "## Project Families", "## Universal Order"),
    ),
    "docs/agent-playbooks/parity-status.md": (
        ("completed baseline table", "## Completed Baseline", "## Source Of Truth"),
    ),
    "docs/agent-playbooks/active-tasks.md": (
        ("all other projects list", "## All Other Projects", None),
    ),
    "docs/agent-playbooks/project-adoption.md": (
        ("product repo starter map", "## Product Repo Starter Map", "## Adoption Workflow"),
    ),
    "docs/agent-playbooks/save-session.md": (
        ("all-project guard sweep", "For all product projects from the umbrella root:", "Use the all-project sweep"),
        ("koda project tag list", "Every memory needs at least one project tag:", "Never store secrets"),
    ),
    "docs/agent-playbooks/agent-os-memory.md": (
        ("project tag table", "| Tag kind | Purpose | Required? | Allowed values |", "For umbrella Agent OS work"),
    ),
}

# Claude and Codex must agree name-for-name, or the same prompt routes to a
# different project depending on which agent read it.
ALIAS_PARITY = (
    (".claude/hooks/koda-context-injector.py", "PROJECT_TAG_MAP"),
    ("scripts/agent-checks/codex-lifecycle-hook.py", "PROJECT_ALIASES"),
)


class RegistryError(RuntimeError):
    """A live registry could not be read or parsed."""


@dataclass
class Finding:
    registry: str
    problem: str


@dataclass
class Report:
    findings: list[Finding] = field(default_factory=list)
    registries_checked: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.findings


def _literal_members(node: ast.AST) -> set[str]:
    value = ast.literal_eval(node)
    if isinstance(value, dict):
        return {str(item) for item in value.values()}
    if isinstance(value, (list, tuple, set)):
        return {str(item) for item in value}
    raise RegistryError(f"unsupported literal type {type(value).__name__}")


def _python_constants(path: Path, names: tuple[str, ...]) -> dict[str, set[str]]:
    try:
        tree = ast.parse(path.read_text())
    except (OSError, SyntaxError) as exc:
        raise RegistryError(f"{path}: {exc}") from exc
    found: dict[str, set[str]] = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id in names:
                try:
                    found[target.id] = _literal_members(node.value)
                except (ValueError, TypeError) as exc:
                    raise RegistryError(f"{path}: {target.id} is not a literal ({exc})") from exc
    missing = set(names) - set(found)
    if missing:
        raise RegistryError(f"{path}: missing constant(s) {sorted(missing)}")
    return found


def _python_alias_map(path: Path, name: str) -> dict[str, str]:
    try:
        tree = ast.parse(path.read_text())
    except (OSError, SyntaxError) as exc:
        raise RegistryError(f"{path}: {exc}") from exc
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name) and target.id == name:
                value = ast.literal_eval(node.value)
                if not isinstance(value, dict):
                    raise RegistryError(f"{path}: {name} is not a dict")
                return {str(k): str(v) for k, v in value.items()}
    raise RegistryError(f"{path}: missing constant {name}")


def _bash_array(path: Path, name: str) -> set[str]:
    try:
        text = path.read_text()
    except OSError as exc:
        raise RegistryError(f"{path}: {exc}") from exc
    match = re.search(rf"^{re.escape(name)}=\(\s*\n(.*?)^\)\s*$", text, re.M | re.S)
    if not match:
        raise RegistryError(f"{path}: missing bash array {name}")
    members = set()
    for raw in match.group(1).splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            members.update(line.split())
    return members


def _markdown_region(path: Path, start: str, end: str | tuple[str, ...] | None) -> list[str]:
    try:
        lines = path.read_text().splitlines()
    except OSError as exc:
        raise RegistryError(f"{path}: {exc}") from exc
    try:
        begin = next(i for i, line in enumerate(lines) if start in line)
    except StopIteration as exc:
        raise RegistryError(f"{path}: region start not found: {start!r}") from exc
    if end is None:
        return lines[begin:]
    markers = (end,) if isinstance(end, str) else tuple(end)
    stop = next(
        (
            i
            for i in range(begin + 1, len(lines))
            if any(marker in lines[i] for marker in markers)
        ),
        None,
    )
    if stop is None:
        raise RegistryError(f"{path}: region end not found: {markers!r}")
    return lines[begin:stop]


def _is_historical(line: str) -> bool:
    lowered = line.lower()
    return any(marker in lowered for marker in HISTORICAL_LINE_MARKERS)


def _check_members(report: Report, registry: str, members: set[str]) -> None:
    report.registries_checked.append(registry)
    if RETIRED_PROJECT in members:
        report.findings.append(
            Finding(registry, f"lists retired project {RETIRED_PROJECT!r} as active")
        )
    for project in REQUIRED_PROJECTS + EXTRA_REQUIRED_BY_REGISTRY.get(registry, ()):
        if project not in members:
            report.findings.append(
                Finding(registry, f"missing active project {project!r}")
            )


def _check_markdown(report: Report, registry: str, lines: list[str]) -> None:
    report.registries_checked.append(registry)
    live = [line for line in lines if not _is_historical(line)]
    for line in live:
        if re.search(rf"\b{re.escape(RETIRED_PROJECT)}\b", line):
            report.findings.append(
                Finding(
                    registry,
                    f"live line names retired project {RETIRED_PROJECT!r}: {line.strip()[:90]}",
                )
            )
            break
    body = "\n".join(live)
    for project in REQUIRED_PROJECTS + EXTRA_REQUIRED_BY_REGISTRY.get(registry, ()):
        if project not in body:
            report.findings.append(
                Finding(registry, f"missing active project {project!r}")
            )


def run_checks(root: Path) -> Report:
    report = Report()

    for rel, names in PYTHON_REGISTRIES.items():
        constants = _python_constants(root / rel, names)
        for name in names:
            _check_members(report, f"{rel}:{name}", constants[name])

    for rel, names in BASH_REGISTRIES.items():
        for name in names:
            _check_members(report, f"{rel}:{name}", _bash_array(root / rel, name))

    for rel, regions in MARKDOWN_REGISTRIES.items():
        for label, start, end in regions:
            _check_markdown(
                report, f"{rel}:{label}", _markdown_region(root / rel, start, end)
            )

    (claude_rel, claude_name), (codex_rel, codex_name) = ALIAS_PARITY
    claude_map = _python_alias_map(root / claude_rel, claude_name)
    codex_map = _python_alias_map(root / codex_rel, codex_name)
    report.registries_checked.append("claude/codex alias parity")
    if claude_map != codex_map:
        only_claude = sorted(set(claude_map) - set(codex_map))
        only_codex = sorted(set(codex_map) - set(claude_map))
        disagree = sorted(
            name for name in set(claude_map) & set(codex_map)
            if claude_map[name] != codex_map[name]
        )
        report.findings.append(
            Finding(
                "claude/codex alias parity",
                "Claude and Codex project routing disagree: "
                f"claude-only={only_claude} codex-only={only_codex} "
                f"different-tag={disagree}",
            )
        )
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=str(ROOT), help="workspace root to check")
    parser.add_argument("--json", action="store_true", help="emit a JSON report")
    args = parser.parse_args(argv)

    try:
        report = run_checks(Path(args.root))
    except RegistryError as exc:
        if args.json:
            print(json.dumps({"ok": False, "error": str(exc)}, indent=2))
        else:
            print(f"ERROR unreadable registry: {exc}")
        return 2

    if args.json:
        print(
            json.dumps(
                {
                    "ok": report.ok,
                    "registries_checked": report.registries_checked,
                    "findings": [
                        {"registry": f.registry, "problem": f.problem}
                        for f in report.findings
                    ],
                },
                indent=2,
            )
        )
    else:
        for finding in report.findings:
            print(f"FAIL {finding.registry}: {finding.problem}")
        if report.ok:
            print(
                f"PASS {len(report.registries_checked)} live project registries agree "
                f"(retired: {RETIRED_PROJECT}; required: {', '.join(REQUIRED_PROJECTS)})"
            )
    return 0 if report.ok else 1


if __name__ == "__main__":
    sys.exit(main())
