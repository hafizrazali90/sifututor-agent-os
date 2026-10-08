#!/usr/bin/env python3
"""Unattended job runner for the home PC (issue #305).

Mac side:
    pc_job.py submit BRIEF.md [--dry-run]   validate, copy to the PC, start the job
    pc_job.py status JOB_ID                 show the job's status file
    pc_job.py result JOB_ID                 show the finished job's result
    pc_job.py list                          list jobs and their states

PC side (started by Windows Task Scheduler through wsl.exe, never by hand):
    pc_job.py run JOB_DIR

Why Task Scheduler and not tmux: WSL2 shuts the Ubuntu machine down when no
Windows-side process is attached, and that kills tmux. A scheduler task keeps a
Windows-side `wsl.exe` alive for the job's whole length.

The runner never merges or deploys. For finish `pr-open` the runner, not
Claude, pushes the branch and opens the pull request after its own checks.
It refuses to start Claude when the hook wiring is missing.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
from pathlib import Path
import re
import shlex
import subprocess
import sys
from zoneinfo import ZoneInfo

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import job_brief  # noqa: E402

MYT = ZoneInfo("Asia/Kuala_Lumpur")
SSH_HOST = "homepc"
PC_USER = "hafiz"
PC_HOME = f"/home/{PC_USER}"
PC_REPO = f"{PC_HOME}/Projects/Sifututor"
PC_CLAUDE = f"{PC_HOME}/.local/bin/claude"
GUARD_HOOK_MIN = 1

TERMINAL = ("done", "failed", "blocked", "timeout")

BUILDER_TOOLS = (
    "Read", "Grep", "Glob", "Edit", "Write",
    "Bash(git status:*)", "Bash(git diff:*)", "Bash(git add:*)", "Bash(git commit:*)",
    "Bash(git log:*)", "Bash(git show:*)", "Bash(ls:*)",
    "Bash(python3 -m unittest:*)",
    "Bash(bash scripts/agent-checks/pre-commit-guard.sh:*)",
    "Bash(python3 scripts/agent-checks/agent-os-doc-navigation-check.py:*)",
)
REVIEWER_TOOLS = (
    "Read", "Grep", "Glob",
    "Bash(git diff:*)", "Bash(git log:*)", "Bash(git show:*)", "Bash(git status:*)", "Bash(ls:*)",
)
REVIEWER_DENIED = ("Edit", "Write", "NotebookEdit")
ROLE_FILES = ("shared-facts.md", "builder.md", "reviewer.md")


# ----------------------------------------------------------------- time ----

def now() -> dt.datetime:
    return dt.datetime.now(dt.timezone.utc)


def myt(moment: dt.datetime) -> str:
    return moment.astimezone(MYT).strftime("%d/%m/%Y %H:%M:%S MYT")


def make_job_id(title: str, moment: dt.datetime | None = None) -> str:
    moment = (moment or now()).astimezone(MYT)
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:30].strip("-") or "job"
    return f"{moment:%Y%m%d-%H%M%S}-{slug}"


# ------------------------------------------------------------- Mac side ----

def clean(text: str) -> str:
    return text.replace("\x00", "").replace("\r", "")


def run_ssh(script: str | None, command: str | None = None, *, runner=subprocess.run) -> str:
    """Run a script inside Ubuntu on the PC (stdin), or one Windows command."""
    if command is None:
        remote = f"wsl -d Ubuntu -u {PC_USER} -e sh -s"
    else:
        remote = command
    proc = runner(["ssh", "-o", "BatchMode=yes", SSH_HOST, remote],
                  input=script, capture_output=True, text=True, check=False)
    out = clean(proc.stdout or "")
    if proc.returncode != 0:
        raise RuntimeError(f"ssh failed ({proc.returncode}): {clean(proc.stderr or '')[:300]}")
    return out


def role_text() -> str:
    root = HERE.parents[1] / "docs" / "agent-playbooks" / "job-roles"
    return "\n\n".join((root / name).read_text() for name in ROLE_FILES if (root / name).is_file())


def b64(text: str) -> str:
    return base64.b64encode(text.encode()).decode()


def install_script(job_id: str, files: dict[str, str]) -> str:
    """Shell script (run in Ubuntu) that writes the job folder."""
    jobdir = f"$HOME/jobs/{job_id}"
    lines = ["set -e", f'mkdir -p "{jobdir}"']
    for name, content in files.items():
        lines.append(f"printf '%s' '{b64(content)}' | base64 -d > \"{jobdir}/{name}\"")
    lines.append(f'chmod +x "{jobdir}/start.sh"')
    lines.append(f'echo installed "{jobdir}"')
    return "\n".join(lines) + "\n"


def start_sh(job_id: str) -> str:
    return (
        "#!/bin/sh\n"
        f'cd "{PC_HOME}/jobs/{job_id}" || exit 1\n'
        f'python3 pc_job.py run "{PC_HOME}/jobs/{job_id}" >> runner.log 2>&1\n'
    )


def schtasks_create(job_id: str) -> str:
    target = f"wsl.exe -d Ubuntu -u {PC_USER} -e {PC_HOME}/jobs/{job_id}/start.sh"
    return f'schtasks /create /tn "job-{job_id}" /tr "{target}" /sc once /st 00:00 /f & schtasks /run /tn "job-{job_id}"'


def submit(brief_path: Path, *, dry_run: bool = False, runner=subprocess.run, out=print) -> int:
    text = brief_path.read_text()
    try:
        parsed = job_brief.parse(text)
    except job_brief.BriefError as exc:
        out(f"REFUSED: {exc}")
        return 2
    errors, normal = job_brief.validate(parsed)
    if errors:
        out("REFUSED: the brief has problems:")
        for error in errors:
            out(f"  - {error}")
        return 2
    job_id = make_job_id(normal["title"])
    files = {
        "brief.md": text,
        "pc_job.py": Path(__file__).read_text(),
        "job_brief.py": (HERE / "job_brief.py").read_text(),
        "role.txt": role_text(),
        "start.sh": start_sh(job_id),
    }
    out(f"Job {job_id}: {normal['title']}")
    out(f"  role {normal['role']}, finish {normal['finish']}"
        + (" (defaulted)" if normal["finish_defaulted"] else ""))
    out(f"  caps: ${normal['max_usd']:g}, {normal['max_turns']} turns, {normal['max_minutes']} minutes"
        + (f" (defaulted: {', '.join(normal['caps_defaulted'])})" if normal["caps_defaulted"] else ""))
    if dry_run:
        out("DRY RUN: nothing was sent to the PC.")
        return 0
    run_ssh(install_script(job_id, files), runner=runner)
    run_ssh(None, command=schtasks_create(job_id), runner=runner)
    out(f"Started {job_id} on the PC. Check with: pc_job.py status {job_id}")
    return 0


def remote_cat(job_id: str, name: str, runner=subprocess.run) -> str:
    if not re.fullmatch(r"[0-9]{8}-[0-9]{6}-[a-z0-9-]+", job_id):
        raise ValueError("job id looks wrong")
    return run_ssh(f'cat "$HOME/jobs/{job_id}/{name}" 2>&1\n', runner=runner)


def list_jobs(runner=subprocess.run) -> str:
    script = (
        'for d in "$HOME"/jobs/*/; do [ -f "$d/status.json" ] || continue; '
        'printf "%s  " "$(basename "$d")"; '
        "python3 -c \"import json,sys; d=json.load(open(sys.argv[1])); print(d.get('state'), d.get('role'), d.get('finish'))\" \"$d/status.json\"; done\n"
    )
    return run_ssh(script, runner=runner)


# -------------------------------------------------------------- PC side ----

class Status:
    """status.json, rewritten atomically at every step."""

    def __init__(self, job_dir: Path) -> None:
        self.path = job_dir / "status.json"
        self.data: dict = {"state": "queued", "started_at_utc": now().isoformat(),
                           "started_at_myt": myt(now())}

    def update(self, **fields) -> None:
        self.data.update(fields)
        self.data["updated_at_utc"] = now().isoformat()
        self.data["updated_at_myt"] = myt(now())
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, indent=2))
        tmp.replace(self.path)


def sh(cmd: list[str], cwd: Path | None = None, timeout: float | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False, timeout=timeout)


def claude_command(claude: str, role: str, prompt: str, system: str, normal: dict) -> list[str]:
    cmd = [claude, "-p", prompt, "--output-format", "json",
           "--max-budget-usd", f"{normal['max_usd']:g}", "--max-turns", str(normal["max_turns"]),
           "--permission-prompts", "none", "--append-system-prompt", system]
    if role == job_brief.REVIEWER:
        cmd += ["--permission-mode", "dontAsk", "--disallowedTools", ",".join(REVIEWER_DENIED),
                "--allowedTools", ",".join(REVIEWER_TOOLS)]
    else:
        cmd += ["--permission-mode", "acceptEdits", "--allowedTools", ",".join(BUILDER_TOOLS)]
    return cmd


def path_allowed(path: str, allowed: list[str]) -> bool:
    return any(path == a.rstrip("/") or path.startswith(a.rstrip("/") + "/") for a in allowed)


def prepare_worktree(repo: Path, worktrees: Path, job_id: str, normal: dict) -> Path:
    path = worktrees / f"job-{job_id}"
    worktrees.mkdir(parents=True, exist_ok=True)
    sh(["git", "fetch", "-q", "origin"], cwd=repo)
    if normal["role"] == job_brief.BUILDER:
        ref = normal["base"]
        if sh(["git", "rev-parse", "--verify", "-q", ref], cwd=repo).returncode != 0:
            raise RuntimeError(f"base {ref} not found")
        if sh(["git", "rev-parse", "--verify", "-q", normal["branch"]], cwd=repo).returncode == 0 or \
                sh(["git", "rev-parse", "--verify", "-q", f"origin/{normal['branch']}"], cwd=repo).returncode == 0:
            raise RuntimeError(f"branch {normal['branch']} already exists")
        proc = sh(["git", "worktree", "add", "-q", "-b", normal["branch"], str(path), ref], cwd=repo)
    else:
        ref = f"origin/{normal['target']}"
        if sh(["git", "rev-parse", "--verify", "-q", ref], cwd=repo).returncode != 0:
            raise RuntimeError(f"target {ref} not found")
        proc = sh(["git", "worktree", "add", "-q", "--detach", str(path), ref], cwd=repo)
    if proc.returncode != 0:
        raise RuntimeError(f"could not create the worktree: {proc.stderr.strip()[:200]}")
    return path


def wire_guards(worktree: Path) -> str | None:
    """Return None when hooks are wired, else the reason to refuse."""
    template = worktree / ".claude" / "settings.template.json"
    if not template.is_file():
        return "refusing to run without guards: the base has no .claude/settings.template.json"
    proc = sh([sys.executable, "scripts/agent-checks/render-claude-settings.py", "--apply"], cwd=worktree)
    settings = worktree / ".claude" / "settings.json"
    if proc.returncode != 0 or not settings.is_file():
        return f"refusing to run without guards: could not build settings.json ({proc.stdout.strip()[:120]})"
    try:
        wired = sum(len(g.get("hooks", [])) for items in json.loads(settings.read_text()).get("hooks", {}).values() for g in items)
    except (OSError, json.JSONDecodeError):
        return "refusing to run without guards: settings.json is unreadable"
    return None if wired >= GUARD_HOOK_MIN else "refusing to run without guards: no hooks are wired"


def working_changes(worktree: Path) -> list[str]:
    """Files modified, staged or created in the working tree (ignored files excluded)."""
    return sorted(line[3:] for line in sh(["git", "status", "--porcelain"], cwd=worktree).stdout.splitlines() if line.strip())


def has_git_identity(worktree: Path) -> bool:
    """A commit needs an author. Accept git config or the GIT_AUTHOR_* variables."""
    if os.environ.get("GIT_AUTHOR_NAME") and os.environ.get("GIT_AUTHOR_EMAIL"):
        return True
    return all(sh(["git", "config", key], cwd=worktree).stdout.strip() for key in ("user.name", "user.email"))


def changed_files(worktree: Path, base: str) -> list[str]:
    names: set[str] = set()
    for cmd in (["git", "diff", "--name-only", f"{base}...HEAD"], ["git", "diff", "--name-only"],
                ["git", "diff", "--name-only", "--cached"], ["git", "ls-files", "--others", "--exclude-standard"]):
        names.update(line for line in sh(cmd, cwd=worktree).stdout.splitlines() if line.strip())
    return sorted(names)


def finish_job(job_dir: Path, status: Status, normal: dict, outcome: dict) -> int:
    ended = now()
    state = outcome["state"]
    status.update(state=state, reason=outcome.get("reason", ""), ended_at_utc=ended.isoformat(),
                  ended_at_myt=myt(ended), **{k: v for k, v in outcome.items() if k not in ("state", "reason", "report")})
    d = status.data
    lines = [
        f"# Job {d.get('job_id')}: {normal.get('title')}", "",
        f"- **Status:** {state.upper()}" + (f" ({outcome['reason']})" if outcome.get("reason") else ""),
        f"- **Role:** {normal.get('role')}, finish {normal.get('finish')}",
        f"- **Caps:** ${normal.get('max_usd'):g}, {normal.get('max_turns')} turns, {normal.get('max_minutes')} minutes",
        f"- **Spent:** ${d.get('cost_usd', 0) or 0:.2f}, {d.get('turns', 0) or 0} turns",
        f"- **Started:** {d.get('started_at_myt')}  **Ended:** {d.get('ended_at_myt')}",
    ]
    if d.get("branch"):
        lines.append(f"- **Branch:** {d['branch']}, commits {d.get('commits', 0)}")
    if d.get("pr_url"):
        lines.append(f"- **Pull request:** {d['pr_url']}")
    if d.get("changed_files") is not None:
        lines.append(f"- **Changed files:** {', '.join(d['changed_files']) or 'none'}")
    lines += ["", "## Report from Claude", "", outcome.get("report") or "(no report)", ""]
    (job_dir / "result.md").write_text("\n".join(lines))
    (job_dir / "result.json").write_text(json.dumps(status.data, indent=2))
    return 0 if state == "done" else 1


def run(job_dir: Path, *, repo: Path | None = None, claude: str | None = None,
        worktrees: Path | None = None, timeout_override: float | None = None, drop_task: bool = True) -> int:
    job_dir = Path(job_dir)
    job_id = job_dir.name
    repo = Path(repo or PC_REPO)
    claude = claude or PC_CLAUDE
    worktrees = Path(worktrees or Path.home() / ".local" / "state" / "sifututor-agent-os" / "worktrees")
    status = Status(job_dir)
    status.update(job_id=job_id)
    try:
        parsed = job_brief.parse((job_dir / "brief.md").read_text())
        errors, normal = job_brief.validate(parsed)
    except (OSError, job_brief.BriefError) as exc:
        blank = {"title": "?", "role": "?", "finish": "?", "max_usd": 0.0, "max_turns": 0, "max_minutes": 0}
        return finish_job(job_dir, status, blank, {"state": "blocked", "reason": f"brief unreadable: {exc}"})
    status.update(title=normal["title"], role=normal["role"], finish=normal["finish"],
                  caps={"max_usd": normal["max_usd"], "max_turns": normal["max_turns"],
                        "max_minutes": normal["max_minutes"]})
    if errors:
        return finish_job(job_dir, status, normal, {"state": "blocked", "reason": "brief failed validation: " + "; ".join(errors)})

    try:
        status.update(state="preparing")
        worktree = prepare_worktree(repo, worktrees, job_id, normal)
        status.update(worktree=str(worktree), branch=normal["branch"] or f"(detached {normal['target']})")
        reason = wire_guards(worktree)
        if reason:
            return finish_job(job_dir, status, normal, {"state": "blocked", "reason": reason})

        if normal["role"] == job_brief.BUILDER and normal["finish"] in ("committed", "pr-open") and not has_git_identity(worktree):
            return finish_job(job_dir, status, normal, {"state": "blocked", "reason": "git identity is not set on this machine (user.name and user.email), so a commit would fail"})

        system = (job_dir / "role.txt").read_text() if (job_dir / "role.txt").is_file() else ""
        prompt = parsed["body"] + (
            f"\n\n---\nJob facts: finish state {normal['finish']}."
            + (f" Work on branch {normal['branch']}. Allowed paths: {', '.join(normal['allowed_paths'])}."
               if normal["role"] == job_brief.BUILDER else f" Review branch {normal['target']} against {normal['base']}."))
        cmd = claude_command(claude, normal["role"], prompt, system, normal)
        status.update(state="running")
        limit = timeout_override if timeout_override is not None else normal["max_minutes"] * 60
        try:
            proc = subprocess.run(cmd, cwd=worktree, capture_output=True, text=True, timeout=limit, check=False)
        except subprocess.TimeoutExpired:
            return finish_job(job_dir, status, normal, {"state": "timeout", "reason": f"wall-clock limit of {normal['max_minutes']} minutes reached"})
        (job_dir / "claude-output.json").write_text(proc.stdout or "")
        try:
            data = json.loads(proc.stdout)
        except (json.JSONDecodeError, TypeError):
            return finish_job(job_dir, status, normal, {"state": "failed", "reason": "claude output was not readable", "report": (proc.stderr or "")[:800]})
        outcome: dict = {"cost_usd": data.get("total_cost_usd"), "turns": data.get("num_turns"),
                         "report": data.get("result") or ""}
        status.update(state="checking", cost_usd=outcome["cost_usd"], turns=outcome["turns"])

        if normal["role"] == job_brief.REVIEWER:
            files, commits = working_changes(worktree), 0
        else:
            files = changed_files(worktree, normal["base"])
            commits = int(sh(["git", "rev-list", "--count", f"{normal['base']}..HEAD"], cwd=worktree).stdout.strip() or 0)
        outcome.update(changed_files=files, commits=commits)
        if data.get("is_error") or data.get("subtype") != "success":
            return finish_job(job_dir, status, normal, {**outcome, "state": "failed", "reason": str(data.get("subtype") or "claude reported an error")})

        if normal["role"] == job_brief.REVIEWER:
            if files:
                return finish_job(job_dir, status, normal, {**outcome, "state": "blocked", "reason": "the reviewer changed files, which a read-only role must not"})
            verdict = re.search(r"Verdict:?\**\s*(ACCEPT|CHANGES NEEDED|BLOCKED)", outcome["report"])
            return finish_job(job_dir, status, normal, {**outcome, "state": "done", "verdict": verdict.group(1) if verdict else "unknown"})

        outside = [f for f in files if not path_allowed(f, normal["allowed_paths"])]
        if outside:
            return finish_job(job_dir, status, normal, {**outcome, "state": "blocked", "reason": "changed files outside allowed_paths: " + ", ".join(outside)})
        dirty = bool(sh(["git", "status", "--porcelain"], cwd=worktree).stdout.strip())
        if normal["finish"] in ("committed", "pr-open"):
            if commits < 1:
                return finish_job(job_dir, status, normal, {**outcome, "state": "blocked", "reason": "finish needs a commit but none was made"})
            if dirty:
                return finish_job(job_dir, status, normal, {**outcome, "state": "blocked", "reason": "uncommitted changes remain"})
        if normal["finish"] == "pr-open":
            status.update(state="finishing")
            push = sh(["git", "push", "-u", "origin", normal["branch"]], cwd=worktree)
            if push.returncode != 0:
                return finish_job(job_dir, status, normal, {**outcome, "state": "failed", "reason": "push failed: " + push.stderr.strip()[:160]})
            body = (f"{outcome['report'][:3000]}\n\nJob {job_id}. Approval: {normal['approval']}\n\n"
                    "🤖 Generated with [Claude Code](https://claude.com/claude-code)\n")
            body_file = job_dir / "pr-body.md"
            body_file.write_text(body)
            pr = sh(["gh", "pr", "create", "--base", normal["base"].removeprefix("origin/"), "--head", normal["branch"],
                     "--title", normal["title"], "--body-file", str(body_file)], cwd=worktree)
            if pr.returncode != 0:
                return finish_job(job_dir, status, normal, {**outcome, "state": "failed", "reason": "pull request failed: " + pr.stderr.strip()[:160]})
            outcome["pr_url"] = pr.stdout.strip().splitlines()[-1] if pr.stdout.strip() else ""
        return finish_job(job_dir, status, normal, {**outcome, "state": "done"})
    except RuntimeError as exc:
        return finish_job(job_dir, status, normal, {"state": "blocked", "reason": str(exc)})
    except Exception as exc:  # the job must always leave a result file
        return finish_job(job_dir, status, normal, {"state": "failed", "reason": f"runner error: {type(exc).__name__}: {exc}"[:200]})
    finally:
        if drop_task and _has("schtasks.exe"):
            subprocess.run(["schtasks.exe", "/delete", "/tn", f"job-{job_id}", "/f"],
                           capture_output=True, check=False)


def _has(name: str) -> bool:
    from shutil import which
    return which(name) is not None


# ------------------------------------------------------------------ CLI ----

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("submit"); p.add_argument("brief", type=Path); p.add_argument("--dry-run", action="store_true")
    for name in ("status", "result"):
        p = sub.add_parser(name); p.add_argument("job_id")
    sub.add_parser("list")
    p = sub.add_parser("run"); p.add_argument("job_dir", type=Path)
    p.add_argument("--repo", type=Path); p.add_argument("--claude"); p.add_argument("--worktrees", type=Path)
    p.add_argument("--timeout-seconds", type=float); p.add_argument("--keep-task", action="store_true")
    args = parser.parse_args(argv)
    if args.cmd == "submit":
        return submit(args.brief, dry_run=args.dry_run)
    if args.cmd == "status":
        print(remote_cat(args.job_id, "status.json")); return 0
    if args.cmd == "result":
        print(remote_cat(args.job_id, "result.md")); return 0
    if args.cmd == "list":
        print(list_jobs()); return 0
    return run(args.job_dir, repo=args.repo, claude=args.claude, worktrees=args.worktrees,
               timeout_override=args.timeout_seconds, drop_task=not args.keep_task)


if __name__ == "__main__":
    raise SystemExit(main())
