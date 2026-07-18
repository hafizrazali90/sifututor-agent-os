# Claude Code Setup — Developer Onboarding

This guide covers everything you need to use Claude Code correctly inside the
Sifututor workspace. It is written for developers joining the team — whether you
have used Claude Code before or not.

Read this once before your first session. Refer back whenever something is
behaving unexpectedly.

---

## Table of Contents

1. [Why Claude Forgets or Mixes Things Up](#1-why-claude-forgets-or-mixes-things-up)
2. [Prerequisites](#2-prerequisites)
3. [Memory Setup — claude-mem](#3-memory-setup--claude-mem)
4. [Opening the Workspace](#4-opening-the-workspace)
5. [Sub-projects in This Workspace](#5-sub-projects-in-this-workspace)
6. [Starting Every Session Correctly](#6-starting-every-session-correctly)
7. [Core Session Workflow](#7-core-session-workflow)
8. [TDD — Mandatory on All Feature and Bug Work](#8-tdd--mandatory-on-all-feature-and-bug-work)
9. [Quality Gates — Never Skip](#9-quality-gates--never-skip)
10. [Skills (Slash Commands) Reference](#10-skills-slash-commands-reference)
11. [Branch Naming](#11-branch-naming)
12. [Commit Message Format](#12-commit-message-format)
13. [Critical Code Paths — Human Review Required](#13-critical-code-paths--human-review-required)
14. [Surgical Changes Principle](#14-surgical-changes-principle)
15. [Specialized Agents](#15-specialized-agents)
16. [Memory Architecture — Who Uses What](#16-memory-architecture--who-uses-what)
17. [How Team Knowledge Propagates](#17-how-team-knowledge-propagates)
18. [Server Map](#18-server-map)
19. [Plane (Project Management)](#19-plane-project-management)
20. [What You Must Never Do](#20-what-you-must-never-do)
21. [Troubleshooting](#21-troubleshooting)
22. [Related Documents](#22-related-documents)

---

## 1. Why Claude Forgets or Mixes Things Up

Claude Code does not have persistent memory by default. Every new chat window
starts blank. Here is what causes confusion and how we solve it.

**Cause 1 — No project declared at the start.**
Claude has no idea whether you are working on `sifu-tutor`, `ripple-suite`,
`lls`, or something else. It may guess wrong and pull rules from the wrong
project.

Fix: Always start your first message with the project name. Examples:

```
"This is sifu-tutor work — I need to fix the invoice status bug."
"Working on ripple-suite — add the new dashboard widget."
"lls bug — the webhook is not firing."
```

**Cause 2 — Context window compression.**
When a session grows very long, Claude Code automatically compresses old
messages. Granular details get summarized away and Claude starts making
mistakes.

Fix: Keep sessions focused. End a session when a task is complete rather than
starting the next task in the same window. claude-mem (installed in step 3)
captures your session automatically so the next session picks up where you left
off.

**Cause 3 — Wrong VS Code workspace.**
If you open VS Code inside a sub-project folder (e.g., inside `sifu-tutor/`),
you only load that project's rules. You lose skills, hooks, and shared
configuration.

Fix: Always open VS Code at `~/Projects/Sifututor` (the umbrella root).

**Cause 4 — claude-mem not installed.**
Without claude-mem, every session starts with zero context. Claude has no
memory of what you worked on yesterday, what decisions were made, or what
gotchas were discovered.

Fix: Install claude-mem once. See step 3.

---

## 2. Prerequisites

Verify all of these before your first session. Ask Hafiz if anything is missing.

| Requirement | How to verify |
| --- | --- |
| Claude Code CLI installed | `claude --version` |
| Node.js 20+ | `node --version` |
| Logged in to Claude Code | `claude` — should open chat, not a login prompt |
| SSH key for webvoyager / production | `ssh webvoyager echo ok` |
| SSH config entries | See below |

### Installing Claude Code and logging in

```bash
npm install -g @anthropic-ai/claude-code
claude
```

The first time you run `claude`, it opens a browser window. Log in with your
Claude.ai account. Once authenticated, the CLI stores your session — you will
not need to log in again unless you sign out.

Verify the install worked:

```bash
claude --version
```

### SSH config

Add to `~/.ssh/config`:

```
Host production
  HostName 151.246.1.164
  Port 19199
  User sifututortutorla
  IdentityFile ~/.ssh/id_ed25519

Host webvoyager
  HostName 151.246.1.218
  Port 19199
  User root
  IdentityFile ~/.ssh/id_ed25519

Host lls
  HostName 187.77.157.173
  Port 22
  User root
  IdentityFile ~/.ssh/id_ed25519_linode
```

Ask Hafiz for the SSH private key files.

> Warning: The alias `staging` is decommissioned. Never use it. When Hafiz or
> docs say "staging" for sifu-tutor, they always mean `sifu-staging.tutorla.tech`
> accessed via the `webvoyager` alias.

---

## 3. Memory Setup — claude-mem

claude-mem gives Claude persistent memory across your sessions. It runs locally
on your machine — your memory is private to you. Install it once and it works
automatically from that point on.

### Why we use claude-mem

Without it, every session starts blank. Claude does not remember what you
worked on last week, what approach you took, or what bugs you hit. With
claude-mem, it does — automatically, without you having to do anything extra
during sessions.

### Installation

```bash
npx claude-mem install
```

That one command:
- Registers 5 lifecycle hooks into Claude Code (SessionStart, UserPromptSubmit,
  PostToolUse, Stop, SessionEnd)
- Starts a local worker service on port 37777
- Sets up SQLite + Chroma vector database on your machine for hybrid search

Verify it installed:

```bash
npx claude-mem status
```

You can also install it from inside Claude Code:

```
/plugin marketplace add thedotmack/claude-mem
```

### What claude-mem does automatically

| Hook | When it fires | What it does |
| --- | --- | --- |
| SessionStart | Opening a chat | Retrieves relevant past context |
| UserPromptSubmit | Each message you send | Checks for relevant memory to inject |
| PostToolUse | After Claude runs a tool | Captures observations |
| Stop / SessionEnd | Closing the session | Summarizes and stores the session |

You do not need to run any command to save or load memory. It is fully
automatic.

### Web viewer

A real-time memory viewer is available at `http://localhost:37777` while the
worker is running. You can browse what claude-mem has stored.

### Privacy control

Wrap anything in `<private>` tags inside the chat to prevent it from being
stored:

```
<private>my temporary password is abc123</private>
```

### System requirements

- Node.js 20+
- Port 37777 free on your machine
- Bun (auto-installed by claude-mem if missing)
- uv Python package manager (auto-installed if missing)

---

## 4. Opening the Workspace

Always open VS Code at the umbrella root:

```bash
cd ~/Projects/Sifututor
code .
```

When you do this, Claude Code automatically loads:

- Global rules from `~/.claude/CLAUDE.md` (server map, TDD, critical rules)
- Umbrella rules from `CLAUDE.md` (sub-project map, MCP map, architecture)
- Every sub-project's `CLAUDE.md` via `additionalDirectories`
- All skills: `sifu-*`, `rn-*`, `ripple-*`, `lls-*`, plus global skills
- All MCP servers: Figma, Chrome DevTools, Wasabi, Neon
- Hooks: branch name validator, conventional commit enforcer, friction logger,
  test coverage gate

None of this needs manual configuration. It all loads from the parent
`.claude/settings.json` and `.mcp.json` which are already set up.

### When to open inside a sub-project instead

Open VS Code inside a sub-project folder **only** when you are doing a heavy
commit cycle that requires sub-project-specific hooks:

- `workflow-gate.py` — blocks commit until verify/QA/review are done
- `quality-gate.py` — runs project-specific lint and build commands
- `memory-flush.py` — flushes session state on session end

These hooks are sub-project-only because they depend on per-project test
runners and build commands.

**Rule of thumb:** If your session will end with a commit, open VS Code inside
the sub-project. For everything else — exploration, research, cross-project
work, discussion — stay at the umbrella root.

---

## 5. Sub-projects in This Workspace

| Directory | Stack | Skills prefix | Status |
| --- | --- | --- | --- |
| `ripple-suite/` | Next.js 15 + Neon Postgres | `ripple-*` | Active rebuild |
| `sifu-tutor/` | Laravel 11 + MySQL 8.4 (SIMS) | `sifu-*` | Active rebuild |
| `sifututor_tutor/` | React Native | `rn-*` | Active rebuild |
| `lls/` | Laravel 11 (Learnest backend) | `lls-*` | Active |
| `lls-frontend/` | React 18 SPA | (generic fallback) | Active |
| `sifututor_parent/` | Parent app rebuild | (generic fallback) | Active |
| `live/` | Production snapshots | — | **Read-only. NEVER modify.** |

Each project has its own `CLAUDE.md` with domain vocabulary (`CONTEXT.md`) and
current goals (`GOALS.md`). Read these before starting work on an unfamiliar
project.

---

## 6. Starting Every Session Correctly

### Step 1 — Open umbrella root in VS Code

```bash
cd ~/Projects/Sifututor
code .
```

### Step 2 — Open Claude Code

In VS Code, use the Claude Code sidebar panel. Or from terminal:

```bash
claude
```

### Step 3 — Declare your project in the first message

This is the single most important habit. Without it, Claude applies the wrong
rules and misroutes skill commands.

```
This is sifu-tutor work — fix the invoice status bug in the payment callback.
```

```
Working on ripple-suite — add the tutor dashboard summary widget.
```

```
lls work — the student enrollment webhook is returning 500.
```

Claude uses this declaration to:
- Apply the correct sub-project CLAUDE.md rules
- Route `/sifu-*`, `/ripple-*`, `/rn-*`, `/lls-*` skills correctly
- Focus memory retrieval on the right project context

### Step 4 — Read the project GOALS.md for unfamiliar tasks

If you are starting on a feature or entering an area you have not touched
before, ask Claude to read the project goals first:

```
Read sifu-tutor/GOALS.md and tell me the current focus before we start.
```

---

## 7. Core Session Workflow

```
Declare project → Work (TDD) → Commit → Verify → End session
```

| Step | What you do | What Claude does |
| --- | --- | --- |
| Declare project | First message names the project | Applies rules, routes skills |
| Work | Describe the task | Writes failing tests first, then implementation |
| Commit | `/sifu-commit` | Validates branch name + commit format, then commits |
| Verify | `/sifu-verify` | Runs lint + tests + build |
| End session | Close the chat | claude-mem captures and stores the session automatically |

Memory is handled by claude-mem automatically. You do not need to run a save
command at the end of each session.

---

## 8. TDD — Mandatory on All Feature and Bug Work

Test-Driven Development is not optional here. Every feature and bug fix follows
this order.

### The correct order — vertical slices

```
test 1 → implement 1 → test 2 → implement 2 → test 3 → implement 3
```

### The wrong order — never do this

```
test 1, test 2, test 3 (all) → implement 1, 2, 3 (all)
```

Writing all tests first then all code (horizontal slicing) is banned. One test,
one implementation, repeat.

### The TDD cycle

```
RED   — Write a failing test. Confirm it fails before touching implementation.
GREEN — Write the minimum code to make the test pass. Nothing more.
FIX   — Refactor if needed. All tests must still be green after refactoring.
```

### Relevant skills

| Command | What it does |
| --- | --- |
| `/sifu-testcases` | Generate test cases from user stories |
| `/sifu-generate-tests` | Write failing tests from the test cases (RED step) |
| `/sifu-verify` | Run all tests + lint + build (GREEN/FIX confirmation) |

`/sifu-testcases` and `/sifu-generate-tests` must run **before** any
implementation. If you catch yourself writing code before tests, stop.

---

## 9. Quality Gates — Never Skip

Every task passes through these gates in order before anything is pushed.

| Gate | What it checks | How |
| --- | --- | --- |
| Gate 1 | Plan reviewed before building | Hafiz approves the approach first |
| Gate 2A | Did the task succeed? | `/sifu-verify` — tests + lint + build all green |
| Gate 2B | Did anything else break? | Surgical scope check, N+1 queries, security scan |
| Gate 2C | Does it look right? (UI work) | `/qa` — visual check on staging |
| Gate 4 | Pre-push adversarial review | `/code-review` — NEVER skipped |

### Gate 4 is the most critical

Gate 4 runs `/code-review` against the full diff before any push. It is an
adversarial review — Claude actively tries to find what is wrong, not just
what looks right. This gate catches bugs that tests miss.

If Gate 4 finds issues, fix them before pushing. Do not push and plan to fix
later.

---

## 10. Skills (Slash Commands) Reference

Skills are slash commands that run inside Claude Code chat. They encode the
team's workflow steps so you do not have to remember the exact sequence.

### sifu-tutor skills

| Command | What it does |
| --- | --- |
| `/sifu-task-router` | Routes the task to the right workflow lane |
| `/sifu-testcases` | Generates test cases from user stories |
| `/sifu-generate-tests` | Writes failing tests (RED step) |
| `/sifu-verify` | Runs lint + tests + build (Gate 2A) |
| `/sifu-qa` | Runs QA checks (Gate 2C) |
| `/sifu-regression-test` | Runs regression test suite |
| `/sifu-commit` | Validates branch + commit format, then commits |
| `/sifu-requesting-code-review` | Prepares code review request |
| `/sifu-release-notes` | Generates release notes |
| `/sifu-save-session` | Manual session flush (used by Hafiz — not needed for staff with claude-mem) |

### ripple-suite skills (prefix: `ripple-`)

`/ripple-task-router`, `/ripple-generate-tests`, `/ripple-verify`,
`/ripple-commit`, `/ripple-qa`, `/ripple-regression-test`, etc.

### React Native / sifututor_tutor skills (prefix: `rn-`)

`/rn-task-router`, `/rn-generate-tests`, `/rn-verify`, `/rn-commit`,
`/rn-qa`, `/rn-regression-test`, etc.

### LLS skills (prefix: `lls-`)

`/lls-task-router`, `/lls-verify`, `/lls-commit`, `/lls-qa`, etc.

### Global skills (work across all projects)

| Command | What it does |
| --- | --- |
| `/task-router` | Dispatcher — routes to the right project task-router |
| `/commit` | Dispatcher — routes to the right project commit skill |
| `/verify` | Dispatcher — routes to the right project verify skill |
| `/code-review` | Review current diff for bugs and quality issues (Gate 4) |
| `/code-review ultra` | Deep multi-agent cloud review — use on large or risky changes |
| `/understand` | Explain an unfamiliar part of the codebase |
| `/plane-update` | Create or update a Plane work item |
| `/qa` | QA checks dispatcher |
| `/diagnose` | Diagnose a bug or production issue |
| `/tdd` | Run the full TDD red-green-refactor cycle |

---

## 11. Branch Naming

The branch name validator hook runs automatically on every commit and push. It
blocks non-conforming names with an error message telling you exactly what is
wrong.

### Allowed formats

```
feat/short-description
fix/short-description
chore/short-description
docs/short-description
test/short-description
audit/short-description
```

With a Plane ticket reference:

```
feat/ST-42-short-description
fix/RS-17-dashboard-null-pointer
```

### Not allowed

- `main` — never commit feature work directly to main
- `staging`, `integration` — shared branches, do not commit to these directly
- Free-form names without the `type/` prefix (e.g., `my-feature`, `hafiz-fix`)

### Rename a branch

```bash
git branch -m old-name feat/your-description
```

### Active branches per project

| Project | Production | Active development |
| --- | --- | --- |
| sifu-tutor | `main` | `integration` + feature branches |
| sifututor_tutor | `main` | `integration` + feature branches |
| ripple-suite | `main` | `staging` + feature branches |
| lls | `main` | feature branches |

---

## 12. Commit Message Format

The conventional commit hook blocks commits that do not match the format. Check
the error output — it tells you exactly what is wrong.

### Required format

```
<emoji> <type>(<scope>): <description>
```

### Examples

```
✨ feat(invoice): add LHDN tax guard to payment callback
🐛 fix(auth): correct session domain in staging env
📝 docs(onboarding): add claude code setup guide
♻️ refactor(billing): extract InvoiceCycleAllocator class
🧪 test(invoice): add failing test for status enum guard
🔧 chore(deps): upgrade Laravel to 11.4
🚀 deploy(staging): push billing revamp to sifu-staging
🔒 security(api): add rate limiting to tutor login endpoint
```

### Emoji reference

| Emoji | Type | Use for |
| --- | --- | --- |
| ✨ | feat | New feature or behaviour |
| 🐛 | fix | Bug fix |
| 📝 | docs | Documentation only |
| ♻️ | refactor | Code restructure, no behaviour change |
| 🧪 | test | Tests only |
| 🔧 | chore | Dependencies, tooling, config |
| 🚀 | deploy | Deployment-related |
| 🔒 | security | Security fix or hardening |

---

## 13. Critical Code Paths — Human Review Required

These areas require Hafiz to review before any code is merged. Do not push
to integration or main on these without explicit approval:

| Area | Why |
| --- | --- |
| Payments and invoicing | Affects revenue and LHDN compliance |
| Commission calculations | Financial output must be verified |
| Authentication and session handling | Security impact |
| Database migrations | Irreversible on production data |
| Mobile API contracts | Breaking changes affect live app users |
| Billing cycle and escalation logic | Multi-step rules with edge cases |

For these areas: implement, run Gate 2A + Gate 4, then **stop and request
review** before merging. Do not self-approve.

---

## 14. Surgical Changes Principle

Every line you change must trace to a specific requirement. Do not refactor
surrounding code while fixing a bug. Do not add features while fixing a feature.
Do not clean up while building.

**Before writing any code, ask:**
- What is the exact requirement this line satisfies?
- Is this line necessary for the task or just nice to have?

If you cannot answer the first question, stop and clarify the requirement.

This principle exists because:
- Unrequested changes introduce bugs in unrelated areas
- Wide diffs make Gate 4 reviews slower and less effective
- Scope creep is the most common cause of regressions

---

## 15. Specialized Agents

Claude Code has specialized agents for specific tasks. These run automatically
when you invoke certain skills, or you can invoke them explicitly.

| Agent type | Use for |
| --- | --- |
| `code-reviewer` | Post-build code review — invoked by `/code-review` |
| `mobile-developer` | React Native components, navigation, context, iOS optimization |
| `laravel-specialist` | Controllers, services, migrations, routes, Eloquent, Sanctum |
| `inertia-react-developer` | React page components, Tailwind, TypeScript, Inertia client |
| `database-optimizer` | MySQL/Eloquent query optimization, schema design |
| `security-auditor` | Read-only security review before merging auth, payment, or user data modules |
| `uiux-expert` | Audit screens and flows for UX quality |
| `typescript-pro` | Advanced TypeScript types, strict typing, migration from JS |

These agents are invoked by Claude automatically when relevant, or you can ask
explicitly:

```
Use the laravel-specialist agent to review this service class.
Use the security-auditor before we merge this auth change.
```

---

## 16. Memory Architecture — Who Uses What

We use a two-layer memory architecture. These layers serve different purposes
and different people.

### Layer 1 — Your personal session memory (claude-mem)

Every developer has their own claude-mem running locally. It captures your
sessions automatically — what you worked on, what decisions were made, what
gotchas were discovered. This memory is private to you.

| | |
| --- | --- |
| Who | Every developer on the team |
| What it stores | Your session context, observations, decisions |
| Scope | Private — your sessions only |
| How to use | Install once, then automatic |
| Cost | Free |

### Layer 2 — Team shared knowledge (CLAUDE.md + docs/)

The team's shared brain lives in version-controlled files, not in a shared
database. This is intentional — shared memory databases degrade in quality
as more people write to them with no review gate.

| | |
| --- | --- |
| Who | Maintained by Hafiz, readable by everyone |
| What it stores | Rules, conventions, domain vocabulary, architectural decisions |
| Scope | Team-wide — loads into every Claude session automatically |
| How it updates | PR to the relevant CLAUDE.md or docs/ file |
| Cost | Free — just git |

Key shared knowledge files:

| File | What it contains |
| --- | --- |
| `~/.claude/CLAUDE.md` | Global rules — server map, TDD, critical rules |
| `CLAUDE.md` (umbrella) | Workspace architecture, sub-project map |
| `sifu-tutor/CLAUDE.md` | SIMS-specific rules and domain |
| `sifu-tutor/CONTEXT.md` | Domain vocabulary (Tutor, Parent, Request, Invoice, etc.) |
| `sifu-tutor/GOALS.md` | Current focus and open tasks |
| `docs/onboarding/` | This guide and other onboarding docs |
| `docs/agent-playbooks/` | Workflow playbooks for specific tasks |

### Layer 3 — Koda semantic memory server (per-user, optional)

Koda is a self-hosted semantic memory server. It used to be Hafiz-only, but it
now supports **per-user isolation**, so each developer can have their own
private space on it. This is complementary to claude-mem, not a replacement:

| | claude-mem (Layer 1) | Koda (Layer 3) |
| --- | --- | --- |
| Where it runs | Local on your machine | Shared server (`koda.tutorla.tech`) |
| Capture | Automatic (hooks) | Manual — Claude calls memory tools |
| Reach | This machine only | Any machine you log in from |
| Best for | Passive session recall | Deliberate decisions/lessons you want to query later |

How the isolation works:

- Your API key maps to **your** user ID. You can only read and write **your
  own** memories — you cannot see or modify anyone else's.
- Memories tagged `user_id = 'shared'` are readable by everyone (curated team
  knowledge). Only Hafiz writes to the shared space.
- This per-user gate is exactly what prevents the quality degradation that an
  open shared-write database would suffer from.

Stored memories get light-touch LLM cleanup (spelling/grammar/tagging) — your
original meaning and wording are preserved.

#### Connecting Koda

1. Ask Hafiz for **your personal Koda API key** (he distributes these privately
   — they are never committed to the repo).
2. Add this server to your `.mcp.json` (either the umbrella `.mcp.json` or your
   per-project one):

   ```jsonc
   {
     "mcpServers": {
       "memory": {
         "type": "http",
         "url": "https://koda.tutorla.tech/mcp",
         "headers": {
           "Authorization": "Bearer <YOUR_PERSONAL_KEY>"
         }
       }
     }
   }
   ```

3. Restart Claude Code. Verify by asking Claude to store and search a test
   memory — it should round-trip and return only your own results.

Do not share your key or commit it anywhere. If your key leaks, tell Hafiz so
he can rotate it.

---

## 17. How Team Knowledge Propagates

When you discover something important during your work — a gotcha, a rule
that should apply to everyone, a workaround for a known issue — the path to
making it team knowledge is:

```
You discover something → Tell Hafiz → Hafiz reviews → 
CLAUDE.md or docs/ updated → Loads into everyone's next session automatically
```

This is better than a shared memory database because:
- Hafiz reviews before it becomes team policy
- Changes are in git — auditable, reversible, searchable
- No service dependency — works even if external tools are down
- Every developer benefits from the next session onward

### How to raise a team knowledge update

Tell Hafiz in Slack or your next sync:

```
"I found that SIMS invoices need the deleted_at IS NULL guard on 
the InvoiceItem table too, not just the Invoice table. Should 
we add this to sifu-tutor/CONTEXT.md?"
```

Hafiz decides, updates the doc, commits it. Done.

---

## 18. Server Map

Memorise this. Using the wrong server causes production incidents.

| Environment | URL | SSH alias | Safe to modify? |
| --- | --- | --- | --- |
| Production (SIMS) | `cloud.tutorla.tech` | `production` | **NO — never** |
| Staging (sifu-tutor) | `sifu-staging.tutorla.tech` | `webvoyager` | Yes — pre-go-live QA |
| Backport QA | `sifu-backport.tutorla.tech` | `webvoyager` | Yes — integration testing |
| LLS production | `learnest.my` | `lls` | With care |

### Staging credentials (sifu-staging)

- Admin login: `admin@sifututor.com` / `password123`
- DB: `sifustaging_SifuTutorDev` / user `sifustaging_user` / `SifuStaging2025!`

### Critical server rules

- Cloudflare proxy is **disabled** on all staging domains — do not enable it.
  It breaks Laravel session cookies.
- The `staging` SSH alias is **dead** (pointed to decommissioned Hostinger VPS).
  Never use it.
- Production app path is `/home/sifututortutorla/public_html` — never
  `/var/www/sifu-tutor`.

---

## 19. Plane (Project Management)

Plane is Hafiz's project board. It is visible to the whole team. Keep it
accurate — Hafiz uses it to track progress without reading chat transcripts.

### Before creating or updating a Plane item

Always run `/plane-update` first. It loads the correct naming rules, project
IDs, and state IDs. Creating a card without reading this skill causes naming
mistakes that pollute the board.

### Naming rules

| Project | Title prefix |
| --- | --- |
| sifu-tutor | `ST-XX:` |
| ripple-suite | `RS-XX:` |
| sifututor_tutor | `STT-XX:` |
| Tooling / DX work | Goes to the `DX` project — not to product projects |

### Required fields at creation

All 9 fields must be filled: title, state, priority, start date, due date,
assignee, description, project, and labels. Cards with null fields get flagged.

### What goes on Plane vs what does not

| Goes on Plane | Does not go on Plane |
| --- | --- |
| Features, bugs, improvements | Daily task notes |
| Things Hafiz needs to track | Internal implementation sub-steps |
| Milestones and deliverables | One-line chores that take under 30 minutes |

---

## 20. What You Must Never Do

Breaking these rules can cause production incidents, data loss, or security
breaches.

| Never | Why |
| --- | --- |
| Modify anything under `live/` | Read-only production snapshots — treat as reference only |
| Push directly to `main` on sifu-tutor or sifututor_tutor | Deploys to production immediately |
| Skip Gate 4 (pre-push code review) | The gate that catches what tests miss |
| Use the `staging` SSH alias | Decommissioned — the server is gone |
| Write SIMS queries without `deleted_at IS NULL` | Soft-deleted records leak into results |
| Read or commit `.env*` files | Secrets must never appear in git history |
| Write implementation before failing tests | TDD is mandatory — tests first always |
| Use `git commit --no-verify` | Bypasses branch name and commit format hooks |
| Push to `hafizrazali90` fork | Stale mirror — push to `Sifututor` org only |
| Touch payments, auth, migrations without Hafiz review | Critical path — see section 13 |
| Write to a `<private>` tag content into public messages | claude-mem captures all chat — tag private content |

---

## 21. Troubleshooting

### Claude is mixing up project rules

Restate the project explicitly mid-session:

```
We are working on sifu-tutor. Apply sifu-tutor rules for this.
```

### Claude does not remember context from a previous session

If claude-mem is installed, it should inject past context automatically at
session start. If it is not appearing:

1. Check the worker is running: `npx claude-mem status`
2. Restart it: `npx claude-mem restart`
3. Check the web viewer at `http://localhost:37777` to see if memories exist

If claude-mem is not installed, install it now (see section 3).

### Skills are not available

Make sure VS Code is opened at `~/Projects/Sifututor` (the umbrella root).
Skills load from the umbrella `.claude/` directory and from each sub-project's
`.claude/` directory via `additionalDirectories`.

### Hook is blocking my commit — branch name error

Rename your branch to match the required format:

```bash
git branch -m old-name feat/your-description
```

### Hook is blocking my commit — message format error

Fix the commit message. The hook error output tells you exactly what is wrong.
The required format is `<emoji> <type>(<scope>): <description>`.

### claude-mem port conflict (port 37777 in use)

```bash
npx claude-mem stop
npx claude-mem start
```

Or change the port in `~/.claude-mem/settings.json`.

### I cannot reach the staging server

Check you are using the `webvoyager` alias, not `staging`:

```bash
ssh webvoyager echo ok
```

If this fails, check your `~/.ssh/config` and that your SSH key is in place.

### A pull request is failing CI but passes locally

Check if the branch is behind `integration`. Rebase before pushing:

```bash
git fetch origin
git rebase origin/integration
```

---

## 22. Related Documents

- [CLAUDE.md](../../CLAUDE.md) — umbrella workspace rules, read every session
- [agent-playbooks/agent-os-quick-start.md](../agent-playbooks/agent-os-quick-start.md) — session startup order
- [agent-playbooks/working-with-hafiz.md](../agent-playbooks/working-with-hafiz.md) — how to work with Hafiz
- [agent-playbooks/plane.md](../agent-playbooks/plane.md) — Plane naming and update rules
- [agent-playbooks/verify.md](../agent-playbooks/verify.md) — verification gate playbook
- [agent-playbooks/commit.md](../agent-playbooks/commit.md) — commit gate playbook
- [agent-playbooks/qa.md](../agent-playbooks/qa.md) — QA playbook
- [agent-playbooks/review.md](../agent-playbooks/review.md) — code review playbook
- [agent-playbooks/context-authority.md](../agent-playbooks/context-authority.md) — when to trust what source
- `sifu-tutor/CONTEXT.md` — SIMS domain vocabulary
- `sifu-tutor/GOALS.md` — current sifu-tutor focus
