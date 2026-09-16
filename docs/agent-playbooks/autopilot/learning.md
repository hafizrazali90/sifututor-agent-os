# How this gets better

A run that does not change the rules has taught us nothing.

## The five signals

**1. A confirmed finding of a new kind.** A reviewer found something real that
no written rule would have caught. Write the rule. It goes in
`design/design-review-rules.md` with the screen that caused it, the way every
rule in that file already does. Next flow, the mistake cannot recur.

**2. A wrong finding.** A reviewer reported something the verifier disproved.
Log it in `misses.md` with what the reviewer measured and what was actually
there. When one reviewer produces several of the same kind, its instructions get
a line about that trap. Today's example: a reviewer measured a card's bottom
edge by scanning up from the bottom of the image and hit the action bar
instead. That became the paragraph in `autopilot-reviewer.md` about checking you
measured the right thing.

**3. An escape.** Hafiz found something every reviewer passed. This is the most
valuable signal in the system and the only one that proves the reviewers are not
yet him. It becomes a new check in `hafiz-profile.md`, worded as a question a
reviewer can ask of any screen, and it is added to the nine. Record his
actual words.

**4. Drift.** A decision was written down and not drawn. The verifier caught
it. If drift happens twice in one flow, the drawing step is wrong, not the
verifier: the chat starts reading the change log back before each export.

**5. A blind spot.** Added 16/09/2026. Not a finding at all: a **kind** of
defect that nothing in the system could have found, however many rounds it ran.
It shows up as a fault discovered by accident, or by Hafiz, or by a new script
written for something else. Three of them in one week, all missed for the same
reason: every check measured **where a node sits**, and none read what was
inside a node, what a node promised, or whether a screen's name matched what it
showed. A blind spot becomes a script, and the script's first job is to be
tightened until every line it prints is true.

## The scoreboard

One row per flow, filled in after his review. This is how we know whether
any of it works.

| Flow | Screens | Findings raised | Confirmed | Wrong | Rounds | Escapes | Blind spots |
|---|---|---|---|---|---|---|---|
| Teaching a class | 23 | | | | 3 | |
| Getting paid | 17 | 6 | 5 | 1 | 4 | not yet reviewed |
| Asking staff | 37 | | | | 4 | |
| Becoming verified | 39 | 110 | 96 | 3 | 5 | awaiting his review |
| Being worth picking | 25 | 71 | 59 | 2 | 4 | not yet reviewed |
| Getting work | 43 | 119 | 104 | 10 | 5 + 2 | not yet reviewed |
| Settings and account | 33 | 62 | 53 | 1 | 5 | not yet reviewed |

The rows above predate the blind-spot column, which is why it is empty; the
three found on 16/09 belong to the file as a whole rather than to one flow.

**Escapes is the number that matters.** Everything else is process. If
escapes fall flow over flow, the reviewers are learning him. If escapes stay
flat while findings rise, the reviewers are getting noisier, not sharper, and
the profile needs work rather than the prompts.

## The rule for adding a seventh agent

Do not add one on a hunch. Add one when the same kind of escape happens in
two flows running. If copy escapes twice, a writer joins. If Malay escapes
twice, a Malay writer joins. If a decision is overruled twice on business
grounds no agent could know, that is not a missing agent, that is a decision
that should have been marked **needs Hafiz** and was not.

## What never changes without him

The nine checks can grow. The rules can grow. But a decision recorded in a
flow spec as his is never quietly reversed by a later run. If a new fact
contradicts an old decision of his, the run keeps his decision, draws it his
way, and puts the contradiction in the decision log.

## Rules this system has produced

Written here so the count is visible. Each one exists because something got
through and had to be caught by hand.

| Run | Rule added | What caused it |
|---|---|---|
| Getting paid, round 4 | B15, a total and its parts must describe the same set | A chart head of RM3,412.00 over bars adding to RM2,220 |
| Getting paid, round 4 | B16, a colour that means something must be named | A highlight that turned out not to exist |
| Getting paid, round 4 | B17, the common case is a variant too | Every slip screen had an adjustment; most slips have none |
| Getting paid, round 4 | B18, trust the render, not the bounding box | A label that measured as fitting and clipped on export |

| Becoming verified, round 1 | B20, a number has a source or it is not on the screen | Three invented durations after decision 7 had deleted one |
| Becoming verified, round 1 | B21, never promise a channel the system does not send on | "and by SMS" copied from Grab Driver |
| Becoming verified, round 1 | B22, one glyph, one meaning | The done tick bulleting rules |

| Becoming verified, round 3 | B4 amended, the bar pins only when content fills the screen | Eleven screens with 140 to 310pt of dead space |
| Becoming verified, after round 3 | The screen table before drawing, and the automated pre-flight | Half of 67 findings were written rules not applied |

| Being worth picking, round 1 | The drawing step reads the screen table back before export | The one row with a number drifted and the drift travelled to three screens |

