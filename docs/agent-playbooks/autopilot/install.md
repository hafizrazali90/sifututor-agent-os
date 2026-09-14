# Installing it

The agent definitions and the runner skill live here so they are versioned
and travel with the repo. Claude Code reads them from the home directory, so
they have to be copied there once, and again whenever they change here.

```bash
cp docs/agent-playbooks/autopilot/agents/autopilot-*.md ~/.claude/agents/
mkdir -p ~/.claude/skills/autopilot
cp docs/agent-playbooks/autopilot/runner-skill.md ~/.claude/skills/autopilot/SKILL.md
```

New agents and skills are registered when a session starts. After copying,
start a new session before `/autopilot` or the five agent types will not be
found.

## What is in here

| File | What it is |
|---|---|
| `decisions.md` | The seven decisions that set this up, in his words |
| `hafiz-profile.md` | The eight checks, built from 20,077 of his messages |
| `sources.md` | What the agents read, in authority order |
| `loop.md` | The run: research, decide, draw, review, hand back |
| `learning.md` | The four signals, the scoreboard, when to add an agent |
| `agents/` | The five agent definitions |
| `runner-skill.md` | The `/autopilot` skill |
| `twin-codex.sh` | The second twin, on a different model |
| `misses.md` | Every wrong finding a twin has made |

## Portability

Nothing in the loop is specific to this app. Three research lanes, a
drawing step, two blind reviewers, a verifier, and a learning pass work on
any design surface. What is specific sits in two files: `hafiz-profile.md`,
which is the reviewer being imitated, and `sources.md`, which names this
project's documents. Swap those two and the system moves.
