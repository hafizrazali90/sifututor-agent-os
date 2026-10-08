#!/usr/bin/env python3
"""Tests for the tracked hook template and its setup script."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = ROOT / "scripts" / "agent-checks" / "render-claude-settings.py"
TEMPLATE_PATH = ROOT / ".claude" / "settings.template.json"


def load_module():
    spec = importlib.util.spec_from_file_location("render_claude_settings", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load render-claude-settings.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class TemplateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module()
        cls.template = json.loads(TEMPLATE_PATH.read_text())

    def test_template_has_twelve_hooks(self) -> None:
        self.assertEqual(len(self.mod.hook_commands(self.template)), 12)

    def test_template_holds_no_machine_path(self) -> None:
        text = TEMPLATE_PATH.read_text()
        self.assertNotIn("/Users/", text)
        self.assertNotIn("/home/", text)

    def test_every_script_exists_in_the_repo(self) -> None:
        self.assertEqual(self.mod.validate_template(self.template, ROOT), [])

    def test_template_holds_exactly_the_expected_hook_scripts(self) -> None:
        # Update this list on purpose when a hook is added or removed.
        expected = sorted([
            "scripts/agent-checks/agent-os-approval-guard.py --resume",
            "scripts/agent-checks/agent-os-approval-guard.py --identity",
            ".claude/hooks/koda-context-injector.py",
            "scripts/agent-checks/agent-os-approval-guard.py",
            "scripts/agent-checks/secret_output_guard.py",
            "scripts/agent-checks/ask-question-size-guard.py",
            ".claude/hooks/validate-branch-name.py",
            ".claude/hooks/conventional-commits.py",
            ".claude/hooks/test-coverage-gate.py",
            ".claude/hooks/friction-logger.py",
            "scripts/agent-checks/skill-tips-hook.py --suggest",
            "scripts/agent-checks/skill-tips-hook.py --tip",
        ])
        found = sorted(cmd.split('"${CLAUDE_PROJECT_DIR}"/', 1)[1] for _e, _m, cmd in self.mod.hook_commands(self.template))
        self.assertEqual(found, expected)

    def test_template_has_only_schema_and_hooks(self) -> None:
        self.assertEqual(sorted(self.template), ["$schema", "hooks"])


class RenderTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.mod = load_module()

    def make_project(self, tmp: Path) -> Path:
        claude = tmp / ".claude"
        claude.mkdir()
        (tmp / "scripts" / "agent-checks").mkdir(parents=True)
        (claude / "hooks").mkdir()
        template = json.loads(TEMPLATE_PATH.read_text())
        for _event, _matcher, command in self.mod.hook_commands(template):
            match = self.mod.SCRIPT_REF.search(command)
            if match:
                path = tmp / match.group(1)
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("")
        (claude / "settings.template.json").write_text(TEMPLATE_PATH.read_text())
        return tmp

    def test_dry_run_creates_nothing(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            self.assertEqual(self.mod.run(project, apply=False), 0)
            self.assertFalse((project / ".claude" / "settings.json").exists())

    def test_apply_creates_the_file_when_missing(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            self.assertEqual(self.mod.run(project, apply=True), 0)
            self.assertTrue((project / ".claude" / "settings.json").is_file())

    def test_existing_file_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            target = project / ".claude" / "settings.json"
            target.write_text('{"hooks": {}}\n')
            self.assertEqual(self.mod.run(project, apply=True), 1)
            self.assertEqual(target.read_text(), '{"hooks": {}}\n')

    def test_machine_path_file_with_same_hooks_counts_as_same(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            template_text = TEMPLATE_PATH.read_text()
            rendered = template_text.replace('\\"${CLAUDE_PROJECT_DIR}\\"', str(project))
            self.assertNotEqual(rendered, template_text, "the replace must change something or this test proves nothing")
            target = project / ".claude" / "settings.json"
            target.write_text(rendered)
            self.assertEqual(self.mod.run(project, apply=True), 0)
            self.assertEqual(target.read_text(), rendered, "an existing file with the same hooks must stay byte for byte")

    def test_unreadable_existing_file_is_reported_and_left_alone(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            target = project / ".claude" / "settings.json"
            target.write_text("{ not json")
            self.assertEqual(self.mod.run(project, apply=True), 1)
            self.assertEqual(target.read_text(), "{ not json")

    def test_dangling_symlink_is_not_followed_or_filled(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            elsewhere = project / "elsewhere.json"
            link = project / ".claude" / "settings.json"
            link.symlink_to(elsewhere)
            self.assertEqual(self.mod.run(project, apply=True), 1)
            self.assertFalse(elsewhere.exists(), "the script must not create the file the link points to")

    def test_file_that_appears_after_the_check_is_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            target = project / ".claude" / "settings.json"
            real_exists = Path.exists

            def racing_exists(path: Path) -> bool:
                result = real_exists(path)
                if path == target and not result and not real_exists(target):
                    target.write_text("{\"hooks\": {}}\n")  # another process creates it right after the check
                return result

            with mock.patch.object(Path, "exists", racing_exists):
                self.assertEqual(self.mod.run(project, apply=True), 1)
            self.assertEqual(target.read_text(), "{\"hooks\": {}}\n")

    def test_template_without_variable_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            project = self.make_project(Path(raw))
            bad = {"hooks": {"PreToolUse": [{"matcher": ".*", "hooks": [
                {"type": "command", "command": "python3 /Users/someone/x.py"}]}]}}
            (project / ".claude" / "settings.template.json").write_text(json.dumps(bad))
            self.assertEqual(self.mod.run(project, apply=False), 1)


if __name__ == "__main__":
    unittest.main()
