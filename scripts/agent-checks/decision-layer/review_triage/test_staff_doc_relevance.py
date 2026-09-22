#!/usr/bin/env python3
"""TDD tests for the staff_doc_relevance signal (Bundle 5 signal 7 of 8).

Required fixture: staff-documentation relevance (does this look like a
staff-facing change that needs a changelog/help-text/What's New entry, per
docs/agent-playbooks/release-documentation.md).
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import staff_doc_relevance  # noqa: E402


class NotStaffFacingTest(unittest.TestCase):
    def test_a_backend_only_change_is_low_priority(self) -> None:
        payload = {"changed_files": [{"path": "app/Services/InvoiceRefundService.php"}]}
        record = staff_doc_relevance.classify(payload)
        self.assertEqual(record["priority"], "low")
        self.assertEqual(record["flags"], [])


class StaffFacingWithNoDecisionTest(unittest.TestCase):
    def test_an_admin_screen_change_with_no_decision_is_flagged(self) -> None:
        payload = {"changed_files": [{"path": "resources/views/admin/invoices/index.blade.php"}]}
        record = staff_doc_relevance.classify(payload)
        self.assertEqual(record["priority"], "high")
        self.assertIn("staff_doc_decision_missing_or_incomplete", record["flags"])

    def test_explicit_staff_facing_hint_with_no_decision_is_flagged(self) -> None:
        payload = {"staff_facing": True, "changed_files": []}
        record = staff_doc_relevance.classify(payload)
        self.assertEqual(record["priority"], "high")


class StaffFacingWithRelevantDecisionTest(unittest.TestCase):
    def test_a_relevant_decision_with_artifacts_is_not_flagged(self) -> None:
        payload = {
            "changed_files": [{"path": "resources/views/admin/invoices/index.blade.php"}],
            "documentation_decision": {
                "decision": "relevant",
                "artifacts": ["CHANGELOG.md"],
            },
        }
        record = staff_doc_relevance.classify(payload)
        self.assertEqual(record["priority"], "low")

    def test_relevant_with_no_artifacts_is_still_flagged(self) -> None:
        payload = {
            "changed_files": [{"path": "resources/views/admin/invoices/index.blade.php"}],
            "documentation_decision": {"decision": "relevant", "artifacts": []},
        }
        record = staff_doc_relevance.classify(payload)
        self.assertEqual(record["priority"], "high")


class StaffFacingWithNotRelevantDecisionTest(unittest.TestCase):
    def test_not_relevant_with_a_reason_is_not_flagged(self) -> None:
        payload = {
            "changed_files": [{"path": "resources/views/admin/invoices/index.blade.php"}],
            "documentation_decision": {"decision": "not_relevant", "reason": "Database index only; nothing staff see or do changes."},
        }
        record = staff_doc_relevance.classify(payload)
        self.assertEqual(record["priority"], "low")

    def test_not_relevant_with_no_reason_is_flagged(self) -> None:
        payload = {
            "changed_files": [{"path": "resources/views/admin/invoices/index.blade.php"}],
            "documentation_decision": {"decision": "not_relevant", "reason": ""},
        }
        record = staff_doc_relevance.classify(payload)
        self.assertEqual(record["priority"], "high")


class StaffFacingWithUrgentDeferralTest(unittest.TestCase):
    def test_urgent_deferral_with_owner_and_issue_is_not_flagged(self) -> None:
        payload = {
            "changed_files": [{"path": "resources/views/admin/payouts/index.blade.php"}],
            "documentation_decision": {
                "decision": "urgent_deferral",
                "owner": "Hafiz Razali",
                "follow_up_issue": "#431",
                "reason": "Shipped mid payout window.",
            },
        }
        record = staff_doc_relevance.classify(payload)
        self.assertEqual(record["priority"], "low")

    def test_urgent_deferral_with_no_owner_is_flagged(self) -> None:
        payload = {
            "changed_files": [{"path": "resources/views/admin/payouts/index.blade.php"}],
            "documentation_decision": {"decision": "urgent_deferral", "owner": "", "follow_up_issue": "#431"},
        }
        record = staff_doc_relevance.classify(payload)
        self.assertEqual(record["priority"], "high")


if __name__ == "__main__":
    unittest.main()
