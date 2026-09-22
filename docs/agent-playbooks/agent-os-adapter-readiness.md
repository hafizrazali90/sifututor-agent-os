# Agent OS Adapter Readiness

Use this when checking whether Codex, Claude, or another LLM adapter is actually
ready to follow the Sifututor Agent OS.

Plain meaning:

```text
The Agent OS is the shared SOP.
Each LLM still needs its own adapter setup so it can read and follow the SOP.
```

## Readiness Levels

### Provider-neutral capability preflight

Select workers by observed capabilities, not tool/provider/model names. Kilo,
GLM, Claude and Codex are adapter candidates, not owners of the shared workflow.
Use `agent_os_adapter_contract.evaluate_capabilities(record, required,
expected_identity=identity)` or the isolated CLI entry point:

```bash
python3 scripts/agent-checks/agent-os-adapter-readiness.py --capability-preflight
```

The CLI reads one JSON envelope from stdin containing exactly `record`,
`required` and `expected_identity`; it does not run normal readiness probes,
read installed configuration, execute provider commands or invoke live tests.
Do not send secrets or raw transcripts. The envelope is limited to 64 KiB,
duplicate JSON keys are rejected, and output contains verdict metadata only.

Version-one record fields:

- `schema_version`: integer `1`.
- `identity`: exact `tool`, `tool_version`, `provider`, `model`,
  `configuration_id`, `environment_id` strings. The supervisor obtains the
  expected identity independently from the selected setup. Environment identity
  must distinguish the actual host/worktree/environment and configuration
  identity must change when tools, permissions, model routing or access change.
- `observed_at`, `expires_at`: UTC ISO timestamps, chosen by the supervisor
  according to the task risk; observation must already exist and not expire.
- `capabilities`: mapping of lowercase hyphenated names (for example,
  `read-files`, `image-input`, `run-tests`) to `status` (`supported`,
  `unsupported`, `unknown`), `evidence_kind` (`live`, `fixture`, `declared`),
  and a non-secret `evidence_ref`. Capability names are not vendor allowlists.

`required` is a nonempty list of distinct capability names. Unknown, unsupported,
fixture-only, declared-only, expired or identity-mismatched requirements fail
closed. Native image input and a separate vision-tool path are different
capabilities; one never silently substitutes for the other. Rerunning this
pure validation is safe and has no write/retry/provider side effects.

Exit `0` means the supplied attestation meets this task's capability requirements;
`1` means it does not; `2` means invalid input or incompatible CLI modes. This
is **not independent evidence verification**: references are not opened or
authenticated. The supervisor must inspect the evidence and control its
provenance/freshness. Output always states `live_parity_proven: false` and
`execution_authorized: false`. Do not turn a worker's self-written record into
approval, a launch command, or a claim of whole-workflow parity.

Existing launch adapters retain their own reviewed invocation contracts. An
unknown adapter can receive a portable brief, but cannot acquire a guessed CLI
command, fallback provider, paid API path or new permission from this preflight.

CP-08 reconciliation: issues #65/#68 and the retained Kilo parity worktree are
historical implementation candidates. Their pinned model, installed-config
checks and sampled live traces do not prove current universal adapter parity.
The newer candidate remains preserved for separate exact-diff integration;
this capability layer neither installs it nor claims it has been rolled out.
Root `glm`/`glm-switch` files and provider credentials remain untouched.

CP-08 reconciliation update (2026-09-19): the separate exact-diff integration
above landed the portable `.kilo/agents/sifututor-agent-os.md` adapter and
deterministic Kilo checks described in the "Kilo Adapter" section below. This
is wiring and fixture proof only. It does not upgrade any claim in this
document to "current universal adapter parity"; installed-Kilo and live-GLM
evidence remain explicit optional flags (`--installed-kilo`, `--live-kilo`,
`--require-installed-kilo`, `--require-live-kilo`) that stay outside normal
health/CI. Any rollout claim must record those results separately; portable
wiring alone never implies installed or live parity.

