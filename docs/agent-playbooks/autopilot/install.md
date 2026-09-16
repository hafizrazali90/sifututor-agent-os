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
start a new session before `/autopilot` or the agent types will not be found.

**This was not theory.** Running the copy on 16/09/2026 turned up
`autopilot-measure.md` living only in `~/.claude/agents/`, never versioned,
about to be silently overwritten by the next copy. It is in this folder now.

**The copy is one-way and it goes stale.** `~/.claude/agents/` is what actually
runs; this folder is only the versioned original. Every edit here needs the copy
re-run, and an edit made directly in `~/.claude/agents/` is lost the next time
anyone copies. Check both before assuming an agent has a rule.

## What is in here

| File | What it is |
|---|---|
| `decisions.md` | Every decision he has made about how this runs, in his words |
| `hafiz-profile.md` | The nine checks, built from 20,077 of his messages |
| `sources.md` | What the agents read, in authority order |
| `loop.md` | The run: research, decide, draw, check, review, hand back |
| `learning.md` | The five signals, the scoreboard, when to add an agent |
| `screen-spec.md` | The table written before any screen is drawn |
| `agents/` | The seven agent definitions |
| `runner-skill.md` | The `/autopilot` skill |
| `reviewer-codex.sh` | The second reviewer, on a different model |
| `misses.md` | Every wrong finding a reviewer or a check has made |
| `how-others-do-this.md` | What the rest of the industry does, what we took, what we still owe |

## The checks live in the design repo, not here

`loop.md` and `runner-skill.md` name six scripts. They are in
`design/scripts/` in the design worktree, not in this folder, because they read
one specific Figma file over the REST API:

| Script | What it alone can see |
|---|---|
| `measure.figma.py` | where a node sits: clipped, off centre, past the fold, overflowing |
| `system.figma.py` | contrast, tap size, a surface too pale to see, a typed colour |
| `malay-check.py` | a Malay screen holding less than its English one |
| `links.figma.py` | every promise a screen makes |
| `artwork.figma.py` | a drawn object cropped through itself |
| `dates.figma.py` | a weekday that does not match its date |

They need `~/.config/sifututor/agent-access/figma-readonly.conf` and
`/usr/bin/python3`, which has Pillow and pymysql. `api.figma.com` does not
resolve from the Codex sandbox, so this lane is Claude-side only.

## Portability

Nothing in the loop is specific to this app. Three research lanes, a
drawing step, two blind reviewers, a verifier, and a learning pass work on
any design surface. What is specific sits in two files: `hafiz-profile.md`,
which is the reviewer being imitated, and `sources.md`, which names this
project's documents. Swap those two and the system moves.
