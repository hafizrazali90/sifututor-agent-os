#!/usr/bin/env python3
"""Lifecycle hooks that steer Sifututor Codex sessions into workflow skills."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from typing import Any
import urllib.request


WORKSPACE = Path("/Users/hafizrazali/Projects/Sifututor")
CODEX_CONFIG = Path.home() / ".codex" / "config.toml"
KODA_URL = "http://178.105.120.34:3848/mcp"
KODA_TIMEOUT = 2
KODA_REQUIRED_TOOLS = {"memory_search", "memory_store", "memory_context", "session_start"}
KODA_HEALTH_TAGS = ["sifututor", "codex", "koda-health"]
PROJECTS = {
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
        return False, f"Codex config not found at {CODEX_CONFIG}"

    try:
        content = CODEX_CONFIG.read_text(encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        return False, f"Could not read Codex config: {exc}"

    memory_block = re.search(r"(?ms)^\[mcp_servers\.memory\]\s*(.*?)(?=^\[|\Z)", content)
    if not memory_block:
        return False, "Codex config has no [mcp_servers.memory] block"

    block = memory_block.group(1)
    url_match = re.search(r'(?m)^\s*url\s*=\s*"([^"]+)"', block)
    token_match = re.search(r'(?m)^\s*bearer_token_env_var\s*=\s*"([^"]+)"', block)
    url = url_match.group(1) if url_match else ""
    token_env = token_match.group(1) if token_match else ""

    if url != KODA_URL:
        return False, f"Codex memory MCP URL is {url or 'missing'}, expected {KODA_URL}"
    if token_env != "KODA_API_KEY":
        return False, f"Codex memory MCP bearer_token_env_var is {token_env or 'missing'}, expected KODA_API_KEY"

    return True, "Codex memory MCP config is direct HTTP with KODA_API_KEY"


def koda_health_check(write: bool = True) -> tuple[bool, list[str]]:
    details: list[str] = []

    config_ok, config_message = codex_memory_config_status()
    if not config_ok:
        return False, [config_message]
    details.append(config_message)

    session, init_error = koda_initialize("codex-koda-health-check")
    if init_error:
        return False, details + [init_error]
    details.append("Koda MCP initialize returned a session id")

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

    missing_tools = sorted(KODA_REQUIRED_TOOLS - tool_names)
    if missing_tools:
        return False, details + [f"Koda missing required tools: {', '.join(missing_tools)}"]
    details.append("Koda required tools are available")

    search_response, search_error = koda_tool_call(
        session,
        "memory_search",
        {
            "query": "Codex Koda startup health check",
            "tags": KODA_HEALTH_TAGS,
            "limit": 5,
        },
        request_id=3,
    )
    if search_error:
        return False, details + [search_error]
    search_payload = parse_tool_content(search_response)
    if not isinstance(search_payload, list):
        return False, details + ["Koda memory_search did not return a memory list"]
    details.append("Koda memory_search read check passed")

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
        "Repair command: `codex mcp remove memory; "
        "codex mcp add memory --url http://178.105.120.34:3848/mcp "
        "--bearer-token-env-var KODA_API_KEY`, then start a fresh Codex session."
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
        "commit",
        "verify",
        "qa",
        "review",
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

    if re.search(r"(^|\s|/|\\)\.env($|\b|[./_-])", normalized) or re.search(r"(^|\s|/|\\)live(/|\\|\b)", normalized):
        return (
            "$task-router",
            [
                "Treat this as a blocked boundary, not implementation work.",
                "Do not read `.env*`, reveal secrets, or modify `live/`.",
                "Explain the boundary in plain language and offer a safe alternative if one exists.",
            ],
            "Prompt requests a forbidden boundary.",
        )

    direct_skill = re.search(
        r"\$(task-router|verify|qa|commit|save-session|handoff|snapshot|diagnose|review|quick-check|product-design)\b",
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

    if any(word in normalized for word in ("push", "deploy", "release", "merge", "pull request", " pr ")):
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
        ok, details = koda_health_check(write=True)
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
        return koda_direct_cli("memory_store", arguments)

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
                    "Workflow automation is active. For non-trivial prompts, the UserPromptSubmit hook will select the required Codex workflow skill.",
                    "Available skills: $task-router, $product-design, $verify, $qa, $commit, $save-session, $handoff, $snapshot, $diagnose, $review.",
                    "Default implementation path: $task-router -> $verify -> $qa -> $review -> $commit -> $save-session. Product-design path: $product-design -> PRD/UX/build prompts -> implementation approval.",
                ]
            ),
        )
        return 0

    if event == "UserPromptSubmit":
        prompt = str(payload.get("prompt") or "")
        skill, actions, reason = classify_prompt(prompt)
        if not skill:
            return 0
        action_text = "\n".join(f"- {action}" for action in actions)
        memory_skills = {"$task-router", "$product-design", "$diagnose", "$verify", "$qa", "$review", "$commit"}
        memory_text = koda_context(prompt, project) if skill in memory_skills else ""
        memory_section = memory_text or "\n".join(
            [
                "Relevant Koda memories: none injected.",
                "Koda startup health should have caught this. Before non-trivial work, run `python3 scripts/agent-checks/codex-lifecycle-hook.py --check-koda` from the umbrella root and repair Koda if it fails.",
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
