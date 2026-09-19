"""Provider-neutral packet tests. No provider, credentials or network."""
import copy
from datetime import datetime, timezone, timedelta
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

import delegation_packet as packet


NOW = datetime(2026, 9, 19, tzinfo=timezone.utc)


def example():
    return {"schema_version": 1, "task_id": "issue-83-example",
            "goal": "Prove the scoped change", "issue": "83",
            "supervisor": "parent", "worker": "worker-1",
            "worktree": "/tmp/task", "branch": "fix/example", "base_revision": "a" * 40,
            "expires_at": "2026-09-20T00:00:00Z", "finish": "local proof",
            "owned_paths": ["docs/example.md"], "exclusions": ["unrelated changes"],
            "acceptance_ids": ["REQ-1"], "required_capabilities": ["read-files", "edit-files"],
            "adapter_identity": {"tool": "example", "tool_version": "1", "provider": "example",
                                 "model": "example", "configuration_id": "local-fixture", "environment_id": "local-task"},
            "brief_file": ".agent-os/delegations/task/brief.md",
            "brief_sha256": packet.hashlib.sha256(b"Approved requirement REQ-1").hexdigest(),
            "handback_file": ".agent-os/delegations/task/receipt.json",
            "state_dir": ".agent-os/delegations/task/state",
            "max_correction_rounds": 1}


