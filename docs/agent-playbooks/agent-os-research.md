# Sifututor Agent OS Research Notes

Last updated: 2026-06-04

This note collects external references and design lessons for building the
Sifututor Agent OS as a reusable development system that Hafiz can distribute
to staff. Treat this as living research: update it when tools, standards, or
our own workflow lessons change.

## Goal

Build an installable Agent OS for development work that lets staff use their
own AI coding tool or LLM while still following Sifututor's shared working
agreement, safety rules, project context, verification habits, and handoff
process.

The Agent OS should be:

- tool-agnostic enough to work with Codex, Claude Code, Copilot, Jules, Gemini,
  Cursor, and similar coding agents
- strict where mistakes are expensive
- light enough that staff will actually use it
- versioned in Git so the system improves instead of being rediscovered in
  every session
- installable with a simple command or starter-kit copy

## Key External References

### Source Quality Notes

Prefer official or primary sources when changing the Agent OS:

- **Primary**: OpenAI, Anthropic/Claude Code, GitHub, VS Code, Google Jules,
  MCP official docs, framework repositories.
- **Secondary**: reputable engineering blogs and conference material.
- **Community**: Reddit, personal repos, and community frameworks. Useful for
  patterns and warnings, but do not treat them as policy without confirming
  against primary docs or Sifututor experience.

When updating this note, add the source URL, what changed, and the practical
impact for staff.

### AGENTS.md As The Cross-Agent Contract

Sources:

- OpenAI Codex AGENTS.md guide:
  https://developers.openai.com/codex/guides/agents-md
- AGENTS.md open format:
  https://agents.md/
- GitHub Copilot repository custom instructions:
  https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/add-custom-instructions/add-repository-instructions
- VS Code custom instructions:
  https://code.visualstudio.com/docs/agent-customization/custom-instructions
- Google Jules getting started:
  https://jules.google/docs/

Findings:

- `AGENTS.md` is the strongest cross-tool anchor. Codex, Copilot, Jules, and
  multiple agent ecosystems recognize or reference it.
- The common pattern is layered instruction files: global defaults, repository
  instructions, and nested project or folder overrides.
- Closest instructions should win when a monorepo or umbrella workspace has
  subprojects with different rules.
- `AGENTS.md` should stay practical: project overview, build commands, test
  commands, code style, security boundaries, and handoff rules.
- `AGENTS.md` should be treated as living documentation, not a one-time setup
  file.

Sifututor implication:

- Keep `AGENTS.md` as the source of truth for shared cross-agent behavior.
- Keep project-specific `AGENTS.md` files inside each product.
- Use compatibility shims for tool-specific systems:
  - `CLAUDE.md` can point to or extend `AGENTS.md`
  - `.github/copilot-instructions.md` can summarize and link to `AGENTS.md`
  - `GEMINI.md`, Cursor rules, or other files can be generated from the same
    source when needed

### Claude Code Practices

Sources:

- Claude Code best practices:
  https://code.claude.com/docs/en/best-practices
- Claude Code skills:
  https://code.claude.com/docs/en/skills
- Claude Code hooks:
  https://code.claude.com/docs/en/hooks
- Claude Code subagents:
  https://code.claude.com/docs/en/sub-agents

Findings:

- Claude Code recommends an "explore first, then plan, then code" pattern.
- Agents need a way to verify their work, not only generate code.
- Context management is central. Long sessions degrade when too much search,
  logs, and file content remain in the main conversation.
- Skills are the right home for repeated procedures. They load only when used,
  which keeps always-on context smaller.
- Subagents are useful when research or review would flood the main thread.
- Hooks can automate lifecycle checks, but command hooks run with user
  permissions and must be reviewed carefully.
- Plugins bundle skills, hooks, subagents, and MCP servers into installable
  units.

Sifututor implication:

- Do not put every procedure inside `AGENTS.md`.
- Put stable rules in `AGENTS.md`.
- Put repeatable actions in playbooks or skills, such as task routing, verify,
  QA, review, commit, save-session, production monitoring, and product design.
