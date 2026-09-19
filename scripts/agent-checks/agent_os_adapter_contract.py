"""Validate supervisor-supplied capability attestations, never launch a worker.

Evidence references are not authenticated here. A pass is eligibility for the
requested capabilities, not execution authority or independent parity proof.
"""
from datetime import datetime, timezone
import re

IDENTITY_KEYS = {"tool", "tool_version", "provider", "model", "configuration_id", "environment_id"}
RECORD_KEYS = {"schema_version", "identity", "observed_at", "expires_at", "capabilities"}
CAPABILITY_KEYS = {"status", "evidence_kind", "evidence_ref"}
SLUG = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")

def _text(value):
    return isinstance(value, str) and 0 < len(value) <= 256 and value == value.strip() and not any(ord(c) < 32 for c in value)

def _identity(value):
    return isinstance(value, dict) and set(value) == IDENTITY_KEYS and all(_text(v) for v in value.values())

def _time(value):
    if not isinstance(value, str) or len(value) > 40:
        raise ValueError("invalid_timestamp")
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None or result.utcoffset().total_seconds() != 0:
        raise ValueError("timestamp_requires_utc")
    return result

def evaluate_capabilities(record, required, *, expected_identity, now=None):
    """Fail closed on stale/mismatched/unproven records; return metadata only.

    Callers must obtain expected_identity from the actual selected setup and
    trust/review the observation independently. environment_id must identify
    the host/worktree/environment scope, not a provider-wide default.
    """
    def result(*reasons):
        return {"ready": not reasons, "reasons": list(reasons), "live_parity_proven": False, "execution_authorized": False, "evidence_basis": "supervisor_attestation"}

    if not isinstance(required, list) or not required or len(required) > 64 or any(not isinstance(c, str) or not SLUG.fullmatch(c) for c in required) or len(set(required)) != len(required):
        return result("invalid_requirements")
    if not _identity(expected_identity):
        return result("invalid_expected_identity")
    if not isinstance(record, dict) or set(record) != RECORD_KEYS or type(record["schema_version"]) is not int or record["schema_version"] != 1 or not _identity(record["identity"]):
        return result("invalid_record")
    capabilities = record["capabilities"]
    if not isinstance(capabilities, dict) or len(capabilities) > 64:
        return result("invalid_capabilities")
    for name, capability in capabilities.items():
        if not isinstance(name, str) or not SLUG.fullmatch(name) or not isinstance(capability, dict) or set(capability) != CAPABILITY_KEYS:
            return result("invalid_capabilities")
        if capability["status"] not in ("supported", "unsupported", "unknown") or capability["evidence_kind"] not in ("live", "fixture", "declared") or not _text(capability["evidence_ref"]):
            return result("invalid_capabilities")
    if record["identity"] != expected_identity:
        return result("identity_mismatch")
    try:
        observed, expires = _time(record["observed_at"]), _time(record["expires_at"])
        current = now if now is not None else datetime.now(timezone.utc)
        if not isinstance(current, datetime) or current.tzinfo is None:
            return result("invalid_clock")
        if not observed <= current < expires:
            return result("observation_not_current")
    except (ValueError, TypeError, OverflowError):
        return result("invalid_timestamp")
    reasons = []
    for capability in required:
        observation = capabilities.get(capability)
        if observation is None:
            reasons.append("capability_missing:" + capability)
        elif observation["status"] != "supported":
            reasons.append("capability_unavailable:" + capability)
        elif observation["evidence_kind"] != "live":
            reasons.append("capability_unproven:" + capability)
    return result(*reasons)
