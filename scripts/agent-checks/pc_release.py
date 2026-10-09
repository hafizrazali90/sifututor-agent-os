#!/usr/bin/env python3
"""Mac-side wrapper for the home PC release readiness loop (issue #350).

    pc_release.py start READINESS.json [--dry-run]   copy to the PC and start the loop
    pc_release.py status RELEASE_ID                  PC readiness, Hafiz gates, loop state
    pc_release.py report RELEASE_ID                  the release report, once the loop has stopped
    pc_release.py file RELEASE_ID PATH               one file from the release folder, e.g. release-pack/11-review-page.md
    pc_release.py gate READINESS|RELEASE_ID ITEM --evidence "text or path" [--sha SHA] [--simulated]
                                                     close a gate (mac or hafiz item) with evidence
    pc_release.py route READINESS|RELEASE_ID direct-prod|staging-first
                                                     change the route; applicability is recomputed
    pc_release.py stop RELEASE_ID                    ask the loop to stop after its current action
    pc_release.py resume RELEASE_ID                  start a stopped, blocked or stuck release again
    pc_release.py clean RELEASE_ID                   remove the finished release's Task Scheduler task (the folder stays)
    pc_release.py list                               releases on the PC and their loop state
    pc_release.py deploy-status RELEASE_ID           the staging gates S1 to S4 of a release and the live state of its staging deploy
    pc_release.py staging-switch ripple|sims on|off|show
                                                     the STOP switch on a staging box (off = unattended deploys refused)

The loop runs on the PC (release_loop.py). It is started through Windows Task
Scheduler exactly as pc_job.py starts a job, because WSL kills detached
processes. It reuses the pc_job.py helpers instead of copying them.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shlex
import re
import subprocess
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import pc_job  # noqa: E402
import release_readiness as rr  # noqa: E402

FOLDER = "releases"
TASK_PREFIX = "release"
CODE_FILES = ("release_loop.py", "release_readiness.py", "pc_job.py", "job_brief.py", "render-claude-settings.py",
              "staging_deploy.py", "staging_remote.py")
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
    data["release_id"] = release_id
    files = {"readiness.json": json.dumps(data, indent=2, ensure_ascii=False) + "\n", **code_files(release_id)}
    s = rr.score(data)
    out(f"Release {release_id}: {data['release']} ({data['repo']}, branch {data['branch']})")
    out(f"  route {data.get('route')}")
    out(f"  PC readiness now {s['percent']}% ({s['pc_green']} of {s['pc_total']} PC items), "
        f"Prod readiness {s['prod_percent']}% ({s['prod_green']} of {s['prod_total']} items before your production go)")
    out(f"  {len([g for g in s['gates'] if g['applicable'] and not g['after_go'] and g['status'] != 'green'])} gates before your go are yours to close "
        "(pc_release.py gate); the loop waits for them and carries on by itself")
    if data.get("staging"):
        cfg = data["staging"]
        out(f"  the loop never merges, never deploys production, never migrates or writes production data; it deploys STAGING only "
            f"({cfg.get('target')}, mode {cfg.get('mode', 'normal')}) through staging_deploy.py: {cfg.get('approval', '')}")
    else:
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
    rr.save(readiness_path, data)  # the local copy now carries the release id, so gate and route can find the release
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
        '[ -f ready.flag ] && echo "ready.flag is present: READY FOR YOUR GO (production deploy)"\n'
        '[ -f STOP ] && echo "STOP file is present"\n'
        'ls inbox/*.json >/dev/null 2>&1 && echo "requests are queued in inbox/"\n'
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


def resolve_id(target: str) -> str:
    """A release id, or the path of the local readiness file that start stamped with it."""
    if ID_RE.fullmatch(target):
        return target
    try:
        release_id = rr.load(target).get("release_id", "")
    except rr.ReadinessError as exc:
        raise ValueError(str(exc)) from exc
    if not release_id:
        raise ValueError("this readiness file was never started, so it has no release id; use the id that start printed")
    return check_id(release_id)


def remote_readiness(release_id: str, subcommand: str, args: list[str], *, runner=subprocess.run) -> str:
    check_id(release_id)
    command = " ".join(shlex.quote(a) for a in ["python3", "release_readiness.py", subcommand, "readiness.json", *args])
    return pc_job.run_ssh(f'cd "$HOME/{FOLDER}/{release_id}" || exit 1\n{command}\n', runner=runner)


def gate(target: str, item: str, evidence: str, *, by: str = "Hafiz", sha: str = "", simulated: bool = False,
         runner=subprocess.run) -> str:
    args = [item, "--evidence", evidence, "--by", by]
    if sha:
        args += ["--sha", sha]
    if simulated:
        args.append("--simulated")
    return remote_readiness(resolve_id(target), "gate", args, runner=runner)


def route(target: str, new_route: str, *, by: str = "Hafiz", runner=subprocess.run) -> str:
    if new_route not in rr.ROUTES:
        raise ValueError("route must be one of " + ", ".join(rr.ROUTES))
    return remote_readiness(resolve_id(target), "route", [new_route, "--by", by], runner=runner)


def clean(release_id: str, *, runner=subprocess.run) -> str:
    """Remove the Task Scheduler task of a finished release. A task cannot reliably delete itself from inside WSL."""
    check_id(release_id)
    out = pc_job.run_ssh(None, command=f'schtasks /delete /tn "{TASK_PREFIX}-{release_id}" /f', runner=runner)
    return out.strip() or "done"


def deploy_status(release_id: str, *, runner=subprocess.run) -> str:
    """The staging gates of a release (S1 to S4), what was deployed, and what the box says now."""
    check_id(release_id)
    return pc_job.run_ssh(f'cd "$HOME/{FOLDER}/{release_id}" || exit 1\npython3 staging_deploy.py report readiness.json\n', runner=runner)


def staging_switch(target: str, action: str, *, shell=None) -> str:
    """The STOP switch on a staging box, from the Mac (its own ssh aliases). `off` makes the box refuse unattended deploys."""
    import staging_deploy
    if target not in staging_deploy.sr.TARGETS:
        raise ValueError("target must be one of " + ", ".join(staging_deploy.sr.TARGETS))
    try:
        return staging_deploy.Deployer(target, shell or rr.RealShell(), actor="mac-switch").switch(action)
    except staging_deploy.DeployError as exc:
        raise ValueError(str(exc)) from exc


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
    p = sub.add_parser("deploy-status"); p.add_argument("release_id")
    p = sub.add_parser("staging-switch"); p.add_argument("target", choices=("ripple", "sims")); p.add_argument("action", choices=("on", "off", "show"))
    p = sub.add_parser("clean"); p.add_argument("release_id")
    p = sub.add_parser("gate"); p.add_argument("target"); p.add_argument("item"); p.add_argument("--evidence", required=True)
    p.add_argument("--by", default="Hafiz"); p.add_argument("--sha", default=""); p.add_argument("--simulated", action="store_true")
    p = sub.add_parser("route"); p.add_argument("target"); p.add_argument("new_route", choices=rr.ROUTES); p.add_argument("--by", default="Hafiz")
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
    elif args.cmd == "deploy-status":
        print(deploy_status(args.release_id))
    elif args.cmd == "staging-switch":
        print(staging_switch(args.target, args.action))
    elif args.cmd == "clean":
        print(clean(args.release_id))
    elif args.cmd == "gate":
        print(gate(args.target, args.item, args.evidence, by=args.by, sha=args.sha, simulated=args.simulated))
    elif args.cmd == "route":
        print(route(args.target, args.new_route, by=args.by))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