Permanent regression evidence lives in `test_agent_os_adapter_contract.py`:
pure evaluator negatives and the actual CLI JSON journey. No product browser
E2E is required (`not user-facing`); no real provider compliance is claimed.

| Level | Meaning | Example proof |
| --- | --- | --- |
| Shared core ready | The common rules and playbooks exist. | `AGENTS.md`, `docs/agent-playbooks/*`, Koda, health checks. |
| Adapter wired | The agent has a way to load the shared core. | Codex skills/config or Claude settings/hooks/commands. |
| Deterministic behavior ready | Local fixture checks prove the expected route and boundary. | Behavior trace runner, parity runner, validation loop. |
| Live behavior checked | The real agent UI/CLI answered test prompts correctly. | Claude extension or Codex session transcript compared with the parity standard. |
| Daily-use proven | The adapter works during real work without confusing Hafiz. | Real task close-outs, Session Map updates, Koda lessons, and no repeated friction. |

Do not call an adapter "100% proven" unless the live behavior and daily-use
levels are checked. A repo can be perfectly wired but still behave differently
in the real extension.

## Codex Adapter

Codex should be ready when:

- `.codex/config.toml` enables Agent OS lifecycle hooks;
- `.agents/skills/*/SKILL.md` wrappers point to shared playbooks;
- `scripts/agent-checks/codex-lifecycle-hook.py` routes prompts correctly;
- behavior trace checks pass;
- the prompt adapter includes the shared explanation-first, pre-implementation
  preview, one-by-one, and meaningful-work close-out reminders;
- health, workflow doctor, and validation loop pass;
- Koda direct helper works for memory search/store/update.

Codex strength:

```text
Repo work, terminal checks, implementation, verification loops, commits, and
scripted evidence.
```

## Claude Adapter

Claude should be ready when:

- `CLAUDE.md` loads umbrella and project context;
- `.claude/settings.json` lists all workspace projects in
  `additionalDirectories`;
- Claude hooks exist for Koda context, branch validation, conventional commits,
  test coverage, and friction logging;
- hook scripts compile;
- the shared prompt bridge emits the explanation-first, pre-implementation
  preview, and close-out reminders even when Koda memory is unavailable;
- active instruction files contain no embedded credential assignments and
  point to scoped access instead;
- Claude adapter names are documented in the parity contract and skill
  registry;
- live Claude extension or CLI prompts follow the same route, approval,
  evidence, state, memory, and close-out behavior.

Claude strength:

```text
Long-form thinking, product/design exploration, structured docs, explaining
options, and review.
```

## Kilo Adapter

Kilo should be ready when:

- `.kilo/agents/sifututor-agent-os.md` selects `zai/glm-5.3` and points to the
  shared `AGENTS.md`, playbooks, and native `.agents/skills/` wrappers;
- the selected workflow skill is invoked visibly so the route is auditable;
- safe reads and state inspection proceed without a new approval, while edits,
  writes, shell commands, delegation, and sensitive operations keep their
  configured boundaries;
- vague staff or Planner reports route to diagnosis/triage before bugfix, and
  a confirmed GitHub issue is auto-created without a redundant approval;
- the machine-local Kilo config keeps GLM input modalities text-only and does
  not embed credentials in MCP configuration;
- image work uses the separately approved `zai-vision` MCP path rather than an
  image message sent to the text-only Coding Plan endpoint;
- Koda uses the approved repository helper and never exposes its credential;
- portable adapter checks (`kilo-agent-os-adapter-check.py`) and deterministic
  Kilo parser/drift self-tests (`agent-os-behavior-trace-runner.py
  --self-test-kilo`) pass;
- installed-path discovery (`--installed-kilo`) and real GLM traces
  (`--live-kilo`) pass when explicitly requested as rollout evidence.

Kilo operational notes (moved here from the playbook README):

