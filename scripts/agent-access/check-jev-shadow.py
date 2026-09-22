#!/usr/bin/env python3
"""Report Jev shadow readiness without printing credential material."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys
import tempfile

CHECKS = Path(__file__).resolve().parents[1] / "agent-checks"
sys.path.insert(0, str(CHECKS))

import agent_os_jev_shadow as shadow  # noqa: E402
import provider_jev  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true", help="Run one small non-sensitive provider canary.")
    args = parser.parse_args()

    environment = shadow.provider_environment()
    provider = provider_jev.JevProvider(config=shadow.shadow_config(), env=environment)
    configured = provider.is_configured()
    dependencies = provider.dependencies_available()
    print(f"JEV credential configured: {'yes' if configured else 'no'}")
    print(f"JEV SDK ready: {'yes' if dependencies else 'no'}")
    print("JEV mode: shadow advisory; never authoritative")
    if not configured or not dependencies:
        return 1
    if args.live:
        with tempfile.TemporaryDirectory() as tmp:
            advice = shadow.observe_prompt(
                "Review this small documentation-only change",
                project="sifututor",
                state_dir=Path(tmp),
                provider=provider,
            )
        print(f"JEV live canary: {'passed' if advice else 'failed safely'}")
        return 0 if advice else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
