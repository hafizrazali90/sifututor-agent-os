"""Verified writes over the existing Koda transport, without repair or retries.

The callback accepts (tool_name, arguments) and returns (MCP response, error).
Only metadata crosses the result boundary; provider diagnostics are never echoed.
"""
from __future__ import annotations

import json
import re
from collections.abc import Callable

STORE_FIELDS = frozenset({'content', 'category', 'why', 'tags', 'source', 'project', 'scope'})
UPDATE_FIELDS = frozenset({'id', 'content', 'why', 'tags', 'source', 'confidence'})
# Current UUID suffix and legacy sequential IDs; reject arbitrary provider text.
MEMORY_ID = re.compile(r'mem_(?:[0-9]{4,12}|[a-f0-9]{12})\Z')


def safe_id(value):
    return value if isinstance(value, str) and MEMORY_ID.fullmatch(value) else None


def payload(response):
    if not isinstance(response, dict) or response.get('error'):
        return None
    result = response.get('result')
    if not isinstance(result, dict) or result.get('isError'):
        return None
    if isinstance(result.get('structuredContent'), (dict, list)):
        return result['structuredContent']
    content = result.get('content', [])
    if not isinstance(content, list):
        return None
    for item in content:
        if isinstance(item, dict) and item.get('type') == 'text':
            try:
                return json.loads(item.get('text', ''))
            except (ValueError, TypeError):
                return None
    return None


def invoke(call, name, arguments):
    try:
        response, error = call(name, arguments)
    except Exception:
        return None, 'transport_unavailable'
    if error:
        # Inspect only to classify; never return the provider's text.
        lowered = str(error).lower()
        if any(word in lowered for word in ('not owned', 'access denied', 'forbidden', 'unauthorized')):
            return None, 'access_denied'
        return None, 'transport_unavailable'
    if isinstance(response, dict) and (response.get('error') or
            isinstance(response.get('result'), dict) and response['result'].get('isError')):
        return None, 'tool_rejected'
    value = payload(response)
    return value, '' if value is not None else 'malformed_response'


def result(state, outcome, record_id=None, *, reason=None, mismatched=(), unavailable=(), duplicate=False):
    value = {'status': 'skipped_exact_duplicate' if duplicate else outcome,
             'write_outcome': outcome,
             'verification': {'state': state}}
    if record_id:
        value['id'] = record_id
        if duplicate:
            value['existing_id'] = record_id
    if reason:
        value['verification']['reason'] = reason
    if mismatched:
        value['verification']['mismatched_fields'] = sorted(mismatched)
    if unavailable:
        value['verification']['unavailable_fields'] = sorted(unavailable)
    if state != 'verified':
        value['next'] = 'Reconcile by exact ID when available; do not blindly retry or repair.'
    return value, 0 if state == 'verified' else 1


def canonical(value):
    return re.sub(r'\s+', ' ', str(value or '').casefold()).strip()


def verify(arguments, record_id, call, outcome, duplicate=False):
    record, error = invoke(call, 'memory_recall', {'id': record_id})
    if error or not isinstance(record, dict) or record.get('id') != record_id:
        return result('verification_unavailable', outcome, record_id,
                      reason=error or 'readback_identity_missing_or_different', duplicate=duplicate)
    mismatched, unavailable = [], []
    for field, expected in arguments.items():
        if field == 'id':
            continue
        if field not in record:
            unavailable.append(field)
        elif field == 'tags':
            actual = record[field]
            if not isinstance(actual, list) or not all(isinstance(t, str) for t in actual) or set(actual) != set(expected):
                mismatched.append(field)
        elif record[field] != expected:
            mismatched.append(field)
    state = ('persisted_but_mismatched' if mismatched else
             'verification_unavailable' if unavailable else 'verified')
    return result(state, outcome, record_id, mismatched=mismatched,
                  unavailable=unavailable, duplicate=duplicate)


