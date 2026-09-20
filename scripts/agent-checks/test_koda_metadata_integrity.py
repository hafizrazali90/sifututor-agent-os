"""Issue #111 regressions: stored-metadata mismatch and compound-query retrieval.

Deterministic and offline. No credentials, no network, no live Koda writes.
Sanitized stand-ins only; the reported live IDs are never contacted here.
"""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import unittest
from unittest.mock import Mock

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import koda_write  # noqa: E402


def load_hyphenated(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclass resolution needs the registered module
    spec.loader.exec_module(module)
    return module


retrieval = load_hyphenated("koda_retrieval_quality", "agent-os-koda-retrieval-quality.py")


def response(value, **extra):
    return {'result': {'content': [{'type': 'text', 'text': json.dumps(value)}], **extra}}, ''


# The shape reported on issue #111: a sanitized store is accepted, but the
# exact-ID readback shows a different category and a rewritten tag set.
REQUESTED = {
    'content': 'Sanitized Agent OS lesson used only as a local fixture.',
    'category': 'lesson',
    'project': 'sifututor',
    'source': 'auto-captured',
    'tags': ['sifututor', 'agent-os', 'koda'],
    'why': 'Future sessions need the sanitized lesson without a live write.',
}
REWRITTEN = {**REQUESTED, 'category': 'fact', 'tags': ['agent-os']}


class MetadataMismatchCorrectionTests(unittest.TestCase):
    def store_calls(self, record):
        return Mock(side_effect=[response([]), response({'id': 'mem_25e09cc41dbd'}),
                                 response({'id': 'mem_25e09cc41dbd', **record})])

    def test_issue_111_store_mismatch_names_the_safe_correction_path(self):
        call = self.store_calls(REWRITTEN)
        result, code = koda_write.verified_write('memory_store', dict(REQUESTED), call)

        self.assertEqual(code, 1)
        self.assertEqual(result['verification']['state'], 'persisted_but_mismatched')
        self.assertEqual(result['verification']['mismatched_fields'], ['category', 'tags'])
        # Update supports tags but not category, so only part of this is client-fixable.
        self.assertEqual(result['correction']['correctable_by_update'], ['tags'])
        self.assertEqual(result['correction']['owner_action_required'], ['category'])
        self.assertEqual(result['correction']['automatic_repair'], 'never')
        self.assertEqual(result['correction']['command'], 'scripts/agent-checks/koda update')
        self.assertIn('actor', result['correction'])

    def test_rewritten_tags_are_distinguished_from_added_tags(self):
        for record, delta in [(REWRITTEN, {'missing': 2, 'unexpected': 0}),
                              ({**REQUESTED, 'tags': REQUESTED['tags'] + ['risk-low']},
                               {'missing': 0, 'unexpected': 1})]:
            with self.subTest(delta=delta):
                call = self.store_calls(record)
                result, _ = koda_write.verified_write('memory_store', dict(REQUESTED), call)
                self.assertEqual(result['verification']['tag_delta'], delta)

    def test_correction_output_never_echoes_requested_or_stored_values(self):
        private = {**REQUESTED, 'category': 'fact', 'tags': ['PRIVATE-TAG'],
                   'why': 'PRIVATE stored rationale'}
        call = self.store_calls(private)
        result, _ = koda_write.verified_write('memory_store', dict(REQUESTED), call)
        self.assertNotIn('PRIVATE', json.dumps(result))
        self.assertNotIn(REQUESTED['content'], json.dumps(result))

    def test_mismatch_never_triggers_a_repair_or_retry_write(self):
        call = self.store_calls(REWRITTEN)
        koda_write.verified_write('memory_store', dict(REQUESTED), call)
        self.assertEqual([c.args[0] for c in call.call_args_list],
                         ['memory_search', 'memory_store', 'memory_recall'])

    def test_client_delivers_requested_metadata_unchanged(self):
        """Negative control: the rewrite is upstream, not client normalization."""
        call = self.store_calls(REWRITTEN)
        koda_write.verified_write('memory_store', dict(REQUESTED), call)
        delivered = call.call_args_list[1].args[1]
        self.assertEqual(delivered, REQUESTED)
        self.assertEqual(delivered['tags'], REQUESTED['tags'])

    def test_update_only_mismatch_needs_no_owner_action(self):
        call = Mock(side_effect=[response({'id': 'mem_7d57c80bb860'}),
                                 response({'id': 'mem_7d57c80bb860', 'content': 'Different text'})])
        result, code = koda_write.verified_write(
            'memory_update', {'id': 'mem_7d57c80bb860', 'content': 'Requested text'}, call)
        self.assertEqual(code, 1)
        self.assertEqual(result['correction']['correctable_by_update'], ['content'])
        self.assertEqual(result['correction']['owner_action_required'], [])

    def test_verified_write_carries_no_correction_plan(self):
        call = self.store_calls(REQUESTED)
        result, code = koda_write.verified_write('memory_store', dict(REQUESTED), call)
        self.assertEqual(code, 0)
        self.assertNotIn('correction', result)

    def test_project_scope_ownership_denial_names_the_required_actor(self):
        call = Mock(return_value=response('not owned by user PRIVATE', isError=True))
        result, code = koda_write.verified_write(
            'memory_update', {'id': 'mem_7d57c80bb860', 'tags': ['sifututor']}, call)

        self.assertEqual(code, 1)
        self.assertEqual(result['write_outcome'], 'rejected')
        self.assertEqual(result['correction']['blocked_by'], 'project_scope_ownership')
        self.assertEqual(result['correction']['automatic_repair'], 'never')
        self.assertIn('actor', result['correction'])
        self.assertNotIn('command', result['correction'])
        self.assertNotIn('PRIVATE', json.dumps(result))
        self.assertEqual(call.call_count, 1)

    def test_unavailable_readback_offers_no_field_correction(self):
        call = Mock(side_effect=[response({'id': 'mem_1234'}), ({}, 'timeout PRIVATE')])
        result, code = koda_write.verified_write(
            'memory_update', {'id': 'mem_1234', 'content': 'Requested text'}, call)
        self.assertEqual(code, 1)
        self.assertEqual(result['verification']['state'], 'verification_unavailable')
        self.assertNotIn('correction', result)


class CorrectionReportTests(unittest.TestCase):
    def report(self, value):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = koda_write.correction_cli(json.dumps(value))
        return out.getvalue(), code

    def test_report_is_offline_and_explains_both_correction_owners(self):
        mismatch = {'id': 'mem_25e09cc41dbd', 'write_outcome': 'accepted',
                    'verification': {'state': 'persisted_but_mismatched',
                                     'mismatched_fields': ['category', 'tags']},
                    'correction': {'automatic_repair': 'never',
                                   'correctable_by_update': ['tags'],
                                   'owner_action_required': ['category'],
                                   'command': 'scripts/agent-checks/koda update',
                                   'actor': 'memory owner or Koda admin'}}
        text, code = self.report(mismatch)
        self.assertEqual(code, 1)
        self.assertIn('mem_25e09cc41dbd', text)
        self.assertIn('persisted_but_mismatched', text)
        self.assertIn('tags', text)
        self.assertIn('category', text)
        self.assertIn('scripts/agent-checks/koda update', text)
        self.assertIn('never', text)

    def test_verified_report_asks_for_no_action(self):
        text, code = self.report({'id': 'mem_1234', 'verification': {'state': 'verified'}})
        self.assertEqual(code, 0)
        self.assertIn('none', text)

    def test_unknown_or_provider_shaped_input_is_not_echoed(self):
        for value in [{'message': 'PRIVATE provider text'}, {'verification': {'state': 'PRIVATE'}},
                      {'id': 'mem_PRIVATE', 'verification': {'state': 'verified'}}, [], 'PRIVATE']:
            with self.subTest(value=value):
                text, code = self.report(value)
                self.assertNotIn('PRIVATE', text)
                self.assertNotEqual(code, 0)

    def test_report_makes_no_transport_call(self):
        with self.assertRaises(AttributeError):
            koda_write.correction_cli.transport  # the entry point owns no transport

    def test_real_shell_cli_explains_a_mismatch_without_credentials(self):
        mismatch = {'id': 'mem_25e09cc41dbd',
                    'verification': {'state': 'persisted_but_mismatched',
                                     'mismatched_fields': ['category', 'tags']},
                    'correction': {'automatic_repair': 'never',
                                   'correctable_by_update': ['tags'],
                                   'owner_action_required': ['category'],
                                   'command': 'scripts/agent-checks/koda update',
                                   'actor': 'memory owner or Koda admin'}}
        completed = subprocess.run(
            ['/bin/bash', str(HERE / 'koda'), 'correction', json.dumps(mismatch)],
            capture_output=True, text=True, timeout=20,
            env={'PATH': str(Path(sys.executable).parent) + ':/usr/bin:/bin'})

        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertIn('scripts/agent-checks/koda update', completed.stdout)
        self.assertIn('owner action', completed.stdout)
        self.assertEqual(completed.stderr, '')


class CompoundQueryRetrievalTests(unittest.TestCase):
    """Compound multi-topic queries return zero while narrower ones find the record."""

    CASE = retrieval.RetrievalCase(
        id="KRF-fixture",
        query="Agent OS Koda metadata integrity compound retrieval regression fixture",
        expected_any_ids=["mem_25e09cc41dbd"],
        narrow_queries=["Koda metadata integrity", "compound retrieval regression"],
    )

    def corpus(self, hits):
        seen = []

        def search(payload):
            seen.append(payload)
            return hits.get(payload["query"], [])

        return search, seen

    def test_compound_zero_with_narrow_hit_is_attributed_upstream(self):
        search, seen = self.corpus({"Koda metadata integrity": [{"id": "mem_25e09cc41dbd"}]})
        report = retrieval.diagnose(self.CASE, 5, search)

        self.assertEqual(report["attribution"], "upstream_compound_query_gap")
        self.assertFalse(report["compound_found"])
        self.assertTrue(report["narrow_found"])
        self.assertEqual(len(seen), 3)

    def test_narrow_probes_never_relax_the_compound_filters(self):
        search, seen = self.corpus({})
        report = retrieval.diagnose(self.CASE, 5, search)

        self.assertTrue(report["filters_unchanged"])
        self.assertEqual({tuple(sorted(p["tags"])) for p in seen}, {tuple(sorted(seen[0]["tags"]))})
        self.assertEqual({p["limit"] for p in seen}, {5})

    def test_zero_everywhere_is_not_proof_the_memory_is_absent(self):
        search, _ = self.corpus({})
        report = retrieval.diagnose(self.CASE, 5, search)
        self.assertEqual(report["attribution"], "not_retrievable")
        self.assertIn("absence", report["meaning"].lower())

    def test_relaxed_filters_are_reported_as_a_client_defect(self):
        def relaxing(query, limit, **_):
            return {"query": query, "limit": limit, "tags": []}

        search, seen = self.corpus({"Koda metadata integrity": [{"id": "mem_25e09cc41dbd"}]})
        report = retrieval.diagnose(self.CASE, 5, search, payload_builder=relaxing)

        self.assertEqual(report["attribution"], "client_filter_relaxation")
        self.assertFalse(report["filters_unchanged"])
        self.assertEqual(len(seen), 1)

    def test_compound_hit_is_reported_as_retrieved_without_extra_probes(self):
        search, seen = self.corpus({self.CASE.query: [{"id": "mem_25e09cc41dbd"}]})
        report = retrieval.diagnose(self.CASE, 5, search)
        self.assertEqual(report["attribution"], "retrieved")
        self.assertEqual(len(seen), 1)

    def test_diagnosis_never_turns_a_failing_case_into_a_pass(self):
        search, _ = self.corpus({"Koda metadata integrity": [{"id": "mem_25e09cc41dbd"}]})
        ok, errors, _memories, report = retrieval.check_case(self.CASE, 5, search=search)

        self.assertFalse(ok)
        self.assertEqual(report["attribution"], "upstream_compound_query_gap")
        self.assertTrue(any("upstream_compound_query_gap" in error for error in errors))

    def test_self_test_mode_runs_offline(self):
        completed = subprocess.run(
            [sys.executable, str(HERE / "agent-os-koda-retrieval-quality.py"), "--self-test"],
            capture_output=True, text=True, timeout=30,
            env={"PATH": "/usr/bin:/bin"})
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertIn("self-test", completed.stdout)
        self.assertNotIn("KODA_API_KEY", completed.stdout + completed.stderr)


if __name__ == '__main__':
    unittest.main()
