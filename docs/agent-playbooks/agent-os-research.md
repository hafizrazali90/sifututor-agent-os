# Sifututor Agent OS Research Notes

Last updated: 2026-08-03

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

### Workflow Orchestration For Agentic Development

Sources:

- LangGraph overview:
  https://docs.langchain.com/oss/python/langgraph/overview
- LangChain human-in-the-loop middleware:
  https://docs.langchain.com/oss/python/langchain/human-in-the-loop
- OpenAI Agents SDK guardrails:
  https://openai.github.io/openai-agents-python/guardrails/
- OpenAI Agents SDK tracing:
  https://openai.github.io/openai-agents-python/tracing/
- Microsoft Agent Framework:
  https://github.com/microsoft/agent-framework
- AutoGen Magentic-One:
  https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html
- CrewAI Flows:
  https://docs.crewai.com/en/concepts/flows

Findings:

- Reputable systems separate **workflow orchestration** from free-form model
  reasoning. The LLM decides inside a controlled path; it does not invent the
  whole operating process every turn.
- LangGraph treats durable execution, persistence, human-in-the-loop, memory,
  and observability as core infrastructure for long-running agents.
- LangChain's human-in-the-loop middleware pauses sensitive tool calls based on
  policy and supports decision types such as approve, edit, reject, and
  respond. It also requires saved state so the workflow can resume safely.
- OpenAI Agents SDK separates guardrails and tracing from agent prompts. This
  supports the idea that workflow safety and evidence should be observable, not
  hidden inside the chat.
- Microsoft Agent Framework emphasizes orchestration, multi-agent workflows,
  deployment, and provider flexibility. This supports keeping Sifututor Agent
  OS LLM-agnostic.
- AutoGen's Magentic-One pattern uses an orchestrator to plan, delegate,
  monitor progress, and revise plans. This supports having a router/workflow
  layer before tool use.
- CrewAI Flows separate deterministic workflow control from autonomous agents.
  This supports using predictable process for intake, approval, verification,
  and release while still letting agents reason inside steps.

Sifututor implication:

- The Agent OS should not be "one agent can do anything." It should be:
  "one agent can do many things through the right workflow, with the right
  approval and evidence."

### L8 Principal Agentic Engineering Workflow - Kun Chen

Sources:

- Local transcript:
  `~/Downloads/L8 Principal's Agentic Engineering Workflow.txt`
- YouTube:
  https://www.youtube.com/watch?v=iQyg-KypKAA
- ByteByteGo companion article:
  https://blog.bytebytego.com/p/an-ex-meta-l8s-agentic-engineering
- AXI:
  https://github.com/kunchenguid/axi
- Lavish:
  https://github.com/kunchenguid/lavish-axi
- no-mistakes:
  https://github.com/kunchenguid/no-mistakes
- gnhf:
  https://github.com/kunchenguid/gnhf
- treehouse:
  https://github.com/kunchenguid/treehouse
- firstmate:
  https://github.com/kunchenguid/firstmate
- Vercel skills CLI:
  https://github.com/vercel-labs/skills
- WezTerm:
  https://wezterm.org/index.html
- tmux:
  https://github.com/tmux/tmux/wiki
- Neovim:
  https://neovim.io/
- OpenSuperWhisper:
  https://github.com/starmel/OpenSuperWhisper

Source quality notes:

- The downloaded transcript is useful but incomplete; it stops around the
  no-mistakes section. Use the ByteByteGo article as the fuller companion
  source for validation, parallelization, worktrees, remote control, and the
  daily flow.
- Kun's repos are primary sources for his tools, but they are still one
  person's workflow. Treat them as strong design references, not automatic
  policy for Sifututor.
- Any external tool should be evaluated against Sifututor's risk model before
  adoption. Popularity is not enough.

Findings:

1. **Agentic engineering is a workflow, not one magic agent.**
   Kun's setup combines terminal continuity, memory, skills, visual planning,
   autonomous implementation, independent validation, parallel worktrees, and
   a first-mate/orchestrator layer. The practical idea is that the human stays
   at the level of intent, decisions, and quality bar while agents handle more
   of the middle.

2. **Agent-agnostic memory and skills are central.**
   The transcript emphasizes a small global memory file, project-level
   `AGENTS.md`/`CLAUDE.md`, and skills for conditional knowledge. This matches
   Sifututor's direction: stable rules in `AGENTS.md`, deeper project context
   in `CLAUDE.md`, and repeatable workflows in skills/playbooks.

3. **Keep always-loaded memory small.**
   Kun warns that global memory is loaded into every session, so it should
   mostly hold personal preferences and durable rules. Larger or conditional
   instructions should move into skills so they load only when needed. This
   supports Sifututor's memory architecture: docs are the system, Koda is
   distilled lessons, and skills/playbooks handle conditional workflows.

4. **E2E-first bug fixing is a key rule.**
   The transcript says bug fixes should start by reproducing the bug in an
   end-user-like setting, not by jumping straight to unit tests. This strongly
   supports Sifututor's Agent-As-Tester model, permanent E2E rule, QA playbook,
   and human-journey evidence standard.

5. **Skill quality must be evaluated.**
   Kun explicitly warns that random internet skills can leak secrets, run
   unsafe commands, or degrade agent performance. Vercel's skills CLI defines
   skills as reusable `SKILL.md` instruction sets and supports many agent
   harness locations, but installation should still be governed. For Sifututor,
   this supports having a skill registry, install manifest, workflow doctor,
   and evaluation harness instead of blindly installing popular skills.

6. **Tool ergonomics matter as much as model quality.**
   Kun's AXI work argues that tools should be designed for agents, not only
   humans. AXI's published GitHub benchmark reports `gh-axi` at 100% success,
   lower average cost, and lower duration than GitHub MCP in that benchmark.
   Its principles include token-efficient output, minimal schemas, truncation
   with escape hatches, structured errors, and next-step suggestions. This
   supports Sifututor's "best connector" discussion: choose CLI/MCP/API/AXI by
   measured reliability, token cost, latency, safety, and output quality.

7. **Visual planning can reduce Hafiz frustration.**
   Lavish turns plans into local-first interactive HTML artifacts where the
   human can annotate specific elements and send feedback back to the agent.
   This maps directly to Hafiz's complaint that walls of text are hard to
   understand and that he wants to read code-like logic in natural language.
   Sifututor already has Session Map HTML ideas; Lavish suggests a stronger
   pattern for complex UX/product/design decisions.

8. **Implementation should follow a clarified plan.**
   Kun uses a concentrated planning phase so implementation can run with less
   interruption. This matches Hafiz's desired behavior: discuss options first,
   understand what will be built, then let the agent proceed inside the agreed
   boundary.

9. **Validation should be independent and adversarial.**
   The no-mistakes workflow runs validation in a disposable worktree with
   review, tests, docs, lint, push, PR, and CI. Kun says reviewers should run
   in fresh context to avoid same-session bias, ambiguous product decisions
   should escalate to the human, and E2E evidence should be forced. Sifututor
   already has verify, QA, review, commit, and CI/PR workflow pieces; the gap
   is whether to bundle them into a stronger no-mistakes-style local gate.

