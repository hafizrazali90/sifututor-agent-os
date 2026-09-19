"""Receipt validation is structural evidence, never semantic acceptance."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import unittest

from completion_receipt import PROOF_DIMENSIONS, validate_receipt

EXPECTED_DIMENSIONS = (
    "entrypoint", "production_caller", "authoritative_result", "bypass_paths",
    "permissions_configuration", "disabled_unavailable", "failure_retry",
    "negative_control", "journey", "regression",
)


def receipt():
    return {
        "schema_version": 1,
        "task_id": "example-task",
        "contract_sha256": "a" * 64,
        "target": {"revision": "local-dirty:reviewed-diff-1", "environment": "local", "state": "changed_locally"},
        "worker": {"id": "builder-session", "outcome": "implemented"},
        "acceptance": [{
            "id": "AC-1", "requirement": "A normal command reaches the shared rule",
            "proof": {dimension: {"status": "recorded", "references": ["synthetic-evidence-1"], "reason": "Synthetic fixture only"} for dimension in EXPECTED_DIMENSIONS},
        }],
        "review": {"reviewer_id": "review-session", "verdict": "accepted", "references": ["synthetic-review-1"], "reason": "Synthetic fixture only"},
    }


class CompletionReceiptTests(unittest.TestCase):
    def test_dimensions_match_independent_contract(self):
        self.assertEqual(EXPECTED_DIMENSIONS, PROOF_DIMENSIONS)

    def test_complete_shape_is_valid(self):
        self.assertEqual([], validate_receipt(receipt()))

    def test_accepted_receipt_cannot_omit_production_caller(self):
        value = receipt()
        del value["acceptance"][0]["proof"]["production_caller"]
        self.assertIn("acceptance[0].proof.production_caller:object_required", validate_receipt(value))

    def test_every_dimension_is_required(self):
        for dimension in EXPECTED_DIMENSIONS:
            with self.subTest(dimension=dimension):
                value = receipt()
                del value["acceptance"][0]["proof"][dimension]
                self.assertTrue(validate_receipt(value))

    def test_recorded_requires_references(self):
        value = receipt()
        value["acceptance"][0]["proof"]["negative_control"]["references"] = []
        self.assertTrue(validate_receipt(value))

    def test_missing_negative_control_cannot_be_accepted(self):
        value = receipt()
        value["acceptance"][0]["proof"]["negative_control"]["status"] = "missing"
        self.assertIn("acceptance[0].proof.negative_control:accepted_with_missing_proof", validate_receipt(value))

    def test_pending_review_preserves_honest_gap(self):
        value = receipt()
        value["review"].update(verdict="pending", reviewer_id="", references=[])
        value["worker"]["outcome"] = "incomplete"
        value["acceptance"][0]["proof"]["journey"].update(status="missing", references=[])
        self.assertEqual([], validate_receipt(value))

    def test_returned_review_can_record_failure(self):
        value = receipt()
        value["review"]["verdict"] = "returned"
        value["worker"]["outcome"] = "failed"
        self.assertEqual([], validate_receipt(value))

    def test_not_applicable_requires_explanation(self):
        value = receipt()
        value["acceptance"][0]["proof"]["permissions_configuration"].update(status="not_applicable", references=[], reason="")
        self.assertTrue(validate_receipt(value))

    def test_self_review_is_not_independent(self):
        value = receipt()
        value["review"]["reviewer_id"] = value["worker"]["id"]
        self.assertTrue(validate_receipt(value))

    def test_accepted_failed_worker_is_inconsistent(self):
        value = receipt()
        value["worker"]["outcome"] = "failed"
        self.assertTrue(validate_receipt(value))

    def test_duplicate_acceptance_id_is_rejected(self):
        value = receipt()
        value["acceptance"].append(copy.deepcopy(value["acceptance"][0]))
        self.assertTrue(validate_receipt(value))

    def test_empty_acceptance_is_rejected(self):
        value = receipt()
        value["acceptance"] = []
        self.assertTrue(validate_receipt(value))

    def test_boolean_schema_version_is_not_one(self):
        value = receipt()
        value["schema_version"] = True
        self.assertTrue(validate_receipt(value))

    def test_contract_requires_full_digest(self):
        value = receipt()
        value["contract_sha256"] = "approval-mentioned-in-chat"
        self.assertTrue(validate_receipt(value))

    def test_target_state_cannot_be_generic_done(self):
        value = receipt()
        value["target"]["state"] = "done"
        self.assertTrue(validate_receipt(value))

    def test_unknown_field_is_rejected_without_echoing_name(self):
        value = receipt()
        value["sensitive-untrusted-field"] = "sensitive-untrusted-value"
        errors = validate_receipt(value)
        self.assertIn("receipt:unexpected_fields", errors)
        self.assertNotIn("sensitive", json.dumps(errors))

    def test_malformed_types_never_crash(self):
        for replacement in (None, True, 12, [], "text"):
            self.assertTrue(validate_receipt(replacement))
            for field in ("target", "worker", "review", "acceptance"):
                value = receipt()
                value[field] = replacement
                self.assertTrue(validate_receipt(value))

    def test_validation_does_not_modify_receipt(self):
        value = receipt()
        original = copy.deepcopy(value)
        validate_receipt(value)
        self.assertEqual(original, value)

    def test_malformed_proof_records_and_references(self):
        for replacement in (None, True, 12, [], "text"):
            value = receipt()
            value["acceptance"][0]["proof"]["entrypoint"] = replacement
            self.assertTrue(validate_receipt(value))
        for replacement in (None, True, 12, [None], [""], "reference"):
            value = receipt()
            value["acceptance"][0]["proof"]["entrypoint"]["references"] = replacement
            self.assertTrue(validate_receipt(value))

    def test_all_nested_unknown_fields_rejected(self):
        for location in (
            lambda v: v["target"], lambda v: v["worker"], lambda v: v["review"],
            lambda v: v["acceptance"][0], lambda v: v["acceptance"][0]["proof"],
            lambda v: v["acceptance"][0]["proof"]["entrypoint"],
        ):
            value = receipt()
            location(value)["private-key-name"] = "private-value"
            errors = validate_receipt(value)
            self.assertTrue(any(e.endswith(":unexpected_fields") for e in errors))
            self.assertNotIn("private", json.dumps(errors))


class ReceiptCliTests(unittest.TestCase):
    def run_cli(self, value):
        return subprocess.run([sys.executable, str(Path(__file__).with_name("completion_receipt.py"))], input=value, text=True, capture_output=True, check=False)

    def test_valid_cli_never_claims_semantic_acceptance(self):
        result = self.run_cli(json.dumps(receipt()))
        self.assertEqual(0, result.returncode)
        output = json.loads(result.stdout)
        self.assertTrue(output["structure_valid"])
        self.assertFalse(output["semantic_acceptance_proven"])
        self.assertNotIn("synthetic-evidence", result.stdout)

    def test_invalid_structure_exit_one(self):
        result = self.run_cli("{}")
        self.assertEqual(1, result.returncode)

    def test_invalid_json_exit_two_and_no_input_echo(self):
        result = self.run_cli("private-untrusted-value")
        self.assertEqual(2, result.returncode)
        self.assertNotIn("private-untrusted", result.stdout + result.stderr)

    def test_duplicate_json_fields_are_rejected(self):
        result = self.run_cli('{"schema_version":1,"schema_version":2}')
        self.assertEqual(2, result.returncode)

    def test_input_size_is_bounded(self):
        result = self.run_cli(" " * (1024 * 1024 + 1) + json.dumps(receipt()))
        self.assertEqual(2, result.returncode)

    def test_references_are_never_read_or_executed(self):
        value = receipt()
        value["acceptance"][0]["proof"]["entrypoint"]["references"] = ["/nonexistent/evidence", "$(not-a-command)"]
        result = self.run_cli(json.dumps(value))
        self.assertEqual(0, result.returncode)
        self.assertEqual("", result.stderr)


if __name__ == "__main__":
    unittest.main()
