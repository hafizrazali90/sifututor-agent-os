#!/usr/bin/env python3
"""Live, provider-neutral Jev routing assistant for Agent OS prompts.

The default assist mode contributes one bounded routing signal to Claude and
Codex. It never changes approval state, runs a tool, overrides deterministic
safety, or persists prompt/response bodies. Provider failure leaves normal
routing intact. A legacy shadow mode remains available for observation-only
rollbacks.
"""

from __future__ import annotations

import fcntl
import json
import os
from datetime import date
from pathlib import Path
import stat
import sys

HERE = Path(__file__).resolve().parent
DECISION_LAYER = HERE / "decision-layer"
ROUTING = DECISION_LAYER / "routing"
for path in (DECISION_LAYER, ROUTING):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

import config as decision_config  # noqa: E402
import provider_jev  # noqa: E402
import shadow_router  # noqa: E402

MIN_PROMPT_LEN = 10
CONF_PATH = Path.home() / ".config" / "sifututor" / "agent-access" / "typesafe-jev.conf"
STATE_DIR = Path.home() / ".local" / "state" / "sifututor-agent-os" / "jev-shadow"


def _mode(env: dict[str, str]) -> str:
    """Resolve off/shadow/assist without breaking the old disable switch."""
    explicit = env.get("SIFUTUTOR_JEV_MODE", "").strip().lower()
    if explicit in {"0", "false", "off", "no", "disabled"}:
        return "off"
    if explicit == "shadow":
        return "shadow"
    if explicit == "assist":
        return "assist"
    if explicit:
        return "shadow"
    if env.get("SIFUTUTOR_JEV_SHADOW", "1").strip().lower() in {"0", "false", "off", "no"}:
        return "off"
    return "assist"


def _credential_from_file(path: Path = CONF_PATH) -> str:
    """Read only TYPESAFE_API_KEY from an owner-only scoped conf file."""
    try:
        if stat.S_IMODE(path.stat().st_mode) & 0o077:
            return ""
        for raw_line in path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            if key.strip().removeprefix("export ").strip() == "TYPESAFE_API_KEY":
                return value.strip().strip('"').strip("'")
    except OSError:
        return ""
    return ""

def provider_environment(env: dict[str, str] | None = None, conf_path: Path = CONF_PATH) -> dict[str, str]:
    source = dict(os.environ if env is None else env)
    key = source.get("TYPESAFE_API_KEY", "") or _credential_from_file(conf_path)
    result = {"PATH": source.get("PATH", "")}
    if key:
        result["TYPESAFE_API_KEY"] = key
    return result


def shadow_config(env: dict[str, str] | None = None) -> dict[str, object]:
    config = decision_config.load_config(env=os.environ if env is None else env)
    config.update(
        {
            "provider": "jev",
            # Live canaries on this machine complete around 1.5 seconds. Keep
            # one bounded attempt with enough headroom, rather than retrying a
            # deadline that is shorter than normal provider latency.
            "timeout_s": 3.0,
            "max_retries": 0,
            "authoritative_decision_types": [],
        }
    )
    return config


def _record_metrics(observation: dict, *, state_dir: Path = STATE_DIR) -> None:
    """Update one daily aggregate. No prompt, answer, reason, or context is stored."""
    state_dir.mkdir(parents=True, exist_ok=True, mode=0o700)
    day = date.today().isoformat()
    path = state_dir / f"{day}.json"
    with (state_dir / ".lock").open("a", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            payload = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
        except (OSError, json.JSONDecodeError):
            payload = {}
        payload.setdefault("schema_version", 1)
        payload["date"] = day
        payload["total"] = int(payload.get("total", 0)) + 1
        outcome = str(observation.get("outcome") or "unknown")
        outcomes = payload.setdefault("outcomes", {})
        outcomes[outcome] = int(outcomes.get(outcome, 0)) + 1
        payload["network_calls"] = int(payload.get("network_calls", 0)) + int(observation.get("network_calls", 0))
        payload["fallbacks"] = int(payload.get("fallbacks", 0)) + int(bool(observation.get("fallback_used")))
        payload["critical_local_only"] = int(payload.get("critical_local_only", 0)) + int(
            bool(observation.get("critical_local_only"))
        )
        payload["latency_ms_total"] = round(
            float(payload.get("latency_ms_total", 0.0)) + float(observation.get("latency_ms", 0.0)), 3
        )
        temporary = path.with_suffix(f".{os.getpid()}.tmp")
        temporary.write_text(json.dumps(payload, sort_keys=True) + "\n", encoding="utf-8")
        os.chmod(temporary, 0o600)
        temporary.replace(path)


def observe_prompt(
    prompt: str,
    *,
    project: str | None = None,
    env: dict[str, str] | None = None,
    conf_path: Path = CONF_PATH,
    state_dir: Path = STATE_DIR,
    provider: object | None = None,
) -> str:
    """Return compact advisory hook context, or empty text on a safe fallback."""
    runtime_env = dict(os.environ if env is None else env)
    mode = _mode(runtime_env)
    if mode == "off" or len((prompt or "").strip()) < MIN_PROMPT_LEN:
        return ""
    try:
        config = shadow_config(runtime_env)
        active_provider = provider or provider_jev.JevProvider(
            config=config, env=provider_environment(runtime_env, conf_path)
        )
        result = shadow_router.route(prompt, declared_project=project, provider=active_provider, config=config)
        observed = result["observability"]
        _record_metrics(
            {
                "outcome": observed.get("outcome"),
                "network_calls": getattr(active_provider, "network_call_count", 0),
                "fallback_used": observed.get("fallback_used"),
                "critical_local_only": result["risk_level"].get("forced", False),
                "latency_ms": observed.get("latency_ms") or 0.0,
            },
            state_dir=state_dir,
        )
        if (
            result.get("provider_called")
            and observed.get("provider") == "jev"
            and observed.get("outcome") == "ok"
            and not observed.get("fallback_used")
        ):
            route = result["workflow_route"]["value"]
            confidence = float(result["workflow_route"].get("confidence") or 0.0)
            if mode == "shadow":
                return (
                    f"Jev shadow advisory: workflow route {route} (confidence {confidence:.2f}). "
                    "This is advisory only; deterministic safety, repository rules, and trusted "
                    "approval state remain authoritative."
                )
            return (
                f"Jev routing assist: suggested workflow route {route} (confidence {confidence:.2f}). "
                "Use this as one bounded routing signal when it fits the current task evidence. "
                "Deterministic safety, repository rules, and trusted approval state remain "
                "authoritative; this suggestion cannot approve or execute actions."
            )
    except Exception:
        return ""
    return ""