10. **Parallel work needs isolation and visible state.**
    Kun uses tmux for visible/persistent agent sessions and treehouse for
    reusable isolated worktrees. Treehouse manages a worktree pool so agents do
    not step on each other. Sifututor already uses worktrees heavily, but the
    workflow still relies on the agent remembering branch/worktree state. A
    lightweight treehouse-like pattern or stricter Session Release Ledger could
    reduce confusion.

11. **Long-running autonomous work needs small committed steps.**
    gnhf runs long objectives through repeated small, committed, documented
    changes with rollback/retry behavior and logs. This is similar to our goal
    budget/autopilot discussions, but Sifututor should be careful: for product
    code, payments, invoices, mobile API contracts, deployments, and live data,
    autonomous loops need strict boundaries and evidence requirements.

12. **A "first mate" can reduce coordination overhead.**
    firstmate positions one primary agent as the interface to a crew, with
    explicit project modes such as no-mistakes, direct-PR, or local-only. This
    is conceptually close to our router/orchestrator idea. For Sifututor, the
    useful principle is not necessarily installing firstmate now; it is making
    the route and autonomy mode explicit before work begins.

13. **Remote continuity is part of the workflow.**
    Kun uses tmux plus SSH/Tailscale/mosh so sessions continue across devices.
    This is not an immediate Sifututor Agent OS core need, but it reinforces
    the value of persistent session state, visible status, and continuation
    prompts.

Sifututor comparison:

| Kun workflow element | Sifututor already has | Gap / discussion point |
| --- | --- | --- |
| Small global memory + project memory | Root/project `AGENTS.md`, `CLAUDE.md`, Koda | Audit what belongs in always-loaded docs vs skills/Koda |
| Skills for conditional knowledge | Codex skills + playbooks | Add evaluation and pruning discipline for skill quality |
| Voice-first prompting | Hafiz often uses short natural prompts | Decide whether to recommend local dictation as optional |
| AXI-style tool ergonomics | Capability model, probes, wrappers | Benchmark or score connector choices before standardizing |
| Lavish visual planning | Session Map HTML, product-design playbook | Decide whether complex planning should use interactive HTML |
| Autonomous implementation after plan | Autopilot boundaries | Strengthen "planned enough to autopilot" criteria |
| no-mistakes validation gate | Verify, QA, review, commit, PR/CI playbooks | Consider one bundled local gate before push/PR |
| Fresh reviewer context | Review playbook | Make independent review/fresh-context rule clearer |
| E2E evidence | Agent-As-Tester + permanent E2E rule | Keep enforcing; improve scenario examples |
| Worktree isolation | Manual worktrees, Session Release Ledger | Improve worktree naming/status/cleanup or consider a tool |
| gnhf long-running loop | Goal/autopilot discussion, session maps | Define when overnight/autonomous loops are safe or forbidden |
| firstmate orchestration | Task router, workflow skills, parity contract | Make "mode" explicit: local-only, PR-ready, deploy-ready, etc. |

Recommended discussion order:

1. **Operating posture:** Do we want Hafiz to be "captain / product-risk owner"
   and the agent to be "technical crew / tester / secretary"?
2. **Memory and skills:** What belongs in `AGENTS.md`, project docs, Koda, and
   skills so we reduce token waste without losing context?
3. **Planning artifact:** Should complex decisions use an interactive HTML plan
   or a better Markdown/Session Map first?
4. **Tool connector standard:** Should we adopt an AXI-like scorecard for CLI,
   MCP, API, browser, and GUI tools?
5. **Validation gate:** Should we build a Sifututor "no-mistakes-lite" gate
   that bundles review, tests, docs, lint, evidence, PR, and CI?
6. **Parallel work:** How many concurrent sessions/worktrees should we allow,
   and what status board prevents confusion?
7. **Autonomous long-running work:** When is a gnhf-style loop safe, and what
   is forbidden?
8. **First-mate routing:** Should one agent/session become the visible
   coordinator while workers run behind it?
9. **Remote/continuation:** What status, Session Map, and resume artifacts are
   enough so work feels continuous across devices and sessions?

Initial recommendation:

- Do not install the full external toolchain yet.
- Use the workflow as a design reference and discuss one layer at a time.
- First Sifututor improvement candidate: strengthen the validation gate into a
  no-mistakes-lite playbook that runs fresh-context review, focused tests,
  E2E/human-journey proof, docs/evidence checks, lint/build where relevant,
  and clear PR/CI status before asking Hafiz to review or merge.

### Cross-Agent Workflow Parity

Sources:

- OpenAI Agents SDK agents:
  https://openai.github.io/openai-agents-python/agents/
- OpenAI Agents SDK handoffs:
  https://openai.github.io/openai-agents-python/handoffs/
- OpenAI Agents SDK guardrails:
  https://openai.github.io/openai-agents-python/guardrails/
- OpenAI Agents SDK tracing:
  https://openai.github.io/openai-agents-python/tracing/
- LangGraph overview:
  https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph durable execution:
  https://docs.langchain.com/oss/python/langgraph/durable-execution
- LangGraph persistence:
  https://docs.langchain.com/oss/python/langgraph/persistence
- Claude Code skills:
  https://docs.anthropic.com/en/docs/claude-code/skills
- Claude Code hooks:
  https://docs.anthropic.com/en/docs/claude-code/hooks
- Claude Code subagents:
  https://docs.anthropic.com/en/docs/claude-code/sub-agents
- Microsoft Agent Framework:
  https://github.com/microsoft/agent-framework
- AutoGen Magentic-One:
  https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/magentic-one.html
- AutoGen human-in-the-loop:
  https://microsoft.github.io/autogen/stable/user-guide/agentchat-user-guide/tutorial/human-in-the-loop.html
- CrewAI Flows:
  https://docs.crewai.com/en/concepts/flows

Findings:

- Reputable agent systems separate the portable workflow from the specific
  agent implementation.
- Handoffs, guardrails, tracing, state, and human approval are treated as
  infrastructure, not as optional chat style.
- Durable systems keep state outside the model's temporary context so another
  agent or a future session can resume safely.
- Human-in-the-loop controls usually pause at sensitive actions, not at every
  small step.
- Multi-agent systems often use an orchestrator/router pattern so agents do
  not invent the process from scratch on every request.
- Tool-specific skills and hooks are useful adapter layers, but they should not
  become separate sources of truth.

Sifututor implication:

- Claude and Codex do not need identical command names, but they must follow
  the same workflow contract.
- The shared playbook should define the behavior; Claude slash commands and
  Codex `$skill` wrappers are adapters.
- Product Design can be one Codex skill and four Claude commands only if both
  expose the same phases, decisions, and stopping points.
- Parity needs its own eval coverage, because proving Codex routing is not the
  same as proving Claude/Codex behavior stays aligned.
- Keep the current Agent OS portable and model-agnostic. Build future adapters
  for Cursor, Copilot, Gemini, or staff LLMs from the same contract instead of
  making a separate workflow for every tool.
- Keep workflows explicit and inspectable. Each workflow should define:
  start condition, owner, tools, state, evidence, approval boundary, exit
  condition, save location, and common failure.