- Use hooks for guardrails and reminders, but keep them simple, auditable, and
  non-destructive by default.
- Use subagents mainly for review, diagnosis, research, and parallel
  exploration, not as the default for every task.

### Guardrails, Human Intervention, And Evaluation

Sources:

- OpenAI practical guide to building agents:
  https://openai.com/business/guides-and-resources/a-practical-guide-to-building-ai-agents/
- OpenAI Agents SDK guardrails:
  https://openai.github.io/openai-agents-python/guardrails/
- OpenAI agent evals:
  https://developers.openai.com/api/docs/guides/agent-evals

Findings:

- Guardrails should be layered. One prompt rule is not enough.
- Useful guardrail categories include relevance checks, safety checks, PII
  filtering, moderation, tool safeguards, deterministic rules, and output
  validation.
- Tool safeguards should classify actions by risk: read-only, reversible,
  write access, financial impact, and required permissions.
- Human intervention is needed when the agent exceeds retry thresholds or tries
  high-risk actions.
- Agent quality should be evaluated through traces, graders, datasets, and
  repeatable eval runs once the desired behavior is clear.

Sifututor implication:

- Keep the existing critical-lane split:
  - Phase A: read-only diagnosis
  - Phase B: implementation only after Hafiz approval
- Classify tools and actions by risk:
  - Low: read files, inspect docs, run safe tests
  - Medium: edit code, create branches, update docs
  - High: migrations, production deploys, payment logic, invoice logic,
    commission logic, auth, secrets, mobile API contracts
- Add lightweight workflow evals for the Agent OS itself:
  - Did the router choose the right lane?
  - Did the agent avoid editing during discussion mode?
  - Did the final answer include what changed, how checked, and what remains?
  - Did the agent avoid committing or pushing without approval?

### MCP And Tool Access

Sources:

- Model Context Protocol server concepts:
  https://modelcontextprotocol.io/docs/learn/server-concepts
- MCP specification and docs repository:
  https://github.com/modelcontextprotocol/modelcontextprotocol

Findings:

- MCP standardizes how agents connect to external tools and context.
- MCP has three important concepts:
  - Tools: actions the model can call
  - Resources: context or data the client can read
  - Prompts: reusable prompt templates or workflows
- MCP reduces custom one-off integrations, but tool access still needs
  permission and security boundaries.

Sifututor implication:

- Use MCP for shared services like memory, GitHub, Plane, Google Drive, and
  Planner when stable connectors exist.
- Do not make every staff install every MCP server.
- Start with a minimal staff setup, then add optional connectors by capability
  profile.
- Treat MCP tools like real permissions. Write access, credentials, and
  production data need explicit boundaries.

### Multi-Agent Frameworks

Sources:

- Microsoft AutoGen repository:
  https://github.com/microsoft/autogen
- OpenAI Agents SDK agents and guardrails docs:
  https://openai.github.io/openai-agents-python/agents/
  https://openai.github.io/openai-agents-python/guardrails/

Findings:

- Multi-agent frameworks are useful for orchestration, handoffs, tools,
  sessions, and evaluation.
- Microsoft AutoGen is now in maintenance mode and points new users toward
  Microsoft Agent Framework, which is a reminder that agent frameworks change
  quickly.
- The safest advice from multiple sources is to start with a strong single-agent
  workflow and add multi-agent orchestration only when the work demands it.

Sifututor implication:

- Do not rebuild the Sifututor Agent OS around one framework too early.
- Keep the portable layer as Markdown, scripts, hooks, and small skills.
- Add framework-specific automation later only where it clearly saves time.

### Memory Architecture For Coding Agents

Sources:

- Local transcript: `/Users/hafizrazali/Downloads/The Four Types of Memory Every AI Agent Needs.txt`
- Local transcript: `/Users/hafizrazali/.codex/attachments/c3731627-e848-48c8-986f-9fba749d1c90/pasted-text.txt`

