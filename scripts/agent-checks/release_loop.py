#!/usr/bin/env python3
"""Release readiness loop for the home PC (issue #350).

PC side (started by Windows Task Scheduler through pc_release.py, never by hand):
    release_loop.py run READINESS.json [--clear-stop] [--drop-task NAME]

A plain, deterministic loop, not an agent that orchestrates agents
(docs/agent-playbooks/autonomous-work-packets.md, "Prefer a plain loop"):

    score -> pick the next open PC item by fixed rules -> run its action
          -> record evidence -> checkpoint -> repeat

Actions: `script` runs a scripted check with no Claude. `builder` and `reviewer`
run one Claude job at a time through the existing runner (pc_job.py), with a
finish state of local or committed only. A failed test check becomes a builder
fix job given the failure output. CHANGES NEEDED becomes a builder fix job given
the findings, then a fresh reviewer job.

It stops at: ready (PC readiness is 100 percent), blocked (an item failed or was
blocked twice, or nothing can run), stuck (two rounds in a row with no change in
score and no new evidence), stopped (a STOP file next to the checkpoint), and
when an item's fixes keep undoing each other. These are stop conditions, not
caps: there is no spend, turn or time cap anywhere, and none may be added.

The loop never merges, deploys, runs a migration or writes production data.
An item that would is handed to Hafiz as a gate and the loop carries on.
The only push the loop makes is a fast-forward of fix commits to the release
branch, and only when the readiness file carries an approval line.
"""

from __future__ import annotations

import argparse
import datetime as dt
import fcntl
import json
import os
from pathlib import Path
import re
import sys
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import job_brief  # noqa: E402
import release_readiness as rr  # noqa: E402

STOP_NAME = "STOP"
FIX_TEXT_LIMIT = 6000
MAX_RESETS = 3  # a fix that keeps undoing another item's proof is a loop, not progress


class LoopError(RuntimeError):
    """The loop cannot go on; the message becomes the blocked reason."""


# ------------------------------------------------------------ job runner ---

class PcJobRunner:
    """Runs one Claude job through the existing runner internals (pc_job.run)."""

    def __init__(self, loop_dir: Path, repo_root: Path | None = None, claude: str | None = None,
                 worktrees: Path | None = None) -> None:
        self.loop_dir = Path(loop_dir)
        self.repo_root = repo_root
        self.claude = claude
        self.worktrees = worktrees

    def run(self, brief_text: str, title: str) -> dict[str, Any]:
        import pc_job  # imported here so the planning code and its tests do not need the runner
        jobs_dir = self.loop_dir / "jobs"
        job_id = pc_job.make_job_id(title)
        job_dir = jobs_dir / job_id
        suffix = 1
        while job_dir.exists():
            suffix += 1
            job_dir = jobs_dir / f"{job_id}-{suffix}"
        job_dir.mkdir(parents=True)
        (job_dir / "brief.md").write_text(brief_text)
        for name in ("role.txt", "settings.template.json", "render-claude-settings.py"):
            if (self.loop_dir / name).is_file():
                (job_dir / name).write_text((self.loop_dir / name).read_text())
        pc_job.run(job_dir, repo=self.repo_root, claude=self.claude, worktrees=self.worktrees, drop_task=False)
        try:
            status = json.loads((job_dir / "result.json").read_text())
        except (OSError, json.JSONDecodeError):
            status = {"state": "failed", "reason": "the job left no readable result.json"}
        report = ""
        try:
            report = json.loads((job_dir / "claude-output.json").read_text()).get("result") or ""
        except (OSError, json.JSONDecodeError):
            pass
        return {**status, "job_id": job_dir.name, "report": report}


# ------------------------------------------------------------- the loop ----