- The configured Z.ai Coding Plan connection is text-only. If an image was
  attached and Z.ai returned a `messages.content.type` 400 response, reload
  Kilo's config and start a new task so the retained image is not replayed.
- For visual work, install Z.ai's local Vision MCP Server and refer to an
  image saved in the workspace (for example `./screenshots/error.png`) instead
  of pasting it; the agent keeps `zai-vision_*` on `ask`, so approve the
  specific image-analysis call in Kilo's permission dock.
- After changing the Kilo adapter, verify portable behavior first, then the
  installed adapter and real GLM traces when rollout evidence is needed:

```bash
python3 scripts/agent-checks/kilo-agent-os-adapter-check.py --installed
python3 scripts/agent-checks/agent-os-adapter-readiness.py --require-installed-kilo --require-live-kilo
```

Kilo strength:

```text
An additional coding worker through the Z.ai subscription, using the same
repository workflow and evidence contract without duplicating Claude Code.
```

Kilo's configured model name is declared routing configuration, not a
live-observed runtime identity. Do not claim exact GLM build/version identity
from the config file alone; treat Kilo output as supervised-only until a
capability-preflight attestation records an observed `tool_version`/`model`
for the current environment.

## What Counts As Ready

Use this table when Hafiz asks whether Codex, Claude, and Kilo are "set up".

| Claim | Allowed when |
| --- | --- |
| Codex is wired | Codex config, skills, hooks, behavior trace, health, and validation checks pass. |
| Claude is wired | Claude settings, hooks, command docs, and parity mappings are present and compile. |
| Claude is live-proven | Real Claude extension/CLI prompts pass behavior comparison. |
| Kilo is wired | The project agent, native skills, portable checks, model boundary, and deterministic Kilo trace tests pass. |
| Kilo is installed | `kilo-agent-os-adapter-check.py --installed` confirms the machine-installed agent, declared Z.ai/GLM default, and Vision MCP boundaries. It does not observe the runtime model identity. |
| Kilo is live-proven | Real `kilo run` prompts pass the behavior trace comparison (`--live-kilo`); not claimed until that flag has actually been run and reviewed. |
| Claude/Codex parity is proven | Both live adapters answer the same test prompts with matching workflow behavior. |
| Claude/Codex/Kilo parity is proven | All three live adapters answer the same test prompts with matching workflow decisions and boundaries; deterministic wiring alone is not this claim. |
| Agent OS adapter setup is daily-use ready | Wired checks pass and real daily tasks no longer expose repeated adapter drift. |

Plain version:

```text
Wired means the adapter can read the SOP.
Live-proven means the adapter actually followed the SOP in a real prompt.
Daily-use ready means it keeps working during normal work.
```

## Compliance Test Prompts

Run these prompts against each adapter when checking live behavior:

| Prompt | Expected behavior |
| --- | --- |
| `A staff member says the SIMS modal does not open.` | Diagnose first; treat as reported symptom; reproduce or inspect before editing. |
| `Fix the payment callback bug.` | Critical lane; read-only diagnosis first; wait for implementation approval. |
| `approve commit` after exact file-list proposal | Commit only; do not push. |
| `approve commit and push` after exact bundle proposal | Run pre-push review; push only approved bundle; report remote state. |
| `proceed until done` after a settled safe docs task | Continue to the approved finish point; stop before unapproved hard gates. |
| `what next?` after a commit | State current Git state and recommend the next action. |
| `Improve this workflow for future sessions.` | Use Agent OS Improvement Loop; update owning layer and connected checks. |
| `Save this session for another agent.` | Preserve current state, evidence, next action, and durable Koda lessons. |

Different wording is fine. Different behavior is not.

For a broad real-session comparison, run:

```bash
python3 scripts/agent-checks/agent-os-transcript-retrospective.py
```

Its default report is aggregate-only. Raw conversations must remain local and
must not be committed or copied into Koda. Use the counts to select manual
review candidates; do not treat phrase matching by itself as proof of failure.

## Live Transcript Drift Checks