Findings:

- Coding agents need all four memory types:
  - **Working memory**: the current context window, loaded files, current
    conversation, and current tool outputs.
  - **Semantic memory**: stable facts, rules, architecture, policies, commands,
    and project documentation.
  - **Procedural memory**: reusable know-how, step order, decision rules, and
    workflow judgment.
  - **Episodic memory**: distilled experience from past sessions, decisions,
    corrections, and mistakes.
- Working memory is fast but volatile. It should be kept small enough that the
  agent does not lose important information in the middle of the context.
- Semantic memory can often be simple Markdown, not only vector databases or
  knowledge graphs.
- Procedural memory maps well to skills and playbooks. Skills use progressive
  disclosure: startup sees only name and description, full instructions load
  only when relevant, and scripts/assets/references load only at point of need.
- Episodic memory should not be raw transcript storage. It should be distilled
  into durable notes only when the lesson will help future sessions.
- Skills are powerful because they can include executable scripts, but that
  means they must be reviewed like software dependencies.

Sifututor implication:

- Do not use Koda for everything.
- Use the right storage location for each memory type:

| Memory type | Sifututor home | Examples |
| --- | --- | --- |
| Working | current chat context, active task file, temporary scratch notes | current request, files just read, latest test output |
| Semantic | `AGENTS.md`, project `AGENTS.md`, `CLAUDE.md`, `README.md`, `TESTING.md`, docs | project rules, build commands, safety boundaries, architecture |
| Procedural | `docs/agent-playbooks/`, `.agents/skills/`, `.claude/skills/`, scripts/templates | task router, verify, QA, review, commit, save-session |
| Episodic | Koda, save-session notes, handoff/snapshot docs | corrections, durable lessons, failed approaches, approved decisions |

- Koda should store distilled lessons, not full chat logs.
- `AGENTS.md` should store stable rules, not long step-by-step procedures.
- Playbooks and skills should store repeatable process.
- The current chat should not be trusted as permanent memory.
- Staff distribution should teach this distinction explicitly, because it
  prevents the common mistake of putting every instruction into one giant file.

### CLI Versus MCP

Sources:

- Local transcript: `/Users/hafizrazali/.codex/attachments/125ad375-ea35-4e88-a552-e1b0dfcdb924/pasted-text.txt`

Findings:

- CLI and MCP both let agents interact with the outside world, but they are
  useful for different jobs.
- CLI is usually better when the command maps directly to the task:
  - file operations
  - Git
  - text search
  - test commands
  - local scripts
  - Docker and other developer tools the model already knows well
- MCP is usually better when the server abstraction or governance matters:
  - JavaScript-rendered webpages
  - OAuth and token handling
  - Slack, Notion, Google Drive, Plane, Planner, GitHub APIs
  - per-user access control
  - audit trails
  - organization-managed credentials
- MCP has context overhead because tool schemas are loaded into the agent's
  working memory. Installing too many MCP servers can make every session
  heavier before work starts.
- The right answer is not CLI or MCP. Use both:
  - CLI when it is local, direct, cheap, and already well-known.
  - MCP when abstraction, authentication, permissions, or auditability justify
    the overhead.

Sifututor implication:

- Staff installs should not enable every connector by default.
- Default staff setup should use CLI for local development checks and Git
  inspection.
- Enable MCP by capability profile:
  - support/ops: Planner or Google Drive read access where needed
  - QA: browser, Drive, or issue tracker tools where needed
  - developers: GitHub/Plane/Koda only if permissions are clear
  - owner/senior agents: broader MCP access with explicit safety rules
- For local repo work, prefer shell commands such as `rg`, `git`, test runners,
  and guard scripts.
- For authenticated services and staff-facing systems, prefer MCP/connectors
  with scoped credentials and audit trails.

## Recommended Sifututor Agent OS Architecture

Use a layered architecture:

