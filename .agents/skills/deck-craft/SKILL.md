---
name: deck-craft
description: Use when asked for a deck, slides, a presentation, or a pitch or briefing deck, or to fix a deck that looks empty, boxy or like a wall of text. Builds every slide as a real graphic with logos and colour badges, checks the layout with a lint, and runs a four-reviewer loop before Hafiz sees it. Must follow docs/agent-playbooks/deck-craft.md.
---

# Deck Craft

Use this skill to build, rebuild or repair a slide deck.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/deck-craft.md
```

Before drawing anything, look at the reference contact sheets the playbook
names. Every body slide carries one real graphic. Text in boxes is not a slide.

## Toolkit

```text
.agents/skills/deck-craft/scripts/    build, render, lint, contact sheets, self-test
.agents/skills/deck-craft/templates/  starter deck, reviewer brief, fix brief
```

Do not show Hafiz a deck until the lint passes and four reviewers report no
BLOCKER or MAJOR.

## Human-Facing Alias

```text
Claude: /deck-craft
Codex: $deck-craft
```
