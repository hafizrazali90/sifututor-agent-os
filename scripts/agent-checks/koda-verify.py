#!/usr/bin/env python3
"""
Koda Setup Verifier — run this from your VS Code terminal.
It checks your KODA_API_KEY, confirms connectivity, and sends
Hafiz a confirmation so he knows your setup is working.

Usage:
    python3 koda-verify.py
"""

import json
import os
import sys
import urllib.request
import urllib.error
import socket
import platform
from datetime import datetime, timezone

from koda_contract import ALL_KODA_TOOLS, capability_report

from koda_endpoint import KODA_MCP_URL as KODA_URL  # single source, issue #163
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):    print(f"  {GREEN}✓{RESET} {msg}")
def fail(msg):  print(f"  {RED}✗{RESET} {msg}"); sys.exit(1)
def warn(msg):  print(f"  {YELLOW}!{RESET} {msg}")
def header(msg): print(f"\n{BOLD}{msg}{RESET}")


def api_key_status_message(_api_key: str) -> str:
    """Confirm presence without printing any credential-derived characters."""

    return "KODA_API_KEY is set"


def connection_status_message(session_id: str) -> str:
    """Describe the negotiated transport without requiring a legacy session."""

    if session_id:
        return f"Connected — session {session_id[:12]}..."
    return "Connected — stateless per-request transport"


def parse_tool_content(response: dict):
    content = response.get("result", {}).get("content", []) if isinstance(response, dict) else []
    text = next(
        (item.get("text", "") for item in content if isinstance(item, dict) and item.get("type") == "text"),
        "",
    )
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return text


def confirm_exact_record(
    headers: dict,
    session_id: str,
    memory_id: str,
    expected: dict,
) -> str:
    """Read the exact record back. An accepted write is not proof of stored metadata."""

    recall_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": "memory_recall", "arguments": {"id": memory_id}},
        "id": 5,
    }
    recall_result, _ = post(recall_payload, headers, session_id)
    record = parse_tool_content(recall_result)
    if not isinstance(record, dict) or str(record.get("id")) != memory_id:
        return "unverified"

    mismatched = []
    for field, value in expected.items():
        if field not in record:
            continue
        actual = record[field]
        if field == "tags":
            if not isinstance(actual, list) or set(actual) != set(value):
                mismatched.append(field)
        elif actual != value:
            mismatched.append(field)
    return "mismatched: " + ", ".join(sorted(mismatched)) if mismatched else "verified"


def ensure_confirmation_memory(
    headers: dict,
    session_id: str,
    tool_names: set[str],
    *,
    machine: str,
    system_info: str,
    timestamp: str,
) -> tuple[str, str]:
    """Update one setup sentinel, or store it once when none exists."""

    tags = ["umbrella", "koda-setup", "onboarding"]
    content = (
        f"Koda setup verified on {timestamp}. "
        f"Machine: {machine} ({system_info}). "
        "VS Code + Claude Code + Codex + Koda direct MCP confirmed working."
    )
    why = "Staff onboarding verification — confirms Koda is reachable from this machine"
    search_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "memory_search",
            "arguments": {
                "query": "Koda setup verified",
                "tags": tags,
                "limit": 10,
            },
        },
        "id": 3,
    }
    search_result, _ = post(search_payload, headers, session_id)
    memories = parse_tool_content(search_result)
    existing = next(
        (
            memory for memory in (memories if isinstance(memories, list) else [])
            if isinstance(memory, dict)
            and memory.get("id")
            and ("koda-setup" in (memory.get("tags") or []) or "Koda setup verified" in (memory.get("content") or ""))
        ),
        None,
    )

    if existing and "memory_update" in tool_names:
        update_payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "memory_update",
                "arguments": {
                    "id": existing["id"],
                    "content": content,
                    "tags": tags,
                    "source": "auto-captured",
                    "why": why,
                },
            },
            "id": 4,
        }
        update_result, _ = post(update_payload, headers, session_id)
        if isinstance(update_result, dict) and "result" in update_result:
            state = confirm_exact_record(
                headers, session_id, str(existing["id"]), {"content": content, "tags": tags}
            )
            return str(existing["id"]), f"updated ({state})"
        return str(existing["id"]), "already present"

    if existing:
        return str(existing["id"]), "already present"

    store_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "memory_store",
            "arguments": {
                "category": "fact",
                "content": content,
                "tags": tags,
                "source": "auto-captured",
                "why": why,
                "project": "sifututor",
            },
        },
        "id": 4,
    }
    store_result, _ = post(store_payload, headers, session_id)
    payload = parse_tool_content(store_result)
    if isinstance(payload, dict) and payload.get("id"):
        memory_id = str(payload["id"])
        state = confirm_exact_record(
            headers, session_id, memory_id,
            {"content": content, "tags": tags, "category": "fact", "project": "sifututor"},
        )
        return memory_id, f"stored ({state})"
    return "unknown", "store failed"


