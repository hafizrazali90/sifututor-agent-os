#!/usr/bin/env python3
"""Mac-side wrapper for the home PC release readiness loop (issue #350).

    pc_release.py start READINESS.json [--dry-run]   copy to the PC and start the loop
    pc_release.py status RELEASE_ID                  PC readiness, Hafiz gates, loop state
    pc_release.py report RELEASE_ID                  the release report, once the loop has stopped
    pc_release.py file RELEASE_ID PATH               one file from the release folder, e.g. release-pack/11-review-page.md
    pc_release.py stop RELEASE_ID                    ask the loop to stop after its current action
    pc_release.py resume RELEASE_ID                  start a stopped, blocked or stuck release again
    pc_release.py list                               releases on the PC and their loop state

The loop runs on the PC (release_loop.py). It is started through Windows Task
Scheduler exactly as pc_job.py starts a job, because WSL kills detached
processes. It reuses the pc_job.py helpers instead of copying them.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pc_job  # noqa: E402
import release_readiness as rr  # noqa: E402

FOLDER = "releases"
TASK_PREFIX = "release"
CODE_FILES = ("release_loop.py", "release_readiness.py", "pc_job.py", "job_brief.py", "render-claude-settings.py")
ID_RE = re.compile(r"[0-9]{8}-[0-9]{6}-[a-z0-9-]+")
SAFE_PATH_RE = re.compile(r"[A-Za-z0-9._-]+(/[A-Za-z0-9._-]+)*")


def check_id(release_id: str) -> str:
    if not ID_RE.fullmatch(release_id):
        raise ValueError("release id looks wrong")
    return release_id


def start_sh(release_id: str) -> str:
    return (
        "#!/bin/sh\n"
        f'cd "{pc_job.PC_HOME}/{FOLDER}/{release_id}" || exit 1\n'
        f'python3 release_loop.py run readiness.json --clear-stop --drop-task "{TASK_PREFIX}-{release_id}" >> loop.log 2>&1\n'
    )


def code_files(release_id: str) -> dict[str, str]:
    files = {name: (HERE / name).read_text() for name in CODE_FILES}
    files["role.txt"] = pc_job.role_text()
    files["settings.template.json"] = (HERE.parents[1] / ".claude" / "settings.template.json").read_text()
    files["start.sh"] = start_sh(release_id)
    return files


def start(readiness_path: Path, *, dry_run: bool = False, runner=subprocess.run, out=print) -> int:
    try:
        data = rr.load(readiness_path)
    except rr.ReadinessError as exc:
        out(f"REFUSED: {exc}")
        return 2
    errors = rr.validate(data)
    if errors:
        out("REFUSED: the readiness file has problems:")
        for error in errors:
            out(f"  - {error}")
        return 2
    release_id = pc_job.make_job_id(data["release"])
    files = {"readiness.json": readiness_path.read_text(), **code_files(release_id)}
    s = rr.score(data)
    out(f"Release {release_id}: {data['release']} ({data['repo']}, branch {data['branch']})")
    out(f"  PC readiness now {s['percent']}% ({s['pc_green']} of {s['pc_total']} PC items); {len(s['gates'])} gates stay with you")
    out("  the loop never merges, deploys, migrates or writes production data")
    out("  no caps: it runs until ready, blocked, stuck or stopped")
    for item in data["items"]:
        reason = rr.forbidden_in_item(item) if rr.is_pc_item(item) else None
        if reason:
            out(f"  note: item {item['id']} would be handed to you at once ({reason})")
    if not data.get("approval"):
        out("  note: no approval line, so fix commits will stay on the PC and not be pushed")
    if dry_run:
        out("DRY RUN: nothing was sent to the PC.")
        return 0
    pc_job.run_ssh(pc_job.install_script(release_id, files, folder=FOLDER), runner=runner)
    pc_job.run_ssh(None, command=pc_job.schtasks_create(release_id, folder=FOLDER, prefix=TASK_PREFIX), runner=runner)
    out(f"Started {release_id} on the PC. Check with: pc_release.py status {release_id}")
    return 0


def resume(release_id: str, *, runner=subprocess.run, out=print) -> int:
    check_id(release_id)
    pc_job.run_ssh(pc_job.install_script(release_id, code_files(release_id), folder=FOLDER), runner=runner)
    pc_job.run_ssh(None, command=pc_job.schtasks_create(release_id, folder=FOLDER, prefix=TASK_PREFIX), runner=runner)
    out(f"Resumed {release_id}: the loop continues from its checkpoint.")
    return 0


def status(release_id: str, *, runner=subprocess.run) -> str:
    check_id(release_id)
    script = (
        f'cd "$HOME/{FOLDER}/{release_id}" 2>/dev/null || {{ echo "no such release"; exit 1; }}\n'
        "python3 release_readiness.py score readiness.json\n"
        '[ -f ready.flag ] && echo "ready.flag is present: READY FOR YOUR GO"\n'
        '[ -f STOP ] && echo "STOP file is present"\n'
        'echo "--- last log lines"; tail -n 6 loop.log 2>/dev/null\n'
    )
    return pc_job.run_ssh(script, runner=runner)


def read_file(release_id: str, name: str, *, runner=subprocess.run) -> str:
    check_id(release_id)
    if not SAFE_PATH_RE.fullmatch(name) or ".." in name.split("/"):
        raise ValueError("path looks wrong")
    return pc_job.run_ssh(f'cat "$HOME/{FOLDER}/{release_id}/{name}" 2>&1\n', runner=runner)


def stop(release_id: str, *, runner=subprocess.run) -> str:
    check_id(release_id)
    pc_job.run_ssh(f'touch "$HOME/{FOLDER}/{release_id}/STOP"\n', runner=runner)
    return f"STOP file created for {release_id}. The loop stops after the action it is running."


def list_releases(*, runner=subprocess.run) -> str:
    script = (
        f'for d in "$HOME"/{FOLDER}/*/; do [ -f "$d/readiness.json" ] || continue; '
        'printf "%s  " "$(basename "$d")"; '
        "python3 -c \"import json,sys; d=json.load(open(sys.argv[1])); l=d.get('loop',{}); print(l.get('status','new'), l.get('rounds',0),'rounds')\" \"$d/readiness.json\"; done\n"
    )
    return pc_job.run_ssh(script, runner=runner)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("start"); p.add_argument("readiness", type=Path); p.add_argument("--dry-run", action="store_true")
    for name in ("status", "report", "stop", "resume"):
        p = sub.add_parser(name); p.add_argument("release_id")
    p = sub.add_parser("file"); p.add_argument("release_id"); p.add_argument("path")
    sub.add_parser("list")
    args = parser.parse_args(argv)
    if args.cmd == "start":
        return start(args.readiness, dry_run=args.dry_run)
    if args.cmd == "status":
        print(status(args.release_id))
    elif args.cmd == "report":
        print(read_file(args.release_id, "release-report.md"))
    elif args.cmd == "file":
        print(read_file(args.release_id, args.path))
    elif args.cmd == "stop":
        print(stop(args.release_id))
    elif args.cmd == "resume":
        return resume(args.release_id)
    elif args.cmd == "list":
        print(list_releases())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