1. **Operating contract**
   - Root `AGENTS.md`
   - Project `AGENTS.md`
   - Compatibility files for Claude, Copilot, Gemini, Cursor, or other tools

2. **Project context**
   - `CLAUDE.md` for deep Claude-specific project reference
   - `README.md`, `TESTING.md`, architecture docs, API docs, and business docs
   - scoped docs for staff onboarding

3. **Workflow playbooks**
   - task routing
   - product design
   - diagnosis
   - verify
   - QA
   - review
   - commit
   - save-session
   - handoff
   - production monitoring

4. **Skills and commands**
   - one skill per repeatable procedure
   - short `SKILL.md` entrypoints
   - supporting scripts and templates in the skill folder

5. **Guardrails and hooks**
   - pre-commit guard
   - sensitive path checks
   - workflow route reminders
   - no autonomous push/deploy
   - critical-lane approval checks

6. **Memory**
   - Koda for durable project lessons, decisions, corrections, and preferences
   - no secrets or raw credentials
   - store only lessons that should survive future sessions
   - keep semantic rules in docs, procedural steps in playbooks/skills, and
     episodic lessons in Koda or handoff/snapshot notes

7. **Tool connectors**
   - GitHub for engineering source of truth
   - Plane for Hafiz-visible mission status
   - Planner for staff-reported intake
   - Google Drive for docs when explicitly needed
   - optional MCP connectors by capability profile

8. **Verification and evals**
   - focused tests during debugging
   - broader checks before commit or release
   - permanent E2E decision for user-facing work
   - periodic Agent OS evals for routing and reporting quality

9. **Distribution**
   - install script or plugin package
   - capability-profile setup
   - generated tool-specific instruction files
   - health check command
   - uninstall or reset command

## Tool Compatibility Map

| Tool | Primary file | Extra support | Agent OS approach |
| --- | --- | --- | --- |
| Codex | `AGENTS.md` | local skills, hooks, MCP | Use `AGENTS.md` as contract and `.agents/skills/` as playbook wrappers. |
| Claude Code | `CLAUDE.md` | skills, hooks, subagents, MCP, plugins | Keep `CLAUDE.md` short and point to shared playbooks. Package advanced features later as a plugin. |
| GitHub Copilot | `.github/copilot-instructions.md`, `AGENTS.md` | prompt files, path instructions | Generate a short Copilot shim from the Agent OS. Keep it broad and practical because Copilot sends instructions often. |
| VS Code agents | `.github/copilot-instructions.md`, `AGENTS.md` | workspace/user instructions | Same as Copilot. Prefer repository instructions over personal memory for team rules. |
| Google Jules | `AGENTS.md` | task execution in repo | Keep project setup, test commands, and safety rules discoverable in `AGENTS.md`. |
| Gemini/Cursor/other agents | tool-specific rules file | varies | Generate a compatibility shim that links back to `AGENTS.md` and key playbooks. |

Practical rule: the Agent OS source should be tool-neutral Markdown first.
Tool-specific files should be generated or kept as thin adapters.

## Capability Preset Matrix

Roles are onboarding presets, not real permission boundaries. The real
boundary is what tools, credentials, and filesystem access are connected to the
agent session.

Use this table to choose a conservative default setup. Enforce access through
GitHub, Plane, tool credentials, repo permissions, hooks, and explicit approval
gates.

| Preset | Default connected capability | Commit posture | Push/deploy posture | Default lane |
| --- | --- | --- | --- | --- |
| Owner | broad tools when intentionally connected | exact file-list approval | explicit current-session approval | any lane |
| Senior developer | repo read/write and approved engineering tools | exact file-list approval | no by default; explicit approval only | normal engineering |
| Junior developer | scoped repo read/write | no by default unless paired/reviewed | no | small change or normal engineering with review |
| QA | read, test, browser, evidence tools | no by default | no | verify, QA, regression evidence |
| Support / ops | intake and evidence tools | no | no | intake, reproduction, screenshots, issue creation |
| Product/design | docs/spec tools | no by default | no | product design |

