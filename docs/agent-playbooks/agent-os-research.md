# Sifututor Agent OS Research Notes

Last updated: 2026-07-01

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


## 2026-09-22 Knowledge Architecture Research (Issue #198)

Research, measurement, and runtime tests behind the progressive-disclosure
redesign of the instruction layer. Implementation and scenario evidence are in
the pull request for issue #198 and the navigation check; this section keeps the sources and the
decisions so future agents do not re-derive them.

### Question

How should Claude, Codex, and future models reach the same shared rules with
less always-loaded context, one owner per rule, and no new infrastructure?

### Runtime tests (this machine, fresh runs on marker files)

| Test | Claude Code 2.1.222 | Codex CLI 0.154.0 |
| --- | --- | --- |
| Directory with only `AGENTS.md` | not loaded (`NONE`) | loaded |
| `CLAUDE.md` containing `@AGENTS.md` | `AGENTS.md` loaded | `CLAUDE.md` not read |
| `CLAUDE.md` symlinked to `AGENTS.md` | loaded | n/a |
| Subdirectory `CLAUDE.md`/`AGENTS.md` below cwd, no file opened | not loaded | not loaded |
| Parent-directory file above a nested Git repo cwd | `CLAUDE.md` loaded | `AGENTS.md` not loaded |
| `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` | unset in this environment | n/a |

Method: `claude -p "<codeword question>" --model haiku --output-format json`
and `codex exec --skip-git-repo-check -s read-only` in scratch directories
that contained only the marker files. These prove loading behaviour, not
instruction compliance.

### Measured baseline (before the change, umbrella root)

| Measure | Value |
| --- | --- |
| Root `CLAUDE.md` (untracked in Git before this change) | 23,664 bytes |
| Root `AGENTS.md` | 12,454 bytes |
| Global `~/.claude/CLAUDE.md` | 12,405 bytes |
| Global `~/.codex/AGENTS.md` | 4,014 bytes |
| Claude prompt at launch, fresh `claude -p` at root (two runs) | 46,385 and 47,207 tokens |
| Claude prompt in an empty directory (tools plus global adapter only) | about 30,100 tokens |
| Codex prompt at launch, `codex exec` at root | 8,533 tokens |
| Active playbooks in `docs/agent-playbooks/` (top level) | 88 files, 1,225,016 bytes, 183,279 words |
| Largest playbooks | `agent-os-workflows.md` 84.9 KB, `agent-os-evals.md` 63.7 KB, `agent-os-review-roadmap.md` 53.7 KB |
| Broken relative links across the instruction layer | 0 of 468 |
| Playbooks with zero inbound Markdown links | 7 (3 historical session saves with no reference at all) |
| Exact duplicate sentences of 8+ words across instruction files | 19 (mostly skill-wrapper boilerplate) |
| Index layers describing the same library | 4 (`README.md`, `doc-owner-route-index.md`, `doc-routing-and-context-loading.md`, `agent-os-quick-start.md`) plus alias tables in 3 docs |
| Most-churned instruction files, last 90 days | `agent-os-eval-coverage-map.md` 78 commits, `agent-os-evals.md` 63, install manifest 54, `task-router.md` 26, `AGENTS.md` 23 |
| Sub-project `AGENTS.md` files linking to the root contract | 5 of 12 |

The important finding was not file size. Claude never received the shared
contract automatically: the umbrella `CLAUDE.md` was a 23.7 KB Claude-only
handbook that told Claude in words to read `AGENTS.md`, which the vendor docs
say only happens "if it decides to open the file". Codex received the contract
natively. That is a structural parity gap, closed by the `@AGENTS.md` import.

### Options compared

| Option | Evidence | Decision |
| --- | --- | --- |
| A. `CLAUDE.md` symlinked to `AGENTS.md` | Documented and tested working; Edit/Write refuse to write through the link; Windows checkouts get a text file; no room for Claude mechanics. | Rejected |
| B. Thin `CLAUDE.md` that imports `AGENTS.md` | Documented exact pattern (`@AGENTS.md` then a Claude section); tested working; never double-loaded even after Claude 2.1.277 adds direct `AGENTS.md` reading; used by `modelcontextprotocol/python-sdk` and `cloudflare/workers-sdk`. | Adopted |
| C. Duplicated model-specific files | No vendor endorses it; Claude docs say contradictory rules are picked arbitrarily; `PostHog/posthog` keeps 40 KB twins that exceed Codex's 32 KiB cap. | Rejected |
| D. Generated adapters | Only one-time copies exist in vendors (`/import`, `/init`); a generator is extra machinery to avoid a one-line import. | Not needed |
| E. Small shared index plus task-triggered docs | Matches Claude's 200-line guidance, Codex's 32 KiB chain cap, Cursor's "reference files instead of copying", llms.txt, and Anthropic's three-level progressive disclosure; `mastra-ai/mastra` is a live example. | Adopted with B |

