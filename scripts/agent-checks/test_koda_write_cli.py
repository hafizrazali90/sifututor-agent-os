"""Real CLI journeys using the parent hook patch on temporary copies only.

Mocks the existing initialized transport boundary; no credential access/network.
"""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent

TRANSPORT_FIXTURE = '''
import json
from pathlib import Path
config = json.loads(Path(__file__).with_name('scenario.json').read_text())
calls = []
def koda_initialize(client_name):
    return {}, ''
def koda_tool_call(session, name, arguments, request_id=2):
    calls.append(name)
    Path(__file__).with_name('calls.json').write_text(json.dumps(calls))
    step = config.pop(0)
    assert name == step['tool'], 'unexpected tool or repeated write'
    if 'arguments' in step:
        assert arguments == step['arguments'], 'wrong exact-ID readback'
    if step.get('timeout'): raise TimeoutError('PRIVATE PROVIDER SENTINEL')
    return step['response'], ''
'''


def step(tool, value=None, *, error=False, timeout=False, arguments=None):
    value = {'tool': tool, 'response': {'result': {'content': [{'type': 'text', 'text': json.dumps(value)}],
                                                  'isError': error}}, 'timeout': timeout}
    if arguments is not None:
        value['arguments'] = arguments
    return value


def stage_parent_integration(root):
    patch = str(HERE / 'fixtures/koda-write-integration.patch')
    pending = subprocess.run(['git', 'apply', '--check', patch], cwd=root,
                             capture_output=True, text=True)
    if pending.returncode == 0:
        return subprocess.run(['git', 'apply', patch], cwd=root, capture_output=True, text=True)
    # Once the parent applies the reviewed hunk, exercise that code unchanged.
    return subprocess.run(['git', 'apply', '--reverse', '--check', patch], cwd=root,
                          capture_output=True, text=True)


