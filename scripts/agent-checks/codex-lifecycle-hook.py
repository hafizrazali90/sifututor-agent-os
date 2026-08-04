#!/usr/bin/env python3
"""Lifecycle hooks that steer Sifututor Codex sessions into workflow skills."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any
import urllib.request

from koda_contract import capability_report


_THIS_FILE = globals().get("__file__")
_DEFAULT_WORKSPACE = Path(_THIS_FILE).resolve().parents[2] if _THIS_FILE else Path.cwd()
WORKSPACE = Path(os.environ.get("SIFUTUTOR_AGENT_OS_ROOT", _DEFAULT_WORKSPACE)).resolve()
SESSION_MAP_DIR = WORKSPACE / ".agent-os" / "session-maps"
CODEX_CONFIG = Path.home() / ".codex" / "config.toml"
KODA_URL = "https://koda.tutorla.tech/mcp"
KODA_STDIO_BRIDGE = str(Path.home() / ".codex" / "bin" / "koda-memory-stdio-bridge.js")
KODA_TIMEOUT = 10
KODA_HEALTH_TAGS = ["sifututor", "codex", "koda-health"]
KODA_HEALTH_PROJECT = "sifututor"
PROJECTS = {
    "kelas",
    "sifu-tutor",
    "ripple-suite",
    "sifututor_tutor",
    "sifututor_parent",
    "lls",
    "lls-frontend",
    "lls-mobile",
    "creative-hub",
    "team-inbox",
    "finch-inbox",
}
PROJECT_ALIASES = {
    "kelas": "kelas",
    "kelasapp": "kelas",
    "kelas-app": "kelas",
    "sifututor_parent": "sifututor_parent",
    "sifututor-parent": "sifututor_parent",
    "parent-app": "sifututor_parent",
    "sifututor_tutor": "sifututor_tutor",
    "sifututor-tutor": "sifututor_tutor",
    "tutor-app": "sifututor_tutor",
    "ripple-suite": "ripple-suite",
    "ripple": "ripple-suite",
    "dashboard": "ripple-suite",
    "sifu-tutor": "sifu-tutor",
    "sifu": "sifu-tutor",
    "lls-frontend": "lls-frontend",
    "lls-mobile": "lls-mobile",
    "lls": "lls",
    "creative-hub": "creative-hub",
    "team-inbox": "team-inbox",
    "finch-inbox": "finch-inbox",
    "finch": "finch-inbox",
}


def emit_context(event: str, message: str) -> None:
    print(
        json.dumps(
            {
                "continue": True,
                "hookSpecificOutput": {
                    "hookEventName": event,
                    "additionalContext": message,
                },
            }
        )
    )


def emit_system(message: str) -> None:
    print(json.dumps({"continue": True, "systemMessage": message}))


def read_payload() -> dict:
    try:
        return json.load(sys.stdin)
    except json.JSONDecodeError:
        return {}


def project_from_cwd(cwd: str) -> str:
    try:
        relative = Path(cwd).resolve().relative_to(WORKSPACE)
    except ValueError:
        return "Sifututor"
    if not relative.parts:
        return "Sifututor"
    first = relative.parts[0]
    return first if first in PROJECTS else "Sifututor"


def active_task_summary(project: str) -> str:
    if project == "Sifututor":
        return "Active task: umbrella workspace, no single project task selected."

    active = WORKSPACE / project / ".claude" / "tasks" / "active.json"
    if not active.exists():
        return f"Active task: none found for {project}."

    try:
        data = json.loads(active.read_text())
    except Exception as exc:  # noqa: BLE001 - hook should not break sessions.
        return f"Active task: could not read {active}: {exc}."

    task_id = data.get("activeTask") or data.get("id") or "none"
    route = data.get("route") or "unknown"
    task_file = data.get("taskFile") or data.get("file") or ""
    summary = f"Active task: {task_id}, route={route}."

    if task_id and task_id != "none":
        candidate = active.parent / f"{task_id}.json"
        if task_file:
            candidate = (active.parent / task_file).resolve()
        if candidate.exists():
            try:
                task = json.loads(candidate.read_text())
                for step in task.get("steps", []):
                    if step.get("status") not in ("done", "skipped"):
                        return f"{summary} Next step: {step.get('name', '?')}."
            except Exception:
                pass
    return summary


def latest_session_map() -> Path | None:
    if not SESSION_MAP_DIR.exists():
        return None
    candidates = sorted(
        SESSION_MAP_DIR.glob("*.md"),
        key=lambda path: (path.stat().st_mtime, path.name),
        reverse=True,
    )
    return candidates[0] if candidates else None


def git_ahead_summary() -> str:
    try:
        result = subprocess.run(
            ["git", "rev-list", "--left-right", "--count", "origin/main...HEAD"],
            cwd=WORKSPACE,
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except Exception:
        return ""
    if result.returncode != 0:
        return ""
    parts = result.stdout.strip().split()
    if len(parts) != 2:
        return ""
    behind, ahead = parts
    if ahead == "0" and behind == "0":
        return ""
    return f"Git state signal: local main is ahead by {ahead} and behind by {behind} compared with origin/main."


def continuation_signal(normalized: str) -> bool:
    patterns = (
        r"^\s*(continue|resume|proceed|go next|next|what next|ok proceed)\s*$",
        r"\bcontinue\b",
        r"\bresume\b",
        r"\bgo next\b",
        r"\bproceed\b",
        r"\bwhat next\b",
        r"\bwhere were we\b",
        r"\bleft (this )?chat\b",
        r"\bfrom last session\b",
    )
    return any(re.search(pattern, normalized) for pattern in patterns)


def smart_resume_actions(normalized: str) -> list[str]:
    latest_map = latest_session_map()
    git_signal = git_ahead_summary()
    has_signal = continuation_signal(normalized) or latest_map is not None or bool(git_signal)
    if not has_signal:
        return []

    actions = [
        "Smart resume check: before broad exploration, check whether this prompt continues the active Session Map or starts a new task.",
    ]
    if latest_map:
        try:
            display_path = latest_map.relative_to(WORKSPACE)
        except ValueError:
            display_path = latest_map
        actions.append(f"Read the latest active Session Map Reference Pack first: `{display_path}`.")
    if git_signal:
        actions.append(git_signal)
    actions.extend(
        [
            "If the active map matches the prompt, summarize main goal, current focus, waiting items, Git state, and the recommended next action before continuing.",
            "If the active map is unrelated, say it looks unrelated and treat the prompt as a new task unless Hafiz wants to resume it.",
        ]
    )
    return actions


def detect_project_from_prompt(prompt: str) -> str:
    lower = prompt.lower()
    matches: list[tuple[int, str]] = []
    for alias, project in sorted(PROJECT_ALIASES.items(), key=lambda item: len(item[0]), reverse=True):
        idx = lower.find(alias)
        if idx >= 0:
            matches.append((idx, project))
    if not matches:
        return ""
    matches.sort(key=lambda item: item[0])
    return matches[0][1]


def post_koda(payload: dict, headers: dict, session_id: str = "") -> tuple[str, str, str]:
    request_headers = dict(headers)
    if session_id:
        request_headers["Mcp-Session-Id"] = session_id
    try:
        req = urllib.request.Request(
            KODA_URL,
            data=json.dumps(payload).encode("utf-8"),
            headers=request_headers,
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=KODA_TIMEOUT) as resp:
            return (
                resp.read().decode("utf-8"),
                resp.headers.get("Content-Type", ""),
                resp.headers.get("Mcp-Session-Id", ""),
            )
    except Exception:
        return "", "", ""


def unwrap_sse(body: str, content_type: str) -> str:
    if body and "text/event-stream" in content_type:
        for line in body.splitlines():
            if line.startswith("data:"):
                return line[len("data:"):].strip()
    return body


def parse_koda_memories(body: str, content_type: str) -> list[dict]:
    try:
        response = json.loads(unwrap_sse(body, content_type))
        content = response.get("result", {}).get("content", [])
        text = ""
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text") or ""
                break
        memories = json.loads(text) if text else []
        return memories if isinstance(memories, list) else []
    except Exception:
        return []


def koda_error(body: str, content_type: str) -> str:
    try:
        response = json.loads(unwrap_sse(body, content_type))
        error = response.get("error", {})
        if isinstance(error, dict):
            message = error.get("message")
            return str(message) if message else ""
    except Exception:
        pass
    return ""


def koda_health_search_arguments() -> dict:
    """Exercise the canonical project filter during every startup health check."""

    return {
        "query": "Codex Koda startup health check",
        "tags": KODA_HEALTH_TAGS,
        "project": KODA_HEALTH_PROJECT,
        "limit": 5,
    }


def koda_headers() -> tuple[dict, str]:
    api_key = os.environ.get("KODA_API_KEY", "")
    if not api_key:
        return {}, "KODA_API_KEY missing"

    return (
        {
            "Content-Type": "application/json",
            "Accept": "application/json, text/event-stream",
            "Authorization": f"Bearer {api_key}",
        },
        "",
    )


def koda_initialize(client_name: str = "codex-lifecycle-hook") -> tuple[dict, str]:
    headers, header_error = koda_headers()
    if header_error:
        return {}, header_error

    init_body, _init_type, session_id = post_koda(
        {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {
                "protocolVersion": "2025-03-26",
                "capabilities": {},
                "clientInfo": {"name": client_name, "version": "1.0"},
            },
            "id": 1,
        },
        headers,
    )
    if not init_body or not session_id:
        return {}, "Koda MCP initialize failed or did not return a session id"

    post_koda({"jsonrpc": "2.0", "method": "notifications/initialized"}, headers, session_id)
    return {"headers": headers, "session_id": session_id}, ""


def koda_tool_call(session: dict, name: str, arguments: dict | None = None, request_id: int = 2) -> tuple[dict, str]:
    body, content_type, _sid = post_koda(
        {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments or {}},
            "id": request_id,
        },
        session["headers"],
        session["session_id"],
    )
    if not body:
        return {}, f"Koda tool call failed: {name}"

    try:
        response = json.loads(unwrap_sse(body, content_type))
    except Exception as exc:  # noqa: BLE001 - hooks report a simple failure.
        return {}, f"Koda tool call returned malformed response for {name}: {exc}"

    if response.get("error"):
        message = koda_error(body, content_type) or "unknown MCP error"
        return {}, f"Koda tool call error for {name}: {message}"

    return response, ""


def print_koda_tool_result(response: dict) -> None:
    """Print the text payload from a Koda MCP tool response without secrets."""

    content = response.get("result", {}).get("content", [])
    printed = False
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            print(item.get("text") or "")
            printed = True
    if not printed:
        print(json.dumps(response.get("result", {}), indent=2))


def read_json_arg_or_stdin(flag: str) -> tuple[dict[str, Any], str]:
    if flag in sys.argv:
        index = sys.argv.index(flag)
        if index + 1 >= len(sys.argv):
            return {}, f"{flag} requires a JSON object argument or '-' for stdin"
        value = sys.argv[index + 1]
        raw = sys.stdin.read() if value == "-" else value
    else:
        raw = sys.stdin.read()

    try:
        data = json.loads(raw)
    except Exception as exc:  # noqa: BLE001 - CLI should report simple errors.
        return {}, f"Invalid JSON for {flag}: {exc}"
    if not isinstance(data, dict):
        return {}, f"{flag} requires a JSON object"
    return data, ""


def koda_direct_cli(tool_name: str, arguments: dict[str, Any]) -> int:
    session, init_error = koda_initialize("codex-koda-direct-cli")
    if init_error:
        print(f"KODA DIRECT FAIL: {init_error}", file=sys.stderr)
        return 1

    response, tool_error = koda_tool_call(session, tool_name, arguments, request_id=2)
    if tool_error:
        print(f"KODA DIRECT FAIL: {tool_error}", file=sys.stderr)
        return 1

    print_koda_tool_result(response)
    return 0


def canonical_memory_content(value: object) -> str:
    """Normalize memory text for exact-content duplicate detection."""

    return re.sub(r"\s+", " ", str(value or "").casefold()).strip()


def koda_store_deduplicated(arguments: dict[str, Any]) -> int:
    """Store through Koda only when no exact-content memory already exists."""

    content = str(arguments.get("content") or "").strip()
    if not content:
        print("KODA DIRECT FAIL: memory_store requires non-empty content", file=sys.stderr)
        return 1

    session, init_error = koda_initialize("codex-koda-deduplicated-store")
    if init_error:
        print(f"KODA DIRECT FAIL: {init_error}", file=sys.stderr)
        return 1

    search_arguments: dict[str, Any] = {"query": content[:500], "limit": 20}
    if arguments.get("project"):
        search_arguments["project"] = arguments["project"]

    search_response, search_error = koda_tool_call(
        session,
        "memory_search",
        search_arguments,
        request_id=2,
    )
    if search_error:
        print(
            f"KODA DIRECT FAIL: duplicate preflight failed; memory was not stored: {search_error}",
            file=sys.stderr,
        )
        return 1

    target = canonical_memory_content(content)
    search_payload = parse_tool_content(search_response)
    if not isinstance(search_payload, list):
        print(
            "KODA DIRECT FAIL: duplicate preflight did not return a memory list; memory was not stored",
            file=sys.stderr,
        )
        return 1

    for memory in search_payload:
        if not isinstance(memory, dict):
            continue
        if canonical_memory_content(memory.get("content")) != target:
            continue
        print(
            json.dumps(
                {
                    "status": "skipped_exact_duplicate",
                    "existing_id": memory.get("id") or "unknown",
                    "next": "use koda update when the canonical memory needs sharper wording",
                }
            )
        )
        return 0

    store_response, store_error = koda_tool_call(
        session,
        "memory_store",
        arguments,
        request_id=3,
    )
    if store_error:
        print(f"KODA DIRECT FAIL: {store_error}", file=sys.stderr)
        return 1
    print_koda_tool_result(store_response)
    return 0


def parse_tool_content(response: dict) -> object:
    content = response.get("result", {}).get("content", [])
    text = ""
    for item in content:
        if isinstance(item, dict) and item.get("type") == "text":
            text = item.get("text") or ""
            break
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        return text


def codex_memory_config_status() -> tuple[bool, str]:
    if not CODEX_CONFIG.exists():
        return True, "Codex memory MCP disabled; using direct Koda CLI/helper path"

    try:
        content = CODEX_CONFIG.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        return False, f"Could not read Codex config: {exc}"

    memory_block = re.search(r"(?ms)^\[mcp_servers\.memory\]\s*(.*?)(?=^\[|\Z)", content)
    if not memory_block:
        return True, "Codex memory MCP disabled; using direct Koda CLI/helper path"

    block = memory_block.group(1)
    url_match = re.search(r'(?m)^\s*url\s*=\s*"([^"]+)"', block)
    token_match = re.search(r'(?m)^\s*bearer_token_env_var\s*=\s*"([^"]+)"', block)
    command_match = re.search(r'(?m)^\s*command\s*=\s*"([^"]+)"', block)
    args_match = re.search(r'(?m)^\s*args\s*=\s*\[(.*?)\]', block, flags=re.S)
    url = url_match.group(1) if url_match else ""
    token_env = token_match.group(1) if token_match else ""
    command = command_match.group(1) if command_match else ""
    args_block = args_match.group(1) if args_match else ""

    if url or token_env:
        if url != KODA_URL:
            return False, f"Codex memory MCP URL is {url or 'missing'}, expected {KODA_URL}"
        if token_env != "KODA_API_KEY":
            return False, f"Codex memory MCP bearer_token_env_var is {token_env or 'missing'}, expected KODA_API_KEY"

        return False, "Codex memory MCP is configured; remove it and use the direct Koda CLI/helper path"

    if command == "node" and KODA_STDIO_BRIDGE in args_block:
        return False, "Codex memory MCP uses the old Koda stdio bridge; remove it and use the direct Koda CLI/helper path"

    return False, "Codex memory MCP config is unknown; remove the memory MCP and use the direct Koda CLI/helper path"


def koda_health_check(write: bool = True) -> tuple[bool, list[str]]:
    details: list[str] = []

    config_ok, config_message = codex_memory_config_status()
    if not config_ok:
        return False, [config_message]
    details.append(config_message)

    session, init_error = koda_initialize("codex-koda-health-check")
    if init_error:
        return False, details + [init_error]
    details.append("Koda direct HTTP initialize returned a session id")

    body, content_type, _sid = post_koda(
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
        session["headers"],
        session["session_id"],
    )
    if not body:
        return False, details + ["Koda tools/list failed"]
    try:
        tools_response = json.loads(unwrap_sse(body, content_type))
        tool_names = {
            tool.get("name")
            for tool in tools_response.get("result", {}).get("tools", [])
            if isinstance(tool, dict)
        }
    except Exception as exc:  # noqa: BLE001
        return False, details + [f"Koda tools/list returned malformed response: {exc}"]

    capabilities = capability_report(tool_names)
    if capabilities["missing_required"]:
        return False, details + [
            f"Koda missing required core tools: {', '.join(capabilities['missing_required'])}"
        ]
    for tier, tier_status in capabilities["tiers"].items():
        if tier_status["missing"]:
            details.append(
                f"Koda {tier} capability tier is partial; missing: {', '.join(tier_status['missing'])}"
            )
        else:
            details.append(f"Koda {tier} capability tier is available")
    if capabilities["unexpected"]:
        details.append(f"Koda also exposes unclassified tools: {', '.join(capabilities['unexpected'])}")

    search_response, search_error = koda_tool_call(
        session,
        "memory_search",
        koda_health_search_arguments(),
        request_id=3,
    )
    if search_error:
        return False, details + [search_error]
    search_payload = parse_tool_content(search_response)
    if not isinstance(search_payload, list):
        return False, details + ["Koda memory_search did not return a memory list"]
    details.append("Koda project-scoped memory_search read check passed")

    if not write:
        return True, details

    health_memory = None
    for memory in search_payload:
        if not isinstance(memory, dict):
            continue
        tags = set(memory.get("tags") or [])
        content = memory.get("content") or ""
        if {"sifututor", "codex", "koda-health"}.issubset(tags) or "Codex Koda startup health check" in content:
            health_memory = memory
            break

    if health_memory and health_memory.get("id") and "memory_update" in tool_names:
        write_response, write_error = koda_tool_call(
            session,
            "memory_update",
            {
                "id": health_memory["id"],
                "content": "Codex Koda startup health check: direct HTTP MCP read/write verified for Sifututor sessions.",
                "why": "Keeps a deduplicated sentinel proving Codex can write to Koda during session startup health checks.",
                "tags": KODA_HEALTH_TAGS,
                "source": "auto-captured",
            },
            request_id=4,
        )
        write_action = f"updated {health_memory['id']}"
    else:
        write_response, write_error = koda_tool_call(
            session,
            "memory_store",
            {
                "content": "Codex Koda startup health check: direct HTTP MCP read/write verified for Sifututor sessions.",
                "category": "fact",
                "why": "Sentinel memory proving Codex can write to Koda during startup health checks.",
                "tags": KODA_HEALTH_TAGS,
                "source": "auto-captured",
                "project": "Sifututor",
            },
            request_id=4,
        )
        write_action = "stored health sentinel"

    if write_error:
        return False, details + [write_error]
    write_payload = parse_tool_content(write_response)
    if write_payload is None:
        return False, details + ["Koda write check returned no content"]
    details.append(f"Koda write check passed ({write_action})")

    return True, details


def koda_repair_text() -> str:
    return (
        "Repair command: run `codex mcp remove memory`, ensure KODA_API_KEY is available "
        "to the shell, then verify with `scripts/agent-checks/koda health`."
    )


def koda_context(prompt: str, project: str) -> str:
    if len(prompt.strip()) < 10:
        return ""

    session, init_error = koda_initialize("codex-lifecycle-hook")
    if init_error:
        return ""

    prompt_project = detect_project_from_prompt(prompt)
    tag_project = prompt_project or (project if project != "Sifututor" else "")

    calls = [
        {"query": prompt[:500], "limit": 3},
    ]
    if tag_project:
        calls.insert(0, {"query": prompt[:500], "limit": 3, "tags": [tag_project]})

    memories: list[dict] = []
    seen: set[str] = set()
    for idx, arguments in enumerate(calls, start=2):
        body, content_type, _sid = post_koda(
            {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {"name": "memory_search", "arguments": arguments},
                "id": idx,
            },
            session["headers"],
            session["session_id"],
        )
        for memory in parse_koda_memories(body, content_type):
            if not isinstance(memory, dict):
                continue
            memory_id = memory.get("id") or ""
            if memory_id and memory_id in seen:
                continue
            if memory_id:
                seen.add(memory_id)
            memories.append(memory)

    bullets = []
    for memory in memories[:3]:
        content = (memory.get("content") or "").strip().splitlines()[0][:180]
        memory_id = memory.get("id") or "memory"
        tags = memory.get("tags") or []
        tag_text = f" [{','.join(tags[:3])}]" if tags else ""
        if content:
            bullets.append(f"- ({memory_id}{tag_text}) {content}")

    if not bullets:
        return ""
    return "Relevant Koda memories (auto-injected, verify before relying):\n" + "\n".join(bullets)


def nontrivial_prompt(prompt: str) -> bool:
    words = prompt.split()
    if len(words) >= 6:
        return True
    triggers = (
        "fix",
        "implement",
        "proceed",
        "continue",
        "resume",
        "go next",
        "what next",
        "commit",
        "verify",
        "qa",
        "review",
        "ui audit",
        "visual qa",
        "screenshot",
        "diagnose",
        "save",
        "handoff",
        "snapshot",
        "push",
        "prd",
        "ux",
        "redesign",
        "brainstorm",
        "build prompts",
    )
    lower = prompt.lower()
    return any(trigger in lower for trigger in triggers)


def discussion_prompt(normalized: str) -> bool:
    """Return True for think-with-me prompts that should not force a workflow."""

    diagnostic_patterns = (
        r"\bdiagnose\b",
        r"\bdebug\b",
        r"\broot cause\b",
        r"\bfailing\b",
        r"\bfailure\b",
        r"\bbroken\b",
        r"\bbug\b",
        r"\berror\b",
        r"\bcrash\b",
        r"\bnot working\b",
    )
    if any(re.search(pattern, normalized) for pattern in diagnostic_patterns):
        return False

    action_patterns = (
        r"\bcommit (this|these|it|the|all)\b",
        r"\bprepare (a )?commit\b",
        r"\bstage (this|these|it|the|all|changes)\b",
        r"\bpush (this|these|it|to|main)\b",
        r"\bdeploy (this|these|it|to)\b",
        r"\bmerge (this|these|it|to|into)\b",
        r"\b(open|create) (a )?(pr|pull request)\b",
        r"\bimplement\b",
        r"\bfix\b",
        r"\bapply\b",
        r"\bmake (the|this|these|it)\b",
        r"\bupdate (the|this|these|it)\b",
        r"\bproceed (with|to)\b",
    )
    if any(re.search(pattern, normalized) for pattern in action_patterns):
        return False

    discussion_patterns = (
        r"\bdiscuss\b",
        r"\blet'?s discuss\b",
        r"\blets discuss\b",
        r"\blearn\b",
        r"\bteach\b",
        r"\bexplain\b",
        r"\banaly[sz]e\b",
        r"\bresearch\b",
        r"\bretrospective\b",
        r"\bpostmortem\b",
        r"\bwhat (mistake|mistakes|went wrong|should|can|could|is|are|do you think)\b",
        r"\bhow (should|can|could|do we|do i|to)\b",
        r"\bwhy\b",
        r"\boptions?\b",
        r"\brecommendation\b",
        r"\barchitecture\b",
        r"\bdesign (the|a|our|full|from|agent|agentic|sifututor)\b",
    )
    return any(re.search(pattern, normalized) for pattern in discussion_patterns)


def report_only_prompt(normalized: str) -> bool:
    """Detect pasted evidence reports that do not ask the agent to act."""

    report_markers = (
        "final report",
        "follow-up report",
        "save-session dry run",
        "dry run, nothing written",
        "guards and checks, in order",
    )
    evidence_markers = (
        "nothing staged",
        "nothing was staged",
        "nothing committed",
        "nothing was committed",
        "nothing pushed",
        "nothing was pushed",
        "bypass: none",
        "no bypass",
    )
    direct_request = re.search(
        r"(?:^|[.!?]\s+)(?:please\s+)?(?:commit|push|deploy|merge|implement|fix|apply|run|create|open)\b",
        normalized,
    )
    return (
        any(marker in normalized for marker in report_markers)
        and any(marker in normalized for marker in evidence_markers)
        and direct_request is None
    )


def commit_prompt(normalized: str) -> bool:
    """Return True only for commit preparation/execution intent."""

    commit_patterns = (
        r"\bcommit (this|these|it|the|all|changes|files|docs|work)\b",
        r"\bprepare (a )?commit\b",
        r"\bcreate (a )?commit\b",
        r"\bmake (a )?commit\b",
        r"\bstage (this|these|it|the|all|changes|files)\b",
        r"\bstaging changes\b",
        r"\bready to commit\b",
        r"\bcommit readiness\b",
    )
    return any(re.search(pattern, normalized) for pattern in commit_patterns)


def classify_prompt(prompt: str) -> tuple[str, list[str], str]:
    """Return a workflow skill, required actions, and a short reason."""

    lower = prompt.lower()
    normalized = re.sub(r"\s+", " ", lower).strip()

    if report_only_prompt(normalized):
        return (
            "",
            [],
            "Prompt is a quoted or pasted report with no direct action request.",
        )

    if re.search(r"(^|\s|/|\\)\.env($|\b|[./_-])", normalized) or re.search(r"(^|\s|/|\\)live(/|\\)", normalized):
        return (
            "$task-router",
            [
                "Treat this as a blocked boundary, not implementation work.",
                "Do not read `.env*`, reveal secrets, or modify `live/`.",
                "Explain the boundary in plain language and offer a safe alternative if one exists.",
            ],
            "Prompt requests a forbidden boundary.",
        )

    if "--no-verify" in normalized or "bypass hook" in normalized or "skip hook" in normalized:
        return (
            "$task-router",
            [
                "Treat this as a blocked bypass request, not implementation work.",
                "Do not use `--no-verify` or skip hooks, tests, or quality gates.",
                "Explain the boundary in plain language and offer to fix the failing hook or test instead.",
            ],
            "Prompt requests a forbidden hook or quality-gate bypass.",
        )

    if "agents.md" in normalized and "claude.md" in normalized and any(
        word in normalized for word in ("conflict", "another", "different", "disagree")
    ):
        return (
            "$task-router",
            [
                "Stop before editing because the source-of-truth instructions conflict.",
                "Report the AGENTS.md versus CLAUDE.md conflict in plain language.",
                "Ask Hafiz which instruction should control before changing files.",
            ],
            "Prompt reports a workflow instruction conflict.",
        )

    direct_skill = re.search(
        r"\$(task-router|verify|qa|commit|save-session|handoff|snapshot|session-map|diagnose|review|quick-check|product-design|monitor-production-logs|sims-ui-audit|workflow-improvement)\b",
        normalized,
    )
    if direct_skill:
        skill = f"${direct_skill.group(1)}"
        return (
            skill,
            [
                f"Use the explicitly requested {skill} skill.",
                "Read the skill body, then the linked shared playbook before acting.",
            ],
            "User explicitly invoked a Codex workflow skill.",
        )

    workflow_efficiency_patterns = (
        "anything redundant",
        "workflow redundancy",
        "reduce workflow",
        "simplify workflow",
        "streamline workflow",
        "speed up our agent os",
        "speed up our dev",
        "improve agent os workflow",
        "improve the agent os workflow",
    )
    if any(pattern in normalized for pattern in workflow_efficiency_patterns):
        return (
            "$workflow-improvement",
            [
                "Use $workflow-improvement to remove repeated work from the Agent OS.",
                "Preserve safety gates and remove duplicate execution, state reads, or documentation instead.",
                "Add focused fixtures before changing hooks or shared workflow behavior.",
            ],
            "Prompt asks for Agent OS workflow efficiency improvement.",
        )

    today_briefing_patterns = (
        "organize everything i need to do today",
        "what do i need to do today",
        "what should i do today",
        "what should i focus on today",
        "what needs me today",
        "what is unfinished",
        "waiting for my approval",
        "waiting on staff",
        "safe to defer",
    )
    if any(pattern in normalized for pattern in today_briefing_patterns):
        return (
            "$task-router",
            [
                "Use the cross-project today briefing route in task-router.md.",
                "From the umbrella workspace, run `python3 scripts/agent-checks/agent-os-today-snapshot.py --include-planner --include-github` once and reuse that snapshot.",
                "Use one bounded Planner read and one bounded GitHub search; do not query the same connector separately for every item.",
                "Label each claim as verified, trusted, reported, historical, stale, or unavailable and show when it was checked.",
                "Perform no more than three targeted follow-up checks, only when fresh evidence can change today's ordering or approval recommendation.",
                "Return exactly these attention groups: Needs Hafiz now, Waiting on staff, Agent can continue, Monitor, and Deferred.",
                "Read-only preparation does not need approval; ask only immediately before the exact write, release, production, access, critical-lane implementation, or destructive action.",
                "Do not use Plane unless Hafiz explicitly asks.",
            ],
            "Prompt asks for a cross-project today briefing.",
        )

    ui_audit_patterns = (
        "sims ui",
        "sims ui/ux",
        "ui/ux audit",
        "ui audit",
        "visual qa",
        "visual audit",
        "screenshot review",
        "review screenshot",
        "screenshots before",
        "spacing",
        "density",
        "disabled button",
        "disabled state",
        "table fit",
        "filter layout",
        "modal padding",
        "dropdown styling",
        "design system consistency",
    )
    ui_surface_patterns = (
        "sifu-tutor",
        "sims",
        "admin ui",
        "browser ui",
        "page",
        "modal",
        "dropdown",
        "table",
        "filter",
        "sidebar",
        "screenshot",
    )
    if any(pattern in normalized for pattern in ui_audit_patterns) and any(
        pattern in normalized for pattern in ui_surface_patterns
    ):
        return (
            "$sims-ui-audit",
            [
                "Use $sims-ui-audit for SIMS browser UI/UX visual judgment.",
                "Read docs/agent-playbooks/sims-ui-audit.md before judging the UI.",
                "Read the relevant sifu-tutor/docs/ui-ux/ source-of-truth docs named by that playbook.",
                "Inspect screenshots or browser states for the changed page, including modals, dropdowns, filters, tables, disabled states, and responsive states when in scope.",
                "Report findings before summary; fix in-scope UI blockers before asking Hafiz to review.",
            ],
            "Prompt asks for SIMS UI/UX audit or screenshot-backed visual QA.",
        )

    if "approve" in normalized and "commit" in normalized and "push" in normalized:
        return (
            "$review",
            [
                "Use $review first as a pre-push risk check for the approved commit+push bundle.",
                "Confirm the exact approved file list from visible chat context before staging.",
                "After review and guard checks pass, commit and push exactly that approved bundle.",
                "Do not include deploy, merge, PR, or unrelated files in the bundle.",
            ],
            "Prompt approves a visible commit+push bundle and requires pre-push review.",
        )

    if "approve" in normalized and "commit" in normalized:
        return (
            "$commit",
            [
                "Use $commit and run the shared pre-commit guard for the approved commit-only bundle.",
                "Stage and commit only the exact approved file list from visible chat context.",
                "Do not push because push was not part of the approval request.",
            ],
            "Prompt approves a visible commit-only bundle.",
        )

    if "koda" in normalized and any(word in normalized for word in ("conflict", "disagree", "disagrees", "contradict", "stale")):
        return (
            "$task-router",
            [
                "Use docs/agent-playbooks/context-authority.md before acting on the Koda conflict.",
                "Identify the owner source for the question: current repo/docs/evidence, Hafiz decision, or historical memory.",
                "Treat Koda as historical context until current files and evidence confirm it.",
                "If Koda is stale, explain the mismatch and update Koda after verification.",
            ],
            "Prompt reports a Koda conflict with current context and needs source-of-truth handling.",
        )

    if "koda" in normalized and any(word in normalized for word in ("workaround", "memory", "accepted", "apply")):
        return (
            "$task-router",
            [
                "Treat Koda as historical context, not automatic permission to edit.",
                "Use docs/agent-playbooks/context-authority.md when memory and current sources might disagree.",
                "Identify the owner source before deciding whether the memory still applies.",
                "Check current files and current repo behavior before applying any remembered workaround.",
                "If the memory is stale, explain the mismatch and update Koda after verification.",
            ],
            "Prompt relies on Koda or historical context and needs current-state verification.",
        )

    if "staff" in normalized and "planner" in normalized and any(
        word in normalized for word in ("only", "not llm", "no llm", "not agent os", "teams")
    ):
        return (
            "$task-router",
            [
                "Treat this as an Agent OS rollout correction: ordinary non-developer staff use Teams Planner only.",
                "Agent OS rollout is for developer staff working in project repos.",
                "Update rollout docs, evals, and memory if durable wording currently mixes those groups.",
            ],
            "Prompt corrects staff rollout scope and Planner intake ownership.",
        )

    if "staff" in normalized and any(
        word in normalized for word in ("install", "tools", "llm", "capability", "access", "payment", "auth", "deploy")
    ):
        return (
            "$task-router",
            [
                "Confirm whether this is developer staff or ordinary non-developer staff, then apply least-privilege access.",
                "Ordinary staff use Teams Planner only; developer staff may use the Developer Staff Kit after project adoption.",
                "Do not grant production, deploy, secret, Koda write, or critical-lane access by default.",
                "Escalate only after Hafiz approves scoped capability, evidence expectations, and review gates.",
            ],
            "Prompt is about developer-staff Agent OS rollout or capability access.",
        )

    if ("planner" in normalized or "staff member" in normalized or "staff says" in normalized) and not any(
        word in normalized for word in ("install", "tools", "llm", "capability", "access")
    ):
        return (
            "$diagnose",
            [
                "Use Planner read-only as intake evidence when relevant and available.",
                "Treat this as a reported symptom, not verified root cause.",
                "Check Planner or available staff-reported context when relevant, then reproduce or inspect before editing.",
                "Do not mutate Planner status, assignment, priority, or content unless Hafiz explicitly asks.",
                "Convert confirmed engineering work into the normal GitHub/task workflow.",
            ],
            "Prompt starts from staff or Planner-reported operational context.",
        )

    if any(
        word in normalized
        for word in (
            "session map",
            "session-map",
            "mindmap",
            "mind map",
            "progress board",
            "return path",
            "side path",
            "side paths",
        )
    ):
        return (
            "$session-map",
            [
                "Use $session-map to create, update, or inspect the live Session Map.",
                "Keep the Human Snapshot readable first, then update structured agent context as needed.",
                "Do not promote local session maps into committed docs unless Hafiz explicitly approves.",
            ],
            "Prompt is asking for live session tracking.",
        )

    if discussion_prompt(normalized):
        return (
            "",
            [],
            "Prompt is asking for discussion, learning, research, analysis, or retrospective; no workflow skill required.",
        )

    product_design_patterns = (
        "prd",
        "lite prd",
        "product requirements",
        "product design",
        "ux spec",
        "ux specification",
        "build prompts",
        "user stories",
        "clarify requirements",
        "requirements clarification",
        "brainstorm",
        "redesign properly",
        "redesign it properly",
        "major redesign",
        "new module",
        "workflow redesign",
    )
    if any(pattern in normalized for pattern in product_design_patterns):
        return (
            "$product-design",
            [
                "Use $product-design before implementation.",
                "Follow the PRD -> clarifier if needed -> UX spec -> backend contract if needed -> build prompts path.",
                "Reduce noise: ask only questions that change requirements, risk, UX, RBAC, data contracts, or acceptance tests.",
            ],
            "Prompt is asking for product design, PRD/UX/build prompts, or major workflow redesign.",
        )

    critical_domain_patterns = (
        "payment",
        "payments",
        "invoice",
        "invoices",
        "commission",
        "commissions",
        "migration",
        "migrations",
        "auth",
        "authentication",
        "mobile api",
        "api response",
        "api contract",
    )
    critical_action_patterns = (
        "fix",
        "change",
        "update",
        "modify",
        "patch",
        "implement",
        "response changed",
        "contract changed",
    )
    if any(domain in normalized for domain in critical_domain_patterns) and any(
        action in normalized for action in critical_action_patterns
    ):
        return (
            "$diagnose",
            [
                "Use $diagnose before editing.",
                "This is a critical lane: auth, payments, invoices, commissions, migrations, deployment, or mobile API contract behavior.",
                "Stop after read-only Phase A diagnosis and wait for approval before implementation.",
            ],
            "Prompt touches a critical lane and requires diagnosis first.",
        )

    if any(word in normalized for word in ("quick check", "quick-check", "health check", "workflow doctor", "doctor", "wired correctly")):
        return (
            "$quick-check",
            [
                "Use $quick-check and run scripts/agent-checks/workflow-doctor.sh from the umbrella root.",
                "Report PASS/FAIL/PARTIAL with any workflow wiring problems before implementation.",
            ],
            "Prompt is asking to check workflow health.",
        )

    if "agent os" in normalized and any(word in normalized for word in ("90%", "90 percent", "90 accuracy", "accuracy")) and any(
        word in normalized for word in ("test", "testing", "improve", "behaving", "behavior")
    ):
        return (
            "$workflow-improvement",
            [
                "Use $workflow-improvement because Hafiz is asking to improve Agent OS behavior, not product code.",
                "Run `python3 scripts/agent-checks/agent-os-validation-loop.py --target 0.90 --max-rounds 3` before claiming the executable Agent OS score.",
                "Explain that the score covers deterministic Agent OS checks, not subjective tone, live LLM judgment, product E2E correctness, or business acceptance.",
                "If the score is below 90%, fix the failing Agent OS layer and rerun instead of lowering the target.",
            ],
            "Prompt asks to test and improve Agent OS behavior against a 90% accuracy target.",
        )

    if all(word in normalized for word in ("claude", "codex")) and any(
        word in normalized for word in ("compare", "different", "differently", "drift", "parity", "same workflow", "behave")
    ):
        return (
            "$workflow-improvement",
            [
                "Use the Claude/Codex behavior comparison path instead of judging wording by taste.",
                "Run the parity runner and compare route, first move, approval boundary, evidence, state language, memory/task routing, and close-out.",
                "Different wording is fine when the shared workflow behavior is equivalent.",
            ],
            "Prompt asks for Claude/Codex behavior comparison.",
        )

    if "agent os" in normalized and any(word in normalized for word in ("ready", "readiness", "install-ready")):
        return (
            "$quick-check",
            [
                "Use $quick-check and run scripts/agent-checks/workflow-doctor.sh from the umbrella root.",
                "Report PASS/FAIL/PARTIAL with any readiness warnings or missing baseline files.",
            ],
            "Prompt is asking to check workflow health.",
        )

    if "live evidence" in normalized and any(word in normalized for word in ("probe", "report", "capability", "check", "summary")):
        return (
            "$quick-check",
            [
                "Use $quick-check for the live evidence probe report.",
                "Run `python3 scripts/agent-checks/agent-os-live-evidence-report.py` to summarize current GitHub, Planner, production monitoring, and Koda retrieval evidence.",
                "Treat the report as read-only evidence only; do not mutate GitHub, Planner, production monitoring, or Koda.",
                "Explain any unavailable source as missing evidence instead of guessing.",
            ],
            "Prompt asks for a live evidence probe report.",
        )

    if "create" in normalized and "issue" in normalized and ("document" in normalized or "plan" in normalized):
        return (
            "$task-router",
            [
                "Treat this as a safe planning bundle only if the scope is clear and non-critical.",
                "Create or link the engineering issue, then document the plan in the relevant Agent OS or project file.",
                "Do not implement product changes until the planned scope is confirmed.",
            ],
            "Prompt asks for a bundled issue-and-plan workflow.",
        )

    if any(word in normalized for word in ("save session", "save-session", "wrap up", "end session", "finish session")):
        return (
            "$save-session",
            [
                "Use $save-session before final response.",
                "Report Koda status, active task, guards, commits/pushes, remaining work, and blockers.",
            ],
            "Prompt is asking to preserve or close session state.",
        )

    if any(word in normalized for word in ("handoff", "hand off", "pass to claude", "pass to codex")):
        return (
            "$handoff",
            [
                "Use $handoff to produce a continuation-ready state summary.",
                "If this is also the end of meaningful work, follow with $save-session.",
            ],
            "Prompt is asking to transfer work to another agent or human.",
        )

    if any(word in normalized for word in ("snapshot", "compact", "compaction", "pause here", "context save")):
        return (
            "$snapshot",
            [
                "Use $snapshot to preserve current goal, task state, next move, and dirty files.",
                "Do not mark the task complete unless the user explicitly asks for a full save-session.",
            ],
            "Prompt is asking to preserve temporary working context.",
        )

    if any(word in normalized for word in ("review", "audit", "code review", "risk review", "pre-commit review")):
        return (
            "$review",
            [
                "Use $review and lead with findings.",
                "Check AGENTS.md, relevant CLAUDE.md, diffs, tests, and workflow violations.",
            ],
            "Prompt is asking for review/audit behavior.",
        )

    if any(phrase in normalized for phrase in ("pull request", " pr ", "pr #")) and any(
        word in normalized for word in ("ready", "merge", "ci", "checks", "approved", "review")
    ):
        return (
            "$review",
            [
                "Use $review for GitHub PR readiness before recommending merge or release.",
                "Run the GitHub read probe or an equivalent safe GitHub read before claiming PR state.",
                "Check CI/check evidence, unresolved review comments, branch/commit state, and changed-file risk.",
                "Do not merge, deploy, or mark accepted unless that boundary is explicitly approved and the evidence is current.",
            ],
            "Prompt asks for GitHub PR readiness.",
        )

    if any(word in normalized for word in ("diagnose", "debug", "root cause", "why", "failing", "failure", "broken", "bug")):
        return (
            "$diagnose",
            [
                "Use $diagnose before editing.",
                "For critical lanes, stop after Phase A diagnosis and wait for approval before implementation.",
            ],
            "Prompt is about bug/root-cause analysis.",
        )

    if any(word in normalized for word in ("verify", "gate 2a", "prove it works", "run checks", "test this")):
        return (
            "$verify",
            [
                "Use $verify and run checks from the project directory.",
                "Separate baseline failures from task-caused failures.",
            ],
            "Prompt is asking for implementation verification.",
        )

    if re.search(r"\bqa\b", normalized) or any(word in normalized for word in ("regression", "smoke", "manual qa", "visual qa")):
        return (
            "$qa",
            [
                "Use $qa and pick the QA tier from route/surface area.",
                "For bugfix/hotfix work, state the old failure mode and regression evidence.",
            ],
            "Prompt is asking for QA or regression evidence.",
        )

    if any(word in normalized for word in ("monitor", "monitoring", "logs", "sentry", "betterstack")) and any(
        word in normalized for word in ("production", "prod", "deploy", "release", "live")
    ):
        return (
            "$monitor-production-logs",
            [
                "Use $monitor-production-logs for production monitoring evidence.",
                "Run the production logs probe or approved read-only Sentry/BetterStack checks before claiming monitoring is clean.",
                "Report counts/status only; do not print secrets, noisy payloads, or unrelated production details.",
                "Do not deploy, rollback, acknowledge issues, or mutate production systems unless Hafiz explicitly approves that separate boundary.",
            ],
            "Prompt asks for production monitoring evidence.",
        )

    if any(person in normalized for person in ("human", "hafiz", "staff")) and any(
        word in normalized for word in ("check", "verify", "qa")
    ):
        return (
            "$verify",
            [
                "Treat this as a verification gap if the agent can safely check it.",
                "Run available browser, mobile, API, CLI, or read-only checks before asking Hafiz or staff.",
                "Ask for human verification only for unavailable credentials, destructive paths, subjective acceptance, or risk sign-off.",
            ],
            "Prompt describes a verification gap where human handoff may need agent-run evidence first.",
        )

    if any(phrase in normalized for phrase in ("unit tests", "backend tests", "api tests")) and any(
        phrase in normalized for phrase in ("staff workflow", "user workflow", "browser", "mobile evidence", "human journey")
    ):
        return (
            "$qa",
            [
                "Report machine-level proof as partial when human-journey evidence is missing.",
                "Gather browser, mobile, API-contract, or manual QA evidence where feasible.",
                "Do not call the real workflow done until the human journey is proved or a named blocker is documented.",
            ],
            "Prompt exposes a human-journey evidence gap.",
        )

    if commit_prompt(normalized):
        return (
            "$commit",
            [
                "Use $commit and run the shared pre-commit guard.",
                "For multi-fix sessions, update docs/agent-playbooks/session-release-ledger.md style status before staging.",
                "Do not commit without explicit current-session approval of the exact file list.",
                "Do not push unless explicitly asked in the current session.",
            ],
            "Prompt is asking for commit preparation or commit execution.",
        )

    if "done" in normalized and any(phrase in normalized for phrase in ("locally", "changed files", "not pushed", "not committed")):
        return (
            "$task-router",
            [
                "Clarify the exact state: done locally, committed, pushed, PR open, merged, deployed, or live-smoke-passed.",
                "Do not imply the change is live or shipped without git, deploy, and smoke evidence.",
                "Recommend the next state transition, such as verify, commit, push, PR, deploy, or close.",
            ],
            "Prompt risks confusing local work with shipped state.",
        )

    if "all fixes" in normalized and "live" in normalized:
        return (
            "$task-router",
            [
                "Inventory every session fix by branch, commit, PR, main status, deploy status, and live smoke status.",
                "Use the Session Release Ledger when more than one fix is in play.",
                "Do not summarize multiple fixes as done without naming each target state.",
            ],
            "Prompt asks for multi-fix live-state truth.",
        )

    production_boundary = any(
        phrase in normalized
        for phrase in (
            "until production",
            "to production",
            "production deploy",
            "deploy production",
            "push production",
            "release production",
        )
    )
    if any(word in normalized for word in ("push", "deploy", "release", "merge", "pull request", " pr ")) or production_boundary:
        return (
            "$review",
            [
                "Use $review first as a pre-push/pre-release risk check.",
                "For multi-fix sessions, inventory every session fix: in main, PR-only, local-only, live, and not-live.",
                "Confirm explicit approval before push, deploy, merge, or PR actions.",
                "Run $verify and $qa first if evidence is missing.",
            ],
            "Prompt is about a high-risk outbound action.",
        )

    if nontrivial_prompt(prompt):
        return (
            "$task-router",
            [
                "Use $task-router before implementation.",
                "Read nearest AGENTS.md and relevant CLAUDE.md.",
                "Search Koda memory and read active task state when present.",
                "If this chat contains multiple fixes, maintain a Session Release Ledger so no commit is stranded off main/live.",
            ],
            "Prompt appears to be non-trivial work.",
        )

    return (
        "",
        [],
        "Prompt appears trivial; no workflow skill required.",
    )


def main() -> int:
    if "--check-koda" in sys.argv:
        ok, details = koda_health_check(write="--write-check" in sys.argv)
        status = "PASS" if ok else "FAIL"
        print(f"KODA {status}")
        for detail in details:
            print(f"- {detail}")
        if not ok:
            print(f"- {koda_repair_text()}")
        return 0 if ok else 1

    if "--koda-search-json" in sys.argv:
        arguments, error = read_json_arg_or_stdin("--koda-search-json")
        if error:
            print(f"KODA DIRECT FAIL: {error}", file=sys.stderr)
            return 1
        return koda_direct_cli("memory_search", arguments)

    if "--koda-store-json" in sys.argv:
        arguments, error = read_json_arg_or_stdin("--koda-store-json")
        if error:
            print(f"KODA DIRECT FAIL: {error}", file=sys.stderr)
            return 1
        return koda_store_deduplicated(arguments)

    if "--koda-update-json" in sys.argv:
        arguments, error = read_json_arg_or_stdin("--koda-update-json")
        if error:
            print(f"KODA DIRECT FAIL: {error}", file=sys.stderr)
            return 1
        return koda_direct_cli("memory_update", arguments)

    payload = read_payload()
    event = payload.get("hook_event_name") or payload.get("hookEventName") or ""
    cwd = payload.get("cwd") or os.getcwd()
    project = project_from_cwd(cwd)
    active_summary = active_task_summary(project)

    if event == "SessionStart":
        source = payload.get("source") or "startup"
        koda_ok, koda_details = koda_health_check(write=True)
        if koda_ok:
            koda_lines = [
                "Koda: healthy, read/write verified.",
                *[f"  - {detail}" for detail in koda_details],
            ]
        else:
            koda_lines = [
                "Koda: FAILED.",
                *[f"  - {detail}" for detail in koda_details],
                f"  - {koda_repair_text()}",
                "  - Fix Koda before doing non-trivial Sifututor work. Do not rely on memory fallback for corrections, saves, or task-start context.",
            ]
        emit_context(
            "SessionStart",
            "\n".join(
                [
                    f"Sifututor Codex session started via {source}.",
                    f"Project detected: {project}.",
                    active_summary,
                    *koda_lines,
                    "Communication default: explain the practical meaning in natural language before technical details; Hafiz is a self-learning engineer without a CS background.",
                    "Explanation-first default: for bugs, PRs, features, or unfamiliar technical topics, explain who uses the workflow, current behavior, expected behavior, and why it matters before findings or code. Before non-trivial implementation, explain the intended build, real options, recommendation, and evidence plan in English once; after approval, continue inside the agreed boundary without re-asking. If Hafiz asks to go one by one, cover one item with its effect, improvement, evidence, and decision, then stop before the next unless he approved an autonomous walkthrough.",
                    "Close-out default: after meaningful work, make the final answer self-contained with what changed, how it was checked, the highest proven state, what remains, one recommended next action, and whether Hafiz needs to decide anything.",
                    "Standing task access: when Hafiz asks Codex to finish a task end-to-end, use the narrowest required local agent-access files/tools without asking another permission question; never print secrets, read repo .env*, or use unrelated access.",
                    "Workflow automation is active. For non-trivial prompts, the UserPromptSubmit hook will select the required Codex workflow skill.",
                    "Available skills: $task-router, $product-design, $verify, $qa, $sims-ui-audit, $commit, $save-session, $handoff, $snapshot, $session-map, $diagnose, $review.",
                    "Default implementation path: $task-router -> $verify -> $qa -> $review -> $commit -> $save-session. SIMS UI path adds $sims-ui-audit before Hafiz review or commit. Product-design path: $product-design -> PRD/UX/build prompts -> implementation approval.",
                ]
            ),
        )
        return 0

    if event == "UserPromptSubmit":
        prompt = str(payload.get("prompt") or "")
        skill, actions, reason = classify_prompt(prompt)
        if not skill:
            return 0
        normalized = re.sub(r"\s+", " ", prompt.lower()).strip()
        if skill == "$task-router":
            actions = [
                *actions,
                *smart_resume_actions(normalized),
                "If the prompt may be a follow-up, adjacent task, paused question, or part of a bigger goal, search `docs/agent-playbooks/mission-ledger` with `rg` and read only the relevant section.",
            ]
        elif skill == "$save-session":
            actions = [
                *actions,
                "Check whether any follow-up, adjacent task, paused decision, or bigger-goal link should be captured in the Mission Ledger; search/open only the relevant project file.",
            ]
        action_text = "\n".join(f"- {action}" for action in actions)
        memory_skills = {"$task-router", "$product-design", "$diagnose", "$verify", "$qa", "$sims-ui-audit", "$review", "$commit", "$session-map"}
        memory_text = koda_context(prompt, project) if skill in memory_skills else ""
        memory_section = memory_text or "\n".join(
            [
                "Relevant Koda memories: none injected.",
                "Trust the SessionStart Koda health result for this session. Do not rerun Koda health after every prompt; recheck only after a reported failure, configuration change, or long resume.",
            ]
        )
        emit_context(
            "UserPromptSubmit",
            "\n".join(
                [
                    "Sifututor workflow dispatcher:",
                    f"- Detected project: {project}.",
                    f"- Selected workflow skill: {skill}.",
                    f"- Reason: {reason}",
                    active_summary,
                    "Required actions:",
                    action_text,
                    memory_section,
                    "Communication default: start with a plain-language explanation and practical meaning, then provide technical file/test/workflow detail.",
                    "Explanation-first default: for bugs, PRs, features, or unfamiliar technical topics, explain who uses the workflow, current behavior, expected behavior, and why it matters before findings or code. Before non-trivial implementation, explain the intended build, real options, recommendation, and evidence plan in English once; after approval, continue inside the agreed boundary without re-asking. If Hafiz asks to go one by one, cover one item with its effect, improvement, evidence, and decision, then stop before the next unless he approved an autonomous walkthrough.",
                    "Close-out default: after meaningful work, make the final answer self-contained with what changed, how it was checked, the highest proven state, what remains, one recommended next action, and whether Hafiz needs to decide anything.",
                    "Standing task access: if the current task already requires scoped access for verify, QA, deploy, smoke, or monitoring, use the narrowest required access without another approval prompt; keep secrets hidden and stay inside the task.",
                    "Do not bypass the selected skill. Read its SKILL.md and the linked docs/agent-playbooks/ file before acting.",
                    "Critical lanes require Phase A diagnosis before implementation: auth, payments, invoices, commissions, migrations, deployment, and mobile API contracts.",
                ]
            ),
        )
        return 0

    if event == "PreCompact":
        trigger = payload.get("trigger") or "unknown"
        emit_system(
            f"Sifututor PreCompact ({trigger}): before relying on compacted context, preserve current goal, active task, next step, dirty state, and durable lessons with $snapshot or $save-session."
        )
        return 0

    if event == "Stop":
        emit_system(
            "Sifututor Stop reminder: if meaningful work occurred, use $save-session before ending. Do not finish with only 'done.' Report Koda memory status, active task, guards, commits/pushes, remaining work, and blockers."
        )
        return 0

    return 0


raise SystemExit(main())
