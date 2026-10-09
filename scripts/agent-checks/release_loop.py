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

It stops at: ready_for_prod_go (Prod readiness is 100 percent: nothing before
the production deploy go is open), blocked (an item failed or was blocked twice,
or nothing can run), stuck (two rounds in a row with no change in score and no
new evidence), stopped (a STOP file next to the checkpoint), and when an item's
fixes keep undoing each other. When every open item is a gate owned by a person
it does not stop: it goes to `waiting` (waiting_for_gate), re-reads the
checkpoint every 60 seconds and carries on the moment a gate gets evidence. The
stuck rule cannot fire while waiting. These are stop conditions, not caps: there
is no spend, turn or time cap anywhere, and none may be added.

The loop never merges, deploys, runs a migration or writes production data.
An item that would is handed to Hafiz as a gate and the loop carries on.
The only push the loop makes is a fast-forward of fix commits to the release
branch, and only when the readiness file carries an approval line.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import sys
import time
from typing import Any, Callable

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import job_brief  # noqa: E402
import release_readiness as rr  # noqa: E402

STOP_NAME = "STOP"
FIX_TEXT_LIMIT = 6000
MAX_RESETS = 5  # a fix that keeps undoing another item's proof is a loop, not progress


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
                 log: Callable[[str], None] | None = None, wait_seconds: int = 60, poll_seconds: int = 2,
                 sleep: Callable[[float], None] = time.sleep, http: Any = None, deploy_poll_seconds: float | None = None) -> None:
        self.path = Path(readiness_path)
        self.dir = self.path.parent
        self.pack = self.dir / "release-pack"
        self.stop_path = self.dir / STOP_NAME
        self.jobs = jobs
        self.shell = shell
        self.repo_root = Path(repo_root) if repo_root else Path.home() / "Projects" / "Sifututor"
        self.worktrees = Path(worktrees) if worktrees else Path.home() / ".local" / "state" / "sifututor-agent-os" / "worktrees"
        self.clear_stop = clear_stop
        self.wait_seconds, self.poll_seconds, self.sleep = wait_seconds, poll_seconds, sleep
        self.http, self.deploy_poll_seconds = http, deploy_poll_seconds
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
        self.checkpoint()  # a restart after a power cut must not hand the next job the same branch name
        return self.loop["job_seq"]

    def branch_token(self) -> str:
        """A per-release token, so job branch names never collide with an earlier release's jobs in the same repo."""
        if not self.loop.get("token"):
            self.loop["token"] = rr.now_utc().strftime("%m%d%H%M%S")
        return self.loop["token"]

    def sha(self) -> str:
        return str(self.loop.get("release_sha", ""))

    def check_context(self) -> rr.CheckContext:
        wt = self.loop.get("worktree")
        ctx = rr.CheckContext(self.data, self.pack, Path(wt) if wt else None, self.repo_dir, self.shell, self.stop_requested,
                              checkpoint=self.checkpoint)
        ctx.http, ctx.sleep, ctx.poll_seconds = self.http, self.sleep, self.deploy_poll_seconds  # the staging checks poll and call sites
        return ctx

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

    def staging_candidate_moved(self) -> bool:
        """The staging candidate branch moved on GitHub: what was checked, deployed and smoke tested is not the new tip.

        S1 to S3 (and S4) go back to open so staging is redeployed on the new commit. Without a staging section this does nothing."""
        cfg = self.data.get("staging")
        if not cfg or not cfg.get("candidate_sha"):
            return False
        import staging_deploy
        ref = staging_deploy.candidate_ref(self.data, cfg)
        tip, why = staging_deploy.local_tip(self.shell, self.repo_dir, ref, self.stop_requested)
        if why or tip == cfg["candidate_sha"]:
            return False  # cannot tell, or unchanged: keep what is proven
        old = cfg["candidate_sha"]
        for gate_id in ("S1", "S2", "S3", "S4"):
            item = self.items().get(gate_id)
            if item is not None and rr.is_pc_item(item) and item.get("status") == "green":
                item["status"] = "open"
                item["resets"] = int(item.get("resets", 0)) + 1
                rr.add_evidence(item, note=f"proof reset: the staging candidate moved from {old[:10]} to {tip[:10]}, so staging is checked again")
        cfg.pop("candidate_sha", None)
        cfg.pop("candidate_ref", None)
        cfg["deploy"] = None
        self.data.pop("staging_sha", None)
        self.event(f"staging candidate {ref} moved to {tip[:10]}: S1 to S4 are checked again")
        return True

    def reset_sensitive(self, sha: str) -> None:
        """The release changed: proof taken on the old commit no longer proves the new one."""
        for item in self.data["items"]:
            sensitive = item.get("sha_sensitive", item.get("action") in ("script", "reviewer") or bool(item.get("doc")))
            if (rr.is_pc_item(item) and item.get("status") == "green" and sensitive
                    and item.get("verified_sha") and item["verified_sha"] != sha):
                item["status"] = "open"
                item["resets"] = int(item.get("resets", 0)) + 1
                rr.add_evidence(item, note=f"proof reset: the release moved to {sha[:10]}, so this is checked again")
                self.event(f"item {item['id']} reset because the release moved to {sha[:10]}")
                for gate_id in item.get("reopens_gates_on_reset", []):
                    gate = self.items().get(gate_id)
                    if gate is not None and gate.get("status") == "green":
                        gate["status"] = "open"
                        rr.add_evidence(gate, note=f"reopened: item {item['id']} was redrafted for {sha[:10]}, so the earlier confirmation no longer covers it")
                        self.event(f"gate {gate_id} reopened because item {item['id']} is redrafted")

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
            f"The release commit is checked out on a scratch branch the runner named; ignore that name, the release branch is "
            f"{self.data['branch']}. See what the release changes with: git diff {self.data['base']}...HEAD",
            ("Use these level-2 headings exactly: " + "; ".join(f"## {h}" for h in headings)) if headings else "Plain Markdown.",
            "Your final message must be the finished document and nothing else: start with a level-1 heading, then the "
            "sections. No preface, no result block. This overrides the result format in your role text. " + self.SAFETY,
        ])
        brief = self.build_brief({
            "title": f"Draft {item['id']}: {item['title']}"[:80], "role": "builder",
            "branch": f"docs/release-draft-{self.branch_token()}-{item['id']}-{seq}", "base": f"origin/{self.data['branch']}",
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
            "branch": f"fix/release-fix-{self.branch_token()}-{item['id']}-{seq}", "base": f"origin/{self.data['branch']}",
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

    def merge_inbox(self) -> None:
        """Apply gate and route requests that people queued while the loop owned the checkpoint."""
        applied, problems = rr.drain_inbox(self.dir, self.data)
        for problem in problems:
            self.event(f"request refused: {problem}")
        if applied or problems:
            for path in applied:
                self.event(f"applied request {path.name}")
            self.checkpoint()
            for path in applied:
                path.unlink(missing_ok=True)

    def waiting_names(self) -> list[str]:
        """Gates the loop is waiting on. Only when nothing else can run and nothing is blocked."""
        if any(i.get("status") == "blocked" for i in self.data["items"] if rr.is_pc_item(i) and rr.is_applicable(i)):
            return []
        return rr.waiting_gates(self.data)

    def release_moved(self) -> bool:
        """Re-read the release branch tip. If it moved, the proof on the old commit is reset (ensure_worktree does that)."""
        old = self.sha()
        try:
            self.ensure_worktree()
        except LoopError:
            return False
        moved = self.sha() != old
        return self.staging_candidate_moved() or moved

    def step(self) -> tuple[str, str] | None:
        self.merge_inbox()
        self.hand_forbidden_to_hafiz()
        if rr.score(self.data)["prod_ready"]:
            if self.release_moved():
                self.checkpoint()
                return None  # somebody pushed to the release branch: check it again before declaring it ready
            return "ready_for_prod_go", ""
        reason = self.blocked_reason()
        if reason:
            return "blocked", reason
        if self.stop_requested():
            return "stopped", "a STOP file appeared"
        item = rr.next_item(self.data)
        if item is None:
            names = self.waiting_names()
            if names:
                return "waiting", ", ".join(names)
            return "blocked", self.nothing_runnable_reason()
        if self.loop.get("status") != "running":
            self.loop.update(status="running", reason="")
            self.loop.pop("waiting_for", None)
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
        if rr.score(self.data)["prod_ready"] and not self.release_moved():
            return "ready_for_prod_go", ""
        self.checkpoint()
        reason = self.blocked_reason()
        if reason:
            return "blocked", reason
        reason = self.stuck_reason()
        if reason:
            return "stuck", reason
        return None

    def wait_for_gates(self, names: str) -> None:
        """Not stuck and not blocked: every open item is a gate owned by a person. Sleep, re-read the checkpoint, carry on."""
        listed = [n.strip() for n in names.split(",")]
        if self.loop.get("status") != "waiting" or self.loop.get("waiting_for") != listed:
            self.loop.update(status="waiting", reason="", waiting_for=listed, waiting_since=rr.myt_text(), current=None)
            self.loop["fingerprints"] = [self.fingerprint()]  # waiting is not a round: the stuck rule starts again afterwards
            self.event(f"waiting_for_gate: {names}")
            self.write_report()
            self.checkpoint()
        for _ in range(max(1, self.wait_seconds // max(1, self.poll_seconds))):
            if self.stop_requested() or rr.pending_ops(self.dir):
                break
            self.sleep(self.poll_seconds)
        self.data = rr.load(self.path)  # re-read the checkpoint: a person may have changed it
        try:
            self.ensure_worktree()  # a new commit on the release branch resets the proof taken on the old one
            self.staging_candidate_moved()
            self.checkpoint()
        except LoopError as exc:
            self.log(f"could not refresh the release worktree while waiting: {exc}")

    def run(self) -> str:
        self.data = rr.load(self.path)
        errors = rr.validate(self.data)
        if errors:
            raise rr.ReadinessError("; ".join(errors))
        self.data.setdefault("loop", {})
        loop = self.loop
        previous = loop.get("current")
        loop.update(status="running", reason="")
        loop.pop("waiting_for", None)
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
            route_item = self.items().get("G0")
            if route_item is not None and route_item.get("status") != "green":
                raise LoopError("the route is not recorded (item G0): create the readiness file with init --route")
            if not self.stop_requested():
                self.ensure_worktree()
            loop["fingerprints"] = [self.fingerprint()]
            self.checkpoint()
            outcome: tuple[str, str] | None = None
            while True:
                outcome = self.step()
                if outcome is None:
                    continue
                if outcome[0] != "waiting":
                    break
                self.wait_for_gates(outcome[1])
        except rr.StopRequested:
            outcome = ("stopped", "a STOP file appeared")
        except LoopError as exc:
            outcome = ("blocked", str(exc))
        return self.conclude(*outcome)

    def conclude(self, status: str, reason: str) -> str:
        self.merge_inbox()
        self.loop.pop("waiting_for", None)
        self.loop.update(status=status, reason=reason, current=None, ended_at=rr.myt_text(), ended_at_utc=rr.now_utc().isoformat())
        self.event(f"loop {status}" + (f": {reason}" if reason else ""))
        self.write_report()
        if status == "ready_for_prod_go":
            (self.dir / "ready.flag").write_text(f"READY FOR YOUR GO (production deploy)\n{rr.myt_text()}\nroute {self.data.get('route')}\n"
                                                 f"release commit {self.sha()}\n")
        self.checkpoint()
        return status

    # ---- the report ----

    def section_lines(self, doc_path: str, heading: str, limit: int = 8, keep_blank: bool = False) -> list[str]:
        try:
            text = (self.dir / doc_path).read_text()
        except OSError:
            return []
        found = re.search(rf"(?ms)^##\s*{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)", text)
        return [ln for ln in (found.group(1).strip().splitlines() if found else []) if keep_blank or ln.strip()][:limit]

    def gate_state(self, gate: dict[str, Any]) -> str:
        if gate["applicable"] is False:
            return f"not applicable, {gate['na_reason']}"
        return gate["status"] + (" (SIMULATED proof run, not a real approval, merge or deploy)" if gate["simulated"] else "")

    def write_report(self) -> None:
        s = rr.score(self.data)
        loop = self.loop
        status = loop["status"]
        title = {"ready_for_prod_go": "READY FOR YOUR PRODUCTION GO", "waiting": "WAITING FOR YOUR GATES", "blocked": "BLOCKED",
                 "stuck": "STUCK", "stopped": "STOPPED"}.get(status, status.upper())
        items = self.items()
        prs = ", ".join(f"#{n}" for n in self.data.get("pr_numbers", [])) or "branch only"
        route = self.data.get("route", "")
        staging = [items[i] for i in ("S1", "S2", "S3") if i in items and rr.is_applicable(items[i])]
        staged = bool(staging) and all(g.get("status") == "green" for g in staging)
        simulated = [g for g in s["gates"] if g["simulated"]]
        if route == "staging-first" and staged:
            proven = "staging deployed and staging smoke checked (evidence on gates S1 to S3); not merged to main, not deployed to production"
        else:
            proven = "not merged, not deployed"
        before_open = [g for g in s["gates"] if g["applicable"] and not g["after_go"] and g["status"] != "green"]
        after_go = [g for g in s["gates"] if g["applicable"] and g["after_go"]]
        lines = [f"# Release report: {self.data['release']}", "",
                 f"**{title}** at {loop.get('ended_at') or rr.myt_text()}" + (f" ({loop['reason']})" if loop.get("reason") else ""),
                 f"Route: {route}. PC readiness {s['percent']}%. Prod readiness {s['prod_percent']}%.", ""]
        if status == "waiting":
            lines += [f"waiting_for_gate: {', '.join(loop.get('waiting_for', []))}. The loop keeps running and continues by itself "
                      "the moment a gate gets evidence (pc_release.py gate).", ""]
        if simulated:
            lines += ["**SIMULATED gates in this report: " + ", ".join(g["id"] for g in simulated)
                      + ". They were closed for a proof run. Nothing was really merged, deployed or approved.**", ""]
        lines += ["## Release state", "",
                  f"- Source: branch {self.data['branch']} ({prs}) on {self.data['github_repo']}, commit {self.sha() or 'unknown'}.",
                  f"- Highest proven state: {proven}. "
                  + ("Every item before your production go is closed on that commit." if s["prod_ready"]
                     else f"{s['pc_green']} of {s['pc_total']} PC items are green."),
                  "- What proves it: the evidence per item below, and the files in release-pack/.",
                  "- Normal smoke: " + ("on staging, see gate S3; production smoke is after your go." if route == "staging-first"
                                        else "not run. Production smoke is after your go (G5)."),
                  "- Change smoke: planned in release-pack/10-smoke-monitoring.md. "
                  + ("Staging run is gate S3; the production run is after your go (G5)." if route == "staging-first"
                     else "It runs after your go (G5)."),
                  "- What is not proven yet: "
                  + ("; ".join(f"{g['id']} {g['title']}" for g in before_open + after_go if g["status"] != "green") or "none")
                  + (f"; PC items not done: {', '.join(s['open_pc'] + s['blocked_pc'])}" if s["open_pc"] or s["blocked_pc"] else "") + ".",
                  ]
        impact = self.section_lines("release-pack/01-scope.md", "Who is affected")
        cleaned = [re.sub(r"^\s*[-*]\s*", "", ln).strip() for ln in impact]
        lines.append("- User impact: " + ("; ".join(cleaned) if cleaned else "see release-pack/01-scope.md (not drafted)"))
        seven = items.get("7")
        if seven and seven.get("status") == "na":
            lines.append(f"- Staff documentation: not relevant, {seven.get('na_reason')}")
        elif seven:
            lines.append(f"- Staff documentation: {seven.get('status')} (item 7); the decision is in the release's own ledger.")
        lines += ["- Recommended next: " + (
                      "read release-pack/11-review-page.md, then say go and run the deploy commands below yourself."
                      if s["prod_ready"] else
                      "close the gates listed above (pc_release.py gate); the loop continues by itself." if status == "waiting" else
                      "fix what the loop could not, then start it again (it resumes)."),
                  "- Decision needed: " + ("yes. The production deploy go is yours." if s["prod_ready"]
                                           else "yes. See the top of this report."), "",
                  "## PC readiness", "", f"{s['percent']}% ({s['pc_green']} of {s['pc_total']} applicable PC items green)", "",
                  "| Item | Status | Evidence |", "| --- | --- | --- |"]
        for item in self.data["items"]:
            if not rr.is_pc_item(item) and not item.get("original_owner"):
                continue
            if item.get("status") == "na" or item.get("applicable") is False:
                lines.append(f"| {item['id']} {item['title']} | not applicable | {item.get('na_reason', '')} |")
                continue
            evidence = item.get("evidence", [])
            greens = [e for e in evidence if e.get("note", "").startswith("green:")]
            summary = greens[-1]["note"].removeprefix("green: ") if greens else (self.describe(evidence[-1]) if evidence else "")
            proof = [self.describe(e) for e in evidence if not e.get("note")][-2:]
            what = "; ".join([summary.replace("|", "/")] + proof) if (summary or proof) else "none"
            owner = " (handed to Hafiz)" if item.get("original_owner") else ""
            lines.append(f"| {item['id']} {item['title']}{owner} | {item.get('status')} | {what} |")
        lines += ["", "## Prod readiness", "",
                  f"{s['prod_percent']}% ({s['prod_green']} of {s['prod_total']} items before your production go are green): "
                  "the PC items plus the gates of this route. The deploy go, production smoke, monitoring and acceptance are never counted.", "",
                  "## Gates before your go (counted in Prod readiness; the PC never does these)", ""]
        for g in s["gates"]:
            if not g["after_go"]:
                lines.append(f"- {g['id']} {g['title']} [{g['owner']}]: {self.gate_state(g)}")
        lines += ["", "## After your go (listed, never counted)", ""]
        for g in s["gates"]:
            if g["after_go"]:
                lines.append(f"- {g['id']} {g['title']} [{g['owner']}]: {self.gate_state(g)}")
        commands = self.section_lines("release-pack/09-deploy-plan.md", "Commands in order", limit=80, keep_blank=True)
        if commands:
            lines += ["", "## Exact deploy commands the plan lists (the PC never runs them; the go is yours)", ""] + commands
        jobs = loop.get("jobs", [])
        elapsed = ""
        if loop.get("started_at_utc"):
            end = loop.get("ended_at_utc") or rr.now_utc().isoformat()
            secs = (dt.datetime.fromisoformat(end) - dt.datetime.fromisoformat(loop["started_at_utc"])).total_seconds()
            elapsed = f"{int(secs // 60)} min {int(secs % 60)} s"
        lines += ["", "## What the loop did", "",
                  f"- Started {loop.get('started_at')}" + (f", ended {loop['ended_at']}" if loop.get("ended_at") else "")
                  + (f", {elapsed}." if elapsed else "."),
                  f"- {loop.get('rounds', 0)} rounds, {len(jobs)} Claude jobs, "
                  f"{sum(int(j.get('turns') or 0) for j in jobs)} turns, list-price equivalent "
                  f"${sum(float(j.get('cost_usd') or 0) for j in jobs):.2f} (billed to the subscription, no cap).",
                  ("- The loop deployed STAGING only, through the staging deploy script (target "
                   f"{self.data['staging'].get('target')}, evidence on S1 to S3). Nothing was merged, deployed to production, or written to production."
                   if self.data.get("staging") else
                   "- Nothing was merged, deployed, migrated or written to production by the loop.")]
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
    return rr.acquire_lock(Path(path).parent)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("run"); p.add_argument("readiness", type=Path)
    p.add_argument("--clear-stop", action="store_true"); p.add_argument("--drop-task")
    p.add_argument("--repo", type=Path); p.add_argument("--claude"); p.add_argument("--worktrees", type=Path)
    args = parser.parse_args(argv)
    lock = None
    for _ in range(6):  # a gate request holds the lock for a moment; wait it out before saying a loop is already running
        lock = acquire_lock(args.readiness)
        if lock is not None:
            break
        time.sleep(1)
    if lock is None:
        print("Another loop is already running on this readiness file.")
        return 3
    import pc_job
    pc_job.prefer_linux_user_tools()
    try:
        runner = PcJobRunner(args.readiness.parent, repo_root=args.repo, claude=args.claude, worktrees=args.worktrees)
        loop = Loop(args.readiness, runner, rr.RealShell(), repo_root=args.repo, worktrees=args.worktrees,
                    clear_stop=args.clear_stop)
        try:
            status = loop.run()
        except rr.ReadinessError as exc:
            print(f"REFUSED: {exc}")
            return 2
        print(f"Loop finished: {status}")
        return 0 if status == "ready_for_prod_go" else 1
    finally:
        if args.drop_task:
            from shutil import which
            if which("schtasks.exe"):
                import subprocess
                subprocess.run(["schtasks.exe", "/delete", "/tn", args.drop_task, "/f"], capture_output=True, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