Graph database or new infrastructure: rejected. No vendor loads a graph;
every vendor loads a small file with links, and Anthropic's own guidance says
path-based just-in-time retrieval avoids "stale indexing". The repo already
has `/graphify` as an optional secondary tool.

### Sources

| Source | Accessed | Tier | What it proves |
| --- | --- | --- | --- |
| https://code.claude.com/docs/en/memory | 2026-09-22 | official | Load order; lazy subdirectory files; `@import` (4 hops, code blocks skipped, external approval); `@AGENTS.md` example; symlink support and limits; 200-line target; direct `AGENTS.md` reading only from 2.1.277 and only without a `CLAUDE.md`; additional-directories env var |
| https://code.claude.com/docs/en/best-practices | 2026-09-22 | official | "keep it short"; "link to docs instead"; over-specified `CLAUDE.md` failure pattern; skills for on-demand knowledge |
| https://code.claude.com/docs/en/skills | 2026-09-22 | official | Descriptions loaded up front, bodies on invocation; 500-line guidance |
| https://code.claude.com/docs/en/prompt-caching | 2026-09-22 | official | `CLAUDE.md` is rebuilt at session start and `/compact`; size of the always-loaded layer is the repeatable cost |
| https://platform.claude.com/docs/en/build-with-claude/prompt-caching | 2026-09-22 | official | Cache invalidation order tools, system, messages; 5-minute TTL refreshed on use |
| https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md | 2026-09-22 | official | 2.1.277: "in a project with no CLAUDE.md, Claude Code reads AGENTS.md instead" |
| Installed `claude` 2.1.222 binary (`strings`) | 2026-09-22 | primary artefact | The "hardcodes CLAUDE.md / AGENTS.md discovery" string belongs to the one-time Codex `/import` feature, not to memory loading |
| https://learn.chatgpt.com/docs/agent-configuration/agents-md | 2026-09-22 | official | Codex chain built once per run, root to cwd, one file per directory, 32 KiB default, stops adding files |
| https://learn.chatgpt.com/docs/config-file/config-reference | 2026-09-22 | official | `project_doc_max_bytes`, `project_doc_fallback_filenames` (empty by default, so `CLAUDE.md` is never read), skills catalog budget |
| https://github.com/openai/codex/blob/main/codex-rs/core/src/agents_md.rs and `config_toml.rs` | 2026-09-22 | OSS source | Shared byte budget; crossing file truncated; later files dropped |
| https://agents.md/ | 2026-09-22 | spec | Nested `AGENTS.md` for monorepos; nearest file wins |
| https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions | 2026-09-22 | official | `copilot-instructions.md`; path-specific `applyTo`; nearest `AGENTS.md` wins; a single root `CLAUDE.md` accepted |
| https://cursor.com/docs/context/rules | 2026-09-22 | official | `.mdc` rules; `AGENTS.md` alternative; "Reference files instead of copying their contents" |
| https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents | 2026-09-22 | vendor publication | Context rot; just-in-time retrieval; progressive disclosure; grep and paths bypass stale indexing |
| https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills | 2026-09-22 | vendor publication | Three levels of progressive disclosure |
| https://llmstxt.org/ | 2026-09-22 | community spec | Index plus links; detail fetched only when needed |
| GitHub contents API for `modelcontextprotocol/python-sdk`, `cloudflare/workers-sdk`, `mastra-ai/mastra`, `microsoft/vscode`, `openai/codex`, `PostHog/posthog`, `pydantic/pydantic-ai` | 2026-09-22 | OSS | Sizes and patterns of real `AGENTS.md`/`CLAUDE.md` pairs |

Inference, not vendor evidence: the mapping of the three skill levels onto an
instruction system (contract, triggered doc, deep playbook), and the claim that
circular prose pointers are a practical failure mode. Community claims that
smaller files improve compliance were not relied on; the 2026 factorial study
cited in the earlier efficiency research found no size effect, so size limits
here are budget constraints, not compliance claims.

### Decisions recorded

- `CLAUDE.md` at the umbrella root is tracked in Git from this change so the
  Claude adapter is reviewable and parity-checked. The old untracked file is
  replaced by the thin adapter; the machine-local copy must be moved aside
  before pulling `main`.
- `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` stays unset. Sub-project
  rules are reached by reading the nearest `AGENTS.md`, which the contract
  already requires.
- `doc-owner-route-index.md` is the single inventory; `README.md` is a short
  start page; the Knowledge Architecture section of
  `doc-routing-and-context-loading.md` owns loading rules and budgets.
- Sub-project `AGENTS.md` files that do not link to `../AGENTS.md` (7 of 12)
  leave Codex without the shared contract inside that repo. Tracked as a
  follow-up in the product repositories, reported by navigation scenarios
  NAV-03 and NAV-04 as advisory when those checkouts are present.