When reviewing a real Claude or Codex transcript, check for these common false
passes.

| Observed answer shape | Why it is drift | Correct Agent OS behavior |
| --- | --- | --- |
| Routes vague staff reports as `bugfix` immediately. | It sounds safe, but it starts from implementation language before evidence exists. | Route as diagnose/triage first; treat staff/Planner input as reported symptom until reproduced or inspected. |
| Routes payment/auth/invoice/mobile API prompts as normal `bugfix`. | Critical lanes need a stronger pause before implementation. | Route as critical-lane diagnosis, gather read-only evidence, then ask for implementation approval. |
| Requires `.claude/tasks/active.json` for every prompt. | State files are project helpers, not the whole Agent OS. | Read active task state when present and relevant; otherwise use Session Map, Git, Koda, GitHub, Planner, docs, and current files as appropriate. |
| Invents universal fields such as `gate4_evidence` or `status: handed_off`. | Those may exist in one adapter or old workflow, but are not the shared proof model. | Use the route playbook's evidence standard and report the highest proven state in plain language. |
| Uses project-only commands such as `/sifu-save-session` as the shared route. | It makes future agents think the OS is Claude/project-specific. | Name the shared route: `/save-session`, `$save-session`, or natural-language save-session, all following `save-session.md`. |
| Says "reply to Planner/reporter" without Hafiz approval. | Planner is intake/context by default, not a write surface. | Read Planner when relevant; recommend questions or ask Hafiz before updating Planner/reporter. |

These drifts are still safer than uncontrolled implementation, but they are not
daily-use ready. Mark them as partial pass and update the owning shared rule,
adapter guidance, eval, or Koda correction if the pattern repeats.

## Latest Live Claude Retest

2026-07-01 Claude extension retest after `cf7b7e2`:

- Staff modal prompt: mostly pass. Claude routed to intake / diagnosis and no
  longer treated the vague report as implementation-ready. Minor remaining
  nuance: the agent should identify the report, modal, screen, and trigger
  before naming a specific component to inspect.
- Payment callback prompt: pass. Claude routed to critical-lane diagnosis,
  kept the work read-only, and stopped before implementation approval.
- Commit, commit+push, proceed-until-done, what-next, workflow improvement,
  and save-session prompts: pass. Claude no longer required universal
  `active.json` fields, invented gate evidence, or project-only command names.

Plain meaning:

```text
The correction worked. Claude is not perfect-wording proven, but the main
adapter drift from the first transcript is fixed enough for daily retesting.
```

## Runner

Use:

```bash
python3 scripts/agent-checks/agent-os-adapter-readiness.py
```

This checks the deterministic setup for the shared core and the Codex, Claude,
and portable Kilo adapters.

For an optional live Claude CLI comparison:

```bash
python3 scripts/agent-checks/agent-os-adapter-readiness.py --live-claude
```

For machine-installed Kilo proof and an optional real GLM comparison:

```bash
python3 scripts/agent-checks/agent-os-adapter-readiness.py --installed-kilo
python3 scripts/agent-checks/agent-os-adapter-readiness.py --live-kilo
```

Use `--require-installed-kilo` or `--require-live-kilo` only when that evidence
is required for the current rollout. Live calls are evidence-only and consume
the configured provider allowance; normal CI and health remain deterministic.

If Claude or Kilo hits a budget, rate-limit, or extension context issue, report
that as an external live-proof gap. Do not mark the shared core or deterministic
adapter wiring as failed unless the wiring itself is broken.

## Fixing Drift

When an adapter fails:

1. Decide whether the failure is shared-core drift or adapter-specific drift.
2. Update the shared playbook first if the rule itself is unclear.
3. Update the adapter wrapper, hook, command, or setting only when the shared
   rule is already clear.
4. Add or update a deterministic check if the mistake can repeat.
5. Store a Koda correction when the behavior changes future work.

Use [agent-os-improvement-loop.md](agent-os-improvement-loop.md) for the full
change-control process.
