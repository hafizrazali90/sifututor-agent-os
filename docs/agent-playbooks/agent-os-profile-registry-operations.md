# Agent OS Profile Registry Operations

Use this when creating, updating, reviewing, or closing real permission profile
records for a person, agent, or developer staff member.

Plain meaning:

```text
The public docs explain the access rules.
The private registry tracks who currently has which profile.
This playbook keeps that private registry useful instead of messy.
```

## Source Of Truth

Recommended private registry:

```text
~/.config/sifututor/agent-os/profile-assignments.md
```

Use the public template:

```text
docs/agent-playbooks/templates/profile-assignment-record.md
```

Do not commit the private registry. Do not copy it into public docs, GitHub
issues, PR bodies, Koda, Session Maps, or chat unless Hafiz explicitly asks for
a sanitized summary.

## What Belongs In The Registry

Store enough information for a future agent or Hafiz to understand the current
permission state.

| Keep | Why |
| --- | --- |
| Person or agent name/id | Identifies who the record is for. |
| Profile | Shows the allowed starting boundary. |
| Project or service boundary | Prevents broad access from leaking into unrelated work. |
| Purpose | Explains why this access exists. |
| Connected tools | Shows what is actually wired. |
| Probe/check evidence summary | Proves the tool worked at activation or review time. |
| Capability states | Separates available, fallback, unknown, blocked, and forbidden. |
| Approval source | Shows why stronger access was allowed. |
| Review point | Prevents forgotten access. |
| Lifecycle state | Shows active, downgraded, suspended, upgraded, or closed. |

Do not store:

- passwords
- tokens
- API keys
- repo `.env*` values
- raw credentials
- raw production data
- customer private payloads
- copied secret-bearing command output
- broad personal notes that are not needed for access review

## Create A Record

Create a private profile record only after there is a real person/agent and a
real job boundary.

Steps:

1. Identify who needs the profile.
2. Name the project, repo, service, or task boundary.
3. Pick the lowest profile that can do the job.
4. Name what remains blocked even if tools are connected.
5. Connect only the tools needed for that profile.
6. Run the smallest safe probe for each connected tool.
7. Record the probe result as a summary, not raw secret-bearing output.
8. Set a review point.
9. Save the record in the private registry.

Plain example:

```text
Give a developer staff member the builder profile for one repo, not every repo.
Record that they can edit scoped code and run local tests, but cannot push,
merge, deploy, read secrets, or touch production.
```

## Update A Record

Update the record when the current access state changes.

Triggers:

- a new tool is connected
- a tool probe changes from unknown to available
- a tool fails and becomes fallback or unknown
- Hafiz approves a temporary escalation
- Hafiz rejects or narrows an access request
- the project or task boundary changes
- the person/agent no longer needs the same profile
- a guard, check, or review finds risk

Update only the fields that changed. Add a short review log entry explaining
the decision in normal language.

## Review A Record

Review records before access becomes stale.

Use this review rhythm:

| Profile | Default review point |
| --- | --- |
| Owner / Hafiz | Event-based only. Review when tools, risk, or policy changes. |
| Internal agent | Current session or task boundary. |
| Developer staff - reader/QA | Every 30-60 days or when the project changes. |
| Developer staff - builder | Every 14-30 days, or at the end of the assigned work. |
| Support / ordinary staff | Usually no registry record; staff stay in Planner intake. |
| Advanced operations | Same session or same operation only. Close immediately after use. |

Review questions:

1. Is the person/agent still doing this work?
2. Is the project/service boundary still correct?
3. Was the access actually used recently?
4. Did any probe/check fail?
5. Can a lower profile do the job now?
6. Are any tools broader than the task needs?
7. Is there any pending approval, risk, or confusion?

Review decision:

| Decision | Meaning |
| --- | --- |
| Keep | Current profile is still needed and safe. |
| Downgrade | Less access is enough. |
| Suspend | Stop using this profile until need, identity, risk, or tool state is clear. |
| Upgrade | More access is needed; requires Hafiz approval with exact scope. |
| Close | Purpose is finished; remove temporary tools and keep only durable lessons. |

## Close Or Downgrade A Record

Close or downgrade when the access purpose is finished.

Steps:

1. Record the final decision.
2. Name what changed: tools removed, profile lowered, or access suspended.
3. Keep only the minimum durable note needed for future understanding.
4. Store durable policy lessons in Koda only if future agents should behave
   differently.
5. Do not store private assignment details in Koda.

Plain example:

```text
The staff member finished the scoped repo task. Downgrade from builder to
reader/QA, remove write tools, keep issue/PR read access if still needed, and
set the next review date.
```

## Audit The Registry

Run a private registry audit when:

- Hafiz asks who has what access
- a project ends
- a staff role changes
- a tool or credential setup changes
- an access mistake happens
- before developer-staff rollout expands
- at least monthly while staff/builder profiles are active

Audit shape:

```text
Profile registry audit: <date>
Records checked: <count>
Active profiles: <count by profile>
Unknown/stale probes: <count/list sanitized>
Overdue reviews: <count/list sanitized>
Recommended changes: <keep/downgrade/suspend/close items>
Secrets check: no secrets intentionally stored / issue found and removed
Decision needed from Hafiz: <yes/no and exact decision>
```

Do not print the full private registry in chat by default. Summarize the useful
state and ask Hafiz only for decisions that require judgment or authority.

## What To Put In Koda

Koda is for durable lessons, not live assignment state.

Store in Koda:

- a reusable access policy correction
- a repeated workflow mistake
- a rule future agents must follow
- a non-obvious lesson from a profile review

Do not store in Koda:

- who currently has a profile
- live connected tools for a person
- private assignment details
- approval trails that belong to a task
- anything secret or credential-like

## Agent Behavior

When an agent needs to use or check profile records:

1. Read public rules first.
2. Read the private registry only if the task needs current assignment state.
3. Use the narrowest relevant information.
4. Never print secrets or raw registry content.
5. Report a sanitized summary.
6. Ask Hafiz only for decisions the agent cannot safely make.

If the registry is missing:

```text
I can use the public profile rules, but I cannot confirm current assignments
because the private registry is not present or not readable in this session.
```

Do not invent profile assignments from memory, role names, or old chat.
