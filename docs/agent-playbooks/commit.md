# Commit Playbook

Use this when the user asks to commit, prepare a commit, or check readiness.

## Hard Rules

- Never commit without explicit user approval of the file list.
- Never push, merge, deploy, or open a PR unless the user explicitly asks in
  the current session.
- Never use `--no-verify`.
- Never commit `.env*`, credentials, tokens, production secrets, `live/`, or
  `.workflow-rollout/`.
- Use direct `git commit -m` flags. Do not use HEREDOC command substitution.

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
4. Confirm release communication for staff-facing changes before staging:
   - `CHANGELOG.md` has a plain-English entry for what changed.
   - Relevant module help content in `src/modules/<module>/lib/help.ts` is
     updated when staff need new guidance, changed wording, or changed steps.
   - A What's New / release seed script or equivalent release entry is prepared
     when staff should be notified in-app.
   - If any item is not relevant, record why in the final answer or PR body.
   - Treat a missing relevant release communication item as a commit blocker,
     even when tests pass.
5. If the session contains multiple fixes, update the Session Release Ledger
   and confirm no intended fix is stranded on another branch or local-only
   commit.
6. Review `git status --short`, `git diff`, and `git diff --staged`.
7. Ask the user to approve the exact staged file list unless already approved.

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
