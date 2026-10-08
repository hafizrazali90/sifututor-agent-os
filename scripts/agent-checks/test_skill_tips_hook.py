#!/usr/bin/env python3
"""Tests for the skill tips file, the tip and suggestion hook, and their wiring (issue #331).

Run: python3 -m unittest scripts/agent-checks/test_skill_tips_hook.py  (or pytest)

SKILL_TIPS_HOOK_PATH points the tests at another copy of the hook. The negative
controls use it to prove the quiet and cap tests fail on a broken copy.
"""

from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = Path(os.environ.get("SKILL_TIPS_HOOK_PATH") or ROOT / "scripts" / "agent-checks" / "skill-tips-hook.py")
TIPS_PATH = ROOT / "docs" / "agent-playbooks" / "skill-tips.json"
COMMAND_PATH = ROOT / ".claude" / "commands" / "skills.md"
TEMPLATE_PATH = ROOT / ".claude" / "settings.template.json"
CODEX_CONFIG = ROOT / ".codex" / "config.toml"
GLOBAL_SKILLS = Path.home() / ".claude" / "skills"

RETIRED = {
    "understand", "understand-chat", "understand-diff", "understand-explain", "understand-dashboard",
    "understand-knowledge", "caveman", "orchestrate", "generate-tests", "friction-review",
    "finch-save-session", "lls-frontend-save-session", "ripple-complexity-auditor", "ripple-next",
    "ripple-start", "ripple-treq", "github-actions",
}
GROUPS = {"start", "build", "test", "review", "commit", "ops", "design", "help"}


def load_hook():
    spec = importlib.util.spec_from_file_location("skill_tips_hook_under_test", HOOK_PATH)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


hook = load_hook()


def entries_for(agent: str = "claude") -> list[dict]:
    return hook.load_entries(TIPS_PATH, agent)


def suggest(prompt: str, state: dict | None = None, **kw):
    state = state if state is not None else hook.empty_state()
    item = hook.decide_suggestion(prompt, entries_for(kw.pop("agent", "claude")), state, **kw)
    return item["name"] if item else None


class MatchingAccepts(unittest.TestCase):
    CASES = [
        ("I think the invoice page is broken, can you find the root cause please", "diagnose"),
        ("please run the smoke test on staging before we ship this release", "qa"),
        ("looks good now, can you commit this with the right message", "commit"),
        ("let's brainstorm how the tutor profile page should work for parents", "brainstorm"),
        ("turn this into issues so we can build them one by one later", "to-issues"),
        ("that is enough for today so wrap up and save what we learned", "save-session"),
        ("can you do a code review of the payment change before I merge it", "review"),
        ("I want you to grill me on this plan before we start building", "grill-me"),
        ("Can you hand off this work to Codex so it can keep going", "handoff"),
    ]

    def test_right_prompts_get_the_right_skill(self) -> None:
        for prompt, expected in self.CASES:
            with self.subTest(prompt=prompt):
                self.assertEqual(suggest(prompt), expected)

    def test_match_is_case_insensitive_and_handles_curly_apostrophes(self) -> None:
        self.assertEqual(suggest("The Parent Payments Page ISN’T working after the last deploy"), "diagnose")


