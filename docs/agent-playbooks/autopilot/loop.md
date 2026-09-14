# The run

One flow at a time. Six agents. The chat draws and decides.

## Before drawing, once

Three agents in parallel. None of them sees the others' work, so none of
them anchors on it.

| Agent | Question |
|---|---|
| `autopilot-data` | What really happens, in numbers |
| `autopilot-system` | What exists, what the backend can do, what it costs staff |
| `autopilot-reference` | How the best apps solve this, named and measured |

The chat reads all three and writes the flow's spec: the facts, then a
decision per question with the options, the number behind it, the reference
app, and the reason. Assumptions are stated as assumptions.

## Before drawing, the board table

One row per board in the flow spec, per `board-spec.md`: the one action and
its colour, the state it shows, every tap and where it goes, every number
and its source. Nothing is drawn until its row exists. This came out of
Becoming verified, where half of 67 findings were written rules not applied
and a fifth were taps with no destination.

## Drawing

The chat draws every board in Figma, on one page per flow, in three
sections: happy path, alternates, Malay. Then re-lays the page so no board
overlaps its neighbour, exports each board, and builds one contact sheet.

Before any export, the chat runs `design/scripts/preflight.figma.js` on the
page and fixes everything it reports. It checks the rules reviewers have
already caught once: button colour by verb, the done tick outside a done row,
white cards without an edge, tertiary on a pastel, counts as words, unbound
white wrappers, empty space above the bar, overlap, and lists every text
button for the destinations column. The export happens only on an empty
report. Then section A of `design-review-rules.md` by eye.

## Review, up to five rounds

Each round:

1. `autopilot-twin` on Claude and the Codex twin run **in parallel and
   blind**, on the same contact sheet and spec. Neither sees the other's
   findings. Neither sees the conversation.
2. `autopilot-verifier` takes both lists and marks each finding CONFIRMED,
   WRONG or UNCHECKABLE, and reports DRIFT between the spec and the boards.
3. The chat fixes every CONFIRMED and every DRIFT. It decides on
   UNCHECKABLE ones and writes the reason. It ignores WRONG ones and logs
   them.
4. Re-export, re-shoot, next round.

Stop when both twins return nothing, or at five rounds. Anything still open
at five goes into the decision log as an open question with what each twin
said, and the run moves on. It never waits for Hafiz.

## After

The change log for a round is written after the export that shows the
changes, never before. On Being worth picking round 3 the log said "fixed"
while the verifier was still reading the previous export, and it reported
eight drifts that were only a sequencing fault. Order is: fix, pre-flight,
export, then log.

The verifier reads a frozen copy of the sheet for its round, saved under a
round-numbered name, never the working file. On Being worth picking round 3
the working sheet was re-exported while the verifier was still reading it.

- Every decision is in the flow's spec, dated, with its reason.
- The contact sheet is in `design/research/`.
- The decision log for the review pack is written.
- Everything is committed.
- The scoreboard in `learning.md` is updated.

## What never stops the run

Nothing. A decision that would once have been a question becomes a row in
the decision log marked **needs Hafiz**, with the option taken, why, and
what hangs on it. The boards affected are named so he can see the blast
radius of changing his mind.

## A rule conflict gets a reference pass, not a question

Hafiz, 14/09/2026: "why dont u check how other app are doing similar
section then we follow and adapt to our current design". When a new pattern
needs something a written rule forbids (the stack card against the flat
card rule), the run does not stop and ask him to arbitrate. It measures how
the apps that solve the same problem do it, including apps whose systems
share our constraint, then brings him the evidence with a recommendation,
or adapts without breaking the rule at all. The question, if one is still
needed, arrives with the measurements attached.
