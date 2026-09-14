---
name: autopilot
description: Design a whole app flow end to end without stopping. Runs research, draws every board in Figma, has two independent twins review it, verifies their findings, fixes, and hands back one review pack. Trigger with /autopilot <flow name>.
---

# Autopilot

Read these first, in this order:

1. `~/Projects/Sifututor/docs/agent-playbooks/autopilot/loop.md` (the run)
2. `~/Projects/Sifututor/docs/agent-playbooks/autopilot/sources.md` (what wins when two sources disagree)
3. `~/Projects/Sifututor/docs/agent-playbooks/autopilot/decisions.md` (how it was set up and why)
4. The design repo's `design/design-review-rules.md`, `design/INDEX.md` and
   `design/specs/patterns.md`

Then run the flow.

## Step 1, research

Three agents at once, in one message so they run together:

- `autopilot-data`
- `autopilot-system`
- `autopilot-reference`

Give each the flow name and one paragraph of what the flow is for. Do not
give them each other's output.

## Step 2, decide

Read all three. Write `design/specs/<flow>.md`:
facts, then every decision with its options, the number, the named reference
app, and the reason. Anything you cannot settle from evidence goes in the
decision log marked **needs Hafiz** with the option you took. You do not stop
for it.

## Step 3, the board table, then draw

First, the rules from before: read the change sections of every flow spec
that shares a component with this flow, and the rules list in
`learning.md`. Each rule is either in the pre-flight or written into this
flow's table before a board is drawn.

Write one row per board in the spec first, per
`~/Projects/Sifututor/docs/agent-playbooks/autopilot/board-spec.md`: action and
colour, state, every tap and its destination, every number and its source.

Then every board: happy path, every alternate, every edge case, plus Malay. Then
re-lay the page per `design/figma-map.md`. Export each board. Build one
contact sheet.

Run `design/scripts/preflight.figma.js` on the page through `use_figma` and fix
everything it reports. Export only on an empty report. Then section A of
`design-review-rules.md` by eye.

## Step 4, review, up to five rounds

Each round:

1. Launch `autopilot-twin` and, in the same message, run
   `docs/agent-playbooks/autopilot/twin-codex.sh <sheet> <spec> <out>`.
   They must not see each other's findings.
2. Launch `autopilot-verifier` with both lists, the sheet and the spec.
3. Fix every CONFIRMED and every DRIFT. Decide UNCHECKABLE ones and write
   why. Log WRONG ones to `autopilot/misses.md`.
4. Re-export, look at the export, then write the round's change log. Never
   the log first. Freeze the exported sheet under a round name; the verifier
   reads the frozen copy, never the working file.

Stop when both twins return nothing or at five rounds.

## Step 5, hand back

- Update `learning.md`: the scoreboard row, any new rule, any new check.
- Retrospect before the next flow: sort every finding by cause, add the
  preventable ones to the pre-flight or the board table, and record what
  changed. The next flow's round count is the test.
- Commit everything.
- Then, in chat: the contact sheet opened on screen, the decisions in plain
  words with the number behind each, what needs him, and what is still open.
  Short sentences. No process words, no round numbers, no agent names.

## Never

- Never stop to ask a question. Mark it **needs Hafiz** and keep going.
- Never let a twin see the conversation. It reviews the picture and the spec.
- Never accept a finding with no evidence.
- Never skip a variant because it is similar to another one.