class MatchingRejects(unittest.TestCase):
    def test_prompt_with_no_trigger_gets_nothing(self) -> None:
        self.assertIsNone(suggest("please rename the variable in the payment page to something clearer"))

    def test_very_short_prompts_get_nothing(self) -> None:
        for prompt in ["commit this", "root cause?", "wrap up", "smoke test now"]:
            with self.subTest(prompt=prompt):
                self.assertIsNone(suggest(prompt))

    def test_prompts_that_name_a_skill_get_nothing(self) -> None:
        for prompt in [
            "use /commit this time and write the message in the usual format please",
            "run $verify on this and then tell me if the root cause is fixed",
            "please do the save-session routine now because we are done for today",
        ]:
            with self.subTest(prompt=prompt):
                self.assertIsNone(suggest(prompt))

    def test_a_named_skill_counts_as_used(self) -> None:
        state = hook.empty_state()
        self.assertIsNone(suggest("run /commit now and then look at the root cause of the failure", state))
        self.assertIn("commit", state["used"])

    def test_slash_and_injected_starts_get_nothing(self) -> None:
        for prompt in [
            "/review the payment change for hidden risks before the merge today",
            "<task-notification> the root cause of the failing build was found here",
            "[Artifact comment sent to Claude] please run the smoke test on this page",
        ]:
            with self.subTest(prompt=prompt):
                self.assertIsNone(suggest(prompt))

    def test_replies_to_a_question_get_nothing(self) -> None:
        self.assertIsNone(suggest("find the root cause of the invoice problem for me please", asked_question=True))
        for prompt in [
            "yes please commit this with the right message and then push it",
            "option 2, and then find the root cause of the problem after that",
            "ok go ahead and run the smoke test on staging for the change",
        ]:
            with self.subTest(prompt=prompt):
                self.assertIsNone(suggest(prompt))

    def test_word_boundaries_stop_partial_matches(self) -> None:
        self.assertIsNone(suggest("the commit itself looks fine but the label on the button is wrong"))
        self.assertIsNone(suggest("my snapshots folder is full of old files that should be cleaned"))

    def test_project_skill_needs_its_project(self) -> None:
        prompt = "will this break the app that tutors already have installed on their phones"
        self.assertIsNone(suggest(prompt, cwd="/work/ripple-suite"))
        self.assertEqual(suggest(prompt, cwd="/work/Sifututor/sifu-tutor"), "mobile-pre-push-qa")
        self.assertEqual(suggest(prompt + " in sims", cwd="/work/Sifututor"), "mobile-pre-push-qa")

    def test_agent_filter_hides_the_other_tools_skills(self) -> None:
        self.assertNotIn("quick-check", [e["name"] for e in entries_for("claude")])
        self.assertIn("quick-check", [e["name"] for e in entries_for("codex")])
        self.assertNotIn("triage", [e["name"] for e in entries_for("codex")])


class QuietSessionRules(unittest.TestCase):
    def test_same_skill_is_never_suggested_twice(self) -> None:
        state = hook.empty_state()
        prompt = "can you find the root cause of the failing invoice page for me"
        self.assertEqual(suggest(prompt, state), "diagnose")
        self.assertIsNone(suggest(prompt, state))

    def test_a_skill_already_used_is_not_suggested(self) -> None:
        state = hook.empty_state()
        state["used"].append("diagnose")
        self.assertIsNone(suggest("can you find the root cause of the failing invoice page", state))

    def test_at_most_three_suggestions_per_session(self) -> None:
        state = hook.empty_state()
        prompts = [
            "can you find the root cause of the failing invoice page for me",
            "please run the smoke test on staging before we ship this release",
            "looks good now, can you commit this with the right message please",
            "let's brainstorm how the tutor profile page should work for parents",
            "that is enough for today so wrap up and save what we learned",
        ]
        results = [suggest(p, state) for p in prompts]
        self.assertEqual([r for r in results if r], ["diagnose", "qa", "commit"])
        self.assertEqual(len(state["suggested"]), 3)

    def test_one_suggestion_per_prompt(self) -> None:
        both = "can you commit this and also find the root cause of the failing invoice page"
        state = hook.empty_state()
        self.assertIsNotNone(suggest(both, state))
        self.assertEqual(len(state["suggested"]), 1)