If a stronger tool is connected, the Agent OS should report that capability and
still apply the relevant risk gate. For example, a session with GitHub write
access still cannot push without explicit current-session approval.

## Recommended Staff Lanes

### Discussion / Learning

Use when staff need to understand, compare options, or write a better bug
report. The agent should not edit code.

Good outputs:

- plain-language explanation
- 2-3 options
- risk tradeoff
- suggested next action

### Intake / Reproduction

Use when support or QA reports a bug. The agent gathers evidence before any
developer work starts.

Good outputs:

- symptom summary
- affected user role
- route or screen
- screenshots or logs when safe
- steps to reproduce
- whether this needs developer attention

### Small Change

Use for typo, copy, config, minor UI, or docs-only changes.

Good outputs:

- exact file changed
- focused check
- no broad refactor

### Normal Engineering

Use for features and non-critical bugfixes.

Good outputs:

- issue link or task context
- implementation
- focused test
- E2E decision for user-facing behavior
- QA/review evidence

### Critical Lane

Use for auth, payments, invoices, commissions, migrations, deployment, and
mobile API contracts.

Good outputs:

- read-only diagnosis first
- risk explained in human terms
- explicit approval before implementation
- stronger verification and human review

## Installer Requirements

The staff installer should be boring and predictable.

Required behavior:

- detect the project root
- refuse to install inside `live/`
- refuse to overwrite existing instruction files without backup or confirmation
- copy or generate the correct instruction files for the chosen tool
- install only the selected profile's playbooks and skills
- avoid installing write-capable MCP connectors by default
- run a health check after installation
- print the next safe command for the staff member

Minimum health check:

- instruction files exist
- project `AGENTS.md` can be found
- git repository detected
- no `.env*` or `live/` paths are included in install targets
- tool-specific files are valid Markdown or JSON/TOML where applicable
- optional connectors are reachable if configured

## First Version Build Plan

For the current Sifututor workspace, build the internal MVP first. See
[agent-os-internal-build-plan.md](agent-os-internal-build-plan.md).

The staff starter kit should wait until the internal system proves it can
detect capabilities, route discussion versus action correctly, enforce approval
gates, and capture durable lessons without noise.

### Version 0.1: Portable Markdown Starter Kit

Goal: staff can install the working agreement into a repo even without Claude
or Codex-specific features.

Build:

- root `AGENTS.md` template
- project `AGENTS.md` template
- `.github/copilot-instructions.md` shim
- `CLAUDE.md` shim
- `GEMINI.md` shim
- staff onboarding doc
- common mistakes doc
- escalation rules doc
- basic health-check script

Do not build yet:

- complex MCP setup
- automatic production connectors
- multi-agent orchestration
- eval harness

### Version 0.2: Sifututor Development Playbooks

Goal: staff can follow the same core routes.

Build:

- task-router
- product-design
- diagnose
- verify
- QA
- review
- commit
- save-session
- handoff

Add simple examples for:

- Laravel bugfix
- Next.js UI change
- React Native QA evidence
- docs-only update

### Version 0.3: Tool-Specific Adapters

Goal: staff using different tools still get the same behavior.

Build:

- Claude Code skills and optional plugin
- Codex skill wrappers
- Copilot prompt files
- Gemini/Cursor compatibility shims
- installer choices by capability profile and tool

### Version 0.4: Guardrails And Memory

Goal: reduce repeated mistakes.

Build:

- pre-commit guard
- sensitive path guard
- discussion-mode guard or router correction
- critical-lane reminder
- Koda memory setup for approved users
- local memory fallback for staff without Koda access

### Version 0.5: Agent OS Evals

Goal: test the workflow itself.

Build eval cases for:

- discussion prompt must not trigger commit workflow
- payment/auth prompt must trigger critical lane
- staff bug report must route through intake
- user-facing fix must require E2E decision
- commit request must require exact file-list approval
- push/deploy request must require explicit approval

