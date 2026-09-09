#!/usr/bin/env python3
"""Validate the portable and installed Kilo Code Agent OS adapter."""

from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import subprocess
import tempfile
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
    "reported symptom",
    "Reading files",
    "behavioral parity contract",
    "agent-os-live-evidence-report.py",
    "Different wording is fine",
    "text-only",
    '"zai-vision_*": ask',
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


def validate_config(config_path: Path) -> None:
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot read Kilo config safely: {exc}")

    provider = config.get("provider", {}).get("zai", {})
    if "glm-5.3" not in provider.get("models", {}):
        fail("configured provider zai does not expose glm-5.3")

    image_models = [
        model_id
        for model_id, model in provider.get("models", {}).items()
        if "image" in model.get("modalities", {}).get("input", [])
    ]
    if image_models:
        fail(
            "Z.ai Coding Plan chat/completions must be text-only; "
            f"remove image input from: {', '.join(sorted(image_models))}"
        )

    vision_mcp = config.get("mcp", {}).get("zai-vision", {})
    command = vision_mcp.get("command", [])
    if vision_mcp.get("type") != "local" or vision_mcp.get("enabled") is not True:
        fail("zai-vision MCP is not enabled as a local server")
    if any(key in vision_mcp for key in ("environment", "env", "headers")):
        fail("zai-vision MCP must not embed credentials in Kilo config")
    if not isinstance(command, list) or len(command) != 1:
        fail("zai-vision MCP must use one machine-local wrapper command")
    wrapper = Path(command[0]).expanduser()
    if not wrapper.is_file() or not os.access(wrapper, os.X_OK):
        fail(f"zai-vision MCP wrapper is missing or not executable: {wrapper}")
    if wrapper.stat().st_mode & 0o077:
        fail(f"zai-vision MCP wrapper permissions are too broad: {wrapper}")


def find_kilo_cli() -> Path | None:
    executable = shutil.which("kilo")
    if executable:
        return Path(executable)

    candidates = sorted(
        (Path.home() / ".vscode" / "extensions").glob(
            "kilocode.kilo-code-*/bin/kilo"
        ),
        reverse=True,
    )
    return candidates[0] if candidates else None


def validate_installed(repo_text: str, installed_agent: Path, config_path: Path) -> None:
    installed_text = validate_agent(installed_agent)
    if installed_text != repo_text:
        fail(f"installed agent differs from {REPO_AGENT}")

    validate_config(config_path)

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

    kilo_cli = find_kilo_cli()
    if kilo_cli is None or not os.access(kilo_cli, os.X_OK):
        fail("Kilo CLI is not available on PATH or inside the VS Code extension")

    agent_list = subprocess.run(
        [str(kilo_cli), "agent", "list"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if (
        agent_list.returncode != 0
        or "sifututor-agent-os (primary)" not in agent_list.stdout
    ):
        fail("installed Kilo runtime does not discover sifututor-agent-os as a primary agent")

    mcp_list = subprocess.run(
        [str(kilo_cli), "mcp", "list"],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if (
        mcp_list.returncode != 0
        or "zai-vision" not in mcp_list.stdout
        or "connected" not in mcp_list.stdout
    ):
        fail("installed Kilo runtime does not report zai-vision as connected")


def expect_failure(label: str, action, expected: str) -> bool:
    try:
        action()
    except SystemExit as exc:
        message = str(exc)
        if expected in message:
            print(f"PASS {label}")
            return True
        print(f"FAIL {label}: expected {expected!r}, got {message!r}")
        return False
    print(f"FAIL {label}: unsafe fixture unexpectedly passed")
    return False


def run_self_test() -> int:
    print("Kilo Agent OS adapter checker self-test")
    outcomes: list[bool] = []
    repo_text = REPO_AGENT.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as temp_dir:
        root = Path(temp_dir)
        agent_path = root / "agent.md"
        agent_path.write_text(repo_text, encoding="utf-8")
        outcomes.append(validate_agent(agent_path) == repo_text)
        print("PASS complete agent fixture" if outcomes[-1] else "FAIL complete agent fixture")

        missing_marker = root / "missing-marker.md"
        missing_marker.write_text(
            repo_text.replace("reported symptom", "unconfirmed report"),
            encoding="utf-8",
        )
        outcomes.append(
            expect_failure(
                "missing behavior marker is rejected",
                lambda: validate_agent(missing_marker),
                "reported symptom",
            )
        )

        embedded_endpoint = root / "embedded-endpoint.md"
        embedded_endpoint.write_text(repo_text + "\napi.z.ai\n", encoding="utf-8")
        outcomes.append(
            expect_failure(
                "embedded provider endpoint is rejected",
                lambda: validate_agent(embedded_endpoint),
                "provider credentials or endpoints",
            )
        )

        wrapper = root / "zai-vision-mcp"
        wrapper.write_text("#!/bin/sh\n", encoding="utf-8")
        wrapper.chmod(0o700)
        base_config = {
            "provider": {
                "zai": {
                    "models": {
                        "glm-5.3": {"modalities": {"input": ["text"]}},
                    }
                }
            },
            "mcp": {
                "zai-vision": {
                    "type": "local",
                    "enabled": True,
                    "command": [str(wrapper)],
                }
            },
        }

        def write_config(name: str, payload: dict) -> Path:
            path = root / name
            path.write_text(json.dumps(payload), encoding="utf-8")
            return path

        valid_config = write_config("valid.json", base_config)
        validate_config(valid_config)
        outcomes.append(True)
        print("PASS safe text-only config fixture")

        image_config = copy.deepcopy(base_config)
        image_config["provider"]["zai"]["models"]["glm-5.3"]["modalities"]["input"].append("image")
        outcomes.append(
            expect_failure(
                "image chat modality is rejected",
                lambda: validate_config(write_config("image.json", image_config)),
                "text-only",
            )
        )

        auth_config = copy.deepcopy(base_config)
        auth_config["mcp"]["zai-vision"]["environment"] = {"TOKEN": "synthetic"}
        outcomes.append(
            expect_failure(
                "embedded MCP auth is rejected",
                lambda: validate_config(write_config("auth.json", auth_config)),
                "must not embed credentials",
            )
        )

        missing_model = copy.deepcopy(base_config)
        missing_model["provider"]["zai"]["models"] = {}
        outcomes.append(
            expect_failure(
                "missing GLM-5.3 model is rejected",
                lambda: validate_config(write_config("missing-model.json", missing_model)),
                "does not expose glm-5.3",
            )
        )

    passed = sum(outcomes)
    total = len(outcomes)
    print(f"Kilo Agent OS adapter checker self-test: {passed}/{total} passed")
    return 0 if passed == total else 1


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--installed", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--installed-agent", type=Path, default=DEFAULT_INSTALLED_AGENT)
    parser.add_argument("--config", type=Path, default=DEFAULT_KILO_CONFIG)
    args = parser.parse_args()

    if args.self_test:
        return run_self_test()

    repo_text = validate_agent(REPO_AGENT)
    if args.installed:
        validate_installed(repo_text, args.installed_agent, args.config)
        print("PASS Kilo Agent OS adapter: repo and installed GLM setup match")
    else:
        print("PASS Kilo Agent OS adapter: portable definition is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
