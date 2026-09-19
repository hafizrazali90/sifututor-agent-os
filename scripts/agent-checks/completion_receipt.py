"""Validate v1 completion receipt structure. Does NOT verify claims or authority.

Import validate_receipt(receipt) -> list[str]. CLI accepts sanitized JSON on
stdin only, emits fixed diagnostics, and never reads evidence references.
Consumers must compare task/contract/target to their own trusted task context
and independently inspect the evidence before accepting work.
"""
import json
import re
import sys

PROOF_DIMENSIONS = (
    "entrypoint", "production_caller", "authoritative_result", "bypass_paths",
    "permissions_configuration", "disabled_unavailable", "failure_retry",
    "negative_control", "journey", "regression",
)
STATES = (
    "changed_locally", "committed_locally", "pushed", "pr_open", "merged",
    "staging_deployed", "production_deployed", "live_checked", "monitored",
)


def validate_receipt(receipt):
    """Return fixed-path shape errors; [] means well-formed, NOT accepted."""
    errors = []

    def obj(value, path):
        if not isinstance(value, dict):
            errors.append(path + ":object_required")
            return {}
        return value

    def text(value, path):
        if not isinstance(value, str) or not value.strip():
            errors.append(path + ":nonempty_text_required")

    def fields(value, allowed, path):
        if set(value) - set(allowed):
            errors.append(path + ":unexpected_fields")

    def choice(value, allowed, path):
        if not isinstance(value, str) or value not in allowed:
            errors.append(path + ":invalid_choice")

    def refs(value, path, required):
        if not isinstance(value, list) or any(not isinstance(v, str) or not v.strip() for v in value):
            errors.append(path + ":reference_list_required")
        elif required and not value:
            errors.append(path + ":evidence_required")

    root = obj(receipt, "receipt")
    fields(root, ("schema_version", "task_id", "contract_sha256", "target", "worker", "acceptance", "review"), "receipt")
    if type(root.get("schema_version")) is not int or root.get("schema_version") != 1:
        errors.append("schema_version:unsupported")
    text(root.get("task_id"), "task_id")
    digest = root.get("contract_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        errors.append("contract_sha256:sha256_required")
    target = obj(root.get("target"), "target")
    fields(target, ("revision", "environment", "state"), "target")
    for field in ("revision", "environment"):
        text(target.get(field), "target." + field)
    choice(target.get("state"), STATES, "target.state")
    worker = obj(root.get("worker"), "worker")
    fields(worker, ("id", "outcome"), "worker")
    text(worker.get("id"), "worker.id")
    choice(worker.get("outcome"), ("implemented", "incomplete", "failed"), "worker.outcome")
    review = obj(root.get("review"), "review")
    fields(review, ("reviewer_id", "verdict", "references", "reason"), "review")
    choice(review.get("verdict"), ("accepted", "returned", "pending"), "review.verdict")
    accepted = review.get("verdict") == "accepted"
    if review.get("verdict") != "pending":
        text(review.get("reviewer_id"), "review.reviewer_id")
        if worker.get("id") == review.get("reviewer_id"):
            errors.append("review.reviewer_id:distinct_reviewer_required")
    elif not isinstance(review.get("reviewer_id"), str):
        errors.append("review.reviewer_id:text_required")
    text(review.get("reason"), "review.reason")
    refs(review.get("references"), "review.references", review.get("verdict") != "pending")
    if accepted and worker.get("outcome") != "implemented":
        errors.append("worker.outcome:accepted_requires_implemented")
    items = root.get("acceptance")
    if not isinstance(items, list) or not items:
        errors.append("acceptance:nonempty_list_required")
        return errors
    seen = set()
    for index, item in enumerate(items):
        path = f"acceptance[{index}]"
        item = obj(item, path)
        fields(item, ("id", "requirement", "proof"), path)
        key = item.get("id")
        text(key, path + ".id")
        if isinstance(key, str):
            if key in seen:
                errors.append(path + ".id:duplicate")
            seen.add(key)
        text(item.get("requirement"), path + ".requirement")
        proof = obj(item.get("proof"), path + ".proof")
        fields(proof, PROOF_DIMENSIONS, path + ".proof")
        for dimension in PROOF_DIMENSIONS:
            field = path + ".proof." + dimension
            record = obj(proof.get(dimension), field)
            fields(record, ("status", "references", "reason"), field)
            status = record.get("status")
            choice(status, ("recorded", "not_applicable", "missing"), field + ".status")
            refs(record.get("references"), field + ".references", status == "recorded")
            text(record.get("reason"), field + ".reason")
            if accepted and status == "missing":
                errors.append(field + ":accepted_with_missing_proof")
    return errors


def main():
    def unique_fields(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate")
            result[key] = value
        return result

    try:
        raw = sys.stdin.buffer.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError("oversized")
        value = json.loads(raw, object_pairs_hook=unique_fields)
        errors = validate_receipt(value)
    except (ValueError, RecursionError):
        print(json.dumps({"structure_valid": False, "semantic_acceptance_proven": False, "errors": ["receipt:invalid_json"]}))
        return 2
    print(json.dumps({"structure_valid": not errors, "semantic_acceptance_proven": False, "errors": errors}))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
