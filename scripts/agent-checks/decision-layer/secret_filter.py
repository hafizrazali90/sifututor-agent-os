#!/usr/bin/env python3
"""Deterministic (non-model) pre-dispatch content filter (build item 8).

Inspects request content for anything shaped like a live secret, access
token, private key, or personal data, and reports it so the engine can
block dispatch before any provider -- including the fake one -- ever sees
the content. Nothing here is a model call; it is regex pattern matching
only, so it is fast, offline, and fully deterministic.

Credential-shaped detection reuses the same rule set as the repo's staged-
diff guard (`secret_artifact_scan.py`) instead of maintaining a second,
possibly-diverging copy of the same regexes. PII-shaped detection (email,
Malaysian IC number, phone number, card number) is specific to this
module, since the staged-diff guard does not need it.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import re
import sys

_HERE = Path(__file__).resolve().parent
_SECRET_ARTIFACT_SCAN_PATH = _HERE.parent / "secret_artifact_scan.py"


def _load_secret_artifact_scan():
    spec = importlib.util.spec_from_file_location(
        "decision_layer_secret_artifact_scan", _SECRET_ARTIFACT_SCAN_PATH
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load the shared secret-artifact scanner")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


_secret_artifact_scan = _load_secret_artifact_scan()

_PII_RULES: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("email address", re.compile(r"\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b")),
    ("Malaysian IC number", re.compile(r"\b\d{6}-\d{2}-\d{4}\b")),
    ("Malaysian mobile number", re.compile(r"\b01[0-46-9]-?\d{7,8}\b")),
    ("card-like number sequence", re.compile(r"\b(?:\d[ -]?){13,19}\b")),
)


def scan(text: str | None) -> list[str]:
    """Return a list of finding labels for one piece of free text."""
    if not text:
        return []

    findings: list[str] = [
        f"credential:{finding.rule}"
        for finding in _secret_artifact_scan.find_secret_findings(text)
    ]
    for label, pattern in _PII_RULES:
        if pattern.search(text):
            findings.append(f"pii:{label}")
    return findings


def scan_request(request: dict) -> list[str]:
    """Scan every free-text-bearing field of a decision request."""
    parts = [str(request.get("context") or "")]
    for option in request.get("options") or []:
        parts.append(str(option))
    return scan("\n".join(parts))
