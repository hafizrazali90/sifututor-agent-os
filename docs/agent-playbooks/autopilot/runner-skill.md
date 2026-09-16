---
name: autopilot
description: Design a whole app flow end to end without stopping. Runs research, draws every screen in Figma, has two independent reviewers review it, verifies their findings, fixes, and hands back one review pack. Trigger with /autopilot <flow name>.
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
give them each other's output. The data and system lanes return their
report inline (their definitions forbid writing files); save each report
to the scratchpad `lanes/<flow>-<lane>.md` yourself before reading the next,
so the spec cites a file and the next session can find it.

## Step 2, decide

Read all three. Write `design/specs/<flow>.md`:
facts, then every decision with its options, the number, the named reference
app, and the reason. Anything you cannot settle from evidence goes in the
decision log marked **needs Hafiz** with the option you took. You do not stop
for it.

## Step 3, the screen table, then draw

First, the rules from before: read the change sections of every flow spec
that shares a component with this flow, and the rules list in
`learning.md`. Each rule is either in the pre-flight or written into this
flow's table before a screen is drawn.

Write one row per screen in the spec first, per
`~/Projects/Sifututor/docs/agent-playbooks/autopilot/screen-spec.md`: action and
colour, state, every tap and its destination, every number and its source.

Then the copy pass: launch `autopilot-copy` with the spec and the screen
table. It returns the copy table for every string on every screen, English
and Malay, with the reader each screen serves and every claim to cut. Draw
from that table, never from your own first draft. After each export, give
it the sheet too: it checks the drawn words against its table.

Then every screen: happy path, every alternate, every edge case, plus Malay. Then
re-lay the page per `design/figma-map.md`. Export each screen. Build one
contact sheet.

Run `design/scripts/preflight.figma.js` on the page through `use_figma` and fix
everything it reports. Export only on an empty report. Then section A of
`design-review-rules.md` by eye.

Then the six checks, all of them, before a reviewer sees anything. They are
free, deterministic, and each one reaches a kind of fault the others cannot:

| Script | What it alone can see |
|---|---|
| `measure.figma.py` | where every node sits: clipped, off centre, past the fold, overflowing |
| `system.figma.py` | contrast, tap size, a surface too pale to see, a colour typed instead of linked |
| `malay-check.py` | a Malay screen holding less than its English one |
| `links.figma.py` | every promise a screen makes, so each can be walked to a destination |
| `artwork.figma.py` | a drawn object cropped through itself, which lives in the pixels and not in the node box |
| `dates.figma.py` | a weekday that does not match its date, in either language |

`links.figma.py` produces a list, not findings. Walk it: each promise ends as a
screen that exists and is named, a screen that is missing and gets drawn, or a
destination that is not ours and is written down so the check stops raising it.

## Step 4, review, up to five rounds

Each round:

1. Launch `autopilot-reviewer` and, in the same message, run
   `docs/agent-playbooks/autopilot/reviewer-codex.sh <sheet> <spec> <out>`.
   They must not see each other's findings.
2. Launch `autopilot-verifier` with both lists, the sheet and the spec.
3. Fix every CONFIRMED and every DRIFT. Decide UNCHECKABLE ones and write
   why. Log WRONG ones to `autopilot/misses.md`.
4. Re-export, look at the export, then write the round's change log. Never
   the log first. Freeze the exported sheet under a round name; the verifier
   reads the frozen copy, never the working file.

Stop when both reviewers return nothing or at five rounds.

## Step 5, hand back

- Update `learning.md`: the scoreboard row, any new rule, any new check.
- Retrospect before the next flow: sort every finding by cause, add the
  preventable ones to the pre-flight or the screen table, and record what
  changed. The next flow's round count is the test.
- Commit everything.
- Then, in chat: the contact sheet opened on screen, the decisions in plain
  words with the number behind each, what needs him, and what is still open.
  Short sentences. No process words, no round numbers, no agent names.

## When a question does reach him

Rare, and only for judgement he holds and the systems do not: what the business
wants, what a tutor would feel, what a Malay reader would say. **A question
about what is true is a lookup, not a question.** Production, the PRDs under
`sifu-tutor/docs/features/`, the backend contracts and the application code
answer those, and two items that sat on the open list for days as his to decide
were both closed in minutes once anyone looked.

When one is genuinely his, it goes through the ask tool, one per message:

1. where the reader meets it, in plain words, never a screen number
2. what is drawn now, marked as the recommendation, and why it was drawn that way
3. two real alternatives, each with what it costs
4. the objection to my own answer, when there is one

Then check his answer against the screen before applying it. On 16/09 an answer
would have printed the same words twice, because the phrase he chose was already
the row title above the line he was choosing for.

## Never

- Never stop to ask a question. Mark it **needs Hafiz** and keep going.
- Never take a number from another screen in this file. A source is upstream:
  production, a PRD, a backend contract, or code.
- Never trust a screen's name. `39 About you, answering out loud` showed a
  keyboard.
- Never let a reviewer see the conversation. It reviews the picture and the spec.
- Never accept a finding with no evidence.
- Never skip a variant because it is similar to another one.