class PacketTests(unittest.TestCase):
    def test_brief_symlink_to_protected_runtime_path_is_not_opened(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            p = example(); root = Path(tmp); p["worktree"] = str(root)
            brief = root/p["brief_file"]; brief.parent.mkdir(parents=True)
            # No protected file exists or is read: only a dangling test symlink.
            brief.symlink_to(brief.parent/".env.synthetic")
            with patch.object(packet.subprocess, "check_output", side_effect=[str(root), p["branch"], p["base_revision"]]), patch.object(Path, "open", side_effect=AssertionError("must not read")):
                self.assertIn("worktree.runtime_escape", packet.worktree_errors(p))

    def test_real_cli_preflight_and_receipt_use_shared_contracts(self):
        from completion_receipt import PROOF_DIMENSIONS
        root = Path(__file__).resolve().parents[2]
        p = example(); p["worktree"] = str(root)
        p["branch"] = subprocess.check_output(["git", "branch", "--show-current"], cwd=root, text=True).strip()
        p["base_revision"] = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        p["adapter_identity"]["environment_id"] = str(root)
        now = datetime.now(timezone.utc)
        p["expires_at"] = (now+timedelta(hours=1)).isoformat()
        record = {"schema_version": 1, "identity": p["adapter_identity"],
                  "observed_at": (now-timedelta(seconds=1)).isoformat(), "expires_at": p["expires_at"],
                  "capabilities": {c: {"status": "supported", "evidence_kind": "live", "evidence_ref": "synthetic-attestation"} for c in p["required_capabilities"]}}
        snapshot = "reviewed-diff-sha256:"+"c"*64
        receipt = {"schema_version": 1, "task_id": p["task_id"], "contract_sha256": packet.contract_digest(p),
                   "target": {"state": "changed_locally", "revision": snapshot, "environment": p["worktree"]},
                   "worker": {"id": p["worker"], "outcome": "implemented"},
                   "acceptance": [{"id": "REQ-1", "requirement": "Scoped example",
                                   "proof": {d: {"status": "recorded", "references": ["fixture-reference"], "reason": "synthetic example only"} for d in PROOF_DIMENSIONS}}],
                   "review": {"reviewer_id": "separate-reviewer", "verdict": "accepted", "references": ["review-ref"], "reason": "synthetic only"}}
        runtime_root = root/".agent-os/delegations"
        runtime_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory(dir=runtime_root) as runtime:
            brief = Path(runtime)/"brief.md"; brief.write_text("Approved requirement REQ-1")
            p["brief_file"] = brief.relative_to(root).as_posix()
            receipt["contract_sha256"] = packet.contract_digest(p)
            paths = [Path(tmp)/n for n in ["packet.json", "capabilities.json", "receipt.json"]]
            for path, value in zip(paths, [p, record, receipt]): path.write_text(json.dumps(value))
            def cli(action, *args):
                r = subprocess.run([sys.executable, str(Path(packet.__file__)), action, "--packet", str(paths[0]), *args], capture_output=True, text=True)
                return r.returncode, json.loads(r.stdout)
            code, result = cli("preflight", "--capabilities", str(paths[1]))
            self.assertEqual(code, 0, result)
            self.assertFalse(result["authority_granted"])
            record["capabilities"]["read-files"]["evidence_kind"] = "fixture"
            paths[1].write_text(json.dumps(record))
            self.assertEqual(cli("preflight", "--capabilities", str(paths[1]))[0], 1)
            options = ["--receipt", str(paths[2]), "--expected-contract-sha256", packet.contract_digest(p), "--expected-target-revision", snapshot]
            code, result = cli("assess-handback", *options)
            self.assertEqual(code, 0, result)
            self.assertFalse(result["semantic_acceptance_proven"])
            self.assertEqual(result["next"], "independent_evidence_review")
            receipt["target"]["revision"] = "stale-diff"
            paths[2].write_text(json.dumps(receipt))
            self.assertEqual(cli("assess-handback", *options)[0], 1)

    def test_changed_brief_content_invalidates_preflight(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp:
            p = example(); root = Path(tmp); p["worktree"] = str(root)
            brief = root/p["brief_file"]; brief.parent.mkdir(parents=True)
            brief.write_text("Changed requirement meaning")
            with patch.object(packet.subprocess, "check_output", side_effect=[str(root), p["branch"], p["base_revision"]]):
                self.assertIn("worktree.brief_changed", packet.worktree_errors(p))

    def test_owned_symlink_cannot_escape_worktree(self):
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as tmp, tempfile.TemporaryDirectory() as outside:
            root = Path(tmp); (root/"docs").symlink_to(outside, target_is_directory=True)
            p = example(); p["worktree"] = str(root)
            with patch.object(packet.subprocess, "check_output", side_effect=[str(root), p["branch"], p["base_revision"]]):
                self.assertIn("worktree.owned_path_escape", packet.worktree_errors(p))

    def test_valid_packet_has_stable_digest(self):
        p = example()
        self.assertEqual(packet.validate_packet(p, now=NOW), [])
        self.assertEqual(packet.contract_digest(p), packet.contract_digest(dict(reversed(list(p.items())))))

    def test_expired_and_nonlocal_boundaries_fail(self):
        for field, value in [("expires_at", "2020-01-01T00:00:00Z"), ("finish", "production live"),
                             ("owned_paths", ["../outside"]), ("owned_paths", [".env.local"]),
                             ("owned_paths", ["live/data"]), ("max_correction_rounds", True),
                             ("acceptance_ids", ["REQ-1", "REQ-1"]), ("brief_file", "outside/brief.md")]:
            with self.subTest(field=field):
                p = example(); p[field] = value
                self.assertTrue(packet.validate_packet(p, now=NOW))

    def test_unknown_fields_and_arbitrary_commands_fail(self):
        p = example(); p["command"] = "PRIVATE"
        self.assertTrue(packet.validate_packet(p, now=NOW))

    def test_brief_carries_digest_owner_boundary_and_acceptance(self):
        p = example(); text = packet.render_brief(p)
        for value in [packet.contract_digest(p), "REQ-1", "local proof", "docs/example.md", "parent"]:
            self.assertIn(value, text)
        self.assertIn("not authorization", text)

    def test_reconcile_requires_independently_pinned_digest_and_exact_ids(self):
        p = example(); digest = packet.contract_digest(p)
        r = {"task_id": p["task_id"], "contract_sha256": digest,
             "acceptance": [{"id": "REQ-1"}], "worker": {"id": "worker-1"},
             "target": {"state": "changed_locally", "revision": p["base_revision"], "environment": p["worktree"]}}
        self.assertEqual(packet.binding_errors(p, r, digest, p["base_revision"]), [])
        for changed in [{**r, "task_id": "different"}, {**r, "contract_sha256": "b"*64},
                        {**r, "acceptance": []}, {**r, "worker": {"id": "stranger"}}]:
            self.assertTrue(packet.binding_errors(p, changed, digest, p["base_revision"]))
        self.assertTrue(packet.binding_errors(p, r, "b"*64, p["base_revision"]))

    def test_receipt_cannot_claim_unapproved_release_state(self):
        p = example(); digest = packet.contract_digest(p)
        r = {"task_id": p["task_id"], "contract_sha256": digest,
             "acceptance": [{"id": "REQ-1"}], "worker": {"id": "worker-1"},
             "target": {"state": "production_deployed", "revision": p["base_revision"], "environment": p["worktree"]}}
        self.assertIn("receipt.target", packet.binding_errors(p, r, digest, p["base_revision"]))

    def test_changed_contract_cannot_renew_itself(self):
        p = example(); frozen = packet.contract_digest(p)
        p["owned_paths"].append("docs/unapproved.md")
        r = {"task_id": p["task_id"], "contract_sha256": packet.contract_digest(p),
             "acceptance": [{"id": "REQ-1"}], "worker": {"id": "worker-1"}}
        self.assertIn("contract.changed", packet.binding_errors(p, r, frozen, p["base_revision"]))

    def test_retry_budget_is_not_permission_to_restart(self):
        self.assertEqual(packet.next_action("returned", 0, 1), "supervisor_review_correction")
        self.assertEqual(packet.next_action("returned", 1, 1), "reconcile_before_new_packet")
        self.assertEqual(packet.next_action("accepted", 0, 1), "independent_evidence_review")
        self.assertEqual(packet.next_action("pending", 0, 1), "await_evidence")

    def test_cli_invalid_input_never_echoes_source(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"packet.json"; path.write_text('{"PRIVATE": true}')
            r = subprocess.run([sys.executable, str(Path(packet.__file__)), "check", "--packet", str(path)],
                               capture_output=True, text=True)
            self.assertNotEqual(r.returncode, 0)
            self.assertNotIn("PRIVATE", r.stdout+r.stderr)

    def test_cli_invalid_flags_never_echo_source(self):
        r = subprocess.run([sys.executable, str(Path(packet.__file__)), "check", "--packet", "unused.json",
                            "--correction-round", "PRIVATE"], capture_output=True, text=True)
        self.assertNotEqual(r.returncode, 0)
        self.assertNotIn("PRIVATE", r.stdout+r.stderr)

    def test_json_duplicate_keys_and_large_input_fail(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"input.json"
            for value in ['{"goal":1,"goal":2}', '['*1200+']'*1200, ' '*1048577]:
                path.write_text(value)
                with self.assertRaises(ValueError):
                    packet.read_safe_json(path)


if __name__ == "__main__":
    unittest.main()
