#!/usr/bin/env python3
"""Decision-layer CLI (build item 2).

Reads a single JSON request from standard input, writes a single JSON
response to standard output. Bad input (unparseable JSON, or JSON that
fails schema validation) prints a small JSON error object to stdout and
exits non-zero, so a caller can always `json.loads()` the output whether
the call succeeded or not.

No provider is dispatched to except the ones named in config (default:
"fake"). Nothing here ever calls a paid or live provider unless the
caller explicitly configures one and supplies its credentials.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import config as config_module  # noqa: E402
import engine  # noqa: E402
import schema  # noqa: E402

_MAX_INPUT_BYTES = 1024 * 1024  # 1 MiB is generous for a single decision request.


def _read_request() -> dict:
    raw = sys.stdin.buffer.read(_MAX_INPUT_BYTES + 1)
    if len(raw) > _MAX_INPUT_BYTES:
        raise ValueError("request:oversized")
    return json.loads(raw)


def _load_config_overrides(config_path: str | None) -> dict:
    if not config_path:
        return {}
    with open(config_path, encoding="utf-8") as handle:
        overrides = json.load(handle)
    if not isinstance(overrides, dict):
        raise ValueError("config:object_required")
    return overrides


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Decision-layer CLI: JSON in on stdin, JSON out on stdout.")
    parser.add_argument("--config", dest="config_path", default=None, help="Optional path to a JSON config overrides file.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        overrides = _load_config_overrides(args.config_path)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema_version": schema.SCHEMA_VERSION, "error": "invalid_config", "detail": str(exc)}))
        return 2

    try:
        request = _read_request()
    except (ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"schema_version": schema.SCHEMA_VERSION, "error": "invalid_json", "detail": str(exc)}))
        return 2

    errors = schema.validate_request(request)
    if errors:
        print(json.dumps({"schema_version": schema.SCHEMA_VERSION, "error": "invalid_request", "detail": errors}))
        return 2

    config = config_module.load_config(overrides=overrides)
    response = engine.decide(request, config=config)
    print(json.dumps(response))
    return 0


if __name__ == "__main__":
    sys.exit(main())
