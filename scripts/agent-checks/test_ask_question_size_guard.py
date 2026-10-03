#!/usr/bin/env python3
"""Regression tests for the AskUserQuestion size guard."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


ROOT = Path(__file__).resolve().parents[2]
GUARD_PATH = ROOT / "scripts" / "agent-checks" / "ask-question-size-guard.py"


def load_guard():
    spec = importlib.util.spec_from_file_location("ask_question_size_guard", GUARD_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load ask question size guard")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def box(question: str, options: list[tuple[str, str]]) -> dict:
    return {
        "questions": [
            {
                "question": question,
                "header": "Decision",
                "multiSelect": False,
                "options": [{"label": label, "description": desc} for label, desc in options],
            }
        ]
    }


SHORT = box(
    "Run the cleanup on production tonight?",
    [("Run it now", "Recommended. Takes about two minutes."), ("Not yet", "Keep it paused.")],
)


class AskQuestionSizeGuardTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.guard = load_guard()

    def reasons(self, tool_input: dict) -> list[str]:
        return self.guard.violations(tool_input)

    def test_short_box_is_allowed(self) -> None:
        self.assertEqual(self.reasons(SHORT), [])

    def test_long_question_is_blocked(self) -> None:
        long_q = " ".join(["word"] * 40) + "?"
        self.assertIn("question_too_long", self.reasons(box(long_q, [("A", "x"), ("B", "y")])))

    def test_many_sentences_are_blocked(self) -> None:
        q = "Here is context. And more context. Which one do you want?"
        self.assertIn("too_many_sentences", self.reasons(box(q, [("A", "x"), ("B", "y")])))

    def test_option_count_is_enforced(self) -> None:
        self.assertIn("option_count", self.reasons(box("Pick one?", [("A", "x")])))
        five = [(f"O{i}", "x") for i in range(5)]
        self.assertIn("option_count", self.reasons(box("Pick one?", five)))

    def test_long_label_and_description_are_blocked(self) -> None:
        opts = [("one two three four five six", "x"), ("B", " ".join(["w"] * 15))]
        found = self.reasons(box("Pick one?", opts))
        self.assertIn("label_too_long", found)
        self.assertIn("description_too_long", found)

    def test_every_question_in_the_call_is_checked(self) -> None:
        bad = box(" ".join(["word"] * 40) + "?", [("A", "x"), ("B", "y")])
        both = {"questions": SHORT["questions"] + bad["questions"]}
        self.assertIn("question_too_long", self.reasons(both))

    def test_malformed_input_is_allowed_not_crashed(self) -> None:
        self.assertEqual(self.reasons({}), [])
        self.assertEqual(self.reasons({"questions": "nope"}), [])

    def run_hook(self, payload: dict) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(GUARD_PATH)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )

    def test_hook_denies_long_box_with_reason(self) -> None:
        long_q = " ".join(["word"] * 40) + "?"
        result = self.run_hook({"tool_name": "AskUserQuestion", "tool_input": box(long_q, [("A", "x"), ("B", "y")])})
        self.assertEqual(result.returncode, 0)
        out = json.loads(result.stdout)["hookSpecificOutput"]
        self.assertEqual(out["permissionDecision"], "deny")
        self.assertIn("chat", out["permissionDecisionReason"])

    def test_hook_is_silent_for_short_box_and_other_tools(self) -> None:
        ok = self.run_hook({"tool_name": "AskUserQuestion", "tool_input": SHORT})
        self.assertEqual((ok.returncode, ok.stdout.strip()), (0, ""))
        other = self.run_hook({"tool_name": "Bash", "tool_input": {"command": "ls"}})
        self.assertEqual((other.returncode, other.stdout.strip()), (0, ""))

    def test_hook_survives_bad_stdin(self) -> None:
        result = subprocess.run(
            [sys.executable, str(GUARD_PATH)], input="not json", text=True, capture_output=True, check=False
        )
        self.assertEqual((result.returncode, result.stdout.strip()), (0, ""))


if __name__ == "__main__":
    unittest.main()