class RunAndFailOpen(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.state_dir = Path(self.tmp.name) / "state"
        patcher = mock.patch.dict(os.environ, {
            "SIFUTUTOR_SKILL_TIPS_STATE_DIR": str(self.state_dir),
            "SIFUTUTOR_SKILL_TIPS_FILE": str(TIPS_PATH),
            "SIFUTUTOR_SKILL_TIPS": "1",
        })
        patcher.start()
        self.addCleanup(patcher.stop)

    def payload(self, prompt: str, session: str = "sess-1", **kw) -> dict:
        return {"session_id": session, "prompt": prompt, **kw}

    def test_state_directory_is_created_when_missing(self) -> None:
        self.assertFalse(self.state_dir.exists())
        out = hook.run("suggest", "claude", self.payload("can you find the root cause of the failing invoice page"))
        self.assertTrue(out.startswith("Suggestion: /diagnose could help here: "))
        self.assertTrue((self.state_dir / "sess-1.json").is_file())

    def test_suggestion_survives_between_calls_in_one_session(self) -> None:
        prompt = "can you find the root cause of the failing invoice page"
        self.assertIsNotNone(hook.run("suggest", "claude", self.payload(prompt)))
        self.assertIsNone(hook.run("suggest", "claude", self.payload(prompt)))
        self.assertIsNotNone(hook.run("suggest", "claude", self.payload(prompt, session="sess-2")))

    def test_broken_tips_file_prints_nothing(self) -> None:
        for content in ["{ not json", "[]", '{"skills": "oops"}', '{"skills": [{"name": 3}]}', ""]:
            with self.subTest(content=content):
                broken = Path(self.tmp.name) / "broken.json"
                broken.write_text(content)
                with mock.patch.dict(os.environ, {"SIFUTUTOR_SKILL_TIPS_FILE": str(broken)}):
                    self.assertIsNone(hook.run("suggest", "claude", self.payload("find the root cause of the invoice bug")))
                    self.assertIsNone(hook.run("tip", "claude", {"session_id": "s", "tool_input": {"skill": "commit"}}))

    def test_missing_tips_file_prints_nothing(self) -> None:
        with mock.patch.dict(os.environ, {"SIFUTUTOR_SKILL_TIPS_FILE": str(Path(self.tmp.name) / "nope.json")}):
            self.assertIsNone(hook.run("suggest", "claude", self.payload("find the root cause of the invoice bug")))

    def test_unwritable_state_directory_prints_nothing(self) -> None:
        blocker = Path(self.tmp.name) / "file-not-dir"
        blocker.write_text("x")
        with mock.patch.dict(os.environ, {"SIFUTUTOR_SKILL_TIPS_STATE_DIR": str(blocker / "child")}):
            self.assertIsNone(hook.run("suggest", "claude", self.payload("can you find the root cause of the failing invoice page")))

    def test_corrupt_state_file_is_treated_as_empty(self) -> None:
        self.state_dir.mkdir(parents=True)
        (self.state_dir / "sess-1.json").write_text("{ broken")
        out = hook.run("suggest", "claude", self.payload("can you find the root cause of the failing invoice page"))
        self.assertIn("/diagnose", out)

    def test_missing_or_bad_session_id_prints_nothing(self) -> None:
        for sid in [None, "", "../escape", "a/b", "x" * 200, 7]:
            with self.subTest(sid=sid):
                self.assertIsNone(hook.run("suggest", "claude", {"session_id": sid, "prompt": "can you find the root cause of the failing page"}))

    def test_kill_switch(self) -> None:
        with mock.patch.dict(os.environ, {"SIFUTUTOR_SKILL_TIPS": "0"}):
            self.assertIsNone(hook.run("suggest", "claude", self.payload("can you find the root cause of the failing invoice page")))

    def test_main_never_fails_on_bad_input(self) -> None:
        env = {**os.environ, "SIFUTUTOR_SKILL_TIPS_STATE_DIR": str(self.state_dir)}
        for stdin in ["", "not json at all", "[1, 2]", "null", '{"prompt": 5, "session_id": "s"}']:
            for mode in ("--suggest", "--tip", "--nonsense"):
                with self.subTest(stdin=stdin, mode=mode):
                    proc = subprocess.run([sys.executable, str(HOOK_PATH), mode], input=stdin, capture_output=True, text=True, env=env, timeout=10)
                    self.assertEqual(proc.returncode, 0)
                    self.assertEqual(proc.stdout.strip(), "")

    def test_main_prints_one_json_line_with_context(self) -> None:
        env = {**os.environ, "SIFUTUTOR_SKILL_TIPS_STATE_DIR": str(self.state_dir)}
        body = json.dumps(self.payload("can you find the root cause of the failing invoice page"))
        proc = subprocess.run([sys.executable, str(HOOK_PATH), "--suggest"], input=body, capture_output=True, text=True, env=env, timeout=10)
        self.assertEqual(proc.returncode, 0)
        out = json.loads(proc.stdout)["hookSpecificOutput"]
        self.assertEqual(out["hookEventName"], "UserPromptSubmit")
        self.assertTrue(out["additionalContext"].splitlines()[0].startswith("Suggestion: /diagnose could help here: "))

    def test_codex_mode_marks_continue_and_hides_claude_only_skills(self) -> None:
        env = {**os.environ, "SIFUTUTOR_SKILL_TIPS_STATE_DIR": str(self.state_dir)}
        body = json.dumps(self.payload("let's go through the issues one by one now"))
        proc = subprocess.run([sys.executable, str(HOOK_PATH), "--suggest", "--agent", "codex"], input=body, capture_output=True, text=True, env=env, timeout=10)
        self.assertEqual(proc.returncode, 0)
        self.assertEqual(proc.stdout.strip(), "", "triage is Claude only")
        body = json.dumps(self.payload("is the workflow working and wired correctly right now", session="s2"))
        proc = subprocess.run([sys.executable, str(HOOK_PATH), "--suggest", "--agent", "codex"], input=body, capture_output=True, text=True, env=env, timeout=10)
        data = json.loads(proc.stdout)
        self.assertTrue(data["continue"])
        self.assertIn("Suggestion: /quick-check", data["hookSpecificOutput"]["additionalContext"])

    def test_reply_detection_reads_the_transcript_tail(self) -> None:
        transcript = Path(self.tmp.name) / "t.jsonl"
        def write(last_text: str) -> None:
            rows = [
                {"type": "assistant", "message": {"content": [{"type": "text", "text": "Earlier statement."}]}},
                {"type": "user", "message": {"content": "hello"}},
                {"type": "assistant", "message": {"content": [{"type": "tool_use", "name": "Bash"}]}},
                {"type": "assistant", "message": {"content": [{"type": "text", "text": last_text}]}},
            ]
            transcript.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
        prompt = "can you find the root cause of the failing invoice page"
        write("Do you want me to start with the invoice page?")
        self.assertTrue(hook.last_assistant_asked_question(str(transcript)))
        self.assertIsNone(hook.run("suggest", "claude", self.payload(prompt, transcript_path=str(transcript))))
        write("Done. The invoice page is fixed.")
        self.assertFalse(hook.last_assistant_asked_question(str(transcript)))
        self.assertIsNotNone(hook.run("suggest", "claude", self.payload(prompt, session="sess-9", transcript_path=str(transcript))))
        self.assertFalse(hook.last_assistant_asked_question(str(Path(self.tmp.name) / "missing.jsonl")))
        self.assertFalse(hook.last_assistant_asked_question(""))

    def test_tip_format_and_once_per_skill(self) -> None:
        payload = {"session_id": "tip-1", "tool_name": "Skill", "tool_input": {"skill": "commit"}}
        first = hook.run("tip", "claude", payload)
        tip = next(e["tip"] for e in entries_for() if e["name"] == "commit")
        self.assertEqual(first.splitlines()[0], f"Tip: /commit: {tip}")
        self.assertIsNone(hook.run("tip", "claude", payload))
        other = hook.run("tip", "claude", {**payload, "tool_input": {"skill": "verify"}})
        self.assertTrue(other.startswith("Tip: /verify: "))
        self.assertIn("Show Hafiz this line once", other)

    def test_tip_ignores_unknown_and_retired_skills_and_accepts_plugin_prefix(self) -> None:
        base = {"session_id": "tip-2", "tool_name": "Skill"}
        self.assertIsNone(hook.run("tip", "claude", {**base, "tool_input": {"skill": "orchestrate"}}))
        self.assertIsNone(hook.run("tip", "claude", {**base, "tool_input": {}}))
        self.assertTrue(hook.run("tip", "claude", {**base, "tool_input": {"skill": "myplugin:diagnose"}}).startswith("Tip: /diagnose: "))

    def test_used_skill_is_not_suggested_afterwards(self) -> None:
        hook.run("tip", "claude", {"session_id": "mix", "tool_name": "Skill", "tool_input": {"skill": "diagnose"}})
        self.assertIsNone(hook.run("suggest", "claude", self.payload("can you find the root cause of the failing invoice page", session="mix")))

    def test_decision_is_fast(self) -> None:
        entries = entries_for()
        prompts = ["can you find the root cause of the failing invoice page"] * 200
        start = time.perf_counter()
        for prompt in prompts:
            hook.decide_suggestion(prompt, entries, hook.empty_state())
        per_call_ms = (time.perf_counter() - start) * 1000 / len(prompts)
        self.assertLess(per_call_ms, 10)


class TipsFile(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.data = json.loads(TIPS_PATH.read_text(encoding="utf-8"))
        cls.skills = cls.data["skills"]

    def test_names_are_unique(self) -> None:
        names = [e["name"] for e in self.skills]
        self.assertEqual(len(names), len(set(names)))

    def test_retired_skills_are_absent_everywhere(self) -> None:
        names = {e["name"] for e in self.skills}
        self.assertEqual(names & RETIRED, set())
        text = TIPS_PATH.read_text(encoding="utf-8")
        command = COMMAND_PATH.read_text(encoding="utf-8") if COMMAND_PATH.exists() else ""
        for name in RETIRED:
            # A retired name is only a problem when used as a skill name, not as an ordinary word.
            self.assertNotIn(f'"name": "{name}"', text, name)
            self.assertIsNone(re.search(r"[`](/|\$)" + re.escape(name) + r"[`]", command), name)

    def test_every_tip_is_one_plain_sentence(self) -> None:
        for e in self.skills:
            tip = e["tip"]
            with self.subTest(skill=e["name"]):
                self.assertTrue(tip.endswith("."), tip)
                self.assertEqual(len(re.split(r"(?<=[.!?])\s+", tip)), 1, tip)
                self.assertLessEqual(len(tip), 200)
                self.assertGreaterEqual(len(tip.split()), 6)

    def test_reasons_are_short_single_phrases(self) -> None:
        for e in self.skills:
            with self.subTest(skill=e["name"]):
                self.assertTrue(e["reason"].endswith("."))
                self.assertEqual(len(re.split(r"(?<=[.!?])\s+", e["reason"])), 1)
                self.assertLessEqual(len(e["reason"]), 120)

    def test_no_em_dashes(self) -> None:
        self.assertNotIn("—", TIPS_PATH.read_text(encoding="utf-8"))
        self.assertNotIn("—", COMMAND_PATH.read_text(encoding="utf-8"))

    def test_triggers_are_two_to_six_lowercase_phrases(self) -> None:
        for e in self.skills:
            with self.subTest(skill=e["name"]):
                self.assertTrue(2 <= len(e["triggers"]) <= 6, e["triggers"])
                for trigger in e["triggers"]:
                    self.assertEqual(trigger, trigger.lower())
                    self.assertGreaterEqual(len(trigger), 3)
                    self.assertEqual(trigger, trigger.strip())

    def test_required_fields_and_values(self) -> None:
        for e in self.skills:
            with self.subTest(skill=e["name"]):
                self.assertIn(e["group"], GROUPS)
                self.assertTrue(e["agents"] and set(e["agents"]) <= {"claude", "codex"})
                self.assertTrue(e["where"] and set(e["where"]) <= {"global", "agents", "repo-claude", "commands"})
                self.assertRegex(e["name"], r"^[a-z][a-z0-9-]*$")

    def test_no_two_skills_share_a_trigger_for_the_same_agent(self) -> None:
        for agent in ("claude", "codex"):
            seen: dict[str, str] = {}
            for e in self.skills:
                if agent not in e["agents"]:
                    continue
                for trigger in e["triggers"]:
                    self.assertNotIn(trigger, seen, f"{trigger!r} used by {seen.get(trigger)} and {e['name']} for {agent}")
                    seen[trigger] = e["name"]

    def test_every_entry_points_to_a_skill_that_exists(self) -> None:
        roots = {
            "agents": lambda n: ROOT / ".agents" / "skills" / n / "SKILL.md",
            "repo-claude": lambda n: ROOT / ".claude" / "skills" / n / "SKILL.md",
            "commands": lambda n: ROOT / ".claude" / "commands" / f"{n}.md",
            "global": lambda n: GLOBAL_SKILLS / n / "SKILL.md",
        }
        for e in self.skills:
            for where in e["where"]:
                if where == "global" and not GLOBAL_SKILLS.is_dir():
                    continue  # CI or a fresh machine has no personal skills folder
                if where == "repo-claude" and not (ROOT / ".claude" / "skills").is_dir():
                    continue  # .claude/skills is not tracked, so a fresh checkout or worktree lacks it
                with self.subTest(skill=e["name"], where=where):
                    self.assertTrue(roots[where](e["name"]).is_file(), roots[where](e["name"]))

    def test_every_umbrella_skill_has_a_tip(self) -> None:
        folder = ROOT / ".agents" / "skills"
        names = {e["name"] for e in self.skills}
        for path in folder.iterdir():
            if (path / "SKILL.md").is_file():
                self.assertIn(path.name, names, f".agents/skills/{path.name} has no entry in skill-tips.json")

    def test_every_tip_appears_in_the_skills_command(self) -> None:
        command = COMMAND_PATH.read_text(encoding="utf-8")
        for e in self.skills:
            with self.subTest(skill=e["name"]):
                self.assertIn(e["tip"], command)
                self.assertRegex(command, r"[`](/|\$)" + re.escape(e["name"]) + r"[`]")

    def test_skills_command_has_a_description(self) -> None:
        self.assertRegex(COMMAND_PATH.read_text(encoding="utf-8"), r"^---\ndescription: .+\n---\n")


class Wiring(unittest.TestCase):
    def test_claude_template_wires_both_hooks(self) -> None:
        template = json.loads(TEMPLATE_PATH.read_text())
        post = [(m["matcher"], h["command"]) for m in template["hooks"]["PostToolUse"] for h in m["hooks"]]
        prompt = [h["command"] for m in template["hooks"]["UserPromptSubmit"] for h in m["hooks"]]
        self.assertTrue(any(mt == "Skill" and c.endswith("skill-tips-hook.py --tip") for mt, c in post), post)
        self.assertTrue(any(c.endswith("skill-tips-hook.py --suggest") for c in prompt), prompt)

    def test_codex_config_wires_the_suggestion_with_the_git_root_pattern(self) -> None:
        text = CODEX_CONFIG.read_text()
        self.assertIn('"$(git rev-parse --show-toplevel)"/scripts/agent-checks/skill-tips-hook.py --suggest --agent codex', text)

    def test_hook_script_has_no_network_or_secret_reads(self) -> None:
        source = HOOK_PATH.read_text()
        for word in ("urllib", "socket", "requests", "http.client", "subprocess"):
            self.assertNotIn(word, source)
        self.assertIsNone(re.search(r"\.env(?![a-z])", source), "the hook must not name a dotenv file")


if __name__ == "__main__":
    unittest.main()
