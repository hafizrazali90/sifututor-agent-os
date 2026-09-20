#!/usr/bin/env python3
"""Regression tests for the live Agent OS project registry check (issue 103).

Positive control: the real workspace tree passes.
Negative controls: each way the registries can drift back makes it fail.
"""

from __future__ import annotations

import importlib.util
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CHECK_PATH = Path(__file__).with_name("agent-os-project-registry-check.py")
ROOT = Path(__file__).resolve().parents[2]


def load_module():
    spec = importlib.util.spec_from_file_location("agent_os_project_registry_check", CHECK_PATH)
    module = importlib.util.module_from_spec(spec)
    # Register before exec: the module defines dataclasses, which resolve
    # their own module from sys.modules during class creation.
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


MODULE = load_module()


def tracked_registry_files() -> list[str]:
    files = list(MODULE.PYTHON_REGISTRIES) + list(MODULE.BASH_REGISTRIES) + list(MODULE.MARKDOWN_REGISTRIES)
    return sorted(set(files))


class ProjectRegistryCheck(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        for rel in tracked_registry_files():
            target = self.tmp / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, target)

    def problems(self, root: Path) -> list[str]:
        return [f"{f.registry}: {f.problem}" for f in MODULE.run_checks(root).findings]

    def patch(self, rel: str, old: str, new: str) -> None:
        path = self.tmp / rel
        text = path.read_text()
        self.assertIn(old, text, f"{rel} no longer contains the patch anchor {old!r}")
        path.write_text(text.replace(old, new, 1))

    # --- positive control -------------------------------------------------

    def test_real_workspace_registries_agree(self):
        self.assertEqual(self.problems(ROOT), [])

    def test_copied_tree_is_a_faithful_baseline(self):
        self.assertEqual(self.problems(self.tmp), [])

    # --- negative controls ------------------------------------------------

    def test_retired_project_readded_to_python_registry_fails(self):
        self.patch(
            "scripts/agent-checks/agent-os-koda-fixture-runner.py",
            '    "finch-inbox",',
            '    "finch-inbox",\n    "team-inbox",',
        )
        problems = self.problems(self.tmp)
        self.assertTrue(
            any("agent-os-koda-fixture-runner.py:PROJECT_TAGS" in p and "team-inbox" in p for p in problems),
            problems,
        )

    def test_retired_project_readded_to_bash_registry_fails(self):
        self.patch(
            "scripts/agent-checks/workflow-doctor.sh",
            "  finch-inbox\n",
            "  finch-inbox\n  team-inbox\n",
        )
        problems = self.problems(self.tmp)
        self.assertTrue(
            any("workflow-doctor.sh:PROJECTS" in p and "team-inbox" in p for p in problems),
            problems,
        )

    def test_retired_project_readded_to_markdown_registry_fails(self):
        self.patch(
            "docs/agent-playbooks/active-tasks.md",
            "- `finch-inbox`",
            "- `finch-inbox`\n- `team-inbox`",
        )
        problems = self.problems(self.tmp)
        self.assertTrue(
            any("active-tasks.md" in p and "team-inbox" in p for p in problems),
            problems,
        )

    def test_active_project_dropped_from_python_registry_fails(self):
        self.patch(
            "scripts/agent-checks/agent-os-today-snapshot.py",
            '    "cx-call-capture-android",\n',
            "",
        )
        problems = self.problems(self.tmp)
        self.assertTrue(
            any("agent-os-today-snapshot.py:PROJECTS" in p and "cx-call-capture-android" in p for p in problems),
            problems,
        )

    def test_kelas_missing_from_koda_registry_fails(self):
        self.patch(
            "scripts/agent-checks/agent-os-koda-fixture-runner.py",
            '    "kelas",\n',
            "",
        )
        problems = self.problems(self.tmp)
        self.assertTrue(
            any("agent-os-koda-fixture-runner.py:PROJECT_TAGS" in p and "kelas" in p for p in problems),
            problems,
        )

    def test_active_project_dropped_from_markdown_registry_fails(self):
        self.patch(
            "AGENTS.md",
            "| `sims-owner-analytics` | Owner-only SIMS analytics service |\n",
            "",
        )
        problems = self.problems(self.tmp)
        self.assertTrue(
            any("AGENTS.md" in p and "sims-owner-analytics" in p for p in problems),
            problems,
        )

    def test_claude_codex_routing_drift_fails(self):
        self.patch(
            "scripts/agent-checks/codex-lifecycle-hook.py",
            '    "cx-call-capture": "cx-call-capture-android",\n',
            "",
        )
        problems = self.problems(self.tmp)
        self.assertTrue(
            any("alias parity" in p for p in problems),
            problems,
        )

    # --- classification: history must survive ------------------------------

    def test_historical_line_may_name_the_retired_project(self):
        self.patch(
            "docs/agent-playbooks/active-tasks.md",
            "- `finch-inbox`",
            "- `finch-inbox`\n- `team-inbox` is retired; see the parity report.",
        )
        self.assertEqual(self.problems(self.tmp), [])

    def test_archive_and_report_files_are_not_parsed_as_live_registries(self):
        parsed = set(tracked_registry_files())
        for historical in (
            "docs/agent-playbooks/claude-codex-parity-implementation-report.md",
            "docs/agent-playbooks/commit-plan.md",
            "docs/agent-playbooks/workflow-rollout-cleanup.md",
            "docs/agent-playbooks/product-push-map.md",
            "scripts/agent-checks/test_claude_hook_dispatch.py",
        ):
            self.assertNotIn(historical, parsed)
            self.assertIn(
                "team-inbox",
                (ROOT / historical).read_text(),
                f"{historical} should still hold its historical team-inbox record",
            )

    # --- CLI contract ------------------------------------------------------

    def test_cli_passes_on_real_tree(self):
        proc = subprocess.run(
            [sys.executable, str(CHECK_PATH), "--root", str(ROOT)],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)
        self.assertIn("PASS", proc.stdout)

    def test_cli_exits_nonzero_on_drift(self):
        self.patch(
            "AGENTS.md",
            "| `finch-inbox` | Finch omnichannel inbox |",
            "| `finch-inbox` | Finch omnichannel inbox |\n| `team-inbox` | WhatsApp/team inbox |",
        )
        proc = subprocess.run(
            [sys.executable, str(CHECK_PATH), "--root", str(self.tmp), "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 1, proc.stdout + proc.stderr)
        self.assertIn("team-inbox", proc.stdout)


if __name__ == "__main__":
    unittest.main()
