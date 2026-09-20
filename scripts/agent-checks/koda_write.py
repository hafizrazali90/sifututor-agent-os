"""Verified writes over the existing Koda transport, without repair or retries.

The callback accepts (tool_name, arguments) and returns (MCP response, error).
Only metadata crosses the result boundary; provider diagnostics are never echoed.
"""
from __future__ import annotations

import json
import re
import sys
from collections.abc import Callable

STORE_FIELDS = frozenset({'content', 'category', 'why', 'tags', 'source', 'project', 'scope'})
UPDATE_FIELDS = frozenset({'id', 'content', 'why', 'tags', 'source', 'confidence'})
# Fields the inspected server accepts on store but not on update. A client
# cannot correct these; only the memory owner or a Koda admin can.
OWNER_ONLY_FIELDS = STORE_FIELDS - UPDATE_FIELDS
CORRECTION_COMMAND = 'scripts/agent-checks/koda update'
CORRECTION_ACTOR = 'memory owner or Koda admin'
OWNERSHIP_BLOCK = 'project_scope_ownership'
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


DENIAL_MARKERS = ('not owned', 'access denied', 'forbidden', 'unauthorized', 'permission denied')


def denies_ownership(*values):
    """Classify an ownership refusal. Inspects text; never returns or prints it."""

    for value in values:
        if isinstance(value, str):
            if any(marker in value.lower() for marker in DENIAL_MARKERS):
                return True
        elif isinstance(value, list):
            if denies_ownership(*value):
                return True
        elif isinstance(value, dict):
            if denies_ownership(*value.values()):
                return True
    return False


def invoke(call, name, arguments):
    try:
        response, error = call(name, arguments)
    except Exception:
        return None, 'transport_unavailable'
    if error:
        # Inspect only to classify; never return the provider's text.
        if denies_ownership(error):
            return None, 'access_denied'
        return None, 'transport_unavailable'
    if isinstance(response, dict) and (response.get('error') or
            isinstance(response.get('result'), dict) and response['result'].get('isError')):
        # The server also refuses project-scope edits inside the tool result itself.
        return None, 'access_denied' if denies_ownership(response) else 'tool_rejected'
    value = payload(response)
    return value, '' if value is not None else 'malformed_response'


def correction_plan(mismatched=(), *, blocked=False):
    """Name the safe operator path. Field names only; never values, never a repair."""

    fields = sorted(mismatched)
    plan = {'automatic_repair': 'never',
            'correctable_by_update': [f for f in fields if f in UPDATE_FIELDS - {'id'}],
            'owner_action_required': [f for f in fields if f in OWNER_ONLY_FIELDS]}
    if plan['correctable_by_update'] and not blocked:
        plan['command'] = CORRECTION_COMMAND
    if blocked:
        plan['blocked_by'] = OWNERSHIP_BLOCK
    if plan['owner_action_required'] or blocked:
        plan['actor'] = CORRECTION_ACTOR
        plan['action'] = ('Ask the owning creator or a Koda admin to correct the named fields '
                          'by exact ID; this client cannot change them.')
    return plan


def result(state, outcome, record_id=None, *, reason=None, mismatched=(), unavailable=(),
           duplicate=False, tag_delta=None, correction=None):
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
    if tag_delta:
        value['verification']['tag_delta'] = tag_delta
    if unavailable:
        value['verification']['unavailable_fields'] = sorted(unavailable)
    if correction:
        value['correction'] = correction
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
    mismatched, unavailable, tag_delta = [], [], None
    for field, expected in arguments.items():
        if field == 'id':
            continue
        if field not in record:
            unavailable.append(field)
        elif field == 'tags':
            actual = record[field]
            if not isinstance(actual, list) or not all(isinstance(t, str) for t in actual):
                mismatched.append(field)
            elif set(actual) != set(expected):
                mismatched.append(field)
                # Counts only: a dropped requested tag and an added server tag
                # need different correction decisions, but neither value is safe to echo.
                tag_delta = {'missing': len(set(expected) - set(actual)),
                             'unexpected': len(set(actual) - set(expected))}
        elif record[field] != expected:
            mismatched.append(field)
    state = ('persisted_but_mismatched' if mismatched else
             'verification_unavailable' if unavailable else 'verified')
    return result(state, outcome, record_id, mismatched=mismatched,
                  unavailable=unavailable, duplicate=duplicate, tag_delta=tag_delta,
                  correction=correction_plan(mismatched) if mismatched else None)


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
                      safe_id(arguments.get('id')), reason=error,
                      correction=correction_plan(blocked=True) if error == 'access_denied' else None)
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


VERIFICATION_STATES = ('verified', 'persisted_but_mismatched', 'verification_unavailable')


def correction_report(value):
    """Explain a verification result offline. Reads only known keys, echoes no free text."""

    verification = value.get('verification') if isinstance(value, dict) else None
    if not isinstance(verification, dict) or verification.get('state') not in VERIFICATION_STATES:
        return ['correction: unreadable verification result'], 2
    state = verification['state']
    supplied = value.get('id') or value.get('existing_id')
    record_id = safe_id(value.get('id')) or safe_id(value.get('existing_id'))
    if supplied and not record_id:
        # An unsafe identifier means this is not a trustworthy sanitized result.
        return ['correction: unreadable verification result'], 2
    lines = [f'state: {state}']
    if record_id:
        lines.append(f'id: {record_id}')
    if state == 'verified':
        lines.append('action: none; the supplied supported fields matched at readback time')
        return lines, 0

    known = STORE_FIELDS | UPDATE_FIELDS
    mismatched = [f for f in verification.get('mismatched_fields') or [] if f in known]
    unavailable = [f for f in verification.get('unavailable_fields') or [] if f in known]
    plan = value.get('correction') if isinstance(value.get('correction'), dict) else {}
    correctable = [f for f in plan.get('correctable_by_update') or [] if f in known]
    owner_only = [f for f in plan.get('owner_action_required') or [] if f in known]

    if mismatched:
        lines.append('mismatched fields: ' + ', '.join(mismatched))
    if unavailable:
        lines.append('unverifiable fields: ' + ', '.join(unavailable))
    if plan.get('blocked_by') == OWNERSHIP_BLOCK:
        lines.append(f'blocked by: {OWNERSHIP_BLOCK}')
    lines.append('automatic repair: never; no retry, retag, or overwrite is performed')
    if correctable:
        lines.append('correct with: ' + CORRECTION_COMMAND
                     + ' (resend the same requested values for: ' + ', '.join(correctable) + ')')
    if owner_only or plan.get('blocked_by'):
        lines.append(f'owner action: ask the {CORRECTION_ACTOR} to correct by exact ID'
                     + (' (' + ', '.join(owner_only) + ')' if owner_only else ''))
    if not correctable and not owner_only and not plan.get('blocked_by'):
        lines.append('next: re-check by exact ID when Koda is reachable; do not rewrite blindly')
    return lines, 1


def correction_cli(raw):
    """Offline operator entry point: no transport, no credentials, no writes."""

    try:
        value = json.loads(raw)
    except (ValueError, TypeError):
        value = None
    lines, code = correction_report(value)
    for line in lines:
        print(line)
    return code


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


def main(argv):
    """Offline correction explainer. The write paths keep their own entry points."""

    if len(argv) == 2 and argv[0] == '--correction-json':
        return correction_cli(sys.stdin.read() if argv[1] == '-' else argv[1])
    print("Usage: koda_write.py --correction-json '<verification-result-json>'|-", file=sys.stderr)
    return 2


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