| Being worth picking, round 3 | The change log is written after the export, not before | A verifier reported eight drifts that were the old export against a new log |
| Being worth picking, round 4 | A rule fixed on one flow is checked on its sibling by the pre-flight, not by memory | patterns.md 8 was fixed on flow 1's hubs in its round 4 and drawn wrong on flow 2's; pre-flight check 9 |
| Getting work, round 3 | A writer joins: `autopilot-copy` writes every string per reader (tutor, parent, staff), English and Malay, before drawing and after each export | Copy escaped in two flows running: an approval rate the data did not hold (flow 2), "most" over an average, platform-side wording, Malay mapped from English (flow 3). Hafiz asked for a narrative and copy expert per audience on 14/09/2026 |
| Getting work, the stack, round 2 | Clone in one call, edit in the next: instance text in a same-script clone ignores the edit | Two Malay screens kept English chips though the script reported the change (B19, third trap) |
| Settings and account, round 4 | Pre-flight check 15, a banned-string list taken from `copy-glossary.md`: a string the glossary retires can never be drawn again | A Malay screen drawn fresh in round 3 shipped "Sentiasa dihantar" the same round the glossary banned it, because only a reviewer was checking. The glossary was a document nothing enforced |
| Settings and account, round 4 | The fold is two marks in the page gutters at 812, never a rule across the content | The full-width dashed line read as a strike-through on four screens, worst through a paragraph of a legal document |
| Settings and account, round 4 | A screen covered by a half sheet is exempt from the empty-tail check | The pre-flight blocked the new discard-sheet screen for 450pt of "empty" screen that a sheet was sitting on |
| Settings and account, round 5 | Copy that names what a notification sends is checked against the backend's own category map, not against what the row is called | Three rows promised messages the code does not send: verification updates in the always-on tier, a slip-ready notification that belongs to parents, and "classes" where the category sends requests |
| Being worth picking, after round 4 | Pre-flight checks 10 and 11 (comparative claims, the same object twice), chevron rows in the destinations list; the table gains a Header column and an empty-state row per editor; the runner reads previous flows' rules before drawing | "Approved far more often" with no rate behind it; the About you book reused for the Quran row; a chevron with nowhere to go; the Profile named as the first hero candidate and drawn standard for four rounds; empty states drawn in round 3 |

| 16/09/2026, the copy and link pass | **B20 amended: a number's source must be upstream of the design.** Production, a PRD, a backend contract or code. Another screen in the same Figma file is not a source | A Nakngaji commission sheet showed RM29 a session, then RM37, against a RM499 package. Every figure was reverse-engineered from a number already printed on another screen, so it satisfied B20's letter and was entirely invented. The real rule, the real rates and the real package prices had been on `origin/main` for weeks in `docs/features/nakngaji/prd.md`, which was not on the sources list |
| 16/09/2026 | **The product docs and the application code join `sources.md`** | As above. No agent was reading the approved feature specs of the system it was designing for |
| 16/09/2026 | **A fact is looked up, never marked "needs Hafiz"** | Two items sat on the open list for days as his to answer. One query and one file closed both in minutes: the commitment fee is RM100 once, on 1,043 of 1,170 rows, which the drawn screen already said |
| 16/09/2026 | **A screen's name is not evidence** | `39 About you, answering out loud` showed a typed answer and a keyboard. The name had been believed for days, hiding the fact that the speaking route, the one that reaches the 79% of tutors who never write anything, had no screen at all |
| 16/09/2026 | **Every promise gets walked: `links.figma.py` joins the run** | It found two entire screens promised everywhere and drawn nowhere, including the commission sheet, linked from 19 screens and the most-linked destination in the file |
| 16/09/2026 | **A check that reads the node box cannot see a crop: `artwork.figma.py` joins the run** | Hafiz found a tray whose lid ran off the top of its own picture, while the run was busy elsewhere. Became check 8 in `hafiz-profile.md` |
| 16/09/2026 | **A spec that retires an asset has to be enforced, not just written** | `asset-generation.md` recorded on 15/09 that the smiling coins were superseded. On 16/09 they were still on four screens, one of them the RM50 referral reward |
| 16/09/2026 | **A rename sweep skips identifiers** | Renaming one invented word across 45 files rewrote `twins.figma.py` inside three specs as a filename that does not exist |
| 16/09/2026 | **Questions go one at a time through the ask tool, each with two real alternatives** | "why dont we just go one by one use ask tools". Thirteen Malay strings went over one at a time and all thirteen came back, three of them redirects. The same thirteen in a file he was asked to read got nowhere |

B16 and B18 are the two that came out of a reviewer being wrong rather than
right, which is the pattern worth watching: a bad measurement usually sits on
top of a real complaint.

## The signal the scoreboard was missing, 16/09/2026

The scoreboard counts findings, confirmations and escapes. It has no column for
the thing that turned out to matter most: **a defect no check could see.**

Three of the worst faults this week were invisible to every script and every
reviewer, for the same reason. The checks all measure **where a node sits**.
None of them read what is **inside** the node, what a node **promises**, or
whether a screen's **name** matches what it shows.

| Fault | Why every check missed it |
|---|---|
| A tray cropped through its own lid | Geometry measures the box. The crop is in the pixels |
| A commission sheet linked from 19 screens and never drawn | Nothing walked the links. A missing screen has no node to measure |
| Invented Nakngaji rates | Arithmetically consistent with the card beside them. Only an upstream source disproves them |

**The question to ask after every flow is no longer "what did the reviewers
find". It is "what kind of thing could nothing here have found".** Each answer
becomes a script, and each script's first run is a false-positive storm that has
to be tightened until every line it prints is true. `artwork.figma.py` printed
13, then 4, and 2 of the 4 were real.
