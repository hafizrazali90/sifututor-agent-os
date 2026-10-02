"""Negative fixtures for authority wiring and shared-session plan regressions."""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("business_rules", HERE / "business-rule-check.py")
RULES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(RULES)


class SharedClassPlans(unittest.TestCase):
    def setUp(self):
        self.packet = json.loads((RULES.ROOT / "docs/business-rules/shared-class-plan.example.json").read_text())

    def reject(self, packet):
        with self.assertRaises(ValueError):
            RULES.validate_proposal(packet)

    def test_one_shared_session(self):
        RULES.validate_proposal(self.packet)

    def test_two_scheduled_lessons_are_two_sessions(self):
        r = self.packet["requests"][0]
        r["scheduled_lessons"].append("lesson-2")
        r["expected_sessions"].append({"lesson": "lesson-2", "participants": r["students"][:]})
        RULES.validate_proposal(self.packet)

    def test_separate_requests_remain_separate(self):
        other = copy.deepcopy(self.packet["requests"][0])
        other["request"] = "other-request"
        self.packet["requests"].append(other)
        RULES.validate_proposal(self.packet)

    def test_student_multiplication_rejected(self):
        r = self.packet["requests"][0]
        r["expected_sessions"] = [{"lesson": "lesson-1", "participants": [s]} for s in r["students"]]
        self.reject(self.packet)

    def test_singular_fk_cannot_drop_other_students(self):
        self.packet["requests"][0]["expected_sessions"][0]["participants"] = ["student-a"]
        self.reject(self.packet)

    def test_duplicate_participant_rejected(self):
        self.packet["requests"][0]["expected_sessions"][0]["participants"].append("student-a")
        self.reject(self.packet)

    def test_code_and_memory_not_intent_authority(self):
        for source in ("classes.student_id", "mem_1591e221e0e1", "approved", ""):
            with self.subTest(source=source):
                self.packet["intent_source"] = source
                self.reject(self.packet)

    def test_no_unknown_or_other_rule_claim(self):
        self.packet["rule_id"] = "BR-025"
        self.reject(self.packet)

    def test_unknown_field_cannot_override_contract(self):
        self.packet["split_per_student"] = True
        self.reject(self.packet)

    def test_empty_or_bad_inputs_fail_closed(self):
        for value in (None, [], {}, {"rule_id": "BR-001"}):
            with self.subTest(value=value):
                self.reject(value)
        for key in ("students", "scheduled_lessons", "expected_sessions"):
            for value in ([], None, True, "one"):
                p = copy.deepcopy(self.packet)
                p["requests"][0][key] = value
                self.reject(p)

    def test_duplicate_request_or_lesson_rejected(self):
        p = copy.deepcopy(self.packet)
        p["requests"].append(copy.deepcopy(p["requests"][0]))
        self.reject(p)
        p = copy.deepcopy(self.packet)
        p["requests"][0]["scheduled_lessons"].append("lesson-1")
        self.reject(p)

    def test_missing_implementation_observation_rejected(self):
        self.packet["implementation_observation"] = ""
        self.reject(self.packet)


class Wiring(unittest.TestCase):
    def test_repository(self):
        RULES.validate_repository(RULES.ROOT)

    def test_broken_entry_or_duplicate_rule_is_detected(self):
        import shutil
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shutil.copytree(RULES.ROOT / "docs/business-rules", root / "docs/business-rules")
            (root / "docs/agent-playbooks").mkdir()
            for path in ("AGENTS.md", "CLAUDE.md", "docs/agent-playbooks/context-authority.md"):
                shutil.copyfile(RULES.ROOT / path, root / path)
            RULES.validate_repository(root)
            agents = (root / "AGENTS.md").read_text()
            (root / "AGENTS.md").write_text(agents.replace("docs/business-rules/README.md", "lost.md"))
            with self.assertRaisesRegex(ValueError, "shared entry"):
                RULES.validate_repository(root)
            (root / "AGENTS.md").write_text(agents)
            register = root / "docs/business-rules/register.md"
            register.write_text(register.read_text() + "\n## BR-001\n")
            with self.assertRaisesRegex(ValueError, "104 unique"):
                RULES.validate_repository(root)


if __name__ == "__main__":
    unittest.main()
