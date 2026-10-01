#!/usr/bin/env python3
"""Tests for the staged-file Biome check."""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
CHECK_PATH = ROOT / "scripts" / "agent-checks" / "biome_staged_check.py"

FAKE_BIOME = """#!/usr/bin/env bash
printf '%s\\n' "$PWD" > "$FAKE_BIOME_LOG"
printf '%s\\n' "$@" >> "$FAKE_BIOME_LOG"
if [ "${FAKE_BIOME_EXIT:-0}" != "0" ]; then
  echo "src/bad.ts format: File content differs from formatting output"
fi
exit "${FAKE_BIOME_EXIT:-0}"
"""


class BiomeStagedCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        base = Path(self.tmp.name)
        self.repo = base / "repo"
        self.repo.mkdir()
        self.log = base / "biome.log"
        self.fake = base / "biome"
        self.fake.write_text(FAKE_BIOME)
        self.fake.chmod(0o755)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.test")
        self.git("config", "user.name", "Test")
        self.write("kept.ts", "export const kept = 1;\n")
        self.write("gone.ts", "export const gone = 1;\n")
        self.git("add", ".")
        self.git("commit", "-q", "-m", "base")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def git(self, *args: str) -> None:
        subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True)

    def write(self, name: str, text: str) -> None:
        path = self.repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

    def run_check(self, cwd: Path | None = None, exit_code: int = 0, binary: Path | None = None):
        env = dict(os.environ)
        env["AGENT_OS_BIOME_BIN"] = str(binary or self.fake)
        env["FAKE_BIOME_LOG"] = str(self.log)
        env["FAKE_BIOME_EXIT"] = str(exit_code)
        return subprocess.run(
            [sys.executable, str(CHECK_PATH)],
            cwd=cwd or self.repo,
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

    def biome_calls(self) -> list[str]:
        return self.log.read_text().splitlines() if self.log.exists() else []

    def test_skips_a_project_without_biome_config(self) -> None:
        self.write("new.ts", "export const a = 1;\n")
        self.git("add", "new.ts")
        result = self.run_check()
        self.assertEqual(result.returncode, 0)
        self.assertIn("no biome.json", result.stdout)
        self.assertEqual(self.biome_calls(), [])

    def test_reports_unavailable_when_biome_is_not_installed(self) -> None:
        self.write("biome.json", "{}\n")
        self.git("add", "biome.json")
        result = self.run_check(binary=Path(self.tmp.name) / "missing-biome")
        self.assertEqual(result.returncode, 0)
        self.assertIn("UNAVAILABLE", result.stdout)

    def test_passes_without_running_biome_when_nothing_is_staged(self) -> None:
        self.write("biome.json", "{}\n")
        self.git("add", "biome.json")
        self.git("commit", "-q", "-m", "config")
        result = self.run_check()
        self.assertEqual(result.returncode, 0)
        self.assertIn("no staged files", result.stdout)
        self.assertEqual(self.biome_calls(), [])

    def test_checks_only_staged_files_from_the_repo_root(self) -> None:
        self.write("biome.json", "{}\n")
        self.write("src/new.ts", "export const a = 1;\n")
        self.write("kept.ts", "export const kept = 2;\n")
        self.write("unstaged.ts", "export const u = 1;\n")
        self.git("add", "biome.json", "src/new.ts", "kept.ts")
        self.git("rm", "-q", "gone.ts")
        result = self.run_check(cwd=self.repo / "src")
        self.assertEqual(result.returncode, 0, result.stderr)
        calls = self.biome_calls()
        self.assertEqual(Path(calls[0]).resolve(), self.repo.resolve())
        self.assertEqual(calls[1], "check")
        checked = calls[calls.index("--") + 1:]
        self.assertEqual(sorted(checked), ["biome.json", "kept.ts", "src/new.ts"])

    def test_blocks_the_commit_when_biome_finds_errors(self) -> None:
        self.write("biome.json", "{}\n")
        self.write("src/bad.ts", "export const  bad=1\n")
        self.git("add", "biome.json", "src/bad.ts")
        result = self.run_check(exit_code=1)
        self.assertEqual(result.returncode, 1)
        self.assertIn("src/bad.ts format", result.stderr)
        self.assertIn("biome check --write", result.stderr)

    def test_reports_unavailable_when_biome_cannot_start(self) -> None:
        self.write("biome.json", "{}\n")
        self.git("add", "biome.json")
        result = self.run_check(exit_code=127)
        self.assertEqual(result.returncode, 0)
        self.assertIn("UNAVAILABLE", result.stdout)
        self.assertIn("exit 127", result.stdout)

    def test_refuses_a_staged_file_whose_disk_copy_differs(self) -> None:
        self.write("biome.json", "{}\n")
        self.write("src/bad.ts", "export const  bad=1\n")
        self.git("add", "biome.json", "src/bad.ts")
        self.write("src/bad.ts", "export const bad = 1;\n")
        result = self.run_check()
        self.assertEqual(result.returncode, 1)
        self.assertIn("- src/bad.ts", result.stderr)
        self.assertEqual(self.biome_calls(), [])


if __name__ == "__main__":
    unittest.main()