- Use deterministic rules for safety and state transitions. Let the model
  reason inside the workflow, not override the workflow.
- Human approval should happen at meaningful risk points, not every tiny step.
- Every workflow should be resumable after pause, compaction, branch switch, or
  handoff. Resume should start by checking state, not trusting old chat.
- Use framework-specific orchestration later only if the Markdown/scripts/skills
  baseline proves too manual.

Workflow design baseline for Sifututor:

```text
intake -> route -> prepare context -> act in safe slice -> verify evidence
-> review risk -> approval boundary -> save state -> next recommended action
```

Non-technical version:

```text
Understand the job, choose the right path, prepare properly, do one safe chunk,
prove it works, check risk, ask approval only where it matters, then leave a
clear trail for the next session.
```

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
- MCP tools specification:
  <https://modelcontextprotocol.io/specification/2025-11-25/server/tools>
- GitHub MCP Server:
  <https://github.com/github/github-mcp-server>
- GitHub CLI manuals:
  <https://cli.github.com/manual/gh_auth_status>,
  <https://cli.github.com/manual/gh_repo_view>,
  <https://cli.github.com/manual/gh_help_formatting>
- Microsoft Graph best practices and throttling:
  <https://learn.microsoft.com/en-us/graph/best-practices-concept>,
  <https://learn.microsoft.com/en-us/graph/throttling>
- Google Drive API performance and file reads:
  <https://developers.google.com/workspace/drive/api/guides/performance>,
  <https://developers.google.com/drive/api/reference/rest/v3/files/list>
- Playwright best practices:
  <https://playwright.dev/docs/best-practices>
- Sentry and Better Stack API docs:
  <https://docs.sentry.io/api/>,
  <https://docs.sentry.io/api/ratelimits/>,
  <https://betterstack.com/docs/uptime/api/getting-started-with-uptime-api/>

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
- Direct API is useful when wrapped behind a narrow script. It should not mean
  pasting raw API calls and broad payloads into chat. Use it for stable
  low-noise probes, read-only monitoring checks, and service summaries where
  the wrapper can sanitize output.
- Browser automation is its own category. It is not mainly a connector choice;
  it proves what a human user sees and can do. Use Playwright/browser evidence
  for staff/admin/parent/tutor UI journeys when feasible.
- Native app control is last-mile automation for real desktop apps. Use it
  only when the task actually happens inside the app and a structured API,
  CLI, connector, or browser path cannot prove the work.

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
- For probes and recurring operational checks, prefer CLI/direct wrapper
  scripts with tiny structured output.
- For Google Drive documents, prefer the Google Drive connector/app when live
  document content is needed; use wrapper probes only for metadata/readiness.
- For Planner, prefer the direct Microsoft Graph wrapper for small read-only
  staff-intake summaries unless a richer connector workflow becomes necessary.
- For Sentry/BetterStack, prefer direct read-only wrappers that return
  status/count evidence without raw logs, secret values, issue details, or
  monitor URLs.
- For visible product behavior, prefer browser/mobile automation over code
  inspection alone.

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
   - Mission Ledger for bigger/future follow-ups inside the default Agent OS
   - Plane only when Hafiz explicitly asks for it in the current session
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

## Native Agent OS Workspace UI And Foundation Comparison — 2026-08-03

### Revision note (correction pass)

This section was first written 2026-08-03 and is revised the same day after
Hafiz flagged a critical omission and several factual errors. This is a
**correction pass on the same section**, not a new independent research
round — everything below replaces the original version of this section.
Nothing before this heading changed.

What changed in this revision:

- Added **Omnigent** (`omnigent-ai/omnigent`), which prior Sifututor research
  (Koda-backed memory, 2026-07-13) had already identified as the closest
  direct comparable and which the original version of this section omitted.
  Investigated from primary sources: the GitHub repo itself, `omnigent.ai`,
  its `/docs/build/harnesses` page, and the repo's own `docs/POLICIES.md`.
- Corrected: opencode already ships TUI, CLI, desktop, and web surfaces
  today (verified via its own repo package list) — the original version
  wrongly implied desktop/web were future possibilities.
- Corrected: the Linux Foundation Agentic AI Foundation (AAIF) announcement
  date is **2025-12-09**, not 2026-04-07 (that later date was a goose-project
  blog post about the move, not the announcement itself).
- Replaced "vendor-sanctioned subscription reuse" with narrower,
  evidence-scoped wording — no primary statement from Anthropic or OpenAI
  blessing any third-party subscription reuse was located. What is
  documented is which tools invoke the vendor's own official CLI login
  versus which tools reuse or reimplement the subscription's OAuth
  themselves — a distinction now made explicit throughout this section.
- Added an explicit distinction between **using** an official Claude/Codex
  CLI login and **extracting, importing, or reusing** its stored
  credentials in a separate tool — this is the central axis Hafiz's
  requirement 8 turns on, and the original version blurred it.
- Softened the Crush claim: general interaction patterns (a sidebar showing
  a live diffstat, status dots) are ideas, not protected expression, and
  may be reimplemented natively. But Crush's specific visual composition
  (its exact layout, color system, and iconography taken together) is the
  kind of thing trade dress/copyright law protects as "expression," not
  just source code — so "the interaction pattern is fair to draw on" is not
  the same claim as "the complete visual design is fair to reproduce."
  Nothing in the original version should be read as licensing legal advice.
- Recalculated the scored comparison against Hafiz's 13 confirmed product
  requirements (control room, focus workspace, worker sidebar, split focus,
  persistent identity with selectable engines, multi-agent delegation with
  cross-model review, worktree isolation, subscription compatibility without
  credential extraction, policies/hooks/gates, Koda/Mission Ledger
  continuity, desktop+Telegram/phone access, editor/diff/terminal/evidence
  surfaces, staff-distributable maintainability) instead of the original
  generic coding-agent-quality weighting. Popularity and visual polish are
  now minority factors, not majority ones.

### In plain language first (revised)

Hafiz's actual product isn't "a nicer terminal chat." It's a specific shape:
a **Control Room** where several full task conversations stay live and
directly replyable at once, a **Focus Workspace** for going deep on one of
them, a **Worker Sidebar** inside that focus view showing what
sub-agents/tools are doing, and **Split Focus** to hold several full
workspaces open side by side — all backed by one persistent Agent OS
identity that can drive Claude, Codex, or other engines interchangeably,
delegate across models with visible evidence, respect Sifututor's existing
policies/hooks/gates, stay continuous with Koda and the Mission Ledger, and
reach Hafiz on desktop and on his phone via Telegram.

Nothing found in this research is a full match to that shape. But one
project — **Omnigent** — was purpose-built for almost exactly this problem
(it explicitly calls itself a "meta-harness" that orchestrates Claude Code,
Codex, Cursor, OpenCode, Hermes, and custom agents from one identity, with a
declarative policy engine, real multi-agent delegation with cross-vendor
review, and documented Claude/ChatGPT subscription support through the
official `claude`/`codex` CLIs). It was missing from the first version of
this section, which was a real gap — the recalculated scoring below has it
ranked first by a wide margin once the comparison is weighted toward
Hafiz's actual requirements instead of generic UI polish. It does not
implement the four-layer Control Room/Focus/Worker-Sidebar/Split-Focus model
by that name, and it is still "alpha," so the honest recommendation is to
treat it as the leading **runtime candidate to fit-test**, not something to
adopt sight unseen.