class IntegratedCLIJourneyTests(unittest.TestCase):
    def run_cli(self, entry, operation, args, steps):
        with tempfile.TemporaryDirectory(prefix='bundle4-koda-cli-') as tmp:
            root = Path(tmp)
            target = root / 'scripts/agent-checks'
            target.mkdir(parents=True)
            for filename in ('koda', 'koda-direct.py', 'codex-lifecycle-hook.py',
                             'agent-os-task-context.py',
                             'koda_contract.py', 'koda_write.py', 'secret_output_guard.py',
                             'test_codex_koda_integration.py'):
                shutil.copy2(HERE / filename, target / filename)
            patch = stage_parent_integration(root)
            self.assertEqual(patch.returncode, 0, patch.stderr)
            (target / 'fixture_transport.py').write_text(TRANSPORT_FIXTURE)
            (target / 'scenario.json').write_text(json.dumps(steps))
            hook = target / 'codex-lifecycle-hook.py'
            hook.write_text(hook.read_text().replace('\nraise SystemExit(main())',
                '\nfrom fixture_transport import koda_initialize, koda_tool_call\nraise SystemExit(main())'))
            if entry == 'shell':
                command = ['/bin/bash', str(target / 'koda'), operation, '-']
            else:
                script = 'koda-direct.py' if entry == 'direct' else 'codex-lifecycle-hook.py'
                command = [sys.executable, str(target / script), '--koda-' + operation + '-json', '-']
            completed = subprocess.run(command, input=json.dumps(args), capture_output=True, text=True,
                                       timeout=10, cwd=root, env={
                                           'PATH': str(Path(sys.executable).parent) + ':/usr/bin:/bin'})
            calls_path = target / 'calls.json'
            calls = json.loads(calls_path.read_text()) if calls_path.exists() else []
            self.assertNotIn('PRIVATE', completed.stdout + completed.stderr)
            self.assertEqual(completed.stderr, '')
            return completed.returncode, json.loads(completed.stdout), calls

    def test_all_real_entrypoints_verify_saved_record(self):
        args = {'content': 'A safe fixture lesson', 'category': 'lesson',
                'tags': ['sifututor', 'koda'], 'source': 'auto-captured'}
        for entry in ('shell', 'direct', 'hook'):
            with self.subTest(entry=entry):
                code, result, calls = self.run_cli(entry, 'store', args, [
                    step('memory_search', []), step('memory_store', {'id': 'mem_1234', 'embedded': True}),
                    step('memory_recall', {'id': 'mem_1234', **args}, arguments={'id': 'mem_1234'})])
                self.assertEqual(code, 0)
                self.assertEqual(result['verification']['state'], 'verified')
                self.assertTrue(result['embedded'])
                self.assertEqual(calls, ['memory_search', 'memory_store', 'memory_recall'])

    def test_cli_mismatch_preserves_id_and_nonzero_does_not_mean_no_write(self):
        args = {'content': 'Fixture lesson', 'category': 'lesson', 'tags': ['sifututor']}
        code, result, calls = self.run_cli('shell', 'store', args, [
            step('memory_search', []), step('memory_store', {'id': 'mem_1234'}),
            step('memory_recall', {'id': 'mem_1234', **args, 'tags': ['default'], 'category': 'fact'})])
        self.assertEqual(code, 1)
        self.assertEqual(result['write_outcome'], 'accepted')
        self.assertEqual(result['id'], 'mem_1234')
        self.assertEqual(result['verification']['mismatched_fields'], ['category', 'tags'])
        self.assertEqual(calls.count('memory_store'), 1)

    def test_cli_read_timeout_never_repeats_update(self):
        code, result, calls = self.run_cli('shell', 'update', {'id': 'mem_1234', 'content': 'Fixture lesson'}, [
            step('memory_update', {'id': 'mem_1234'}), step('memory_recall', timeout=True)])
        self.assertEqual(code, 1)
        self.assertEqual(result['verification']['state'], 'verification_unavailable')
        self.assertEqual(result['id'], 'mem_1234')
        self.assertEqual(result['write_outcome'], 'accepted')
        self.assertEqual(calls, ['memory_update', 'memory_recall'])

    def test_cli_ownership_denial_never_writes_replacement(self):
        code, result, calls = self.run_cli('direct', 'update', {'id': 'mem_1234', 'content': 'Fixture lesson'}, [
            step('memory_update', 'not owned by user PRIVATE PROVIDER SENTINEL', error=True)])
        self.assertEqual(code, 1)
        self.assertEqual(result['write_outcome'], 'rejected')
        self.assertEqual(calls, ['memory_update'])

    def test_cli_retry_of_known_duplicate_does_not_write(self):
        args = {'content': 'Fixture lesson', 'category': 'lesson'}
        for _ in range(2):
            code, result, calls = self.run_cli('shell', 'store', args, [
                step('memory_search', [{'id': 'mem_1234', 'content': 'Fixture lesson'}]),
                step('memory_recall', {'id': 'mem_1234', **args})])
            self.assertEqual(code, 0)
            self.assertEqual(result['write_outcome'], 'existing_record')
            self.assertEqual(calls, ['memory_search', 'memory_recall'])

    def test_parent_patch_preserves_existing_koda_suite(self):
        with tempfile.TemporaryDirectory(prefix='bundle4-parent-suite-') as tmp:
            root = Path(tmp)
            target = root / 'scripts/agent-checks'
            target.mkdir(parents=True)
            for name in ('codex-lifecycle-hook.py', 'secret_output_guard.py', 'koda_contract.py',
                         'agent-os-task-context.py',
                         'koda_write.py', 'koda-verify.py', 'koda-direct.py',
                         'test_codex_koda_integration.py', 'test_koda_direct.py', 'test_koda_write.py'):
                shutil.copy2(HERE / name, target / name)
            applied = stage_parent_integration(root)
            self.assertEqual(applied.returncode, 0, applied.stderr)
            already_applied = stage_parent_integration(root)
            self.assertEqual(already_applied.returncode, 0, already_applied.stderr)
            suite = subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(target),
                                    '-p', 'test_*koda*.py'], cwd=root, capture_output=True, text=True, timeout=15)
            self.assertEqual(suite.returncode, 0, suite.stderr)


if __name__ == '__main__':
    unittest.main()
