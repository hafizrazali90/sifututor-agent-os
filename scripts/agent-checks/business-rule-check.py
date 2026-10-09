#!/usr/bin/env python3
"""Check business-rule source wiring and declared shared-class acceptance plans.

This is deterministic document/plan validation, not application or LLM testing.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
INTENT_SOURCE = "docs/business-rules/README.md#shared-class-contract-br-001"


def identifiers(value: object, label: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{label} must be a nonempty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{label} must contain nonempty strings")
    if len(set(value)) != len(value):
        raise ValueError(f"{label} must be unique")
    return value


def validate_proposal(packet: object) -> None:
    """Validate declared outcomes for BR-001; no code/schema inference allowed."""
    if not isinstance(packet, dict):
        raise ValueError("proposal must be an object")
    required = {"rule_id", "intent_source", "implementation_observation", "requests"}
    if set(packet) != required:
        raise ValueError("proposal must contain exactly the documented fields")
    if packet["rule_id"] != "BR-001" or packet["intent_source"] != INTENT_SOURCE:
        raise ValueError("cite the confirmed BR-001 intent source, not code or memory alone")
    observation = packet["implementation_observation"]
    if not isinstance(observation, str) or not observation.strip():
        raise ValueError("record implementation evidence separately, or explicitly say not inspected")
    requests = packet["requests"]
    if not isinstance(requests, list) or not requests:
        raise ValueError("requests must be a nonempty list")
    seen = set()
    for request in requests:
        if not isinstance(request, dict) or set(request) != {
            "request", "students", "scheduled_lessons", "expected_sessions"
        }:
            raise ValueError("invalid request example fields")
        identity = request["request"]
        if not isinstance(identity, str) or not identity.strip() or identity in seen:
            raise ValueError("request examples need distinct nonempty identities")
        seen.add(identity)
        students = identifiers(request["students"], "students")
        lessons = identifiers(request["scheduled_lessons"], "scheduled_lessons")
        sessions = request["expected_sessions"]
        if not isinstance(sessions, list) or len(sessions) != len(lessons):
            raise ValueError("BR-001: one session per scheduled lesson, not per student")
        covered = set()
        for session in sessions:
            if not isinstance(session, dict) or set(session) != {"lesson", "participants"}:
                raise ValueError("invalid expected session fields")
            lesson = session["lesson"]
            if not isinstance(lesson, str) or lesson not in lessons or lesson in covered:
                raise ValueError("BR-001: every scheduled lesson must appear exactly once")
            covered.add(lesson)
            participants = identifiers(session["participants"], "participants")
            if set(participants) != set(students):
                raise ValueError("BR-001: retain all selected participants in the shared session")


def validate_repository(root: Path) -> None:
    base = root / "docs/business-rules"
    register = (base / "register.md").read_text()
    ids = re.findall(r"^## (BR-\d{3})$", register, re.M)
    expected = [f"BR-{n:03d}" for n in range(1, 106)]
    if sorted(ids) != expected:
        raise ValueError("register must retain 105 unique, consecutive rule IDs")
    source_data = json.loads((base / "sources.json").read_text())
    sources = source_data["sources"]
    if len(sources) != 149 or len({s["path"] for s in sources}) != 149:
        raise ValueError("source inventory must retain 149 distinct candidate locators")
    for source in sources:
        if not re.fullmatch(r"[0-9a-f]{64}", source["sha256"]):
            raise ValueError("source locator needs a content hash")
        if not source.get("depth") or not source.get("authority"):
            raise ValueError("source reading depth and authority must be explicit")
    reasons = (base / "decision-reasons.md").read_text()
    if sorted(re.findall(r"^## (BR-\d{3})$", reasons, re.M)) != expected:
        raise ValueError("recorded reasons must cover the same 105 rule IDs")
    for name in ("README.md", "register.md", "open-decisions.md", "memory-audit.md", "decision-reasons.md", "reconciliation.md", "review.md"):
        text = (base / name).read_text()
        for target in re.findall(r"\]\(([^)]+)\)", text):
            if target.startswith(("https://", "http://", "#")):
                continue
            if not (base / target.split("#", 1)[0]).is_file():
                raise ValueError(f"broken business-rule link in {name}")
    readme = (base / "README.md").read_text()
    for phrase in ("one shared class session", "not one class per student", "not a live model-compliance guarantee"):
        if phrase not in readme:
            raise ValueError(f"missing business contract: {phrase}")
    if "docs/business-rules/README.md" not in (root / "AGENTS.md").read_text():
        raise ValueError("shared entry point lost business-rule loading")
    if not re.search(r"^@AGENTS\.md\s*$", (root / "CLAUDE.md").read_text(), re.M):
        raise ValueError("Claude adapter must import the shared contract")
    if "../business-rules/README.md" not in (root / "docs/agent-playbooks/context-authority.md").read_text():
        raise ValueError("authority owner lost the business-rule route")
    validate_proposal(json.loads((base / "shared-class-plan.example.json").read_text()))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proposal", type=Path, help="validate a BR-001 declared acceptance example")
    args = parser.parse_args()
    try:
        if args.proposal:
            validate_proposal(json.loads(args.proposal.read_text()))
            print("PASS BR-001 declared example; application behaviour not tested")
        else:
            validate_repository(ROOT)
            print("PASS business-rule inventory, authority links and shared-class example")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(f"FAIL business-rule check: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