def verified_write(tool, arguments, call: Callable):
    """Write at most once and verify the exact record, including duplicate returns.

    Exit zero means the supported caller-supplied fields were observed matching.
    Exit one does NOT imply no write. Inspect write_outcome and the retained ID.
    """
    allowed = STORE_FIELDS if tool == 'memory_store' else UPDATE_FIELDS
    if tool not in {'memory_store', 'memory_update'} or not isinstance(arguments, dict):
        return result('verification_unavailable', 'not_attempted', reason='invalid_request')
    if set(arguments) - allowed:
        return result('verification_unavailable', 'not_attempted', reason='unsupported_fields')
    if ('tags' in arguments and (not isinstance(arguments['tags'], list) or
            not all(isinstance(tag, str) for tag in arguments['tags']))):
        return result('verification_unavailable', 'not_attempted', reason='invalid_tags')
    if tool == 'memory_store':
        content = arguments.get('content')
        if not isinstance(content, str) or not content.strip() or not arguments.get('category'):
            return result('verification_unavailable', 'not_attempted', reason='missing_store_fields')
        search_args = {'query': content.strip()[:500], 'limit': 20}
        # Preserve existing preflight breadth; narrowing by requested tags could
        # miss a record whose tags were rewritten. No retrieval algorithm change.
        if arguments.get('project'):
            search_args['project'] = arguments['project']
        records, error = invoke(call, 'memory_search', search_args)
        if error or not isinstance(records, list):
            return result('verification_unavailable', 'not_attempted', reason='duplicate_preflight_failed')
        for record in records:
            if isinstance(record, dict) and canonical(record.get('content')) == canonical(content):
                record_id = safe_id(record.get('id'))
                if not record_id:
                    return result('verification_unavailable', 'existing_record', reason='missing_id', duplicate=True)
                return verify(arguments, record_id, call, 'existing_record', duplicate=True)
    elif not safe_id(arguments.get('id')) or not set(arguments) - {'id'}:
        return result('verification_unavailable', 'not_attempted', reason='invalid_id')

    written, error = invoke(call, tool, arguments)
    if error:
        return result('verification_unavailable',
                      'rejected' if error in {'access_denied', 'tool_rejected'} else 'unknown',
                      safe_id(arguments.get('id')), reason=error)
    if not isinstance(written, dict):
        return result('verification_unavailable', 'unknown', safe_id(arguments.get('id')), reason='malformed_response')
    record_id = safe_id(written.get('id'))
    if not record_id:
        return result('verification_unavailable', 'accepted', safe_id(arguments.get('id')), reason='missing_returned_id')
    if tool == 'memory_update' and record_id != arguments['id']:
        return result('verification_unavailable', 'accepted', record_id, reason='update_id_mismatch')
    # Current server signals its duplicate short circuit in message/warning.
    # Never echo either field: they may include provider/private text.
    duplicate = tool == 'memory_store' and (
        str(written.get('message', '')).startswith('Duplicate detected') or
        str(written.get('warning', '')).startswith('LLM identified this as a duplicate'))
    answer, code = verify(arguments, record_id, call,
                          'existing_record' if duplicate else 'accepted', duplicate=duplicate)
    if duplicate:
        # The server's semantic duplicate decision is not our exact preflight.
        answer['status'] = 'server_duplicate'
    # Preserve non-sensitive established result fields for existing callers.
    for field in ('embedded', 'processed', 're_embedded'):
        if isinstance(written.get(field), bool):
            answer[field] = written[field]
    if isinstance(written.get('fields_updated'), list):
        answer['fields_updated'] = [f for f in written['fields_updated'] if isinstance(f, str) and f in UPDATE_FIELDS]
    return answer, code


def write_cli(tool, arguments, initialize, tool_call):
    """Shared CLI adapter: use existing credentials/transport, sanitize all errors."""
    try:
        session, error = initialize('codex-koda-verified-write')
    except Exception:
        session, error = {}, True
    if error:
        answer, code = result('verification_unavailable', 'not_attempted', reason='initialize_failed')
    else:
        request_id = 1
        def call(name, args):
            nonlocal request_id
            request_id += 1
            return tool_call(session, name, args, request_id=request_id)
        answer, code = verified_write(tool, arguments, call)
    print(json.dumps(answer, sort_keys=True))
    return code
