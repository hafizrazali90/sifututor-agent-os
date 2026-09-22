# Hook survey — what exists today (read 2026-09-22)

This is the source-of-truth survey for bundle 8 (issue #161). Every script
named below was opened and read in full before writing this file; nothing
here is from memory. File contents can drift after this date — re-read the
named source before trusting this file for anything beyond understanding
`hook-policy`'s design intent.

Scope note: this survey covers the umbrella `sifututor-agent-os` repo
(`.claude/hooks/`, `scripts/agent-checks/`) plus four sub-project
`.claude/hooks/` directories in the sibling `~/Projects/Sifututor` workspace
(`ripple-suite`, `sifu-tutor`, `sifututor_tutor`, `lls`), read read-only for
survey purposes. This repo does not vendor copies of those sub-project
files; two representative ones (`quality-gate.py`, `workflow-gate.py`) were
snapshotted into `fixtures/originals/` for parity testing — see the header
comment on each snapshot for the exact source path and read date.

## 1. Branch name validation

**Claude side** — `.claude/hooks/validate-branch-name.py` (this repo, the
umbrella copy; installed verbatim into `sifututor_tutor`, `lls`, and
`ripple-suite` — byte-identical, confirmed by md5). `sifu-tutor`'s copy has
drifted: different docstring, different exception handling (`except
json.JSONDecodeError` + exit 1 vs a silent catch-all + exit 0), a narrower
deployment-branch allowlist (missing `nakngaji-*`), and no `release/*`
allowlist. This drift is the concrete "duplicated logic" problem: four
supposedly-identical copies, one of them silently different.

- Input: Claude `PreToolUse` JSON on stdin — `{tool_name, tool_input:
  {command}}`.
- Only inspects `Bash` tool calls containing `git checkout -b` or `git
  switch -c`.
- Extracts the branch name with `git (?:checkout -b|switch -c)\s+([^\s]+)`.
- Allows a fixed base-branch set (`main`, `master`, `develop`, `staging`,
  `dev`, `live-qa`, `integration`, `sifu-staging`, `sifu-backport`),
  deployment branches matching `^(sifu|lls|learnest|nakngaji)-[a-z0-9...]`,
  release branches matching `^release[/-][a-z0-9...]`, and anything inside
  an `ssh ` command (can't validate a remote branch name).
- Otherwise requires `type/kebab-description` where type is one of `feat
  feature fix refactor hotfix chore docs perf test ci`.
- Output on reject: `hookSpecificOutput.permissionDecision = "deny"` with a
  long human-readable reason. Output on accept: exit 0, no stdout.

**Codex side** — `scripts/agent-checks/codex-pre-tool-use.py`, lines ~108-119.
Same intent, independently reimplemented as one inline regex compiled from
the same four allow-groups, checked with `.match()` instead of allow-list
membership. It reads `tool_input.command`/`tool_input.cmd` rather than
Claude's `tool_input.command` only, and resolves `cwd` differently (see
`read_request()`). This is real cross-agent duplication: the same policy,
written twice, already observed to be able to drift the way the Claude
copies did.

## 2. Commit message format (Conventional Commits)

**Claude side** — `.claude/hooks/conventional-commits.py` (this repo's
umbrella copy; the four sub-projects' copies are NOT identical — see md5
table below). Parses the *first* `-m "..."` flag's value with a regex, takes
its first line, and requires it to match `^[^\x00-\x7F\s]*\s*?(feat|fix|docs
|style|refactor|perf|test|chore|ci|build|revert|wip)(\(.+\))?:\s.+` (an
optional leading emoji, then a conventional-commits type). Skipped entirely
if `--no-verify` is present, or if no `-m` flag can be extracted (e.g.
`--amend` with no message). Deny output uses the same
`hookSpecificOutput.permissionDecision = "deny"` shape as branch validation.

md5 of `conventional-commits.py` across projects: ripple-suite ==
sifu-tutor (`c16699d2...`), sifututor_tutor and lls each have their own
distinct hash — three different bodies for what is meant to be one shared
rule.

**Codex side** — no independent Conventional Commits regex exists. Instead
`codex-pre-tool-use.py` blocks the *HEREDOC* commit-message pattern
(`$(cat <<`, `<<EOF`, `<<'EOF'`) outright on any `git commit`, which the
Claude-side script does not check at all (its docstring only *warns* that
HEREDOC messages parse wrong; it does not block them). This is a real
coverage gap in the opposite direction: Codex blocks something Claude
silently mis-parses.

## 3. Quality gate (pre-commit lint/build reminder)

Representative real implementation read: `ripple-suite/.claude/hooks/
quality-gate.py` (frozen snapshot: `fixtures/originals/
ripple_quality_gate_snapshot.py`, read 2026-09-22 from
`~/Projects/Sifututor/ripple-suite/.claude/hooks/quality-gate.py`).

- Only fires on `git commit` (not `--no-verify`).
- Reads staged files via `git diff --cached --name-only --diff-filter=ACMR`
  in `project_root` (two directories above the hook file).
- If any staged `.ts/.tsx/.js/.jsx` file sits under a "code directory"
  (`src/`, `app/`, `pages/`, `components/`, `lib/`, `hooks/`, `utils/`,
  `types/`, `modules/`), emits `permissionDecision: "ask_user"` listing the
  files and asking the human to confirm `npm run lint && npm run build`
  passed. This is a soft, human-confirmable gate — it never hard-denies.
- If any staged file starts with one of a fixed critical-path list
  (`src/middleware.ts`, `src/lib/db.ts`, `src/app/api/auth/`, tutor-payments
  module, etc.), emits a second, stricter `ask_user` prompt.
- `lls` and `sifututor_tutor` have their own `quality-gate.py` with
  different extensions/paths/commands (PHP lint vs `npm run check` vs `npm
  run lint && npm run build`) — same shape, different parameters. This is
  exactly the "same policy, different config" case `hook-policy`'s
  `checks/quality_gate.py` is written to generalize instead of duplicate.

## 4. Workflow gate (mandatory step enforcement before commit)

Representative real implementation read: `ripple-suite/.claude/hooks/
workflow-gate.py` (frozen snapshot: `fixtures/originals/
ripple_workflow_gate_snapshot.py`, read 2026-09-22).

- Only fires on `git commit` (not `--no-verify`).
- Reads `.claude/tasks/active.json` → `taskFile` → the task JSON at that
  path. Exits 0 (allow) whenever any of these are missing/unreadable — a
  project with no active task state is never blocked by this gate.
- Reads `route` and `steps` (list of `{name, status, ...}`) from the task.
- Unconditionally requires `verify` and `qa` steps to be `done` or
  `skipped` when present in `steps`.
- On `route in {hotfix, bugfix}`: requires `regression_test` to be `done`
  (with non-empty `evidence.red_output` and `evidence.green_output`) or
  `skipped`; requires `defect_analysis` to be `done` or `skipped`.
- On `route in {hotfix, bugfix, feature, small-change}`: requires
  `release_notes` to be `done` or `skipped`.
- Any unmet requirement accumulates into one `deny` with a bulleted list of
  every missing step plus the task file path to edit.
- `sifu-tutor`/`sifututor_tutor` share one workflow-gate.py body (md5
  `f0b36490...`); `ripple-suite` and `lls` each have their own distinct
  body (different route names, e.g. LLS routes differ). Three genuinely
  different bodies encoding "the same idea, parameterized by project" —
  again a config-not-code case.

## 5. Command-safety / content guard

`scripts/agent-checks/secret_output_guard.py` (this repo) is already the
single shared implementation — every hook (`quality-gate.py`,
`workflow-gate.py` via `claude_hook_dispatch.py`, and the Codex lifecycle
hook per `docs/agent-playbooks/agent-os-hook-dispatcher.md`) is expected to
route through it rather than reimplement it. It exposes
`evaluate_command(command: str) -> Decision(allowed, reason)`, a large
ordered table of regexes blocking whole-environment dumps, raw credential
files, secret-store reads, shell tracing, etc., plus a separate
`evaluate_tool_request()` for visual-capture-during-credential-reveal
blocking. Because this one is already consolidated, `hook-policy`'s
`checks/command_safety.py` **wraps it directly** (imports and calls the
real function) rather than reimplementing it — the "parity" here is
definitional, not approximate.

`codex-pre-tool-use.py` additionally hard-denies, inline, a short list not
covered by `secret_output_guard.py`: `--no-verify`, `git reset --hard`,
`git checkout --`, `rm -rf` on `live/`/`.workflow-rollout/`, and direct
reads of `.env*` via `cat/sed/awk/.../node`. These are cheap, deterministic,
always-safe checks with no Claude-side equivalent found (Claude relies on
its own permission `deny` rules in `settings.local.json` for some of these
instead of a hook). `hook-policy` reimplements this short list as its own
checks (`check_codex_safety_guards.py`: `NoVerifyBypassGuard`,
`DestructiveGitGuard`, `ProtectedPathGuard`) so the *policy* — not just the
Codex script — becomes the one shared source, with a parity fixture proving
equal behavior against the real `codex-pre-tool-use.py`.

**Known upstream gap found while writing the parity fixture**: the real
`git checkout --` regex in `codex-pre-tool-use.py` is `` git\s+checkout\s+--\b ``.
`\b` is a word-boundary assertion, and `-` is not a word character, so this
only matches when `--` is immediately followed by a word character with no
space (`git checkout --foo`) — it does **not** match the actual common Git
syntax `git checkout -- <path>` (space before the path), which is the real
destructive form this guard is meant to catch. Confirmed directly against
the live script (`echo '{"tool_name":"exec","tool_input":{"command":"git
checkout -- file.txt"}}' | python3 scripts/agent-checks/codex-pre-tool-use.py`
prints nothing, i.e. allows). `DestructiveGitGuard.run()` mirrors this exact
(buggy) behavior on purpose — `test_check_codex_safety_guards.py` locks
both the caught form and the missed form as separate, named tests — because
this bundle's job is behavior-identical parity, not silently fixing an
upstream hook it is explicitly forbidden from touching. Fixing the regex
itself is a small, separate, future change to `codex-pre-tool-use.py` (or,
after cutover, to this module) and is out of this bundle's scope.

## 6. What's genuinely expensive/model-backed today

Nothing in the surveyed hooks calls a network service or a model directly.
The closest real analogue is `docs/agent-playbooks/agent-os-hook-dispatcher.md`'s
description of Codex's `SessionStart` Koda health check and
`.claude/hooks/koda-context-injector.py`'s memory lookup, both of which are
documented to "fail silently" today rather than degrade visibly. Bundle 1's
`scripts/agent-checks/decision-layer/` already builds a bounded
timeout/retry/fallback wrapper for a real model-backed provider (see
`engine.py`, `retry.py`, `provider_jev.py`) for a *different* concern
(typed yes/no policy decisions, not hook gating). `hook-policy` does not
depend on or modify that module; it implements its own small, purpose-built
timeout wrapper (`dispatcher.py::_run_expensive`) for the two representative
expensive-check examples this bundle ships
(`checks/expensive_examples.py`), because hook gating's failure contract
(required → block, advisory → degrade-visibly) is stricter than the
decision-layer's (always falls back to `"undetermined"`, whether the check
was required or advisory). Documenting this distinction here is intentional
so a future engineer does not "simplify" by merging the two.

