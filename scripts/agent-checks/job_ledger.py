#!/usr/bin/env python3
"""A small ledger of which machine, account and AI ran each job.

The Session Map page shows a Jobs list with machine, account and AI. The PC
runner (pc_job.py) writes its own entry when it starts a job. A job launched on
the Mac under another account records itself with:

  python3 scripts/agent-checks/job_ledger.py record --name "CRM build job 4" \\
      --machine Mac --account sthafizrazali --ai Claude --state running
  python3 scripts/agent-checks/job_ledger.py record --name "CRM build job 4" \\
      --machine Mac --account sthafizrazali --ai Claude --state done

  python3 scripts/agent-checks/job_ledger.py json [--since-hours 24]
prints the rows to put in the page's `jobs` field.

States: queued, running, done, failed. The page has only its own six state
words, so queued shows as Not started, running as Discussing and done as Done,
and a failed job shows as Done with "(failed)" after its name.
Agreed with Hafiz on 17/10/2026.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import time

STATE_TO_PAGE = {"queued": "todo", "running": "discussing", "done": "done", "failed": "done"}


def jobs_dir() -> Path:
    override = os.environ.get("AGENT_OS_JOBS_DIR")
    return Path(override) if override else Path.home() / ".agent-os" / "jobs"


def record(name: str, machine: str, account: str, ai: str, state: str = "running", now: float | None = None) -> bool:
    """Append one entry. Returns False, never raises, so a job is never held up by its record."""
    fields = [str(value).strip() for value in (name, machine, account, ai)]
    if not all(fields) or state not in STATE_TO_PAGE:
        return False
    entry = {"at": time.time() if now is None else now, "name": fields[0], "machine": fields[1], "account": fields[2], "ai": fields[3], "state": state}
    try:
        directory = jobs_dir()
        directory.mkdir(parents=True, exist_ok=True)
        with (directory / "jobs.jsonl").open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        return False
    return True


def rows(since_hours: float | None = None, now: float | None = None) -> list[dict]:
    moment = time.time() if now is None else now
    try:
        lines = (jobs_dir() / "jobs.jsonl").read_text(encoding="utf-8").splitlines()
    except OSError:
        return []
    latest: dict[str, dict] = {}
    for line in lines:
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if not isinstance(entry, dict) or entry.get("state") not in STATE_TO_PAGE or not entry.get("name"):
            continue
        latest[str(entry["name"])] = entry  # the last entry for a name wins, and the first one fixes its place
    result = []
    for name, entry in latest.items():
        if since_hours is not None and moment - float(entry.get("at") or 0) > since_hours * 3600:
            continue
        result.append(
            {
                "n": f"{name} (failed)" if entry["state"] == "failed" else name,
                "where": str(entry.get("machine") or ""),
                "acct": str(entry.get("account") or ""),
                "ai": str(entry.get("ai") or ""),
                "s": STATE_TO_PAGE[entry["state"]],
            }
        )
    return result


def _arg(argv: list[str], flag: str, default: str = "") -> str:
    return argv[argv.index(flag) + 1] if flag in argv and argv.index(flag) + 1 < len(argv) else default


def main(argv: list[str]) -> int:
    command = argv[0] if argv else ""
    if command == "record":
        ok = record(_arg(argv, "--name"), _arg(argv, "--machine"), _arg(argv, "--account"), _arg(argv, "--ai"), _arg(argv, "--state", "running"))
        print("recorded" if ok else "not recorded: give --name, --machine, --account, --ai and a state of queued, running, done or failed")
        return 0 if ok else 2
    if command == "json":
        hours = _arg(argv, "--since-hours")
        print(json.dumps(rows(float(hours) if hours else None), indent=2, ensure_ascii=False))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
