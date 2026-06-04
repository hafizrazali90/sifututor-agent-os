# Agent OS Quick Start

Use this at the start of a fresh Codex or Claude session in the Sifututor
workspace.

The goal is simple: understand the current session before acting.

## Startup Order

1. **Identify the workspace and project**
   - Confirm cwd is under `/Users/hafizrazali/Projects/Sifututor`.
   - Identify whether the work is umbrella-level or inside a product repo.
   - Read the nearest `AGENTS.md`.

2. **Run Agent OS health**

   From the umbrella root:

   ```bash
   scripts/agent-checks/agent-os-health.sh
   ```

   This reports current capability, Koda direct health, active task state, and
   approval gates.

3. **Classify context accuracy**
   - Use [context-authority.md](context-authority.md).
   - Treat Koda memories as historical or trusted until checked.
   - Treat staff reports as reported symptoms until reproduced or inspected.
   - Stop if important sources conflict.

4. **Choose the lightest lane**
   - Discussion / learning
   - Intake / reproduction
   - Product design
   - Small change
   - Normal engineering
   - Critical lane
   - Verify / QA / review / commit / save-session

5. **Check risk gates**
   - Commit needs exact file-list approval.
   - Push, PR, merge, and deploy need explicit current-session approval.
   - Critical lanes need diagnosis first, then approval before implementation.
   - Never read `.env*`.
   - Never modify `live/`.
   - Never use `--no-verify`.

6. **Do the work**
   - Keep scope narrow.
   - Prefer existing project patterns.
   - Verify with the smallest useful check first.
   - For user-facing work, make the E2E decision explicit.

7. **Close out clearly**
   - Status
   - Meaning
   - Checked
   - Recommended next
   - Decision needed
   - Koda save status when durable memory mattered

## Fast Path For Discussion

If Hafiz is asking to discuss, learn, compare options, or think through a
workflow:

- do not edit files unless Hafiz says proceed
- do not force commit/verify/QA ceremony
- explain in plain language first
- offer 2-3 options when a decision is real

## Fast Path For Implementation

If Hafiz says proceed with a safe docs or workflow update:

1. Read the relevant docs.
2. Make the narrow edit.
3. Run `scripts/agent-checks/agent-os-health.sh`.
4. Run `scripts/agent-checks/pre-commit-guard.sh`.
5. Report what changed, how checked, and what remains.

## Fast Path For Critical Lanes

For auth, payments, invoices, commissions, migrations, deployment, or mobile API
contracts:

1. Diagnose only.
2. Explain risk in human terms.
3. Wait for Hafiz approval.
4. Implement only after approval.
5. Verify more strongly than normal work.

## Useful Files

- [agent-os.md](agent-os.md): Agent OS overview.
- [agent-os-internal-build-plan.md](agent-os-internal-build-plan.md):
  internal MVP plan.
- [context-authority.md](context-authority.md): context accuracy rules.
- [agent-os-memory.md](agent-os-memory.md): Koda memory discipline.
- [agent-os-evals.md](agent-os-evals.md): workflow eval cases.
- [capabilities.example.json](capabilities.example.json): capability manifest
  example.
- [agent-os-installation.md](agent-os-installation.md): install/check guide for
  applying the Agent OS baseline to a project.
- [task-router.md](task-router.md): route selection.
- [verify.md](verify.md), [qa.md](qa.md), [review.md](review.md),
  [commit.md](commit.md), [save-session.md](save-session.md): core workflow
  playbooks.

## Startup Output Shape

Good startup summary:

```text
Agent OS health: pass
Project: Sifututor umbrella
Capability: local filesystem and git available; Koda direct health pass
Context: user request is discussion / docs / implementation / critical lane
Approval needed: none yet / commit / push / deploy / critical implementation
Next: <single recommended next action>
```