## md5 table (evidence for the duplication claims above)

```text
validate-branch-name.py:
  ripple-suite      == sifututor_tutor == lls == (this repo's umbrella copy)  1f3a003a46fde3d0de40e5205fc5f993
  sifu-tutor (DRIFTED)                                                         87f1474ade3fb21dec2101a12b55404b

conventional-commits.py:
  ripple-suite      == sifu-tutor        c16699d283fe89a53a5a8ec0fd688948
  sifututor_tutor (own body)             9840c798b69e381247b4ee22fcbda3b4
  lls (own body)                         97bccf5e1c6c765d1455c30ca6a6ff42

workflow-gate.py:
  sifu-tutor        == sifututor_tutor   f0b36490dae818c33f481389afc7be23
  ripple-suite (own body)                9fa6c1d02c2b756e4162950b313be798
  lls (own body)                         9c315d8e107fce7517032bb8c07f3f9d
```

## What this bundle does and does not do with the above

`hook-policy` (this directory) implements one parameterized check per
policy above, proves each one produces the same accept/reject decision as
the *current* real script for the same input (see `tests/test_parity_*.py`),
and exposes thin Claude/Codex adapters that call the same checks instead of
each reimplementing them. It does not touch, replace, or re-register any of
the files named in this survey. Live cutover — pointing an actual
`.claude/hooks/*.py` file or `settings.json` hook registration at this
module — is a separate, future, carefully-reviewed decision. See the PR
body for the explicit statement.