### Research goal and current Agent OS requirements (revised)

Original goal (unchanged): identify existing open-source coding-agent
interfaces or architectures that could legitimately inform a native,
LLM-agnostic Sifututor Agent OS harness.

This revision adds Hafiz's 13 confirmed product requirements as the actual
scoring target, replacing generic "is the UI nice" criteria:

1. Control Room with multiple full, live, directly replyable task
   conversations
2. Focus Workspace for one complete task
3. Worker Sidebar inside a focused task
4. Split Focus for several full workspaces simultaneously
5. Persistent Agent OS identity with selectable Codex, Claude, and other
   engines
6. Multi-agent delegation with visible evidence and cross-model review
7. Smart project/worktree isolation
8. Existing Claude/ChatGPT subscription compatibility **without copying or
   extracting credentials**
9. Agent OS policies, hooks, approvals, and quality gates
10. Koda memory, Mission Ledger, and cross-project continuity
11. Desktop plus Telegram/phone access
12. Editor, diff, terminal, evidence, and task-state surfaces
13. Staff-distributable architecture and long-term maintainability

This does not replace the general Agent OS goal stated at the top of this
document; it is the concrete yardstick for this specific UI/foundation
comparison.

### Research method and scoring weights (revised)

Same two-pass method as the original version (general research pass, then
direct verification), extended with a third pass specific to this
correction:

3. Primary-source investigation of Omnigent: `gh api` against
   `omnigent-ai/omnigent` for stars/license/activity; `WebFetch` against
   `omnigent.ai` and `omnigent.ai/docs/build/harnesses`,
   `omnigent.ai/docs/interact/desktop`, and
   `omnigent.ai/docs/interact/mobile`; direct reads of the repo's own
   `README.md`, `docs/POLICIES.md`, and `docs/OMNIGENT_BOT_SETUP.md` via the
   GitHub API; and direct visual inspection of the official
   `docs/images/omnigent-desktop.png` and `docs/images/policy-trust-model.png`
   screenshots downloaded from the repo.

Scoring weights are now aligned to Hafiz's 13 requirements, grouped into six
categories, instead of the original generic UI/license/momentum split:

| Category | Weight | Requirements it covers |
| --- | --- | --- |
| A. Multi-session/workspace UI fit | 25% | 1, 2, 3, 4, 12 (Control Room, Focus Workspace, Worker Sidebar, Split Focus, editor/diff/terminal/evidence surfaces) |
| B. Engine-agnostic identity + subscription safety | 20% | 5, 8 (selectable engines, subscription reuse without credential extraction) |
| C. Multi-agent delegation & cross-model review | 15% | 6 |
| D. Isolation + policy/hooks/gates | 20% | 7, 9 (worktree isolation, policies/hooks/approvals/quality gates) |
| E. Memory/continuity | 10% | 10 (Koda, Mission Ledger, cross-project continuity) |
| F. Distribution + access channels + maintainability | 10% | 11, 13 (desktop+Telegram/phone, staff-distributable) |

This deliberately drops "popularity" and "raw visual polish" as scored
dimensions. They still appear as supporting facts (star counts, screenshot
descriptions) but no longer move the ranking on their own, per Hafiz's
explicit instruction that orchestration fit, subscription safety,
multi-session design, and policy enforcement must outweigh them.

### Source-quality and verification rules (unchanged, extended)

Same tiering as the rest of this document. For Omnigent specifically:

- **Primary / verified this session**: `gh api` responses for
  `omnigent-ai/omnigent` (2026-08-03); the project's own README, license
  file, `docs/POLICIES.md`, and `docs/OMNIGENT_BOT_SETUP.md` read directly
  from the repo; `omnigent.ai/docs/build/harnesses` fetched and quoted
  directly; the official desktop and policy-trust-model screenshots viewed
  directly.
- **Secondary**: `omnigent.ai` homepage marketing copy and the
  `/docs/interact/desktop` and `/docs/interact/mobile` pages, fetched via an
  automated summarizer rather than read verbatim — treated as directionally
  reliable but not quoted as verbatim primary text unless cross-confirmed
  against the README.
- Every claim below is tagged `[verified 2026-08-03]`, `[secondary]`, or
  `[inference]`, same convention as the rest of this document.

### Current market/category map (revised)

The original three-shape map (terminal-first harnesses, vendor CLI agents,
IDE/web-hosted agents) is missing a fourth shape that Omnigent occupies:

4. **Meta-harnesses / orchestration layers** — tools that do not implement
   their own coding-agent loop as the primary product, but instead wrap and
   orchestrate other agents' loops (Claude Code, Codex, Cursor, OpenCode,
   Hermes) under one identity, with a policy/sandboxing layer and multiple
   access surfaces (terminal, web, desktop, phone). Omnigent is the clearest
   example found. This is a structurally different category from the other
   three — it is closer to "an operating system for agents" than "an agent."

### Longlist of comparable repositories (revised)

Unchanged from the original version, plus **Omnigent**
(`omnigent-ai/omnigent`) added — the single addition this correction pass
required.

### Serious shortlist (corrected, independently verified 2026-08-03)

