# The board spec, written before drawing

Hafiz, 14/09/2026: "check the overall where you should improve so that we
dont have to waste time going in loop so many times for things that can be
avoid! maybe a clearer uiux spec or something before build."

On Becoming verified, three rounds raised 67 findings. Sorted by cause:

| Cause | Share | What would have caught it |
|---|---|---|
| A written rule not applied | about half | A pre-flight run before export |
| A tappable thing with no destination | a fifth | Listing every tap before drawing |
| Copy that promised or counted something with no source | a tenth | A source column in the board spec |
| No rule existed yet | a tenth | These become rules; unavoidable |
| Execution slip (clipped, wrong asset in slot) | the rest | Looking at the export |

So two things now happen before any board is drawn.

## 1. A line per board in the flow spec

Under a heading **Boards** in `design/specs/<flow>.md`, one row per board:

| # | Board | One action, colour | State it shows | Header | Every tap and where it goes | Numbers on it and their source |
|---|---|---|---|---|---|---|

Rules that fill the columns:

- **One action.** Blue if it commits (save, send, apply, pay, agree). Black
  if it proceeds (continue, next, open, see). Text for the safe option. The
  colour is decided here, in words, not in Figma.
- **State.** Which of the flow's states this board is: the common case, the
  single item, the long list, the other brand, the addition, the Malay, the
  sent-back. B17: the common case is listed first.
- **Header.** Standard, Coloured or Hero, per patterns.md 1a. Coloured when
  one task fills the screen and has one outcome; Hero for a celebration or
  a programme page with an illustration; Standard otherwise.
- **Every tap.** Text buttons, chevron rows, links in a sentence, header
  actions. Each names a board in this flow, a flow that owns it, or a
  not-drawn entry with the reason. B14.
- **Numbers.** Every duration, count, limit, rate and money figure, with the
  production query, code line, or document that backs it. B20. If the cell is
  empty the number does not go on the board.

The twins review against this table. Drift is any board that disagrees with
its row.

## 2. The pre-flight runs before every export

`design/scripts/preflight.figma.js` in the app repo, pasted into
`use_figma` with the page id. It reports: button colour against the verb, checklist rows against
patterns.md 8, comparative claims in copy, the same object twice on a board,
chevron rows and text buttons for the destinations column,
the done tick outside a done row, white cards with no edge, tertiary text on
a pastel, counts written as words, unbound white wrapper fills, empty space
above the pinned bar, board overlap, and every text button so it can be
checked against the destinations column.

A non-empty report is fixed, not disclosed. The export happens only when it
is empty.

## After Being worth picking, 14/09/2026

Four rounds, 71 findings, 59 confirmed, 2 wrong. One round fewer than the
first flow, on more boards. Sorted by cause:

| Cause | Share | What now catches it |
|---|---|---|
| A written rule not applied, most often one fixed on the sibling flow | about a third | Pre-flight check 9 (checklist rows), and the rules step below |
| A state or variant not drawn: empty, other brand, long list, the preview behind a link | a quarter | The Empty and Header columns below; the pre-flight lists chevron rows |
| Copy that claimed more than the data holds | a tenth | Pre-flight check 10 flags comparative claims for the table |
| Execution slip: clipped wordmark, a light object, an object reused | a sixth | Pre-flight check 11 (same object twice); the export is looked at before the log is written |
| A tap with no destination | a tenth | Chevron rows join the destinations list |

Three things change in the table and the run:

- **Header style column.** Standard, Coloured or Hero, from patterns.md 1a,
  decided per board in words. The Profile was named as the first hero
  candidate in the pattern file and drawn standard for four rounds because
  nobody chose.
- **Empty state row.** Every editor and every list gets its empty state as
  its own row before drawing, listed next to the filled one. 92.8% of tutors
  start empty; the empty board is the common case, B17.
- **Rules from previous flows.** Before drawing, read the change logs of
  every flow that shares a component with this one and the rules list in
  `learning.md`. Each rule is either enforced by the pre-flight or written
  into this flow's table. A fix that lands on one flow and not its sibling
  costs a round.

## What this should do to the numbers

The scoreboard in `learning.md` records rounds and findings per flow.
Becoming verified took three rounds and 67 findings with neither of these in
place. Being worth picking is the first flow with both. If its round count
does not drop, the checks are wrong, not the reviewers.