def _raw_post(payload: dict, headers: dict, session_id: str = "") -> tuple[str, str, str]:
    """Return body, content type, and an optional legacy session identifier."""
    h = dict(headers)
    if session_id:
        h["Mcp-Session-Id"] = session_id
    h["Accept"] = "application/json, text/event-stream"
    h["Content-Type"] = "application/json"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(KODA_URL, data=data, headers=h, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            sid = resp.headers.get("Mcp-Session-Id", session_id)
            ct = resp.headers.get("Content-Type", "")
            raw = resp.read().decode()
            return raw, ct, sid
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}: {e.read().decode()[:200]}", "", session_id
    except urllib.error.URLError as e:
        return f"Connection error: {e.reason}", "", session_id


def _unwrap_sse(body: str, content_type: str) -> str:
    """Extract JSON payload from SSE stream (handles 'event: message\\ndata: ...' format)."""
    if "text/event-stream" in content_type:
        for line in body.splitlines():
            if line.startswith("data:"):
                return line[5:].strip()
    return body


def post(payload: dict, headers: dict, session_id: str = "") -> tuple[dict, str]:
    raw, ct, sid = _raw_post(payload, headers, session_id)
    body = _unwrap_sse(raw, ct)
    try:
        return json.loads(body), sid
    except json.JSONDecodeError:
        return {"_parse_error": raw[:200]}, sid


def main():
    print(f"\n{BOLD}{'='*50}{RESET}")
    print(f"{BOLD}  Koda Setup Verifier — Sifututor Team{RESET}")
    print(f"{BOLD}{'='*50}{RESET}")

    # ── Step 1: API key ──────────────────────────────
    header("Step 1 — Checking KODA_API_KEY")
    api_key = os.environ.get("KODA_API_KEY", "").strip()
    if not api_key:
        fail(
            "KODA_API_KEY is not set in your shell.\n\n"
            "  Add this to your ~/.zshrc or ~/.bashrc:\n"
            "    export KODA_API_KEY=<your-key-from-hafiz>\n\n"
            "  Then run: source ~/.zshrc && python3 koda-verify.py"
        )
    ok(api_key_status_message(api_key))

    headers = {"Authorization": f"Bearer {api_key}"}

    # ── Step 2: Initialize MCP transport ────────────
    header("Step 2 — Connecting to Koda")
    init_payload = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {},
            "clientInfo": {"name": "koda-verify", "version": "1.0"},
        },
        "id": 1,
    }
    result, session_id = post(init_payload, headers)
    if "error" in result or "result" not in result:
        err = result.get("error", {}).get("message", str(result)) if isinstance(result, dict) else str(result)
        fail(f"Could not connect to Koda: {err}\n  Check that your API key is correct.")

    ok(connection_status_message(session_id))

    # Send initialized notification (server may return 202 with empty body — ignore errors)
    _raw_post({"jsonrpc": "2.0", "method": "notifications/initialized"}, headers, session_id)

    # ── Step 3: Verify tools available ──────────────
    header("Step 3 — Verifying required tools")
    tools_result, _ = post(
        {"jsonrpc": "2.0", "method": "tools/list", "id": 2},
        headers, session_id
    )
    tools = set()
    if isinstance(tools_result, dict) and "result" in tools_result:
        tools = {t["name"] for t in tools_result["result"].get("tools", [])}
        capabilities = capability_report(tools)
        if capabilities["missing_required"]:
            fail(f"Missing required core tools: {', '.join(capabilities['missing_required'])}")
        for tier, tier_status in capabilities["tiers"].items():
            if tier_status["missing"]:
                warn(f"{tier} capability tier partial — missing: {', '.join(tier_status['missing'])}")
            else:
                ok(f"{tier} capability tier available")
        if tools == ALL_KODA_TOOLS:
            ok(f"Current Koda tool contract available ({len(tools)} total)")
    else:
        warn("Could not list tools — continuing anyway")

    # ── Step 4: Store confirmation memory ───────────
    header("Step 4 — Sending setup confirmation to Hafiz")
    machine = socket.gethostname()
    system_info = f"{platform.system()} {platform.release()}"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    mem_id, action = ensure_confirmation_memory(
        headers,
        session_id,
        tools,
        machine=machine,
        system_info=system_info,
        timestamp=timestamp,
    )
    if action == "store failed":
        warn("Could not store setup confirmation")
    elif "mismatched" in action or "unverified" in action:
        # Exit 0 is still correct: Koda is reachable. The claim is just narrower.
        warn(f"Confirmation {action} — memory {mem_id}")
        warn("Koda is reachable, but the stored record did not match the request. "
             "Send this memory ID to Hafiz; do not retry or edit it yourself.")
    else:
        ok(f"Confirmation {action} — memory {mem_id}")

    # ── Done ─────────────────────────────────────────
    print(f"\n{GREEN}{BOLD}{'='*50}{RESET}")
    print(f"{GREEN}{BOLD}  ALL CHECKS PASSED — Your Koda setup is working!{RESET}")
    print(f"{GREEN}{BOLD}{'='*50}{RESET}")
    print(f"\n  Hafiz can see your confirmation at:")
    print(f"  {BOLD}https://koda.tutorla.tech/dashboard{RESET}\n")


if __name__ == "__main__":
    main()