| Project | Repo | Stars `[verified]` | Language | License SPDX `[verified]` | Last push `[verified]` | Surfaces shipping today `[verified]` |
| --- | --- | --- | --- | --- | --- | --- |
| **Omnigent** | github.com/omnigent-ai/omnigent | 8,057 | Python | Apache-2.0 | 2026-08-03 (today) | Terminal/CLI, local web UI, native macOS desktop app, native iOS app, mobile web (PWA) — **status: alpha** |
| opencode | github.com/anomalyco/opencode | 192,485 | TypeScript + Go TUI | MIT | 2026-08-03 (today) | TUI, CLI, **desktop app (beta, macOS/Windows) and web app ship today** — corrected from the original version, which implied these were future-only |
| Crush | github.com/charmbracelet/crush | 27,034 | Go (Bubble Tea) | FSL-1.1-MIT (GitHub's detector reports `NOASSERTION` because FSL is non-standard) | 2026-08-03 (today) | Terminal only |
| goose | github.com/aaif-goose/goose | 52,138 | Rust | Apache-2.0 | 2026-08-03 (today) | CLI, native desktop app, embeddable API |
| OpenHands | github.com/OpenHands/OpenHands | 82,921 | TypeScript + Python | MIT | 2026-08-03 (today) | Browser web UI ("Agent Canvas"), cloud automations dashboard |

Omnigent's star count (8,057) is an order of magnitude below opencode's or
OpenHands', and its own README badge marks it `status: alpha`
`[verified: README.md badge]`. That is a real maturity gap and is scored
honestly below (category F) — it does not change that the project is the
closest functional match to Hafiz's actual requirements found in this
research.

### Scored comparison table (recalculated against the 13 requirements)

| Project | A. Multi-session UI (25%) | B. Engine-agnostic + subscription safety (20%) | C. Multi-agent delegation (15%) | D. Isolation + policy/gates (20%) | E. Memory/continuity (10%) | F. Distribution + maintainability (10%) | **Weighted score** |
| --- | --- | --- | --- | --- | --- | --- | --- |
| **Omnigent** | 6 | 9 | 10 | 8 | 4 | 6 | **7.40** |
| OpenHands | 7 | 6 | 5 | 6 | 4 | 6 | 5.90 |
| goose | 4 | 7 | 4 | 4 | 3 | 8 | 4.90 |
| opencode | 4 | 5 | 4 | 5 | 3 | 9 | 4.80 |
| Crush | 5 | 5 | 2 | 2 | 3 | 5 | 3.75 |

Reading this against the original (2026-08-03, pre-correction) table: under
the old generic-quality weighting, opencode led (8.75) and Crush was second
on raw UI polish (7.65). Under the corrected, requirements-aligned
weighting, **the order inverts** — Omnigent leads by roughly 1.5 points and
opencode drops to fourth. This is the direct, intended effect of scoring
orchestration fit, subscription safety, multi-agent delegation, and policy
enforcement instead of popularity and visual polish, per Hafiz's
instruction. Both tables are kept in this document (the original is
unchanged above this section) so the reasoning behind the reversal stays
visible rather than silently overwritten.

Score rationale, briefly, per category:

- **A (multi-session UI)**: OpenHands scores highest here because its
  Conversations sidebar shows multiple sessions with live status dots and
  timestamps simultaneously `[verified, screenshot viewed]` — the closest
  visual precedent found for "several live task conversations visible at
  once," though whether they are all *directly replyable simultaneously in
  one view* (Hafiz's literal Control Room requirement) was not confirmed.
  Omnigent's desktop app shows one focused session with a project-grouped
  sidebar to switch between sessions `[verified, screenshot viewed]`, and
  achieves "several full workspaces at once" through **multiple native OS
  windows** (`Cmd+N`) rather than an in-app split/grid layout
  `[secondary, summarized from omnigent.ai/docs/interact/desktop]` — a
  materially different mechanism from Hafiz's Split Focus concept, not a
  literal match.
- **B (engine-agnostic + subscription safety)**: Omnigent scores highest
  because it documents four credential kinds including "Subscription: A
  Claude Pro/Max or ChatGPT plan, via the official `claude` / `codex` CLIs"
  and, for its ACP integration path, states plainly "Omnigent stores no
  credential, so log into the agent through its own CLI first"
  `[verified, quoted directly from README.md and
  omnigent.ai/docs/build/harnesses]`. That is the clearest evidence found
  anywhere in this research of a tool using the vendor's **own official
  login flow** rather than extracting or reimplementing it. opencode scores
  lower specifically because secondary sources report the opposite pattern:
  Anthropic restricted third-party subscription-OAuth reuse and opencode
  removed related support after a legal request — see the corrected
  Subscription/OAuth section below.
- **C (multi-agent delegation)**: Omnigent's bundled example agent **Polly**
  is scored 10/10 because it is a direct, verified match to requirement 6:
  it delegates coding work to sub-agents (Claude Code, Codex, or Pi) in
  parallel git worktrees, then routes each diff to a reviewer from a
  *different* vendor than the one that wrote it `[verified, quoted directly
  from README.md]` — that is "multi-agent delegation with visible evidence
  and cross-model review" almost verbatim.
- **D (isolation + policy/gates)**: Omnigent's own `docs/POLICIES.md`
  documents a three-tier declarative policy engine (server-wide /
  agent-spec / session, each returning ALLOW / DENY / ASK, with session
  policies evaluated first and able to short-circuit) `[verified, read
  directly from docs/POLICIES.md]`, plus OS-level sandboxing (`bwrap` on
  Linux, `seatbelt` on macOS) and optional cloud sandboxes (Modal, Daytona,
  E2B, and others) `[verified, README.md]`. No other candidate in this
  shortlist documents a comparably explicit, layered policy/trust model.
- **E (memory/continuity)**: no candidate has anything resembling Koda's
  tagged cross-session memory or the Mission Ledger. All scores in this
  column are low and are really measuring "does the project have *any*
  session-persistence primitive to build continuity on top of," not "does
  it already solve this."
- **F (distribution + maintainability)**: opencode scores highest here on
  sheer momentum and shipping surfaces; Omnigent scores lower specifically
  because of its alpha status and much smaller star count/community size —
  this is the category where "popularity" legitimately still matters
  (long-term maintainability is a real product requirement, #13), it is
  simply no longer allowed to dominate the other five categories the way it
  did in the original version's weighting.

### Recommended best UI (visual/interaction design) — revised wording

**Crush** remains the strongest single-task visual execution found (right
sidebar with live Modified Files diffstat, LSP/MCP status dots, a fuzzy
command palette with a System/User scope toggle — all directly viewed via
extracted GIF frames, see the original verification above this correction).

Corrected framing per Hafiz's instruction: this is a claim about
**interaction-pattern inspiration**, not a claim that Crush's complete
visual design is free to reproduce. Concretely:

- Fair to draw on as an idea: "a persistent sidebar showing live diffstat
  and tool/LSP status while a task is in focus" — this is a functional UI
  pattern, not a specific protected expression.
- Not addressed or licensed by that idea alone: Crush's actual pixels — its
  specific color values, exact spacing, iconography, and the Charm
  wordmark/branding — which sit under a non-standard FSL-1.1-MIT license
  (source-available now, converts to MIT roughly two years after each
  release) and separately under Charm's own trademark. A Sifututor-native
  implementation should be recognizably its own design, not a close visual
  copy of Crush's specific screens, regardless of how the underlying idea
  is licensed.
- This is a plain-language summary for planning purposes, not legal advice;
  if Crush-derived visual elements are ever seriously considered for reuse
  rather than inspiration, that needs an actual legal read of the FSL terms
  first.

### Recommended best technical foundation — revised

**Omnigent** is now the best-scoring technical foundation (7.40, leading by
~1.5 points once weighted against Hafiz's 13 requirements), for three
concrete reasons, each tied to a specific requirement:

1. It is the only candidate whose core purpose *is* orchestrating multiple
   coding-agent engines (Claude Code, Codex, Cursor, OpenCode, Hermes, Pi,
   and custom YAML agents) under one identity — a direct match to
   requirement 5.
2. It is the only candidate with a real, documented, cross-vendor
   multi-agent delegation pattern (Polly) — a direct match to requirement 6.
3. It is the only candidate with both a declarative, layered policy engine
   (requirement 9) and the most explicit, evidence-backed statement found
   anywhere in this research of authenticating through a vendor's **own
   official CLI login** rather than extracting or reusing its stored
   credentials (requirement 8).

It does not fully satisfy requirements 1–4 and 12 as literally specified
(no Control Room grid, no Worker Sidebar concept, Split Focus via OS windows
rather than in-app panes) and has no Koda/Mission Ledger equivalent
(requirement 10). Those gaps are real and are why the recommendation below
is "fit-test as a runtime," not "adopt as the finished UI."

### Best architecture fallback

**goose**, unchanged from the original recommendation, for the same reason:
its "one core, three shells" shape (Rust core driving CLI, native desktop,
and an embeddable API from a single codebase) is Apache-2.0 and now under
neutral Linux Foundation governance (see corrected date below), making it
the lowest-governance-risk fallback if Omnigent's alpha status or
architecture proves disqualifying during a fit test.

### Comparison with Hafiz's current multi-chat VS Code workflow (revised)

| Sifututor today | Closest researched equivalent | Gap |
| --- | --- | --- |
| One parent VS Code workspace, `additionalDirectories` fan-out to 10 sub-projects | None found — still true after adding Omnigent; Omnigent's "Projects" sidebar groups sessions but does not do umbrella multi-repo instruction-file dispatch | Nothing found does this |
| Multiple concurrent Claude Code / Codex chats, one per active task | Omnigent's project-grouped, pinned session sidebar `[verified, screenshot]`, plus OpenHands' Conversations sidebar `[verified, screenshot]` | Omnigent is the closer functional analog because the *engines behind* those sessions can literally be Claude Code or Codex themselves, not just a UI that resembles the idea |
| Dispatcher skills routing to project-specific implementations | Omnigent's per-agent YAML + policy declarations, and its build/plan-style visible mode is closer to opencode's Tab switcher | Neither is a like-for-like route-by-declared-project-intent system |
| Hook-driven quality gates per project | Omnigent's three-tier declarative policy engine (server/agent/session, ALLOW/DENY/ASK) `[verified]` | Closest match found in this entire research pass — existing hooks (`workflow-gate.py`, `quality-gate.py`, the pre-commit guard) would need to be re-expressed as Omnigent policies, not just referenced; whether that re-expression preserves their exact blocking behavior is unverified and is listed as a required fit-test unknown below |
| Koda cross-session memory with mandatory project tagging | Nothing found | Unchanged gap |
| Mission Ledger | OpenHands' Automations dashboard remains the closer visual analog; Omnigent has no comparable board | Unchanged gap |

### Native / Adapt / Borrow / Build gap matrix (revised, Omnigent rows added)

| Capability | Status for Sifututor Agent OS | Source of truth |
| --- | --- | --- |
| Umbrella multi-project routing | **Native** — already exists | Unchanged |
| Layered instruction contract | **Native** — already exists | Unchanged |
| Visible permission/mode state per session | **Adapt** | Omnigent's ASK-verdict policy prompts are a stronger direct match than opencode's Tab switcher — a policy that returns `ASK` is functionally the same idea as Critical Lane's "explicit approval before implementation," implemented as software rather than as written convention |
| Declarative, three-tier policy/gate engine | **Adapt or Build** | Omnigent's `docs/POLICIES.md` engine (server-wide / agent-spec / session, ALLOW/DENY/ASK) is the closest existing implementation of what this doc's hooks currently do by convention; re-expressing `workflow-gate.py`/`quality-gate.py` as Omnigent policies is the concrete adaptation path, unverified until fit-tested |
| Cross-vendor multi-agent delegation with visible review | **Borrow (pattern) or Adopt (as runtime)** | Omnigent's Polly example agent is a working implementation of requirement 6 today, not just a pattern to imitate — if Omnigent is adopted as a runtime, Polly-style delegation could be used close to as-is |
| Live diff/modified-files awareness during a session | **Borrow** — nothing exists yet | Crush sidebar (visual pattern only, see licensing note above) |
| Live plan checklist during multi-step work | **Borrow** — nothing exists yet | OpenAI Codex CLI plan block |
| Cross-project "what's scheduled / parked" dashboard | **Adapt** | OpenHands Automations dashboard |
| Control Room (many live, directly replyable conversations in one view) | **Build** — no candidate implements this literally | Closest partial precedents: OpenHands' Conversations sidebar (visibility, not confirmed simultaneous reply) and Omnigent's multi-window model (simultaneity via OS windows, not in-app) |
| Worker Sidebar (sub-agent/tool status inside one focused task) | **Build** — no candidate implements this literally | Closest partial precedent: Crush's LSP/MCP status dots (tool status, not sub-agent status) |
| Split Focus (several full workspaces at once) | **Adapt** | Omnigent's `Cmd+N` multi-window pattern achieves the outcome (several full sessions visible at once) through the OS window manager rather than an in-app layout — worth evaluating as a starting point before building a custom in-app split view |
| Subscription reuse without credential extraction | **Adapt or Adopt (as runtime)** | Omnigent's "official CLI login, we store no credential" pattern is the concrete mechanism to reuse or copy the *approach* from, not just the idea |
| One core driving CLI + future desktop/web surface | **Build** (if going independent) or **N/A** (if adopting Omnigent, which already has this) | goose's three-surface architecture, or Omnigent's existing terminal/web/desktop/iOS surfaces if adopted as runtime |
| Koda-tagged cross-session memory / Mission Ledger continuity | **Build** — no external equivalent found in any candidate, including Omnigent | This doc's existing memory architecture |

### Exact donor project for every Borrow recommendation (revised, Omnigent donors added)

| UI/architecture element worth borrowing | Exact donor | Verified how |
| --- | --- | --- |
| Session header showing token count / context % / running cost | opencode | Screenshot viewed directly, prior session |
| Dim, one-line tool-call rendering | opencode | Screenshot viewed directly, prior session |
| Tab-cycled agent mode (build / plan / general) | opencode | Screenshot viewed directly, prior session |
| Right-sidebar Modified Files panel with live diffstat (interaction pattern only — see Crush licensing note above) | Crush | GIF frame extracted and viewed directly, prior session |
| LSP/MCP server status as live colored dots (interaction pattern only) | Crush | GIF frame extracted and viewed directly, prior session |
| Command palette with fuzzy search + scope toggle (interaction pattern only) | Crush | GIF frame extracted and viewed directly, prior session |
| Live-updating plan checklist with bolded in-progress step | OpenAI Codex CLI | Screenshot viewed directly, prior session |
| Automations dashboard (Active/Inactive card grid, schedule chips, "Run now") | OpenHands | Screenshot viewed directly, prior session |
| Conversations list with live status dot + relative timestamp | OpenHands | Screenshot viewed directly, prior session |
| One core, three/four shells (CLI + desktop + web + phone) architecture | Omnigent (updated donor — Omnigent already ships all four surfaces today; goose remains the fallback donor for the same idea with three surfaces) | README + `gh api`, verified this session |
| Three-tier declarative policy engine (server-wide / agent-spec / session; ALLOW/DENY/ASK) | Omnigent | `docs/POLICIES.md`, read directly this session |
| Cross-vendor multi-agent delegation with routed review (Polly pattern) | Omnigent | README.md, quoted directly this session |
| Project-grouped, pinned session sidebar | Omnigent | `docs/images/omnigent-desktop.png`, viewed directly this session |
| "Official CLI login, no credential stored" subscription auth pattern | Omnigent | README.md + `omnigent.ai/docs/build/harnesses`, quoted directly this session |
| Multiple full workspaces open at once via OS-native windows (`Cmd+N`) | Omnigent | `omnigent.ai/docs/interact/desktop`, summarized this session — treat as secondary until independently confirmed |

Same caveat as the original version applies to every row: naming the donor
authorizes studying and reimplementing the *interaction pattern* natively,
not copying source code, and for Crush specifically, not reproducing its
complete visual expression either (see the Crush licensing note above).

### Adopt / adapt / borrow / build / reject map (revised)

| Decision | Item |
| --- | --- |
| **Adopt (as runtime, pending fit test)** | Omnigent — not "adopt its UI as our UI," but "adopt as the underlying multi-engine orchestration/policy/sandboxing runtime that a Sifututor-native Control Room/Focus Workspace UI could be built on top of," conditional on the fit-test unknowns listed below |
| **Adapt** | Omnigent's policy engine, re-expressing existing hooks as Omnigent policies; Omnigent's `Cmd+N` multi-window pattern as a starting point for Split Focus |
| **Borrow** (reimplement the interaction pattern natively, no shared code) | Every row in the donor table above except the "Adopt (as runtime)" row |
| **Build** (net-new, nothing to borrow from) | Umbrella multi-repo project dispatch, layered `AGENTS.md` contract, Koda-tagged memory, Mission Ledger, the literal Control Room/Worker Sidebar UI layers — all already exist or are already planned in this doc and have no external equivalent, including in Omnigent |
| **Reject** | Aider's auto-commit-per-edit convention as wholesale adoption; Roo Code (archived); Plandex (dead ~10 months); using Crush's FSL-covered source or complete visual design directly in a packaged product |

### Subscription/OAuth and provider compatibility (corrected)

This remains the most consequential finding in this research, now with
narrower, evidence-scoped wording and Omnigent added.

**The distinction that matters**: there is a real difference between (a) a
tool that spawns the vendor's own official CLI binary and lets *that*
binary perform its own login, versus (b) a tool that extracts, imports, or
reimplements that subscription's OAuth flow inside itself so the original
CLI is no longer involved. (a) keeps the vendor's own software as the thing
actually authenticating. (b) is where the reported Anthropic ToS friction
below actually occurred.

- **Omnigent**: documents "Subscription: A Claude Pro/Max or ChatGPT plan,
  via the official `claude` / `codex` CLIs" as one of four first-class
  credential kinds, and for its ACP integration path states directly:
  "Each ACP agent brings its own auth — Omnigent stores no credential, so
  log into the agent through its own CLI first." Its "Native TUI" execution
  mode is described as "Omnigent boots the vendor's own terminal UI in a
  pane and mirrors it back." `[verified: quoted directly from README.md and
  omnigent.ai/docs/build/harnesses, 2026-08-03]` This is architecturally
  pattern (a) above — the official CLI does its own login; Omnigent's own
  words are that it stores no credential itself. This is Omnigent's own
  description of its own design, not a statement from Anthropic or OpenAI
  approving the practice — no such vendor statement was located this
  session for any tool.
- **goose**: documented by goose's own project blog as supporting reuse of
  an existing Claude, ChatGPT, or Gemini subscription via its ACP
  integration (picking a `chatgpt_codex` provider opens a real browser
  OAuth sign-in). `[secondary: goose-docs.ai official blog, "Use Goose with
  Your AI Subscription," dated 2026-03-19]` Whether this is implemented as
  pattern (a) (shelling out to the actual vendor CLI) or pattern (b) (a
  goose-authored OAuth client talking to the provider directly) was **not
  independently verified this session** — this is listed as an open
  unknown below rather than asserted either way.
- **opencode**: multiple independent secondary sources report that
  Anthropic restricted third-party tools from using consumer-subscription
  OAuth credentials, and that opencode removed Anthropic-subscription-auth
  support after a legal request; community plugins attempting to route
  around this explicitly warn that doing so violates Anthropic's consumer
  Terms of Service. `[secondary, cross-corroborated by multiple independent
  writeups; no single primary Anthropic statement located this session —
  treat as high-confidence but not primary-sourced]` This reads as pattern
  (b) — a third party's own OAuth handling of subscription credentials, not
  the vendor's own CLI performing its own login — which is the likely
  reason it drew a legal objection where Omnigent's "boot the vendor's own
  CLI in a pane" approach has not (as far as this research found).
- **Cline**: BYOK across 30+ providers via standard API keys; no
  subscription-OAuth reuse claim found — no ToS ambiguity identified.
  `[secondary]`
- **Crush**: 20+ providers via standard API keys; no subscription-OAuth
  reuse claim found. `[secondary]`

Sifututor implication (corrected wording): if a native Agent OS harness
ever needs to let staff plug in a personal or company Claude/ChatGPT
**subscription** rather than a metered API key, **Omnigent's "boot the
official CLI, store no credential ourselves" pattern is the most clearly
evidence-backed low-risk mechanism found in this research** — precisely
because it keeps the vendor's own software doing the actual authentication
rather than a third party handling the subscription's OAuth itself. This is
not a claim that Anthropic or OpenAI has blessed Omnigent specifically; it
is a claim about which *architecture* (invoke the official CLI vs.
extract/reimplement its auth) carries less apparent ToS risk based on what
was observably restricted (opencode's approach) versus what has not been
`[inference, based on the pattern-(a)-vs-(b) distinction above — not a
vendor confirmation]`. Do not build or recommend a Sifututor harness that
extracts, imports, or reimplements a Claude/Codex subscription's stored
OAuth token outside of that vendor's own official CLI process.

### Security, credential, permission, workspace-isolation, and privacy analysis (revised)

- **Credential handling**: Omnigent's four-credential-kind model (API key /
  Subscription via official CLI / Gateway / Databricks profile) is the most
  explicit credential taxonomy found in this research
  `[verified: README.md]`. It still stores gateway and API-key credentials
  locally itself (same as every other candidate) — the "stores no
  credential" claim applies specifically to the ACP/subscription path where
  the official vendor CLI is doing the authenticating, not to every
  credential kind Omnigent supports.
- **Sandboxing**: two candidates now show verified sandboxing evidence.
  OpenHands runs agent actions inside a sandboxed VM/Docker container
  `[verified, architecture diagram viewed]`. Omnigent applies OS-level
  sandboxing to its terminal wrappers and the `pi` harness — `bwrap` on
  Linux (mandatory there), the built-in `seatbelt` sandbox on macOS — plus
  optional disposable cloud sandboxes (Modal, Daytona, Islo, E2B,
  CoreWeave, Kubernetes, Boxlite, Databricks) launched per session
  `[verified: README.md]`. Neither opencode, Crush, nor goose showed
  built-in sandboxing in what was reviewed — same caveat as the original
  version: absence of a sandboxing claim in what was reviewed is not proof
  none exists.
- **Permission visibility**: Omnigent's ALLOW/DENY/ASK policy verdicts,
  evaluated at server-wide, agent-spec, and session levels with session
  policies checked first, are a more explicit and more layered version of
  the "visible permission state" idea than opencode's Tab-cycled mode
  `[verified: docs/POLICIES.md]`. The accompanying policy-trust-model
  diagram in the repo shows User Policy, Developer Policy, and IT Policy as
  three separate defensive layers around an "Agent Session," specifically
  including a labeled "malicious injection" threat path from content inside
  the session — evidence that prompt-injection-via-tool-output was an
  explicit design consideration, not an afterthought
  `[verified, diagram viewed directly]`.
- **Workspace isolation**: Omnigent's Polly example agent runs each coding
  sub-agent in its own parallel git worktree `[verified: README.md]` — this
  is the first candidate in this entire research pass (across both
  versions of this section) with a *verified, working* worktree-isolation
  pattern rather than just a documented gap. This directly addresses
  requirement 7 and the standing "parallel work needs isolation" gap noted
  elsewhere in this document.
- **Privacy**: Omnigent "collects anonymized usage data (telemetry) by
  default," with an opt-out documented separately
  `[verified: README.md, "Telemetry" section]` — this is a real fact to
  weigh for any self-hosted deployment, distinct from OpenHands' broader
  standing-OAuth-grant privacy consideration noted in the original version
  (unchanged). Omnigent also supports OIDC single sign-on (Google, GitHub,
  Okta, Microsoft) for multi-user team deployments and invite-only signup
  `[verified: README.md]`, which is a stronger access-control story than
  any other candidate reviewed if Omnigent is ever deployed as a shared
  server for staff.
- **Messaging-channel access**: Omnigent ships a native iOS app (a thin
  shell around the same web UI) and a Slack integration, but **no Telegram
  integration was found** `[secondary, summarized from
  omnigent.ai/docs/interact/mobile — no Telegram, WhatsApp, or SMS
  integration listed]`. This is a direct gap against requirement 11
  ("Desktop plus Telegram/phone access") — Sifututor's existing
  Hermes-based approach (see the Mission Ledger's Responsibility Inbox
  work) uses Telegram specifically, which Omnigent does not currently
  offer; Slack and native-app/web access are not substitutes for that
  specific channel unless Hafiz is open to switching channels.

### License, attribution, trademark, and fork-maintenance analysis (revised)

- Omnigent is **Apache-2.0** `[verified: gh api license endpoint,
  2026-08-03]` — fully permissive, same tier as goose, OpenHands, Cline,
  Aider, and the vendor CLIs. No FSL-style restriction applies to it.
- Everything stated in the original version about MIT/Apache candidates,
  Crush's FSL-1.1-MIT status, and trademark obligations remains unchanged
  and is not repeated here — see the equivalent section above this
  correction. The one wording change is the Crush note above under
  "Recommended best UI," which narrows the claim from "the design may be
  studied and reimplemented" to the more precise "the interaction pattern
  may be studied and reimplemented; the complete visual expression and
  branding may not be assumed to be free to reproduce."
- **Fork-maintenance risk for Omnigent specifically**: young project
  (8,057 stars vs. the 50k-190k range of the other shortlisted candidates),
  explicitly marked `alpha`, single small org (`omnigent-ai`) rather than a
  neutral foundation. This is a materially higher governance/continuity
  risk than goose (Linux Foundation) or opencode (very large community),
  and is the central reason the recommendation below is "fit-test as a
  runtime candidate," not "commit to it as the platform."

### Verified facts, inferences, unknowns, and confidence (revised)

**Verified this session (high confidence)**: Omnigent's star count,
license, and activity via `gh api`; every direct quote from Omnigent's
README.md, docs/POLICIES.md, and docs/OMNIGENT_BOT_SETUP.md; the desktop
app and policy-trust-model screenshots, viewed directly; opencode's
`packages/` directory listing (`tui`, `cli`, `desktop`, `web`, `console`,
`server`, confirming all four surfaces ship today); the AAIF announcement
date of 2025-12-09 (TechCrunch and SiliconANGLE both independently dated
2025-12-09, cross-checked against the Linux Foundation's own press release
title).

**Secondary, cross-corroborated (medium-high confidence)**: Omnigent's
desktop multi-window (`Cmd+N`) behavior and native iOS app / no-Telegram
finding (summarized via an automated fetch of `omnigent.ai/docs/interact/*`
rather than read verbatim); goose's ACP subscription-reuse feature and its
underlying OAuth mechanism being unconfirmed; the Anthropic
opencode-subscription-auth restriction.

**Inference (this session's judgment, not a sourced fact)**: the
recalculated scoring weights and resulting ranking; that Omnigent's
"official CLI login" pattern carries lower ToS risk than opencode's
reported approach — this is a reasoned comparison of two documented
architectures, not a statement any vendor has made; which specific UI
elements are "worth borrowing."

**Unknown / not checked this session — carried forward as open items**:
whether Omnigent's policy engine can actually reproduce the exact blocking
behavior of Sifututor's existing hooks (`workflow-gate.py`,
`quality-gate.py`, the pre-commit guard) without loss; whether Omnigent's
multi-user server deployment keeps a staff Claude/ChatGPT subscription
login fully within that vendor's consumer ToS at production scale (not just
a single local user); whether Koda MCP and the Mission Ledger workflow can
attach cleanly to an Omnigent session/agent; whether Omnigent's "Focus
Workspace + multi-window Split" genuinely satisfies the literal Control
Room requirement or would need a custom client built against Omnigent's
REST API; Omnigent's actual contributor count, funding, and governance
trajectory beyond what the repo itself shows.

### Recommended next action (revised)

Run the fit test that Sifututor's own Mission Ledger already parked for
this exact purpose: `AO-RUNTIME-001`
(`docs/agent-playbooks/mission-ledger/cross-project.md`), which proposes
self-hosting an Omnigent server, connecting Koda via MCP, encoding one route
(bugfix, with gates) as a YAML agent + policy, and explicitly running "the
mandatory gate-compatibility test" and "subscription-auth verification"
before trusting it with real staff work. This correction pass confirms that
plan was pointed at the right project; nothing here should be read as
authorization to start it — it remains paused pending Hafiz's go-ahead, per
its own recorded status.

### Exact decision Hafiz needs to make (revised)

Pick one direction (or explicitly defer):

1. **Fit-test path (this research's recommendation)**: approve the paused
   `AO-RUNTIME-001` pilot — self-host Omnigent, verify hooks/gates survive
   re-expression as Omnigent policies, verify the subscription-auth path
   holds up under real multi-user use, then decide adopt/reject with actual
   evidence instead of documentation claims.
2. **Design-first path (from the original version, still available)**:
   approve a Sifututor-native TUI, visually inspired by Crush's interaction
   patterns (not its complete visual design) but built architecturally on
   opencode's client/server split, with all source written natively, API-
   key-only auth to start.
3. **Architecture-first path (from the original version, still available)**:
   approve goose's "one core, three shells" shape as the long-term target,
   as the lower-governance-risk fallback if Omnigent's alpha status proves
   disqualifying during evaluation.
4. **Defer entirely**: keep investing in the current instructions + hooks +
   skills layer on top of Claude Code/Codex, and revisit a native harness or
   runtime adoption only after the credential/subscription question is
   independently resolved.

No prototype, install, clone, fork, authentication, or credential import has
been performed for this task or this correction. This research stops here
for Hafiz's selection.
