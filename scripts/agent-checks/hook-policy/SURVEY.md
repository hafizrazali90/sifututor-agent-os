# hook-policy: live-hook parity harness (issue #161, PR #175)

**This PR is a tested parity harness, not completed consolidation.** The only
live behaviour it changes is one regex in `scripts/agent-checks/codex-pre-tool-use.py`
(issue #177). No hook was moved, merged, re-registered, or removed. This
directory owns no policy: every rule lives in the live script the harness
invokes.

## Files

```text
parity_harness.py       fixtures + subprocess runner over the live hooks + md5 drift report
test_parity_harness.py  the tests (unittest); one skip when no sub-projects are reachable
measure.py              latency and false-block rate of the live hooks over the same fixtures
SURVEY.md               this file
```

Run:

```bash
python3 -m unittest discover -s scripts/agent-checks/hook-policy -p 'test_*.py'
python3 scripts/agent-checks/hook-policy/parity_harness.py   # parity + drift table
python3 scripts/agent-checks/hook-policy/measure.py          # JSON latency report
```

From a worktree (no sub-project checkouts under the repo root) set
`SIFUTUTOR_WORKSPACE_ROOT=~/Projects/Sifututor` to get the drift table; without
it the drift test skips and says so.

## Authoritative hook per policy

| Policy | Authoritative live script | Registered by | Fixtures |
|---|---|---|---|
| Branch name (`type/kebab`) for Claude | `.claude/hooks/validate-branch-name.py` (umbrella) | umbrella `.claude/settings.json` (gitignored), sub-project `settings.json` pointing at each project's own copy | `BRANCH_FIXTURES` (12) |
| Conventional Commits for Claude | `.claude/hooks/conventional-commits.py` (umbrella) | same as above | `COMMIT_FIXTURES` (9) |
| Branch name for Codex | `scripts/agent-checks/codex-pre-tool-use.py` lines 110 to 119 (inline copy of the same rule) | `.codex/config.toml` | `BRANCH_FIXTURES` (12), run against this script too |
| `--no-verify`, `git reset --hard`, `git checkout --`, `rm -rf live|.workflow-rollout`, `.env` reads, HEREDOC commits (Codex) | `scripts/agent-checks/codex-pre-tool-use.py` | `.codex/config.toml` | `CODEX_FIXTURES` (17) |
| Hook path resolution for umbrella vs project launches | `scripts/agent-checks/claude_hook_dispatch.py` `audit_project_hook_configuration()` | n/a (audit) | planted temp fixture |
| Secret and command safety | `scripts/agent-checks/secret_output_guard.py` | umbrella `settings.json`, `run-shared-hook.sh` | not in this harness; it has its own tests |
| `quality-gate.py`, `workflow-gate.py`, `session-start.py`, `memory-flush.py` | each sub-project's own copy; the umbrella files of the same name are dispatcher wrappers that hand off to the project copy | sub-project `settings.json` | none (see cutover map, step 4) |

The Codex branch-name rule is a second implementation of the Claude one. The
harness runs the same 12 fixtures against both and both agree today; that is
the parity claim, not a merge.

## Issue #177 fix (the one live change)

Old guard: `git\s+checkout\s+--\b`. `\b` after `--` only matches when a word
character follows with no space, so `git checkout -- file.txt` and a bare
`git checkout --` were allowed.

New guard: `git\s+checkout\s+--(?:\s|$|\b)`. Every other rule in the file is
byte-identical. Regression fixtures in `CODEX_FIXTURES` and named tests:
`git checkout -- file.txt` (deny), `git checkout --` (deny),
`git status && git checkout -- src/` (deny), `git checkout --foo` (still
deny), `git checkout -b feat/x` (still allow).

## Drift table (md5, computed 2026-09-22 by `parity_harness.drift_report`)

Umbrella copies: `validate-branch-name.py` = `9aaece19`,
`conventional-commits.py` = `81ba4d42`. Every sub-project copy differs from
the umbrella copy. Rows are grouped by identical md5; the harness prints one
row per directory.

| Hook | md5 | Sub-projects carrying that body |
|---|---|---|
| `validate-branch-name.py` | `1f3a003a` | ripple-suite, sifututor_tutor, lls, lls-frontend, lls-mobile |
| `validate-branch-name.py` | `87f1474a` | sifu-tutor (and its seven `sifu-tutor-*` task worktrees) |
| `validate-branch-name.py` | `a1f184ea` | creative-hub |
| `validate-branch-name.py` | absent | cx-call-capture-android, finch-inbox, kelas, sifututor_parent, sims-owner-analytics |
| `conventional-commits.py` | `c16699d2` | ripple-suite, sifu-tutor (and its task worktrees) |
| `conventional-commits.py` | `9840c798` | sifututor_tutor |
| `conventional-commits.py` | `97bccf5e` | lls |
| `conventional-commits.py` | `d653e3ec` | lls-frontend |
| `conventional-commits.py` | `8ef4e72f` | lls-mobile |
| `conventional-commits.py` | `77a3f6b6` | creative-hub |
| `conventional-commits.py` | absent | cx-call-capture-android, finch-inbox, kelas, sifututor_parent, sims-owner-analytics |

Diffed against the umbrella `validate-branch-name.py` on 2026-09-22: the
`1f3a003a` body and creative-hub's `a1f184ea` body lack the `nakngaji-*`
deployment and `release/*` allowlists and exit 1 on malformed JSON (the
umbrella exits 0); sifu-tutor's `87f1474a` body is narrower still, with base
branches `main master develop staging dev` only and no deployment or release
allowlist at all. The `conventional-commits.py` bodies were not diffed here.

`sims-owner-analytics` is absent because it already has no hook logic of its
own: its `.claude/hooks/run-shared-hook.sh` resolves the umbrella script and
`exec`s it. That is the end state the cutover map moves the others to. The
earlier version of this file claimed the umbrella copy of
`validate-branch-name.py` matched ripple-suite; it does not, and that claim is
withdrawn. Reconverging these copies is issue #176, not this PR.

## Cutover and removal map (future, none of it done here)

There is one source of truth per policy (the table above). Each step below
replaces a duplicate with a hand-off to that source and names the evidence
required before it may land.

**Step 0 (this PR).** Harness + #177 fix. Evidence: both suites green, 50/50
fixtures match, `claude_hook_dispatch.py --root ~/Projects/Sifututor` reports
60/60 resolvable, 0 blocking.

**Step 1 (issue #176, one PR per project, in this order):** ripple-suite,
sifututor_tutor, lls, lls-frontend, lls-mobile, creative-hub, then sifu-tutor
last because its copy differs most from the umbrella rule (narrower base and
deployment allowlists), so its behaviour change is the largest. In each
project, replace `.claude/hooks/validate-branch-name.py` and
`.claude/hooks/conventional-commits.py` with a byte-identical copy of the
umbrella file. `settings.json` is not edited in this step. The `sifu-tutor-*`
task worktrees are not edited; they pick the change up when rebased.
Evidence before merge: `drift_report` shows `identical` for that project on
both hooks; `run_hook(<project copy>, ...)` over `BRANCH_FIXTURES` and
`COMMIT_FIXTURES` reports 0 mismatches; `claude_hook_dispatch.py --root`
still 0 blocking; Hafiz confirms the umbrella allowlist is the agreed rule for
that project.

**Step 2 (after every Step 1 row reads `identical`, one PR per project, same
order):** delete the project's two copies and add the project-side
`run-shared-hook.sh` exactly as `sims-owner-analytics` ships it; change the
two `settings.json` entries to `bash .claude/hooks/run-shared-hook.sh
validate-branch-name.py` and `... conventional-commits.py`. After this the
umbrella file is the only body on disk. Evidence before merge:
`run-shared-hook.sh --resolve-only <hook>` prints the umbrella path from both
a direct checkout and a `Sifututor-worktrees/<name>` worktree;
`claude_hook_dispatch.py --root` 0 blocking; `drift_report` shows `absent`
for that project; a real `git checkout -b bad_name` in that project is
denied from both launch positions (manual check, recorded in the PR).

**Step 3 (after Step 2 is complete for every project):** remove the inline
branch-name regex from `codex-pre-tool-use.py` (lines 110 to 119) and have it
invoke `.claude/hooks/validate-branch-name.py` by subprocess with the same
payload shape the harness uses. Evidence before merge: `codex:branch-name`
suite 0 mismatches before and after; `measure.py` latency for that suite
recorded before and after (baseline today: mean 29 ms, median 28 ms,
subprocess-inclusive) and the delta accepted by Hafiz; `.codex/config.toml`
unchanged.

**Step 4 (not scheduled):** `quality-gate.py`, `workflow-gate.py`,
`session-start.py`, `memory-flush.py`. Each project's copy is its own source
of truth today and no shared implementation exists, so there is nothing to
cut over to. Prerequisite before any consolidation is proposed: a fixture set
per project, of the same shape as `BRANCH_FIXTURES`, run by this harness
against the project's live copy, green in that project's CI. Until then those
files stay project-owned and out of this directory's scope.

## What remains for #161 after this PR

- One PreToolUse dispatcher: the umbrella still registers five separate
  PreToolUse processes (approval guard, secret guard, branch name, commit
  message, test-coverage gate) and each sub-project registers its own set.
- Metadata-only failure logging across that dispatcher.
- Route-scoped optional MCP loading with capability preflight.
- Before/after latency and false-block comparison. `measure.py` is the
  baseline tool; today's baseline is 22 to 29 ms mean per live hook
  invocation (subprocess-inclusive) and 0.0 false-block rate on every suite.

## Known limitations

- The harness asserts documented accept/deny outcomes for fixture commands.
  It does not prove two implementations are equivalent for all inputs.
- No plain `git commit` fixture runs against the Codex guard, because the
  live guard would shell out to `pre-commit-guard.sh` against the current
  checkout, which is git state, not policy.
- `secret_output_guard.py` and the per-project gates are not covered here.
- The live drift test skips from a worktree unless
  `SIFUTUTOR_WORKSPACE_ROOT` is set; the planted-fixture drift test always
  runs.
