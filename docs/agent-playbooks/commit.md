# Commit Playbook

Use this when the user asks to commit, prepare a commit, or check readiness.

## Hard Rules

- Never commit without user approval of the file list. Approval can be a short
  reply such as `proceed`, `continue`, `yes`, or `ok` only when the previous
  agent message clearly proposed an exact commit-only bundle with file list,
  guard/check plan, and stop-before-push boundary.
- Never push, merge, deploy, or open a PR unless the user explicitly asks in
  the current session.
- Never use `--no-verify`.
- Never commit `.env*`, credentials, tokens, production secrets, `live/`, or
  `.workflow-rollout/`.
- Use direct `git commit -m` flags. Do not use HEREDOC command substitution.
- Do not add an agent name as a commit co-author unless Hafiz explicitly asks.
- Do not commit manually edited generated files unless the project explicitly
  treats that generated artifact as human-maintained.

## Before Staging

1. Run the shared guard from the project:

   ```bash
   ../scripts/agent-checks/pre-commit-guard.sh
   ```

   From the umbrella root:

   ```bash
   scripts/agent-checks/pre-commit-guard.sh
   ```

2. Read workflow state:
   - state-file projects: `.claude/tasks/active.json` and referenced task file
3. Confirm required `verify`, `qa`, `regression_test`, `review`, or
   `defect_analysis` steps are complete for the route.
   - For user-facing feature, bugfix, hotfix, or small-change work, confirm the
     permanent E2E regression decision is complete: added, updated, or not
     feasible with a named blocker and follow-up test/fixture.
   - For every changed staff/admin/parent/tutor/student/customer workflow,
     confirm the exact permanent E2E file that covers it. If any changed
     workflow has no permanent E2E and no explicit accepted exception, stop
     before commit.
4. Confirm release communication for staff-facing changes before staging:
   - `CHANGELOG.md` has a plain-English entry for what changed.
   - Relevant module help content in `src/modules/<module>/lib/help.ts` is
     updated when staff need new guidance, changed wording, or changed steps.
   - A What's New / release seed script or equivalent release entry is prepared
     when staff should be notified in-app.
   - If any item is not relevant, record why in the final answer or PR body.
   - Treat a missing relevant release communication item as a commit blocker,
     even when tests pass.
   - If the changelog or release-note artifact is generated in that project,
     edit the source-of-truth release note or generator input instead of
     hand-editing generated output.
5. If the session contains multiple fixes, update the Session Release Ledger
   and confirm no intended fix is stranded on another branch or local-only
   commit.
6. Apply the Review And Risk Checkpoint from [review.md](review.md). Plain
   meaning: before saving the commit, confirm the change is scoped, evidenced,
   honest about state, not hiding critical-lane risk, not missing relevant
   release communication, and not confusing multi-fix session state.
7. Apply [no-mistakes-lite.md](no-mistakes-lite.md). Plain meaning: before
   committing, make one final honesty pass over scope, proof, missing evidence,
   state, approval boundary, and recommended next action.
8. Review `git status --short`, `git diff`, and `git diff --staged`.
9. Ask the user to approve the exact staged file list unless already approved.

## Message Format

```text
[emoji] type(scope): description
```

Examples:

```text
🐛 fix(invoices): guard declined payment callbacks
✨ feat(auth): add parent session renewal endpoint
🧪 test(payments): cover duplicate webhook delivery
📝 docs(workflow): add shared agent playbooks
```

Allowed types follow root `AGENTS.md`. Keep the description imperative,
lowercase after the scope, under 72 characters where practical, and without a
period.

## Correct Commit Command Shape

Use:

```bash
git commit -m "🐛 fix(invoices): guard declined payment callbacks"
```

For a body, use repeated direct flags:

```bash
git commit \
  -m "🐛 fix(invoices): guard declined payment callbacks" \
  -m "Records the declined FIUU callback without mutating paid invoices."
```

Do not use:

```bash
git commit -m "$(cat <<'EOF'
🐛 fix(invoices): guard declined payment callbacks
EOF
)"
```

The conventional commit hook sees the literal command substitution and can
reject or misread it.

## After Commit

1. Capture the SHA with `git rev-parse --short HEAD`.
2. If a state-file task is active, record commit evidence in the task state only
   if the project workflow expects manual state updates.
3. Report SHA, message, and files committed.
4. Always state the recommended next action in plain language.

If the commit is local and not pushed, do not end with only:

```text
Not pushed yet.
```

Say what Hafiz should do next:

```text
Not pushed yet.
Recommended next: approve push if you want this on GitHub; otherwise we can
continue local work.
```

Plain meaning: after a commit, Hafiz should never have to ask whether the next
step is push, continue, review, save-session, or stop.