class Loop:
    def __init__(self, readiness_path: Path | str, jobs: Any, shell: Any, *, repo_root: Path | str | None = None,
                 worktrees: Path | str | None = None, clear_stop: bool = False,
                 log: Callable[[str], None] | None = None) -> None:
        self.path = Path(readiness_path)
        self.dir = self.path.parent
        self.pack = self.dir / "release-pack"
        self.stop_path = self.dir / STOP_NAME
        self.jobs = jobs
        self.shell = shell
        self.repo_root = Path(repo_root) if repo_root else Path.home() / "Projects" / "Sifututor"
        self.worktrees = Path(worktrees) if worktrees else Path.home() / ".local" / "state" / "sifututor-agent-os" / "worktrees"
        self.clear_stop = clear_stop
        self.log = log or (lambda message: print(f"[{rr.myt_text()}] {message}", flush=True))
        self.data: dict[str, Any] = {}

    # ---- small helpers ----

    @property
    def loop(self) -> dict[str, Any]:
        return self.data["loop"]

    def stop_requested(self) -> bool:
        return self.stop_path.exists()

    def checkpoint(self) -> None:
        rr.save(self.path, self.data)

    def event(self, message: str) -> None:
        self.loop.setdefault("events", []).append(f"{rr.myt_text()}: {message}")
        self.log(message)

    @property
    def project(self) -> bool:
        return self.data["repo"] != "agent-os"

    @property
    def repo_dir(self) -> Path:
        return self.repo_root / self.data["repo"] if self.project else self.repo_root

    def items(self) -> dict[str, dict[str, Any]]:
        return rr.item_map(self.data)

    def next_seq(self) -> int:
        self.loop["job_seq"] = int(self.loop.get("job_seq", 0)) + 1
        return self.loop["job_seq"]

    def sha(self) -> str:
        return str(self.loop.get("release_sha", ""))

    def check_context(self) -> rr.CheckContext:
        wt = self.loop.get("worktree")
        return rr.CheckContext(self.data, self.pack, Path(wt) if wt else None, self.repo_dir, self.shell, self.stop_requested)

    # ---- release worktree ----

    def ensure_worktree(self) -> None:
        """Check out origin/<release branch> in the loop's own worktree, installing packages for a project repo."""
        branch = self.data["branch"]
        slug = re.sub(r"[^a-z0-9]+", "-", self.data["release"].lower()).strip("-") or "release"
        wt = Path(self.loop.get("worktree") or self.worktrees / f"release-{slug}")
        self.loop["worktree"] = str(wt)
        stop = self.stop_requested
        code, out = self.shell.run(["git", "fetch", "-q", "origin"], cwd=self.repo_dir, stop_check=stop)
        if code != 0:
            raise LoopError(f"git fetch failed (exit {code}): {rr.tail(out, 3)}")
        if (wt / ".git").exists():
            code, out = self.shell.run(["git", "checkout", "-q", "--detach", f"origin/{branch}"], cwd=wt, stop_check=stop)
        else:
            wt.parent.mkdir(parents=True, exist_ok=True)
            code, out = self.shell.run(["git", "worktree", "add", "-q", "--detach", str(wt), f"origin/{branch}"],
                                       cwd=self.repo_dir, stop_check=stop)
        if code != 0:
            raise LoopError(f"cannot check out origin/{branch} (exit {code}): {rr.tail(out, 3)}")
        code, out = self.shell.run(["git", "rev-parse", "HEAD"], cwd=wt, stop_check=stop)
        sha = out.strip().splitlines()[-1] if code == 0 and out.strip() else ""
        lock = wt / "package-lock.json"
        if self.project and lock.is_file():
            import hashlib
            digest = hashlib.sha256(lock.read_bytes()).hexdigest()
            if digest != self.loop.get("lock_hash") or not (wt / "node_modules").exists():
                code, out = self.shell.run(["npm", "ci", "--no-audit", "--no-fund", "--prefer-offline"], cwd=wt, stop_check=stop)
                if code != 0:
                    raise LoopError(f"npm ci failed in the release worktree (exit {code}): {rr.tail(out, 3)}")
                self.loop["lock_hash"] = digest
        old = self.loop.get("release_sha", "")
        self.loop["release_sha"] = sha
        if old and sha and old != sha:
            self.reset_sensitive(sha)

    def reset_sensitive(self, sha: str) -> None:
        """The release changed: proof taken on the old commit no longer proves the new one."""
        for item in self.data["items"]:
            sensitive = item.get("sha_sensitive", item.get("action") in ("script", "reviewer"))
            if (rr.is_pc_item(item) and item.get("status") == "green" and sensitive
                    and item.get("verified_sha") and item["verified_sha"] != sha):
                item["status"] = "open"
                item["resets"] = int(item.get("resets", 0)) + 1
                rr.add_evidence(item, note=f"proof reset: the release moved to {sha[:10]}, so this is checked again")
                self.event(f"item {item['id']} reset because the release moved to {sha[:10]}")

    # ---- recording ----

    def record_job(self, item: dict[str, Any], role: str, res: dict[str, Any]) -> None:
        self.loop.setdefault("jobs", []).append({
            "job_id": res.get("job_id", ""), "item": item["id"], "role": role, "state": res.get("state", ""),
            "turns": res.get("turns") or 0, "cost_usd": res.get("cost_usd") or 0,
            "ended": rr.myt_text(), "verdict": res.get("verdict", "")})

    def green(self, item: dict[str, Any], evidence: list[dict[str, Any]], summary: str) -> None:
        for entry in evidence:
            rr.add_evidence(item, **entry)
        rr.add_evidence(item, note=f"green: {summary}", sha=self.sha()[:10])
        item["status"] = "green"
        item["failures"] = 0
        item["verified_sha"] = self.sha()
        item.pop("pending_fix", None)
        item.pop("blocked_reason", None)
        self.event(f"item {item['id']} green: {summary}")

    def fail(self, item: dict[str, Any], summary: str, *, evidence: list[dict[str, Any]] | None = None,
             fix_text: str = "") -> None:
        for entry in evidence or []:
            rr.add_evidence(item, **entry)
        rr.add_evidence(item, note=f"failed: {summary}")
        item["failures"] = int(item.get("failures", 0)) + 1
        item["last_failure"] = summary
        self.event(f"item {item['id']} failed ({item['failures']}): {summary}")
        if item["failures"] >= 2:
            item["status"] = "blocked"
            item["blocked_reason"] = summary
        elif fix_text:
            item["pending_fix"] = fix_text[:FIX_TEXT_LIMIT]

    # ---- briefs ----

    def build_brief(self, fields: dict[str, Any], body: str) -> str:
        if self.project:
            fields = {**fields, "repo": self.data["repo"]}
        issue = str(self.data.get("issue", ""))
        if issue.isdigit() and issue != "0":
            fields = {**fields, "issue": issue}
        lines = ["---"] + [f"{k}: {v}" for k, v in fields.items() if v not in ("", None)] + ["---", body]
        text = "\n".join(lines) + "\n"
        errors, _ = job_brief.validate(job_brief.parse(text))
        if errors:
            raise LoopError("the loop built a brief the runner refuses: " + "; ".join(errors))
        return text

    def release_facts(self) -> str:
        prs = ", ".join(f"#{n}" for n in self.data.get("pr_numbers", [])) or "none yet"
        return (f"Release: {self.data['release']} (repo {self.data['repo']}, branch {self.data['branch']}, "
                f"base {self.data['base']}, issue #{self.data.get('issue', '0')}, PR {prs}, commit {self.sha()[:10] or 'unknown'}).")

    SAFETY = ("Do not merge, push, deploy, run a migration or write production data. Write English, no em dashes, "
              "times in MYT. Say what you did not check.")

    # ---- actions ----

    def act(self, item: dict[str, Any]) -> None:
        if item.get("pending_fix"):
            return self.act_fix(item)
        action = item.get("action")
        if action == "script":
            return self.act_script(item)
        if action == "builder":
            return self.act_builder(item)
        if action == "reviewer":
            return self.act_reviewer(item)
        item["status"] = "blocked"
        item["blocked_reason"] = "the item has no action the PC can run"
        rr.add_evidence(item, note="blocked: the item has no action the PC can run")

    def act_script(self, item: dict[str, Any]) -> None:
        check = rr.effective_check(item)
        if not check:
            return self.fail(item, "a script item needs a check")
        res = rr.run_check(check, self.check_context())
        if res["ok"]:
            return self.green(item, res["evidence"], res["summary"])
        fix = f"{res['summary']}\n\n{res.get('detail', '')}" if item.get("fix_on_failure") else ""
        self.fail(item, res["summary"], evidence=res["evidence"], fix_text=fix)

    def act_builder(self, item: dict[str, Any]) -> None:
        if item.get("doc"):
            return self.act_doc(item)
        return self.run_code_job(item, item.get("instruction", item["title"]))

    def act_doc(self, item: dict[str, Any]) -> None:
        doc = item["doc"]
        seq = self.next_seq()
        headings = doc.get("headings", [])
        body = "\n\n".join([
            self.release_facts(),
            f"You are drafting one document for the release readiness pack. You change no file. Task: {item['title']}.",
            item.get("instruction", ""),
            f"The release branch is checked out. See what it changes with: git diff {self.data['base']}...HEAD",
            ("Use these level-2 headings exactly: " + "; ".join(f"## {h}" for h in headings)) if headings else "Plain Markdown.",
            "Your final message must be the finished document and nothing else: start with a level-1 heading, then the "
            "sections. No preface, no result block. This overrides the result format in your role text. " + self.SAFETY,
        ])
        brief = self.build_brief({
            "title": f"Draft {item['id']}: {item['title']}"[:80], "role": "builder",
            "branch": f"docs/release-draft-{item['id']}-{seq}", "base": f"origin/{self.data['branch']}",
            "finish": "local", "allowed_paths": ".release-loop-scratch"}, body)
        res = self.jobs.run(brief, f"Draft {item['id']} {item['title']}"[:60])
        self.record_job(item, "builder", res)
        job_note = {"job_id": res.get("job_id", ""), "note": f"builder job {res.get('state')}"}
        if res.get("state") != "done":
            return self.fail(item, f"the drafting job {res.get('state')}: {res.get('reason', '')}"[:200], evidence=[job_note])
        text = (res.get("report") or "").strip()
        first = re.search(r"(?m)^#", text)
        if first:
            text = text[first.start():]
        if not text:
            return self.fail(item, "the drafting job returned no document", evidence=[job_note])
        target = self.dir / doc["path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(target.name + ".tmp")
        tmp.write_text(rr.redact(text) + "\n")
        os.replace(tmp, target)
        check = rr.effective_check(item)
        outcome = rr.run_check(check, self.check_context()) if check else rr.result(True, "no check")
        evidence = [job_note, {"path": doc["path"], "note": "drafted by a builder job"}]
        if outcome["ok"]:
            return self.green(item, evidence + outcome["evidence"], outcome["summary"])
        self.fail(item, outcome["summary"], evidence=evidence + outcome["evidence"])

    def act_reviewer(self, item: dict[str, Any]) -> None:
        seq = self.next_seq()
        body = "\n\n".join([
            self.release_facts(),
            f"Review this branch as a release candidate. Task: {item['title']}.",
            item.get("instruction", ""),
            "End with the result format of your role. Start the result with the line 'Verdict: ACCEPT', "
            "'Verdict: CHANGES NEEDED' or 'Verdict: BLOCKED'. Name file and line for every finding. " + self.SAFETY,
        ])
        brief = self.build_brief({
            "title": f"Review {item['id']}: {item['title']}"[:80], "role": "reviewer",
            "target": self.data["branch"], "base": self.data["base"]}, body)
        res = self.jobs.run(brief, f"Review {item['id']} {item['title']}"[:60])
        self.record_job(item, "reviewer", res)
        job_note = {"job_id": res.get("job_id", ""), "note": f"reviewer job {res.get('state')}"}
        if res.get("state") != "done":
            return self.fail(item, f"the review job {res.get('state')}: {res.get('reason', '')}"[:200], evidence=[job_note])
        report = res.get("report") or ""
        self.pack.mkdir(parents=True, exist_ok=True)
        rel = f"release-pack/review-{item['id']}.md"
        for name in (f"review-{item['id']}.md", f"review-{item['id']}-{seq}.md"):
            (self.pack / name).write_text(rr.redact(report) + "\n")
        check = rr.effective_check(item) or {"type": "verdict_file", "base": "pack", "path": rel}
        outcome = rr.run_check(check, self.check_context())
        evidence = [job_note] + outcome["evidence"]
        if outcome["ok"]:
            return self.green(item, evidence, outcome["summary"])
        verdict = rr.VERDICT_RE.search(report)
        findings = report if verdict and verdict.group(1) == "CHANGES NEEDED" else ""
        self.fail(item, outcome["summary"], evidence=evidence,
                  fix_text=f"The cold reviewer said CHANGES NEEDED. Fix these findings:\n\n{findings}" if findings else "")

    def act_fix(self, item: dict[str, Any]) -> None:
        self.run_code_job(item, item["pending_fix"], fix=True)

    def run_code_job(self, item: dict[str, Any], task: str, *, fix: bool = False) -> None:
        """A builder job that changes the release branch: committed locally, then pushed by the loop (fast-forward only)."""
        seq = self.next_seq()
        paths = self.data.get("fix_allowed_paths") or []
        if not paths:
            return self.fail(item, "the readiness file has no fix_allowed_paths, so no builder may change code")
        commands = [c["run"] if isinstance(c, dict) else c for c in rr._check_commands(item.get("check"))]
        body = "\n\n".join([
            self.release_facts(),
            ("Fix the release branch. " if fix else "Change the release branch. ") + f"Item {item['id']}: {item['title']}.",
            task,
            ("After the change, run these and they must pass: " + "; ".join(commands)) if commands else "",
            "Make the smallest change, commit it on your branch with a conventional commit message that names the "
            f"issue (#{self.data.get('issue', '0')}), and run the commit guard first. Never loosen a test or skip a check. " + self.SAFETY,
        ])
        brief = self.build_brief({
            "title": f"Fix {item['id']}: {item['title']}"[:80], "role": "builder",
            "branch": f"fix/release-fix-{item['id']}-{seq}", "base": f"origin/{self.data['branch']}",
            "finish": "committed", "allowed_paths": ", ".join(paths)}, body)
        res = self.jobs.run(brief, f"Fix {item['id']} {item['title']}"[:60])
        self.record_job(item, "builder", res)
        job_note = {"job_id": res.get("job_id", ""), "note": f"builder job {res.get('state')}, {res.get('commits', 0)} commit(s)"}
        if res.get("state") != "done":
            return self.fail(item, f"the builder job {res.get('state')}: {res.get('reason', '')}"[:200], evidence=[job_note])
        if int(res.get("commits") or 0) < 1:
            if not fix:
                self.event(f"item {item['id']}: the builder job changed nothing")
                return  # no failure and no evidence: a repeat is what the stuck rule catches
            return self.fail(item, "the fix job made no commit", evidence=[job_note])
        pushed, why = self.push_fix(res)
        if not pushed:
            return self.fail(item, why, evidence=[job_note])
        item.pop("pending_fix", None)
        rr.add_evidence(item, **job_note, files=", ".join(res.get("changed_files") or []))
        self.event(f"item {item['id']}: fix pushed to {self.data['branch']}")
        self.ensure_worktree()
        if not fix:
            check = rr.effective_check(item)
            if check:
                return self.act_script(item)
            self.green(item, [], "the builder job changed the release and it was pushed")

    def push_fix(self, res: dict[str, Any]) -> tuple[bool, str]:
        branch = self.data["branch"]
        if branch in rr.PROTECTED_BRANCHES or branch == str(self.data.get("base", "")).removeprefix("origin/"):
            return False, f"refusing to push to protected branch {branch}"
        if not self.data.get("approval"):
            return False, "the fix is committed on the PC but not pushed: the readiness file has no approval line"
        worktree = res.get("worktree")
        if not worktree:
            return False, "the fix job did not report its worktree"
        code, out = self.shell.run(["git", "push", "origin", f"HEAD:refs/heads/{branch}"], cwd=worktree, stop_check=self.stop_requested)
        if code != 0:
            return False, f"pushing the fix to {branch} failed (exit {code}): {rr.tail(out, 3)}"
        return True, ""

    # ---- rules ----

    def hand_forbidden_to_hafiz(self) -> None:
        """Stop rule (d): never run an action that would merge, deploy, migrate or write production data."""
        for item in self.data["items"]:
            if not (rr.is_pc_item(item) and rr.is_applicable(item)) or item.get("status") == "green":
                continue
            why = rr.forbidden_in_item(item)
            if why:
                item["original_owner"] = item["owner"]
                item["owner"] = "hafiz"
                item["status"] = "open"
                rr.add_evidence(item, note=f"moved to Hafiz's gates, the PC will not run it: {why}")
                self.event(f"item {item['id']} handed to Hafiz: {why}")

    def fingerprint(self) -> list[int]:
        return [rr.score(self.data)["pc_green"], rr.evidence_count(self.data)]

    def blocked_reason(self) -> str | None:
        for item in self.data["items"]:
            if rr.is_pc_item(item) and rr.is_applicable(item) and item.get("status") != "green":
                if int(item.get("failures", 0)) >= 2:
                    return f"item {item['id']} ({item['title']}) failed twice: {item.get('last_failure', item.get('blocked_reason', ''))}"
                if int(item.get("resets", 0)) >= MAX_RESETS:
                    return f"item {item['id']} was reset {item['resets']} times: the fixes keep undoing each other"
        return None

    def stuck_reason(self) -> str | None:
        """Stop rule (c): two rounds in a row with no change in score and no new evidence."""
        fps = self.loop.get("fingerprints", [])
        if len(fps) >= 3 and fps[-1] == fps[-2] == fps[-3]:
            return "two rounds in a row changed nothing: no change in score and no new evidence"
        return None

    def nothing_runnable_reason(self) -> str:
        pieces = []
        items = self.items()
        for item in self.data["items"]:
            if rr.is_pc_item(item) and rr.is_applicable(item) and item.get("status") != "green":
                if item.get("status") == "blocked":
                    pieces.append(f"item {item['id']} blocked: {item.get('blocked_reason', 'no reason recorded')}")
                else:
                    waiting = [d for d in item.get("depends_on", []) if items[d].get("status") not in ("green", "na")]
                    pieces.append(f"item {item['id']} waits on {', '.join(waiting) or 'nothing it can run'}")
        return "nothing can run: " + "; ".join(pieces)

    def step(self) -> tuple[str, str] | None:
        self.hand_forbidden_to_hafiz()
        if rr.score(self.data)["ready"]:
            return "ready", ""
        reason = self.blocked_reason()
        if reason:
            return "blocked", reason
        if self.stop_requested():
            return "stopped", "a STOP file appeared"
        item = rr.next_item(self.data)
        if item is None:
            return "blocked", self.nothing_runnable_reason()
        self.loop["current"] = {"item": item["id"], "action": "fix" if item.get("pending_fix") else item.get("action"),
                                "started_at": rr.myt_text()}
        self.checkpoint()
        try:
            self.act(item)
        except rr.StopRequested:
            self.loop["current"] = None
            self.checkpoint()
            return "stopped", "a STOP file appeared while an action was running"
        except LoopError as exc:
            self.fail(item, str(exc)[:200])
        except Exception as exc:  # a bug must be a recorded failure, never a lost checkpoint
            self.fail(item, f"loop error: {type(exc).__name__}: {exc}"[:200])
        self.loop["current"] = None
        self.loop["rounds"] = int(self.loop.get("rounds", 0)) + 1
        fps = self.loop.setdefault("fingerprints", [])
        fps.append(self.fingerprint())
        self.checkpoint()
        if rr.score(self.data)["ready"]:
            return "ready", ""
        reason = self.blocked_reason()
        if reason:
            return "blocked", reason
        reason = self.stuck_reason()
        if reason:
            return "stuck", reason
        return None

    def run(self) -> str:
        self.data = rr.load(self.path)
        errors = rr.validate(self.data)
        if errors:
            raise rr.ReadinessError("; ".join(errors))
        self.data.setdefault("loop", {})
        loop = self.loop
        previous = loop.get("current")
        loop.update(status="running", reason="")
        loop.setdefault("rounds", 0)
        loop.setdefault("job_seq", 0)
        loop.setdefault("jobs", [])
        loop.setdefault("started_at", rr.myt_text())
        loop.setdefault("started_at_utc", rr.now_utc().isoformat())
        loop.pop("ended_at", None)
        loop["current"] = None
        if previous:
            self.event(f"the previous run stopped while running item {previous.get('item')} ({previous.get('action')}); it runs again")
        (self.dir / "ready.flag").unlink(missing_ok=True)
        if self.clear_stop:
            self.stop_path.unlink(missing_ok=True)
        try:
            if not self.stop_requested():
                self.ensure_worktree()
            loop["fingerprints"] = [self.fingerprint()]
            self.checkpoint()
            outcome: tuple[str, str] | None = None
            while outcome is None:
                outcome = self.step()
        except rr.StopRequested:
            outcome = ("stopped", "a STOP file appeared")
        except LoopError as exc:
            outcome = ("blocked", str(exc))
        return self.conclude(*outcome)

    def conclude(self, status: str, reason: str) -> str:
        self.loop.update(status=status, reason=reason, current=None, ended_at=rr.myt_text(), ended_at_utc=rr.now_utc().isoformat())
        self.event(f"loop {status}" + (f": {reason}" if reason else ""))
        self.write_report()
        if status == "ready":
            (self.dir / "ready.flag").write_text(f"READY FOR YOUR GO\n{rr.myt_text()}\nrelease commit {self.sha()}\n")
        self.checkpoint()
        return status

    # ---- the report ----

    def section_lines(self, doc_path: str, heading: str, limit: int = 8) -> list[str]:
        try:
            text = (self.dir / doc_path).read_text()
        except OSError:
            return []
        found = re.search(rf"(?ms)^##\s*{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)", text)
        return [ln for ln in (found.group(1).strip().splitlines() if found else []) if ln.strip()][:limit]

    def write_report(self) -> None:
        s = rr.score(self.data)
        loop = self.loop
        status = loop["status"]
        title = {"ready": "READY FOR YOUR GO", "blocked": "BLOCKED", "stuck": "STUCK", "stopped": "STOPPED"}.get(status, status.upper())
        items = self.data["items"]
        prs = ", ".join(f"#{n}" for n in self.data.get("pr_numbers", [])) or "branch only"
        lines = [f"# Release report: {self.data['release']}", "",
                 f"**{title}** at {loop.get('ended_at', rr.myt_text())}"
                 + (f" ({loop['reason']})" if loop.get("reason") else ""), "",
                 "## Release state", "",
                 f"- Source: branch {self.data['branch']} ({prs}) on {self.data['github_repo']}, commit {self.sha() or 'unknown'}.",
                 "- Highest proven state: not merged, not deployed. "
                 + ("Every PC check is done on that commit." if s["ready"] else f"PC checks are {s['percent']}% done."),
                 "- What proves it: the evidence per item below, and the files in release-pack/.",
                 "- Normal smoke: not run. Production smoke is your gate (G5).",
                 "- Change smoke: planned in release-pack/10-smoke-monitoring.md, not run. It is your gate (G5).",
                 "- What is not proven yet: "
                 + ("; ".join(f"{g['id']} {g['title']}" for g in s["gates"] if g["applicable"] and g["status"] != "green") or "none")
                 + (f"; PC items not done: {', '.join(s['open_pc'] + s['blocked_pc'])}" if not s["ready"] else "") + ".",
                 ]
        impact = self.section_lines("release-pack/01-scope.md", "Who is affected")
        lines.append("- User impact: " + (" ".join(impact) if impact else "see release-pack/01-scope.md (not drafted)"))
        seven = self.items().get("7")
        if seven and seven.get("status") == "na":
            lines.append(f"- Staff documentation: not relevant, {seven.get('na_reason')}")
        elif seven:
            lines.append(f"- Staff documentation: {seven.get('status')} (item 7); the decision is in the release's own ledger.")
        lines += ["- Recommended next: " + ("read release-pack/11-review-page.md, then decide on the merge and the production deploy go."
                                          if s["ready"] else "fix what the loop could not, then start it again (it resumes)."),
                  "- Decision needed: " + ("yes. Confirm the review page (G1), then say whether to merge and deploy."
                                           if s["ready"] else "yes. See the reason at the top."), "",
                 "## PC readiness", "", f"{s['percent']}% ({s['pc_green']} of {s['pc_total']} applicable PC items green)", "",
                 "| Item | Status | Evidence |", "| --- | --- | --- |"]
        for item in items:
            if not rr.is_pc_item(item) and not item.get("original_owner"):
                continue
            if item.get("status") == "na" or item.get("applicable") is False:
                lines.append(f"| {item['id']} {item['title']} | not applicable | {item.get('na_reason', '')} |")
                continue
            ev = [e for e in item.get("evidence", []) if e.get("note", "").startswith("green:")] or item.get("evidence", [])[-1:]
            what = "; ".join(self.describe(e) for e in ev[-1:]) or "none"
            owner = " (handed to Hafiz)" if item.get("original_owner") else ""
            lines.append(f"| {item['id']} {item['title']}{owner} | {item.get('status')} | {what} |")
        lines += ["", "## Your gates (the PC never does these)", ""]
        for g in s["gates"]:
            state = g["status"] if g["applicable"] else f"not applicable, {g['na_reason']}"
            lines.append(f"- {g['id']} {g['title']} [{g['owner']}]: {state}")
        jobs = loop.get("jobs", [])
        elapsed = ""
        if loop.get("started_at_utc") and loop.get("ended_at_utc"):
            secs = (dt.datetime.fromisoformat(loop["ended_at_utc"]) - dt.datetime.fromisoformat(loop["started_at_utc"])).total_seconds()
            elapsed = f"{int(secs // 60)} min {int(secs % 60)} s"
        lines += ["", "## What the loop did", "",
                  f"- Started {loop.get('started_at')}, ended {loop.get('ended_at')}" + (f", {elapsed}." if elapsed else "."),
                  f"- {loop.get('rounds', 0)} rounds, {len(jobs)} Claude jobs, "
                  f"{sum(int(j.get('turns') or 0) for j in jobs)} turns, list-price equivalent "
                  f"${sum(float(j.get('cost_usd') or 0) for j in jobs):.2f} (billed to the subscription, no cap).",
                  "- Nothing was merged, deployed, migrated or written to production by the loop."]
        for j in jobs:
            lines.append(f"  - {j['job_id']} ({j['role']}, item {j['item']}): {j['state']}"
                         + (f", verdict {j['verdict']}" if j.get("verdict") else ""))
        (self.dir / "release-report.md").write_text("\n".join(lines) + "\n")

    @staticmethod
    def describe(entry: dict[str, Any]) -> str:
        if entry.get("note"):
            return str(entry["note"])[:160].replace("|", "/")
        bits = [f"{k} {entry[k]}" for k in ("command", "exit_code", "path", "pr", "job_id") if k in entry]
        return ", ".join(bits)[:160].replace("|", "/")


# -------------------------------------------------------------------- CLI --

def acquire_lock(path: Path):
    handle = open(path.parent / "loop.lock", "w")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        handle.close()
        return None
    return handle


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run"); p.add_argument("readiness", type=Path)
    p.add_argument("--clear-stop", action="store_true"); p.add_argument("--drop-task")
    p.add_argument("--repo", type=Path); p.add_argument("--claude"); p.add_argument("--worktrees", type=Path)
    args = parser.parse_args(argv)
    lock = acquire_lock(args.readiness)
    if lock is None:
        print("Another loop is already running on this readiness file.")
        return 3
    import pc_job
    pc_job.prefer_linux_user_tools()
    try:
        runner = PcJobRunner(args.readiness.parent, repo_root=args.repo, claude=args.claude, worktrees=args.worktrees)
        loop = Loop(args.readiness, runner, rr.RealShell(), repo_root=args.repo, worktrees=args.worktrees,
                    clear_stop=args.clear_stop)
        status = loop.run()
        print(f"Loop finished: {status}")
        return 0 if status == "ready" else 1
    finally:
        if args.drop_task:
            from shutil import which
            if which("schtasks.exe"):
                import subprocess
                subprocess.run(["schtasks.exe", "/delete", "/tn", args.drop_task, "/f"], capture_output=True, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
