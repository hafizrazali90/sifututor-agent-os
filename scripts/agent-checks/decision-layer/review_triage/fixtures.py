#!/usr/bin/env python3
"""Named fixture payloads for the review-triage module (Bundle 5, issue
#166).

Each function returns one complete `triage_change()` payload. Kept in one
shared module so `test_triage.py`, other signal tests, and any future
caller can reuse the exact same fixtures instead of re-typing near-
duplicate payloads. Every fixture required by the task specification is
covered here:

  - a clean small fix with complete evidence (low priority for attention)
  - a change with unrelated file diffs mixed in (flagged)
  - a test file with a removed assertion (flagged as possibly-weakened)
  - a payments-touching change (deterministically flagged regardless of
    provider output)
  - a user-facing change with no named E2E/QA evidence (flagged as missing
    human-journey evidence)
  - a CI failure that is inferable as flaky, one inferable as real, and one
    that is not inferable either way
  - a review comment that reads as blocking and one that reads as
    informational
  - an acceptance-criteria item with no named evidence
  - a staff-facing change with no recorded documentation decision
"""

from __future__ import annotations


def clean_small_fix() -> dict:
    """A clean small fix: tiny diff, related file, complete evidence, not
    user-facing evidence gaps. Every signal should come back low."""
    return {
        "task_description": "Fix a typo in the tutor list empty-state copy.",
        "changed_files": [
            {"path": "src/modules/tutor/EmptyState.tsx", "additions": 2, "deletions": 1, "kind": "code", "related_to_task": True},
        ],
        "test_diff_notes": [],
        "ci_results": [{"job": "unit", "status": "passed", "failure_text": ""}],
        "review_comments": [{"author": "codex", "body": "LGTM, nice small fix."}],
        "acceptance_criteria": [{"item": "Typo no longer shows in the empty state", "evidence": "screenshot: docs/evidence/empty-state-fix.png"}],
        "is_user_facing": True,
        "human_journey_evidence": ["tests/e2e/tutor-list-empty-state.spec.ts"],
        "staff_facing": False,
        "documentation_decision": None,
    }


def unrelated_files_mixed_in() -> dict:
    """Scope-creep fixture: an unrelated file diff mixed into the change."""
    return {
        "task_description": "Fix the tutor payout rounding bug.",
        "changed_files": [
            {"path": "app/Services/PayoutRoundingService.php", "additions": 4, "deletions": 2, "kind": "code", "related_to_task": True},
            {"path": "resources/js/components/UnrelatedChart.tsx", "additions": 80, "deletions": 0, "kind": "code", "related_to_task": False},
        ],
    }


def weakened_test_removed_assertion() -> dict:
    """Weakened-test fixture: an assertion was removed with no stated
    reason."""
    return {
        "task_description": "Fix invoice refund rounding.",
        "changed_files": [{"path": "app/Services/InvoiceRefundService.php", "additions": 6, "deletions": 2, "kind": "code"}],
        "test_diff_notes": [
            {"file": "tests/Feature/InvoiceRefundTest.php", "note": "removed assertRefundAmount check", "assertion_removed": True, "reason_stated": False},
        ],
    }


def payments_touching_change() -> dict:
    """Critical-lane fixture: a payments-touching change, which must
    deterministically classify high priority regardless of what a provider
    would guess."""
    return {
        "task_description": "Adjust invoice rounding for partial refunds.",
        "changed_files": [{"path": "app/Services/InvoiceRefundService.php", "additions": 12, "deletions": 3, "kind": "code", "related_to_task": True}],
        "test_diff_notes": [],
        "ci_results": [{"job": "unit", "status": "passed", "failure_text": ""}],
        "review_comments": [],
        "acceptance_criteria": [{"item": "Refund amount never goes negative", "evidence": "tests/Feature/InvoiceRefundTest.php"}],
        "is_user_facing": True,
        "human_journey_evidence": ["tests/e2e/invoice-refund.spec.ts"],
    }


def user_facing_no_e2e_evidence() -> dict:
    """Missing human-journey-evidence fixture: user-facing change, no named
    E2E or manual-QA evidence."""
    return {
        "task_description": "Add a filter dropdown to the tutor list screen.",
        "changed_files": [{"path": "src/modules/tutor/TutorListFilters.tsx", "additions": 40, "deletions": 5, "kind": "code", "related_to_task": True}],
        "is_user_facing": True,
        "human_journey_evidence": [],
    }


def ci_failure_flaky() -> dict:
    """CI failure category fixture: inferable as flaky."""
    return {"ci_results": [{"job": "e2e", "status": "failed", "failure_text": "Test timed out after 30000ms waiting for selector"}]}


def ci_failure_real() -> dict:
    """CI failure category fixture: inferable as real."""
    return {"ci_results": [{"job": "unit", "status": "failed", "failure_text": "AssertionError: expected 100 to equal 90"}]}


def ci_failure_not_inferable() -> dict:
    """CI failure category fixture: the flaky-vs-real distinction is not
    inferable from the input given."""
    return {"ci_results": [{"job": "deploy", "status": "failed", "failure_text": "job exited with code 17"}]}


def review_comment_blocking() -> dict:
    """Comment-triage fixture: a comment that reads as blocking."""
    return {"review_comments": [{"author": "hafiz", "body": "This must be fixed before merge: the refund amount can go negative."}]}


def review_comment_informational() -> dict:
    """Comment-triage fixture: a comment that reads as informational."""
    return {"review_comments": [{"author": "codex", "body": "nit: consider renaming this variable for clarity."}]}


def acceptance_evidence_missing() -> dict:
    """Acceptance-to-evidence mapping fixture: one item has no named
    evidence."""
    return {
        "acceptance_criteria": [
            {"item": "Refund amount never goes negative", "evidence": "tests/Feature/RefundRoundingTest.php"},
            {"item": "Staff can see the corrected amount on the invoice screen", "evidence": None},
        ]
    }


def staff_facing_missing_doc_decision() -> dict:
    """Staff-documentation-relevance fixture: a staff-facing change with no
    recorded documentation decision."""
    return {
        "changed_files": [{"path": "resources/views/admin/invoices/index.blade.php", "additions": 10, "deletions": 2, "kind": "code"}],
        "documentation_decision": None,
    }