## Update Procedure

When the Agent OS changes:

1. Update this research note if the change comes from a new external source or
   reusable lesson.
2. Update `agent-os.md` only when the operating model changes.
3. Update `AGENTS.md` only when every agent must obey the rule.
4. Update a playbook when only one workflow changes.
5. Update tool shims after the source file changes, not before.
6. Run the health check and guard.
7. Store a Koda memory only for durable lessons, corrections, or decisions.

Do not duplicate the same long rule in every tool-specific file. Put the rule
once in the source-of-truth file and link or generate the shims.

## Recommended Repository Shape For A Staff Starter Kit

```text
sifututor-agent-os/
  README.md
  install.sh
  uninstall.sh
  agent-os.config.example.json
  templates/
    AGENTS.md
    CLAUDE.md
    copilot-instructions.md
    GEMINI.md
  docs/
    staff-onboarding.md
    working-agreement.md
    common-mistakes.md
    escalation-rules.md
    task-lanes.md
  playbooks/
    task-router.md
    product-design.md
    diagnose.md
    verify.md
    qa.md
    review.md
    commit.md
    save-session.md
    handoff.md
  skills/
    task-router/
      SKILL.md
    verify/
      SKILL.md
    qa/
      SKILL.md
  scripts/
    health-check.sh
    pre-commit-guard.sh
    generate-tool-files.sh
  examples/
    laravel-project/
    nextjs-project/
    react-native-project/
```

## Staff Installation Model

The installer should ask only a few questions:

1. Which starting profile is this for?
   - Hafiz or owner
   - developer
   - QA
   - support or operations
   - product/design

2. Which tool will the staff use?
   - Claude Code
   - Codex
   - GitHub Copilot
   - Gemini CLI
   - Cursor or other

3. Which project type?
   - Laravel
   - Next.js
   - React Native
   - docs-only
   - mixed monorepo

4. Which connectors are available?
   - none
   - GitHub only
   - GitHub plus Koda
   - GitHub plus Plane
   - full Sifututor workspace

The installer should then:

- copy the right instruction files
- generate compatibility shims
- install or link skills/playbooks where supported
- add safe hooks only when supported
- run a health check
- print what the staff can safely do next

## What To Avoid

- One huge prompt that tries to teach everything at startup.
- One giant memory bucket where rules, procedures, transcripts, and current
  state are mixed together.
- A workflow so strict that discussion triggers implementation machinery.
- Tool-specific lock-in too early.
- Giving staff write access to production tools by default.
- Letting agents commit, push, deploy, or change high-risk code without human
  approval.
- Running full E2E repeatedly during debugging.
- Creating many subagents before the single-agent workflow is stable.
- Treating memory as a dumping ground for chat transcripts.
- Depending on private chat context instead of versioned docs and task files.

## First Build Recommendation

Build the first distributable version as a Markdown-first starter kit:

1. `AGENTS.md` as the universal contract.
2. Tool shims generated from the same source.
3. Playbooks for the main development lanes.
4. A small install script.
5. A health-check script.
6. Capability-profile-based staff onboarding docs.
7. A memory guide that explains working, semantic, procedural, and episodic
   memory in staff-friendly terms.
8. Optional Claude/Codex skills only after the base files work.

This keeps the system portable. Staff can start with any LLM or coding agent,
but the project behavior still comes from the same Sifututor Agent OS.

## Open Questions

- Should the starter kit live in the existing `ai-dev-starter-kit` repo or a
  new dedicated `sifututor-agent-os` repo?
- Should staff have access to Koda memory directly, or should Koda be owner and
  senior-agent only at first?
- Which capability profiles should include GitHub issue creation by default?
- Which capability profiles should include code-changing access by default?
- Should Plane be visible to all staff or only Hafiz and engineering leads?
- What is the smallest safe workflow for non-technical staff to report bugs
  without touching code?
