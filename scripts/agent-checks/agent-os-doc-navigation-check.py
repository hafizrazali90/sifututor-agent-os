#!/usr/bin/env python3
"""Check that the Agent OS knowledge architecture stays navigable.

The Agent OS uses progressive disclosure: a small shared entry point
(`AGENTS.md`), a thin Claude adapter (`CLAUDE.md` importing `AGENTS.md`), one
owner index (`docs/agent-playbooks/doc-owner-route-index.md`), a routing
matrix (`docs/agent-playbooks/doc-routing-and-context-loading.md`), and deep
playbooks that are opened only when a task triggers them.

This check proves the wiring without a model call:

- every relative Markdown link and `@import` in the instruction layer resolves;
- `CLAUDE.md` imports `AGENTS.md` and imports nothing else (adapter drift);
- always-loaded entry points stay inside their byte budgets, including the
  Codex 32 KiB `AGENTS.md` chain budget for any sub-project checkout present;
- every active playbook is named in the owner index and every playbook the
  index names exists; archived docs are not linked from the entry layer;
- scenario fixtures (`fixtures/doc-navigation-scenarios.json`) reach the
  documents they must reach within a hop budget, still carry the safety
  phrases they own, import exactly what they must (a product `CLAUDE.md`
  imports its own `AGENTS.md` and nothing else), and the routing matrix rows
  include or exclude the expected documents.

Every result has one state:

- pass: evaluated and correct; counted as passed.
- fail: evaluated and wrong; fails the run.
- advisory: evaluated and wrong in a product repository that is still
  migrating; reported, does not fail the run, and is NOT counted as passed.
- unavailable: the optional product checkout is absent, so nothing was
  evaluated; reported, does not fail the run, and is excluded from the counts.
  An absent checkout is never evidence that the repository is correct.

Run: scripts/agent-checks/agent-os-doc-navigation-check.py [--verbose]
Self-test on synthetic roots: --self-test
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
import tempfile
from collections import deque
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = Path(__file__).resolve().parent / "fixtures" / "doc-navigation-scenarios.json"

PLAYBOOK_DIR = "docs/agent-playbooks"
INDEX_FILE = f"{PLAYBOOK_DIR}/doc-owner-route-index.md"
ROUTING_FILE = f"{PLAYBOOK_DIR}/doc-routing-and-context-loading.md"
ARCHIVE_DIR = f"{PLAYBOOK_DIR}/archive"
ENTRY_LAYER = ("AGENTS.md", "CLAUDE.md", f"{PLAYBOOK_DIR}/task-router.md", ROUTING_FILE)

# Byte budgets for always-loaded files. AGENTS.md is loaded by Codex natively
# and by Claude through the CLAUDE.md import; CLAUDE.md is loaded by Claude at
# launch and inside every sub-project session (parent-directory concatenation).
# Codex reads at most 32 KiB across the AGENTS.md chain (root to cwd).
BUDGETS = {
    "AGENTS.md": 16 * 1024,
    "CLAUDE.md": 8 * 1024,
}
CODEX_CHAIN_BUDGET = 32 * 1024

# Directories under docs/agent-playbooks that are not standalone playbooks.
INDEX_EXEMPT_DIRS = {"archive", "mission-ledger", "templates", "project-profiles"}
INDEX_EXEMPT_FILES = {"README.md", "doc-owner-route-index.md"}

LINK_RE = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
PATH_TOKEN_RE = re.compile(r"`((?:\.\./|\./)?(?:[\w.-]+/)*[\w.-]+\.md)`")
BARE_PATH_RE = re.compile(r"^\s*((?:\.\./)+(?:[\w.-]+/)*[\w.-]+\.md)\s*$", re.MULTILINE)
IMPORT_RE = re.compile(r"^@(\S+)\s*$")
FENCE_RE = re.compile(r"^\s*(```|~~~)")


@dataclass
class Result:
    check_id: str
    passed: bool
    detail: str
    warning: bool = False
    state: str = ""

    def __post_init__(self) -> None:
        if not self.state:
            self.state = "pass" if self.passed else "fail"
        # Only fail blocks the run; advisory and unavailable are reported
        # separately and never counted as passed.
        self.passed = self.state != "fail"


@dataclass
class Graph:
    root: Path
    edges: dict[str, set[str]] = field(default_factory=dict)
    imports: dict[str, list[str]] = field(default_factory=dict)
    broken: list[tuple[str, str]] = field(default_factory=list)
    texts: dict[str, str] = field(default_factory=dict)


def rel(root: Path, path: Path) -> str:
    """Root-relative key; symlinked sub-project checkouts keep their logical path."""
    absolute = path if path.is_absolute() else (root / path)
    try:
        return Path(os.path.normpath(absolute)).relative_to(root).as_posix()
    except ValueError:
        try:
            return path.resolve().relative_to(root.resolve()).as_posix()
        except ValueError:
            return path.as_posix()


def strip_code(text: str) -> tuple[str, str]:
    """Return (prose without fenced blocks, prose without fences or code spans)."""
    kept: list[str] = []
    in_fence = False
    for line in text.splitlines():
        if FENCE_RE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence:
            kept.append(line)
    no_fence = "\n".join(kept)
    no_spans = re.sub(r"`[^`\n]*`", "", no_fence)
    return no_fence, no_spans


def scan_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for name in ("AGENTS.md", "CLAUDE.md"):
        if (root / name).is_file():
            candidates.append(root / name)
    candidates.extend(sorted((root / PLAYBOOK_DIR).rglob("*.md")) if (root / PLAYBOOK_DIR).is_dir() else [])
    candidates.extend(sorted((root / ".agents" / "skills").glob("*/SKILL.md")))
    candidates.extend(sorted((root / ".kilo" / "agents").glob("*.md")))
    return candidates


def resolve_target(root: Path, source: Path, target: str) -> Path | None:
    target = target.split("#", 1)[0]
    if not target or target.startswith(("http://", "https://", "mailto:")):
        return None
    candidate = (source.parent / target)
    if candidate.exists():
        return candidate
    return None


def resolve_token(root: Path, source: Path, token: str) -> Path | None:
    for base in (source.parent, root, root / PLAYBOOK_DIR):
        candidate = base / token
        if candidate.is_file():
            return candidate
    return None


def build_graph(root: Path, extra_files: list[Path] | None = None) -> Graph:
    graph = Graph(root=root)
    files = scan_files(root) + list(extra_files or [])
    for path in files:
        if not path.is_file():
            continue
        key = rel(root, path)
        text = path.read_text(encoding="utf-8", errors="replace")
        graph.texts[key] = text
        no_fence, no_spans = strip_code(text)
        edges = graph.edges.setdefault(key, set())
        for match in LINK_RE.finditer(no_spans):
            raw = match.group(1)
            if raw.startswith(("http://", "https://", "mailto:", "#")):
                continue
            resolved = resolve_target(root, path, raw)
            if resolved is None:
                graph.broken.append((key, raw))
            else:
                edges.add(rel(root, resolved))
        for line in no_fence.splitlines():
            imp = IMPORT_RE.match(line)
            if imp:
                graph.imports.setdefault(key, []).append(imp.group(1))
                resolved = resolve_target(root, path, imp.group(1))
                if resolved is None:
                    graph.broken.append((key, "@" + imp.group(1)))
                else:
                    edges.add(rel(root, resolved))
        # Path pointers count as navigation edges wherever they appear, including
        # fenced "read this file" blocks, because agents follow raw text paths.
        for match in PATH_TOKEN_RE.finditer(text):
            resolved = resolve_token(root, path, match.group(1))
            if resolved is not None:
                edges.add(rel(root, resolved))
        for match in BARE_PATH_RE.finditer(text):
            resolved = resolve_token(root, path, match.group(1))
            if resolved is not None:
                edges.add(rel(root, resolved))
    return graph


def hops(graph: Graph, start: str, target: str, limit: int) -> int | None:
    if start == target:
        return 0
    seen = {start}
    queue: deque[tuple[str, int]] = deque([(start, 0)])
    while queue:
        node, depth = queue.popleft()
        if depth >= limit:
            continue
        for nxt in graph.edges.get(node, ()):
            if nxt == target:
                return depth + 1
            if nxt not in seen:
                seen.add(nxt)
                queue.append((nxt, depth + 1))
    return None


def playbook_inventory(root: Path) -> list[str]:
    base = root / PLAYBOOK_DIR
    if not base.is_dir():
        return []
    names: list[str] = []
    for path in sorted(base.glob("*.md")):
        if path.name in INDEX_EXEMPT_FILES:
            continue
        names.append(path.name)
    return names


def index_named_files(index_text: str) -> set[str]:
    names = set(PATH_TOKEN_RE.findall(index_text))
    names.update(m.group(1).split("#", 1)[0] for m in LINK_RE.finditer(index_text))
    return {Path(n).name for n in names if n.endswith(".md")}


def matrix_row(text: str, row: str) -> str | None:
    wanted = row.strip().lower()
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if cells and cells[0].strip("`*").lower() == wanted:
            return line
    return None


def structural_checks(root: Path, graph: Graph) -> list[Result]:
    results: list[Result] = []

    # DN-001 links and imports resolve.
    if graph.broken:
        sample = "; ".join(f"{src} -> {tgt}" for src, tgt in graph.broken[:6])
        results.append(Result("DN-001", False, f"{len(graph.broken)} unresolved link(s)/import(s): {sample}"))
    else:
        total = sum(len(v) for v in graph.edges.values())
        results.append(Result("DN-001", True, f"all relative links and imports resolve ({total} edges)"))

    # DN-002 CLAUDE.md imports AGENTS.md and nothing else.
    claude = root / "CLAUDE.md"
    if not claude.is_file():
        results.append(Result("DN-002", False, "CLAUDE.md missing: Claude cannot reach AGENTS.md automatically"))
    else:
        imports = graph.imports.get("CLAUDE.md", [])
        if imports == ["AGENTS.md"]:
            results.append(Result("DN-002", True, "CLAUDE.md imports AGENTS.md and nothing else"))
        elif "AGENTS.md" not in imports:
            results.append(Result("DN-002", False, "CLAUDE.md does not import AGENTS.md (needs a line `@AGENTS.md`)"))
        else:
            extra = [i for i in imports if i != "AGENTS.md"]
            results.append(Result("DN-002", False, f"CLAUDE.md imports more than AGENTS.md at launch: {extra}"))

    # DN-003 entry-point byte budgets.
    for name, budget in BUDGETS.items():
        path = root / name
        if not path.is_file():
            continue
        size = path.stat().st_size
        results.append(Result("DN-003", size <= budget, f"{name} is {size} bytes (budget {budget})"))

    # DN-004 Codex AGENTS.md chain budget for present sub-projects.
    agents = root / "AGENTS.md"
    if agents.is_file():
        root_size = agents.stat().st_size
        worst = ("(root only)", root_size)
        for child in sorted(root.iterdir()):
            if child.is_dir() and not child.name.startswith(".") and (child / "AGENTS.md").is_file():
                total = root_size + (child / "AGENTS.md").stat().st_size
                if total > worst[1]:
                    worst = (child.name, total)
        results.append(
            Result(
                "DN-004",
                worst[1] <= CODEX_CHAIN_BUDGET,
                f"largest AGENTS.md chain is {worst[1]} bytes via {worst[0]} (Codex budget {CODEX_CHAIN_BUDGET})",
            )
        )

    # DN-005 owner index coverage both ways.
    index_path = root / INDEX_FILE
    if not index_path.is_file():
        results.append(Result("DN-005", False, f"{INDEX_FILE} missing"))
    else:
        index_text = graph.texts.get(INDEX_FILE) or index_path.read_text(encoding="utf-8", errors="replace")
        named = index_named_files(index_text)
        active = playbook_inventory(root)
        missing_from_index = [n for n in active if n not in named]
        existing = {p.name for p in (root / PLAYBOOK_DIR).rglob("*")}
        existing.update(p.name for p in scan_files(root))
        dangling = sorted(
            n for n in named
            if n not in existing and n not in {"AGENTS.md", "CLAUDE.md", "TESTING.md", "RELEASE-DOCS.md", "README.md", "GOALS.md"}
        )
        if missing_from_index:
            results.append(Result("DN-005", False, f"active playbooks missing from the owner index: {missing_from_index}"))
        else:
            results.append(Result("DN-005", True, f"all {len(active)} active playbooks are named in the owner index"))
        if dangling:
            results.append(Result("DN-006", False, f"owner index names files that do not exist: {dangling}"))
        else:
            results.append(Result("DN-006", True, "every playbook the owner index names exists"))

    # DN-007 archived docs are not linked from the entry layer.
    archive = root / ARCHIVE_DIR
    if archive.is_dir():
        archived = {rel(root, p) for p in archive.rglob("*.md")}
        leaks = [
            (entry, target)
            for entry in ENTRY_LAYER
            for target in sorted(graph.edges.get(entry, ()))
            if target in archived
        ]
        results.append(
            Result(
                "DN-007",
                not leaks,
                "archived docs are not linked from the entry layer" if not leaks else f"entry layer links archived docs: {leaks}",
            )
        )

    # DN-008 orphan warning: active playbooks with no inbound edge from any other active doc.
    inbound: dict[str, int] = {}
    for src, targets in graph.edges.items():
        if src.startswith(ARCHIVE_DIR):
            continue
        for tgt in targets:
            if tgt != src:
                inbound[tgt] = inbound.get(tgt, 0) + 1
    orphans = [
        n for n in playbook_inventory(root)
        if inbound.get(f"{PLAYBOOK_DIR}/{n}", 0) == 0
    ]
    if orphans:
        results.append(Result("DN-008", True, f"playbooks with no inbound reference (consider archive or link): {orphans}", warning=True))
    else:
        results.append(Result("DN-008", True, "every active playbook has at least one inbound reference"))
    return results


def scenario_checks(root: Path, graph: Graph, fixture: dict) -> list[Result]:
    results: list[Result] = []
    routing_rel = fixture.get("routing_matrix", ROUTING_FILE)
    routing_text = graph.texts.get(routing_rel, "")
    for scenario in fixture.get("scenarios", []):
        sid = scenario["id"]
        title = scenario.get("title", "")
        if scenario.get("self_test"):
            results.append(Result(sid, True, f"{title}: proven by --self-test (run separately in health)"))
            continue
        entries = scenario.get("entry", [])
        missing_entries = [e for e in entries if not (root / e).is_file()]
        if missing_entries and scenario.get("optional_entry"):
            results.append(Result(sid, True, f"{title}: not evaluated, checkout absent ({missing_entries})", state="unavailable"))
            continue
        failures: list[str] = []
        if missing_entries:
            failures.append(f"entry missing {missing_entries}")
        # Sub-project entry and import files live outside the default scan; add them to the graph.
        local_graph = graph
        wanted = list(entries) + [spec["file"] for spec in scenario.get("imports", [])]
        extra = [root / e for e in dict.fromkeys(wanted) if e not in graph.texts and (root / e).is_file()]
        if extra:
            local_graph = build_graph(root, extra_files=extra)
        for want in scenario.get("reach", []):
            target = want["file"]
            limit = int(want.get("max_hops", 2))
            best = None
            for entry in entries:
                found = hops(local_graph, entry, target, limit)
                if found is not None and (best is None or found < best):
                    best = found
            if best is None:
                failures.append(f"{target} not reachable within {limit} hop(s) from {entries}")
        for spec in scenario.get("mentions", []):
            text = local_graph.texts.get(spec["file"]) or (
                (root / spec["file"]).read_text(encoding="utf-8", errors="replace") if (root / spec["file"]).is_file() else ""
            )
            for phrase in spec.get("phrases", []):
                if phrase not in text:
                    failures.append(f"{spec['file']} no longer says {phrase!r}")
        for spec in scenario.get("imports", []):
            if not (root / spec["file"]).is_file():
                failures.append(f"{spec['file']} missing, so it cannot import {spec.get('must_import', [])}")
                continue
            imports = local_graph.imports.get(spec["file"], [])
            for must in spec.get("must_import", []):
                if must not in imports:
                    failures.append(f"{spec['file']} must import {must} (found {imports or 'no import'})")
            if spec.get("only"):
                extra_imports = [i for i in imports if i not in spec.get("must_import", [])]
                if extra_imports:
                    failures.append(f"{spec['file']} imports {extra_imports} beyond {spec.get('must_import', [])}")
            for fragment in spec.get("must_not_import_containing", []):
                bad = [i for i in imports if fragment in i]
                if bad:
                    failures.append(f"{spec['file']} imports {bad} (contains {fragment!r})")
        for spec in scenario.get("matrix_rows", []):
            line = matrix_row(routing_text, spec["row"])
            if line is None:
                failures.append(f"routing matrix has no row {spec['row']!r}")
                continue
            for doc in spec.get("include", []):
                if doc not in line:
                    failures.append(f"row {spec['row']!r} must name {doc}")
            for doc in spec.get("exclude", []):
                if doc in line:
                    failures.append(f"row {spec['row']!r} must not name {doc}")
        for spec in scenario.get("max_bytes", []):
            path = root / spec["file"]
            if path.is_file() and path.stat().st_size > int(spec["bytes"]):
                failures.append(f"{spec['file']} is {path.stat().st_size} bytes (limit {spec['bytes']})")
        if failures and scenario.get("advisory"):
            # Product repositories are separate Git repos; report their wiring
            # gaps without failing the umbrella health sweep.
            results.append(Result(sid, False, f"{title}: advisory, fix in the product repo: " + "; ".join(failures), state="advisory"))
        elif failures:
            results.append(Result(sid, False, f"{title}: " + "; ".join(failures)))
        else:
            results.append(Result(sid, True, title))
    return results


def run(root: Path, fixture_path: Path, verbose: bool = False) -> int:
    graph = build_graph(root)
    fixture = json.loads(fixture_path.read_text()) if fixture_path.is_file() else {"scenarios": []}
    results = structural_checks(root, graph) + scenario_checks(root, graph, fixture)
    print_results(results, verbose)
    return 1 if any(r.state == "fail" for r in results) else 0


def summarise(results: list[Result]) -> str:
    counts = {k: sum(1 for r in results if r.state == k) for k in ("pass", "fail", "advisory", "unavailable")}
    evaluated = counts["pass"] + counts["fail"] + counts["advisory"]
    notes = sum(1 for r in results if r.state == "pass" and r.warning)
    scenarios = len([r for r in results if r.check_id.startswith("NAV")])
    return (
        f"agent-os-doc-navigation-check: {counts['pass']}/{evaluated} evaluated checks passed, "
        f"{counts['fail']} failed, {counts['advisory']} advisory, "
        f"{counts['unavailable']} unavailable (not evaluated, not counted), "
        f"{scenarios} scenarios, {notes} note(s)"
    )


def print_results(results: list[Result], verbose: bool) -> None:
    for r in results:
        if r.state == "fail":
            print(f"FAIL {r.check_id} {r.detail}")
        elif r.state == "advisory":
            print(f"ADVISORY {r.check_id} {r.detail}")
        elif r.state == "unavailable":
            print(f"UNAVAILABLE {r.check_id} {r.detail}")
        elif r.warning:
            print(f"NOTE {r.check_id} {r.detail}")
        elif verbose:
            print(f"PASS {r.check_id} {r.detail}")
    print(summarise(results))


# --- self-test on synthetic roots -------------------------------------------

def _write(root: Path, relpath: str, text: str) -> None:
    path = root / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _synthetic_root(root: Path) -> None:
    _write(root, "AGENTS.md", "# AGENTS\nSee [task-router.md](docs/agent-playbooks/task-router.md) and [index](docs/agent-playbooks/doc-owner-route-index.md).\nSafety: never read `.env*`.\n")
    _write(root, "CLAUDE.md", "# CLAUDE\n@AGENTS.md\n\nClaude only.\n")
    _write(root, "docs/agent-playbooks/task-router.md", "# Router\nUse [commit.md](commit.md).\n")
    _write(root, "docs/agent-playbooks/commit.md", "# Commit\nRun the guard.\n")
    _write(root, "docs/agent-playbooks/doc-owner-route-index.md", "# Index\n`task-router.md`, `commit.md`, `doc-routing-and-context-loading.md`\n")
    _write(root, "docs/agent-playbooks/doc-routing-and-context-loading.md", "# Routing\n| Work type | Must read first | Then |\n| --- | --- | --- |\n| Commit | `commit.md` | none |\n")
    # A present, correctly wired product checkout (evaluated as blocking).
    _write(root, "prod/AGENTS.md", "# prod\nShared contract: [../AGENTS.md](../AGENTS.md)\n")
    _write(root, "prod/CLAUDE.md", "# prod\n@AGENTS.md\n")
    # A product checkout still migrating (evaluated as advisory).
    _write(root, "mig/AGENTS.md", "# mig\nShared contract: [../AGENTS.md](../AGENTS.md)\n")
    _write(root, "mig/CLAUDE.md", "# mig\nRead AGENTS.md.\n")


def _synthetic_fixture() -> dict:
    return {
        "routing_matrix": ROUTING_FILE,
        "scenarios": [
            {
                "id": "NAV-S1",
                "title": "claude reaches commit",
                "entry": ["CLAUDE.md"],
                "reach": [{"file": "docs/agent-playbooks/commit.md", "max_hops": 3}],
                "mentions": [{"file": "AGENTS.md", "phrases": [".env*"]}],
                "matrix_rows": [{"row": "Commit", "include": ["commit.md"], "exclude": ["release-deploy-live-monitoring.md"]}],
            },
            {
                "id": "NAV-SP",
                "title": "product checkout wiring",
                "optional_entry": True,
                "entry": ["prod/AGENTS.md"],
                "reach": [{"file": "AGENTS.md", "max_hops": 1}],
                "imports": [{"file": "prod/CLAUDE.md", "must_import": ["AGENTS.md"], "only": True}],
            },
            {
                "id": "NAV-SA",
                "title": "migrating product checkout",
                "optional_entry": True,
                "advisory": True,
                "entry": ["mig/AGENTS.md"],
                "reach": [{"file": "AGENTS.md", "max_hops": 1}],
                "imports": [{"file": "mig/CLAUDE.md", "must_import": ["AGENTS.md"], "only": True}],
            },
        ],
    }


def _state(results: list[Result], check_id: str) -> str:
    return next((r.state for r in results if r.check_id == check_id), "absent")


def _pass_count(results: list[Result]) -> int:
    return sum(1 for r in results if r.state == "pass")


def self_test() -> int:
    def failed(check_id):
        return lambda res: check_id in {r.check_id for r in res if r.state == "fail"}

    def baseline(res):
        return (
            not [r for r in res if r.state == "fail"]
            and _state(res, "NAV-SP") == "pass"
            and _state(res, "NAV-SA") == "advisory"
        )

    def absent_not_counted(res):
        # Removing a passing checkout must lower the passed count by exactly
        # one: the scenario becomes unavailable, never a pass.
        return (
            _state(res, "NAV-SP") == "unavailable"
            and _pass_count(res) == _pass_count(_baseline_results()) - 1
            and "1 unavailable" in summarise(res)
        )

    cases = [
        ("baseline passes; present product checkout evaluated as pass; migrating one as advisory", lambda r: None, baseline),
        ("broken link detected", lambda r: _write(r, "docs/agent-playbooks/task-router.md", "# Router\nUse [missing](nope.md).\n"), failed("DN-001")),
        ("missing AGENTS import detected", lambda r: _write(r, "CLAUDE.md", "# CLAUDE\nRead AGENTS.md please.\n"), failed("DN-002")),
        ("extra launch import detected", lambda r: _write(r, "CLAUDE.md", "# CLAUDE\n@AGENTS.md\n@docs/agent-playbooks/commit.md\n"), failed("DN-002")),
        ("oversize entry point detected", lambda r: _write(r, "CLAUDE.md", "# CLAUDE\n@AGENTS.md\n" + ("x" * (BUDGETS["CLAUDE.md"] + 1)) + "\n"), failed("DN-003")),
        ("unindexed playbook detected", lambda r: _write(r, "docs/agent-playbooks/orphan.md", "# Orphan\n"), failed("DN-005")),
        ("index naming a missing file detected", lambda r: _write(r, "docs/agent-playbooks/doc-owner-route-index.md", "# Index\n`task-router.md`, `commit.md`, `doc-routing-and-context-loading.md`, `ghost.md`\n"), failed("DN-006")),
        ("archived doc linked from entry detected", lambda r: (_write(r, "docs/agent-playbooks/archive/old.md", "# Old\n"), _write(r, "AGENTS.md", "# AGENTS\n[task-router.md](docs/agent-playbooks/task-router.md) [index](docs/agent-playbooks/doc-owner-route-index.md) [old](docs/agent-playbooks/archive/old.md)\nnever read `.env*`.\n")), failed("DN-007")),
        ("unreachable scenario target detected", lambda r: (_write(r, "docs/agent-playbooks/task-router.md", "# Router\nNo links here.\n"), _write(r, "docs/agent-playbooks/doc-owner-route-index.md", "# Index\n`task-router.md`, `doc-routing-and-context-loading.md`\n")), failed("NAV-S1")),
        ("lost safety phrase detected", lambda r: _write(r, "AGENTS.md", "# AGENTS\n[task-router.md](docs/agent-playbooks/task-router.md) [index](docs/agent-playbooks/doc-owner-route-index.md)\n"), failed("NAV-S1")),
        ("matrix row drift detected", lambda r: _write(r, "docs/agent-playbooks/doc-routing-and-context-loading.md", "# Routing\n| Work type | Must read first | Then |\n| --- | --- | --- |\n| Commit | `commit.md`, `release-deploy-live-monitoring.md` | none |\n"), failed("NAV-S1")),
        ("missing product CLAUDE import detected", lambda r: _write(r, "prod/CLAUDE.md", "# prod\nPlease read AGENTS.md.\n"), failed("NAV-SP")),
        ("wrong product CLAUDE import detected", lambda r: _write(r, "prod/CLAUDE.md", "# prod\n@../AGENTS.md\n"), failed("NAV-SP")),
        ("extra product CLAUDE import detected", lambda r: _write(r, "prod/CLAUDE.md", "# prod\n@AGENTS.md\n@README.md\n"), failed("NAV-SP")),
        ("missing product CLAUDE file detected", lambda r: (r / "prod/CLAUDE.md").unlink(), failed("NAV-SP")),
        ("product contract without upward route detected", lambda r: _write(r, "prod/AGENTS.md", "# prod\nNo shared route.\n"), failed("NAV-SP")),
        ("absent optional checkout is unavailable and not counted as passed", lambda r: (shutil.rmtree(r / "prod")), absent_not_counted),
        ("advisory migration failure is not counted as passed", lambda r: None, lambda res: _state(res, "NAV-SA") == "advisory" and not any(x.check_id == "NAV-SA" and x.state == "pass" for x in res)),
    ]
    failures = 0
    for name, mutate, check in cases:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _synthetic_root(root)
            mutate(root)
            results = _results(root)
            ok = bool(check(results))
            detail = "" if ok else f" (states: {sorted((r.check_id, r.state) for r in results if r.state != 'pass')})"
            print(f"{'PASS' if ok else 'FAIL'} self-test: {name}{detail}")
            if not ok:
                failures += 1
    print(f"agent-os-doc-navigation-check self-test: {len(cases) - failures}/{len(cases)} cases passed")
    return 1 if failures else 0


def _results(root: Path) -> list[Result]:
    graph = build_graph(root)
    return structural_checks(root, graph) + scenario_checks(root, graph, _synthetic_fixture())


def _baseline_results() -> list[Result]:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        _synthetic_root(root)
        return _results(root)


def main() -> int:
    parser = argparse.ArgumentParser(description="Check Agent OS knowledge navigation, ownership, adapters, and scenarios.")
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--fixture", type=Path, default=FIXTURE)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--self-test", action="store_true", help="prove the check detects broken navigation on synthetic roots")
    args = parser.parse_args()
    if args.self_test:
        return self_test()
    return run(args.root, args.fixture, verbose=args.verbose)


if __name__ == "__main__":
    sys.exit(main())
