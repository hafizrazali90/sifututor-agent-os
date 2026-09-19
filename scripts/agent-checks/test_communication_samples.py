"""Regression coverage for the communication sample assessment entry point."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

RUNNER = Path(__file__).with_name('agent-os-response-shape-runner.py')
spec = importlib.util.spec_from_file_location('response_shape', RUNNER)
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class CommunicationSamples(unittest.TestCase):
    def test_unreviewed_short_reply_is_pending_not_failed_shape(self):
        result = runner.assess_sample({'text': 'Yes.', 'context': 'A trivial factual question.'})
        self.assertEqual(result['mechanical_violations'], [])
        self.assertEqual(result['status'], 'manual_review_required')
        self.assertEqual(len(result['manual_pending']), 6)

    def test_reviewed_examples(self):
        path = RUNNER.with_name('communication-samples.json')
        for sample in json.loads(path.read_text()):
            with self.subTest(sample=sample['id']):
                self.assertEqual(runner.assess_sample(sample)['status'], sample['expected_status'])

    def test_bad_review_cannot_silently_pass(self):
        for review in ({'C1': {'verdict': 'pass', 'reason': ''}}, {'C7': {'verdict': 'pass', 'reason': 'typo'}}):
            with self.assertRaises(ValueError):
                runner.assess_sample({'text': 'Yes.', 'context': 'Question', 'review': review})

    def test_unknown_checker_rejected(self):
        with self.assertRaises(ValueError):
            runner.assess_sample({'text': 'Yes.', 'context': 'Question', 'checks': ['typo']})

    def test_brand_in_outbound_text_is_checked(self):
        self.assertTrue(runner.brand_capitalization_violations('```text\nSifuTutor is ready.\n```'))

    def test_literals_are_preserved(self):
        self.assertEqual(runner.brand_capitalization_violations(
            'Sifututor uses `example_SifuTutorDev`, https://example.com/SifuTutor and\n```python\nSifuTutor = 1\n```'), [])

    def test_semantic_checks_do_not_pretend_to_detect_failures(self):
        samples = json.loads(RUNNER.with_name('communication-samples.json').read_text())
        for sample in samples:
            if sample['id'] in ('wrong-language', 'invented-reporter', 'false-live', 'altered-identifier'):
                sample.pop('review')
                self.assertEqual(runner.assess_sample(sample)['status'], 'manual_review_required')

    def test_malformed_fields_rejected(self):
        for sample in (None, [], {}, {'text': 'x', 'context': ''},
                       {'text': 'x', 'context': 'y', 'review': []},
                       {'text': 'x', 'context': 'y', 'checks': [{}]}):
            with self.subTest(sample=sample), self.assertRaises(ValueError):
                runner.assess_sample(sample)

    def test_cli_reviewed_pass_and_failure(self):
        samples = json.loads(RUNNER.with_name('communication-samples.json').read_text())
        for sample in samples:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'samples.json'
                path.write_text(json.dumps([sample]))
                result = subprocess.run([sys.executable, str(RUNNER), '--samples', str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 1 if sample['expected_status'] == 'failed' else 0)
                self.assertFalse(json.loads(result.stdout)['live_agent_compliance_proven'])

    def test_cli_metadata_only_and_exit_codes(self):
        for payload, code in [([{'text': 'PRIVATE_SENTINEL', 'context': 'Question'}], 3), ([], 2), ({}, 2)]:
            with tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / 'samples.json'
                path.write_text(json.dumps(payload))
                result = subprocess.run([sys.executable, str(RUNNER), '--samples', str(path)], capture_output=True, text=True)
                self.assertEqual(result.returncode, code)
                self.assertNotIn('PRIVATE_SENTINEL', result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
