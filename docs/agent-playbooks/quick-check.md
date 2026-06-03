# Quick Check Playbook

Use this at the start of a Codex or Claude session when you want to confirm the
workflow layer is healthy before real work starts.

## What It Checks

- Agent OS capability, Koda direct health, and approval gates
- root git status
- active project/task state
- shared guard scripts
- Codex skill visibility
- Codex hook config presence
- Claude parent `additionalDirectories`
- all-project workflow baseline

## Command

From the umbrella root:

```bash
scripts/agent-checks/workflow-doctor.sh
```

## Output Shape

```text
QUICK CHECK - PASS | FAIL | PARTIAL

Doctor:
- <workflow-doctor result>

Agent OS:
- <agent-os-health result>

Active work:
- <project/task summary>

Codex:
- <skills/hooks/trust status>

Claude:
- <additionalDirectories/session config status>

Next:
- <safe next action>
```

## If It Fails

Do not start implementation until you understand the failure. Fix missing
workflow files, invalid JSON, broken hook scripts, or guard failures first.

If only the all-project sweep fails but `agent-os-health.sh` passes, the
umbrella Agent OS may still be usable for docs/workflow discussion. Do not start
product implementation until the relevant project failure is understood.
