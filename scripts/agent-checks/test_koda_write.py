"""Contract tests for verified Koda writes; no credentials or network."""
import json
import unittest
from unittest.mock import Mock

import koda_write


def response(value, **extra):
    return {'result': {'content': [{'type': 'text', 'text': json.dumps(value)}], **extra}}, ''


class WriteIntegrityTests(unittest.TestCase):
    def test_correct_store_round_trip(self):
        args = {'content': 'Keep a durable lesson.', 'category': 'lesson',
                'tags': ['sifututor', 'koda'], 'source': 'auto-captured'}
        call = Mock(side_effect=[response([]), response({'id': 'mem_1234'}),
                                 response({'id': 'mem_1234', **args})])
        result, code = koda_write.verified_write('memory_store', args, call)
        self.assertEqual(code, 0)
        self.assertEqual(result['verification']['state'], 'verified')
        self.assertEqual(result['id'], 'mem_1234')
        self.assertEqual([c.args[0] for c in call.call_args_list],
                         ['memory_search', 'memory_store', 'memory_recall'])
        self.assertEqual(call.call_args_list[-1].args[1], {'id': 'mem_1234'})

    def test_rewritten_contract_fields_fail_without_exposing_values(self):
        for field, actual in [('category', 'fact'), ('tags', ['koda']),
                              ('content', 'private changed body'), ('source', 'correction'),
                              ('project', 'other'), ('why', 'rewritten reason')]:
            with self.subTest(field=field):
                args = {'content': 'Keep a durable lesson.', 'category': 'lesson',
                        'tags': ['sifututor', 'koda'], 'source': 'auto-captured',
                        'project': 'sifututor', 'why': 'Durable reason'}
                record = {'id': 'mem_1234', **args, field: actual}
                call = Mock(side_effect=[response([]), response({'id': 'mem_1234'}), response(record)])
                result, code = koda_write.verified_write('memory_store', args, call)
                self.assertEqual(code, 1)
                self.assertEqual(result['verification']['state'], 'persisted_but_mismatched')
                self.assertEqual(result['verification']['mismatched_fields'], [field])
                self.assertNotIn('private changed body', json.dumps(result))
                self.assertEqual(call.call_count, 3)

    def test_tag_order_and_server_defaults_are_deliberate(self):
        args = {'content': 'Lesson', 'category': 'lesson', 'tags': ['sifututor', 'koda']}
        record = {'id': 'mem_1234', **args, 'tags': ['koda', 'sifututor'],
                  'source': 'auto-captured', 'confidence': 'inferred', 'project': 'default'}
        call = Mock(side_effect=[response([]), response({'id': 'mem_1234'}), response(record)])
        result, code = koda_write.verified_write('memory_store', args, call)
        self.assertEqual(code, 0)
        self.assertEqual(result['verification']['state'], 'verified')

    def test_absent_scope_is_unavailable_and_explicit_scope_mismatch_fails(self):
        args = {'content': 'Lesson', 'category': 'lesson', 'scope': 'project'}
        for scope in [None, 'personal', 'project']:
            with self.subTest(scope=scope):
                record = {'id': 'mem_1234', 'content': 'Lesson', 'category': 'lesson'}
                if scope is not None:
                    record['scope'] = scope
                call = Mock(side_effect=[response([]), response({'id': 'mem_1234'}), response(record)])
                result, code = koda_write.verified_write('memory_store', args, call)
                self.assertEqual(code, 0 if scope == 'project' else 1)
                if scope is None:
                    self.assertEqual(result['verification']['unavailable_fields'], ['scope'])

    def test_update_mismatch_never_repairs_concurrent_edit(self):
        call = Mock(side_effect=[response({'id': 'mem_1234'}),
                                response({'id': 'mem_1234', 'content': 'Another writer changed it'})])
        result, code = koda_write.verified_write('memory_update',
                         {'id': 'mem_1234', 'content': 'Requested change'}, call)
        self.assertEqual(code, 1)
        self.assertEqual(result['verification']['mismatched_fields'], ['content'])
        self.assertEqual([c.args[0] for c in call.call_args_list], ['memory_update', 'memory_recall'])

    def test_timeout_and_access_denied_preserve_id_without_retry(self):
        for failure in [({}, 'timeout PRIVATE'), response('not owned by user PRIVATE', isError=True),
                        TimeoutError('PRIVATE')]:
            with self.subTest(failure=type(failure).__name__):
                call = Mock(side_effect=[response({'id': 'mem_1234'}), failure])
                result, code = koda_write.verified_write('memory_update', {'id': 'mem_1234', 'source': 'correction'}, call)
                self.assertEqual(code, 1)
                self.assertEqual(result['id'], 'mem_1234')
                self.assertEqual(result['write_outcome'], 'accepted')
                self.assertEqual(result['verification']['state'], 'verification_unavailable')
                self.assertNotIn('PRIVATE', json.dumps(result))
                self.assertEqual(call.call_count, 2)

    def test_missing_id_and_ambiguous_write_are_not_success(self):
        for reply, outcome in [(response({'message': 'accepted'}), 'accepted'),
                               (({}, 'timeout PRIVATE'), 'unknown')]:
            call = Mock(side_effect=[response([]), reply])
            result, code = koda_write.verified_write('memory_store', {'content': 'Lesson', 'category': 'lesson'}, call)
            self.assertEqual((code, result['write_outcome']), (1, outcome))
            self.assertEqual(call.call_count, 2)
            self.assertNotIn('PRIVATE', json.dumps(result))

    def test_preflight_duplicate_is_recalled_not_written(self):
        args = {'content': 'Lesson', 'category': 'lesson'}
        for category in ['lesson', 'fact']:
            call = Mock(side_effect=[response([{'id': 'mem_1234', 'content': '  LESSON  '}]),
                                    response({'id': 'mem_1234', 'content': 'Lesson', 'category': category})])
            result, code = koda_write.verified_write('memory_store', args, call)
            self.assertEqual(code, 0 if category == 'lesson' else 1)
            self.assertEqual(result['status'], 'skipped_exact_duplicate')
            self.assertEqual(result['existing_id'], 'mem_1234')
            self.assertEqual([c.args[0] for c in call.call_args_list], ['memory_search', 'memory_recall'])

    def test_server_duplicate_is_not_a_new_save(self):
        call = Mock(side_effect=[response([]), response({'id': 'mem_1234', 'message': 'Duplicate detected — use memory_update', 'processed': True}),
                                response({'id': 'mem_1234', 'content': 'Different', 'category': 'fact'})])
        result, code = koda_write.verified_write('memory_store', {'content': 'Lesson', 'category': 'lesson'}, call)
        self.assertEqual(code, 1)
        self.assertEqual(result['write_outcome'], 'existing_record')
        self.assertEqual(result['status'], 'server_duplicate')
        self.assertEqual(result['existing_id'], 'mem_1234')
        self.assertTrue(result['processed'])

    def test_unsupported_fields_are_rejected_before_write(self):
        for tool, args in [('memory_store', {'content': 'Lesson', 'category': 'lesson', 'confidence': 'confirmed'}),
                           ('memory_update', {'id': 'mem_1234', 'category': 'lesson'})]:
            call = Mock()
            result, code = koda_write.verified_write(tool, args, call)
            self.assertEqual((code, result['write_outcome']), (1, 'not_attempted'))
            call.assert_not_called()

    def test_ownership_rejection_does_not_trigger_fallback_write(self):
        call = Mock(return_value=response('not owned by user PRIVATE', isError=True))
        result, code = koda_write.verified_write('memory_update', {'id': 'mem_1234', 'content': 'Lesson'}, call)
        self.assertEqual(code, 1)
        self.assertEqual(result['write_outcome'], 'rejected')
        self.assertEqual(call.call_count, 1)
        self.assertNotIn('PRIVATE', json.dumps(result))

    def test_malformed_readback_envelopes_are_safe_unavailable(self):
        for malformed in [{'result': {'content': None}}, {'result': {'content': 7}},
                          {'result': {'content': [{'type': 'text', 'text': 'PRIVATE'}]}}, []]:
            call = Mock(side_effect=[response({'id': 'mem_1234'}), (malformed, '')])
            result, code = koda_write.verified_write('memory_update', {'id': 'mem_1234', 'content': 'Lesson'}, call)
            self.assertEqual(code, 1)
            self.assertEqual(result['verification']['state'], 'verification_unavailable')
            self.assertNotIn('PRIVATE', json.dumps(result))

    def test_update_with_only_id_cannot_be_vacuously_verified(self):
        call = Mock(side_effect=[response({'id': 'mem_1234'}), response({'id': 'mem_1234'})])
        result, code = koda_write.verified_write('memory_update', {'id': 'mem_1234'}, call)
        self.assertEqual(code, 1)
        self.assertEqual(result['write_outcome'], 'not_attempted')
        call.assert_not_called()

    def test_identifier_like_private_text_is_not_echoed(self):
        call = Mock(side_effect=[response([]), response({'id': 'mem_PRIVATE_TOKEN'})])
        result, code = koda_write.verified_write('memory_store', {'content': 'Lesson', 'category': 'lesson'}, call)
        self.assertEqual(code, 1)
        self.assertNotIn('PRIVATE', json.dumps(result))
        self.assertEqual(call.call_count, 2)

    def test_write_cli_initialization_failure_is_safe_and_has_no_write(self):
        import contextlib
        import io
        call = Mock()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = koda_write.write_cli('memory_store', {}, Mock(return_value=({}, 'PRIVATE')), call)
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(out.getvalue())['write_outcome'], 'not_attempted')
        self.assertNotIn('PRIVATE', out.getvalue())
        call.assert_not_called()

    def test_update_success_preserves_only_supported_metadata(self):
        args = {'id': 'mem_1234', 'source': 'correction', 'confidence': 'confirmed'}
        call = Mock(side_effect=[response({'id': 'mem_1234', 're_embedded': False,
                                          'fields_updated': ['source', 'confidence', 'PRIVATE'],
                                          'message': 'PRIVATE', 'warning': 'PRIVATE',
                                          'similar_existing': [{'content': 'PRIVATE'}]}), response(args)])
        result, code = koda_write.verified_write('memory_update', args, call)
        self.assertEqual(code, 0)
        self.assertEqual(result['fields_updated'], ['source', 'confidence'])
        self.assertFalse(result['re_embedded'])
        self.assertNotIn('PRIVATE', json.dumps(result))

    def test_readback_must_identify_the_exact_record(self):
        for record in [{'content': 'Lesson'}, {'id': 'mem_5678', 'content': 'Lesson'}]:
            call = Mock(side_effect=[response({'id': 'mem_1234'}), response(record)])
            result, code = koda_write.verified_write('memory_update', {'id': 'mem_1234', 'content': 'Lesson'}, call)
            self.assertEqual(code, 1)
            self.assertEqual(result['id'], 'mem_1234')
            self.assertEqual(result['verification']['state'], 'verification_unavailable')

    def test_missing_duplicate_id_and_preflight_failure_do_not_write(self):
        for reply in [response([{'content': 'Lesson'}]), ({}, 'PRIVATE timeout')]:
            call = Mock(return_value=reply)
            result, code = koda_write.verified_write('memory_store', {'content': 'Lesson', 'category': 'lesson'}, call)
            self.assertEqual(code, 1)
            self.assertEqual(call.call_count, 1)
            self.assertNotIn('PRIVATE', json.dumps(result))


if __name__ == '__main__':
    unittest.main()
