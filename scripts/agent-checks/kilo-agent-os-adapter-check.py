#!/usr/bin/env python3
"""Validate the portable and installed Kilo Code Agent OS adapter."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
REPO_AGENT = ROOT / ".kilo" / "agents" / "sifututor-agent-os.md"
DEFAULT_INSTALLED_AGENT = Path.home() / ".config" / "kilo" / "agent" / "sifututor-agent-os.md"
DEFAULT_KILO_CONFIG = Path.home() / ".config" / "kilo" / "kilo.jsonc"

REQUIRED_AGENT_MARKERS = (
    "mode: primary",
    "model: zai/glm-5.3",
    "AGENTS.md",
    ".agents/skills/",
    "scripts/agent-checks/koda search",
    "scripts/agent-checks/pre-commit-guard.sh",
    "critical lane",
    ".env",
    "live/",
)


def fail(message: str) -> None:
    raise SystemExit(f"FAIL Kilo Agent OS adapter: {message}")


def validate_agent(path: Path) -> str:
    if not path.is_file():
        fail(f"missing {path}")
    text = path.read_text(encoding="utf-8")
    missing = [marker for marker in REQUIRED_AGENT_MARKERS if marker not in text]
    if missing:
        fail(f"{path} missing markers: {', '.join(missing)}")
    if "ANTHROPIC_AUTH_TOKEN" in text or "api.z.ai" in text:
        fail(f"{path} must not carry provider credentials or endpoints")
    return text


def validate_installed(repo_text: str, installed_agent: Path, config_path: Path) -> None:
    installed_text = validate_agent(installed_agent)
    if installed_text != repo_text:
        fail(f"installed agent differs from {REPO_AGENT}")

    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read Kilo config safely: {exc}")

    provider = config.get("provider", {}).get("zai", {})
    if "glm-5.3" not in provider.get("models", {}):
        fail("configured provider zai does not expose glm-5.3")

    # Kilo may keep provider credentials in VS Code's encrypted secret storage
    # rather than its JSON config. Validate the provider/model wiring here and
    # leave credential proof to a live request so this check never reads or
    # prints a secret.

    try:
        extensions = subprocess.run(
            ["code", "--list-extensions", "--show-versions"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.lower()
    except (OSError, subprocess.CalledProcessError) as exc:
        fail(f"cannot inspect VS Code extensions: {exc}")
    if "kilocode.kilo-code@" not in extensions:
        fail("Kilo Code VS Code extension is not installed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--installed", action="store_true")
    parser.add_argument("--installed-agent", type=Path, default=DEFAULT_INSTALLED_AGENT)
    parser.add_argument("--config", type=Path, default=DEFAULT_KILO_CONFIG)
    args = parser.parse_args()

    repo_text = validate_agent(REPO_AGENT)
    if args.installed:
        validate_installed(repo_text, args.installed_agent, args.config)
        print("PASS Kilo Agent OS adapter: repo and installed GLM setup match")
    else:
        print("PASS Kilo Agent OS adapter: portable definition is valid")


if __name__ == "__main__":
    main()
