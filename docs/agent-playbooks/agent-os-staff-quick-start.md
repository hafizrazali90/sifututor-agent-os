# Agent OS Staff Quick Start

Use this guide when a Sifututor staff member wants to use the Agent OS with
Codex, Claude, GitHub Copilot, Cursor, Gemini, or another LLM-assisted coding
tool.

The goal is not to give every staff member every tool. The goal is to give each
person a safe starting setup that helps them report, investigate, document,
verify, or build work without touching production or secrets.

## First Rule

Start with the smallest safe capability.

Staff should not get production, deploy, payment, auth, database, or secret
access by default. Add those only when Hafiz explicitly approves the need and
the access can be audited.

## Which Path To Use

| Staff need | Recommended path | What they can do first |
| --- | --- | --- |
| Report bugs or support issues | Any LLM plus the working agreement | Write clear bug reports and reproduction notes |
| QA or regression checks | Codex or Claude with project docs | Run guided checks and produce evidence |
| Developer work | Codex or Claude with repo access | Make small scoped changes after issue/task routing |
| Product/design thinking | Codex, Claude, or chat LLM | Draft PRDs, UX notes, and build prompts |
| Non-technical operations | Chat LLM plus docs only | Summarize issues and prepare handoff notes |

## Install Or Check A Project

From the umbrella Agent OS repo:

```bash
scripts/agent-checks/agent-os-install.sh
```

To check a product repo:

```bash
scripts/agent-checks/agent-os-install.sh --target path/to/project
```

To create missing baseline files after reading the dry-run output:

```bash
scripts/agent-checks/agent-os-install.sh --target path/to/project --apply
```

The installer source of truth is
[agent-os-install-manifest.json](agent-os-install-manifest.json). Do not copy
baseline rules by hand if the manifest or installer can check them.

## Tool Setup Paths

### Codex

Use Codex when the staff member needs code reading, implementation help, local
checks, or Git-aware work.

First commands:

```bash
cat AGENTS.md
scripts/agent-checks/agent-os-health.sh
scripts/agent-checks/agent-os-install.sh --target path/to/project
```

Codex should follow the repo-local playbooks and ask for explicit approval
before commit, push, PR, merge, deploy, or critical implementation.

### Claude Code

Use Claude Code when the staff member benefits from Claude skills, review, QA,
or broader reasoning over project files.

First commands:

```bash
cat AGENTS.md
cat CLAUDE.md
scripts/agent-checks/agent-os-install.sh --target path/to/project
```

Claude should use the same shared playbooks under `docs/agent-playbooks/` and
the same approval gates as Codex.

### Other LLM Or Editor Tool

Use this path for GitHub Copilot, Cursor, Gemini, or a general chat model.

Give the tool these files as the starting context:

- `AGENTS.md`
- the target project's `AGENTS.md`
- the target project's `CLAUDE.md` or equivalent project reference
- [agent-os.md](agent-os.md)
- [agent-os-quick-start.md](agent-os-quick-start.md)
- the relevant workflow playbook, such as [diagnose.md](diagnose.md),
  [qa.md](qa.md), [review.md](review.md), or [product-design.md](product-design.md)

If the tool cannot run guard scripts, the staff member must run the commands
manually and paste the result into the tool.

## Safe Default Permissions

Allowed by default:

- read project docs
- read source code
- run local non-destructive checks
- write notes, QA evidence, and draft docs
- prepare proposed changes for review

Needs explicit approval:

- edit source code
- create commits
- push branches
- open PRs
- change GitHub issue state
- update Plane ownership, priority, or roadmap direction

Never allowed by default:

- read `.env*`
- modify `live/`
- reveal or copy secrets
- deploy
- push with `--force`
- bypass hooks with `--no-verify`
- change production data
- touch payment, auth, invoice, commission, migration, or mobile API contract
  behavior without diagnosis and approval

## Memory

Koda is preferred for Hafiz and approved engineering agents because it gives
durable cross-session memory.

Staff without Koda should use a local memory fallback:

- keep short notes in a project handoff doc
- save only durable lessons, not raw transcripts
- include date, project, issue/task link, what was learned, and next action
- never store secrets, customer private data, tokens, or raw production payloads

Good local memory note:

```text
2026-06-04 - sifututor_parent - QA
Lesson: parent app release versions must be checked with npm run check-version.
Next: verify package-lock metadata if package.json version changes.
```

Bad local memory note:

```text
Here is the whole chat transcript and copied credentials.
```

## First-Run Verification

After setup, run:

```bash
scripts/agent-checks/agent-os-health.sh
scripts/agent-checks/agent-os-install.sh --target path/to/project
```

From the product repo, run:

```bash
../scripts/agent-checks/pre-commit-guard.sh
```

If any check fails, do not continue into implementation. Fix the baseline first
or ask Hafiz/engineering lead for help.

## How Staff Should Ask The Agent

Good prompts:

```text
Read AGENTS.md and the project AGENTS.md. I want to report a bug. Help me write
clear reproduction steps without changing code.
```

```text
Use the QA playbook. Check this screen and tell me what evidence is missing.
Do not commit or push.
```

```text
Use the product-design playbook. Help me turn this idea into a small PRD.
No implementation yet.
```

Risky prompts:

```text
Fix everything and push it.
```

```text
Deploy this now.
```

```text
Read all files including env and production snapshots.
```

## Escalation

Escalate to Hafiz or an engineering lead when:

- the task involves production, secrets, deploy, payments, auth, invoices,
  commissions, migrations, or mobile API contracts
- the agent asks for access the staff member does not understand
- the checks fail and the reason is unclear
- the staff report and reproduction evidence disagree
- the change would affect customers, billing, tutors, parents, or staff workflow

## Close-Out Shape

Every staff-assisted session should end with:

```text
Status: done / partly done / blocked
Meaning: what changed or what was learned
Checked: commands, evidence, or why not checked
Recommended next: one next action
Decision needed: yes/no, and what decision
```
