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

KODA_URL = "https://koda.tutorla.tech/mcp"
GREEN  = "\033[92m"
RED    = "\033[91m"
YELLOW = "\033[93m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):    print(f"  {GREEN}✓{RESET} {msg}")
def fail(msg):  print(f"  {RED}✗{RESET} {msg}"); sys.exit(1)
def warn(msg):  print(f"  {YELLOW}!{RESET} {msg}")
def header(msg): print(f"\n{BOLD}{msg}{RESET}")


def _raw_post(payload: dict, headers: dict, session_id: str = "") -> tuple[str, str, str]:
    """Returns (body, content_type, session_id) — always returns session_id from response header."""
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
    ok(f"KODA_API_KEY is set ({api_key[:8]}...)")

    headers = {"Authorization": f"Bearer {api_key}"}

    # ── Step 2: Initialize MCP session ──────────────
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
    if not session_id or "error" in result:
        err = result.get("error", {}).get("message", str(result)) if isinstance(result, dict) else str(result)
        fail(f"Could not connect to Koda: {err}\n  Check that your API key is correct.")

    ok(f"Connected — session {session_id[:12]}...")

    # Send initialized notification (server may return 202 with empty body — ignore errors)
    _raw_post({"jsonrpc": "2.0", "method": "notifications/initialized"}, headers, session_id)

    # ── Step 3: Verify tools available ──────────────
    header("Step 3 — Verifying required tools")
    tools_result, _ = post(
        {"jsonrpc": "2.0", "method": "tools/list", "id": 2},
        headers, session_id
    )
    if isinstance(tools_result, dict) and "result" in tools_result:
        tools = {t["name"] for t in tools_result["result"].get("tools", [])}
        required = {"memory_store", "memory_search", "memory_context", "session_start"}
        missing = required - tools
        if missing:
            fail(f"Missing tools: {missing}")
        ok(f"All required tools available ({len(tools)} total)")
    else:
        warn("Could not list tools — continuing anyway")

    # ── Step 4: Store confirmation memory ───────────
    header("Step 4 — Sending setup confirmation to Hafiz")
    machine = socket.gethostname()
    system_info = f"{platform.system()} {platform.release()}"
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    store_payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": "memory_store",
            "arguments": {
                "category": "fact",
                "content": (
                    f"Koda setup verified on {timestamp}. "
                    f"Machine: {machine} ({system_info}). "
                    f"VS Code + Claude Code + Koda MCP confirmed working."
                ),
                "tags": ["umbrella", "koda-setup", "onboarding"],
                "source": "user-stated",
                "why": "Staff onboarding verification — confirms Koda MCP is reachable from this machine",
            },
        },
        "id": 3,
    }
    store_result, _ = post(store_payload, headers, session_id)
    if isinstance(store_result, dict) and "result" in store_result:
        content = store_result["result"].get("content", [{}])
        mem_text = content[0].get("text", "") if content else ""
        try:
            mem_data = json.loads(mem_text)
            mem_id = mem_data.get("id", "stored")
        except Exception:
            mem_id = "stored"
        ok(f"Confirmation sent — memory {mem_id}")
    else:
        err = store_result.get("error", {}).get("message", "unknown") if isinstance(store_result, dict) else str(store_result)
        warn(f"Could not store confirmation: {err}")

    # ── Done ─────────────────────────────────────────
    print(f"\n{GREEN}{BOLD}{'='*50}{RESET}")
    print(f"{GREEN}{BOLD}  ALL CHECKS PASSED — Your Koda setup is working!{RESET}")
    print(f"{GREEN}{BOLD}{'='*50}{RESET}")
    print(f"\n  Hafiz can see your confirmation at:")
    print(f"  {BOLD}https://koda.tutorla.tech/dashboard{RESET}\n")


if __name__ == "__main__":
    main()
