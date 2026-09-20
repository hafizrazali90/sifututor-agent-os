#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys
import types
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
MODULE = HERE / "codex-lifecycle-hook.py"
source = MODULE.read_text().split("\nraise SystemExit(main())", 1)[0]
module = types.ModuleType("codex_lifecycle_weekly_test")
module.__file__ = str(MODULE)
sys.modules[module.__name__] = module
exec(compile(source, str(MODULE), "exec"), module.__dict__)


class WeeklyDeliveryRoutingTests(unittest.TestCase):
    def test_natural_language_routes_to_weekly_delivery(self):
        skill, actions, _reason = module.classify_prompt("What shipped this week?")
        self.assertEqual(skill, "$weekly-delivery")
        self.assertTrue(any("do not rank" in action.lower() for action in actions))

    def test_direct_skill_invocation_is_supported(self):
        skill, _actions, _reason = module.classify_prompt("$weekly-delivery for last week")
        self.assertEqual(skill, "$weekly-delivery")


if __name__ == "__main__":
    unittest.main()
