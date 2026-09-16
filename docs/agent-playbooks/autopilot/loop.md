# The run

One flow at a time. Seven agents. The chat draws and decides.

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

## Before drawing, the screen table

One row per screen in the flow spec, per `screen-spec.md`: the one action and
its colour, the state it shows, every tap and where it goes, every number
and its source. Nothing is drawn until its row exists. This came out of
Becoming verified, where half of 67 findings were written rules not applied
and a fifth were taps with no destination.

## Drawing

The chat draws every screen in Figma, on one page per flow, in three
sections: happy path, alternates, Malay. Then re-lays the page so no screen
overlaps its neighbour, exports each screen, and builds one contact sheet.

Before any export, the chat runs `design/scripts/preflight.figma.js` on the
page and fixes everything it reports. It checks the rules reviewers have
already caught once: button colour by verb, the done tick outside a done row,
white cards without an edge, tertiary on a pastel, counts as words, unbound
white wrappers, empty space above the bar, overlap, and lists every text
button for the destinations column. The export happens only on an empty
report. Then section A of `design-review-rules.md` by eye.

## Review, up to five rounds

Each round:

0. **`autopilot-measure` runs first, before any reviewer.** It reads the Figma
   file itself over the REST API and reports geometry as arithmetic: text cut
   by something that clips, a mark off centre in its own box, content past the
   bottom of its screen, a screen past 812 with no fold, a rail that does not
   reach its dots, a frame wider than the phone it sits in. Run it with
   `/usr/bin/python3 design/scripts/measure.figma.py <page-id> ...` and fix
   everything it finds before a reviewer looks at a sheet.

   It exists because six review rounds passed over a tick 4pt from one edge of
   its box and 10pt from the other, a badge hanging outside the object it
   marks in 113 places, and an 861pt page note nested inside a 375pt phone
   screen where it rendered as a clipped banner. A reviewer reading a PNG cannot
   see any of that; arithmetic on coordinates sees all of it in seconds. It
   also catches the chat's own mistakes within a minute of making them: it
   caught a row rebuilt to 788pt inside a 375pt screen on the first run after
   the edit.

0a. **What the size and fit checks look for, added 16/09/2026.** Hafiz pointed
   at one green `5 of 5` marker and said to check every flow for the same
   thing. That one marker turned into four checks and 38 fixes:

   - **ICON-SIZE / ART-SIZE** against the scale in `core-components.md`
     (24/20/16 for line icons; 44, 64, 72, 112, 120, 160 for 3D objects). A
     glyph inside a badge, a dot or a rail stop is exempt, decided by shape
     and not by layer name, because the same badge is called badge, mark and
     rail in three different flows.
   - **ROUND-TIGHT**: text inside a pill or circle with too little clearance
     for the curve. It measures `absoluteRenderBounds`, the inked glyphs, not
     the text frame; measuring the frame called every centred avatar initial
     cramped.
   - **TEXT-SPILLS**: content drawn outside a holder that does not clip. A
     holder that clips hides the overflow and one that scrolls lets the
     reader reach it, so neither is a finding.
   - **CLIPPED** now covers component instances and artwork, not only text.
     That is what found the Sifututor wordmark cut off on two payout slips.

   Every one of those started as a false-positive storm (155 findings, then
   115) and only became useful after the exemption was made exact. **A check
   that reports correct work is worse than no check**, because the real
   findings drown. Tighten the rule until every line it prints is true, then
   fix.

0c. **The rest of the check suite, added 16/09/2026.** Three more scripts run
   with the two above. All five are cheap, deterministic and reach things a
   reviewer looking at a PNG cannot.

   - **`links.figma.py`** lists every promise a screen makes: a row with a
     chevron, a button by its label, text in the link blue. It cannot tell you
     whether the destination exists, so the run walks the list. On its first
     use it found **two entire screens promised everywhere and drawn nowhere**:
     the commission sheet, linked from 12 English screens and 7 Malay ones and
     the most-linked destination in the file, and the read-back for a sent
     report, linked from 6. Both specs had been written and approved days
     earlier. Nothing else in the run would ever have noticed.
   - **`artwork.figma.py`** reads the image bytes rather than the node box.
     Every drawn object is a PNG with a transparent background, so the object
     is exactly where the alpha is; a long run of object along one edge means
     the crop went through it. It exists because Hafiz found a tray whose lid
     ran off the top of its own picture while the run was busy elsewhere. Every
     geometry check measures where a node **sits**; this fault lives in the
     pixels and nothing could see it.
   - **`dates.figma.py`** checks every weekday written beside a date, in both
     languages.

   Two exemptions `artwork.figma.py` needed on its first run, and the shape of
   every exemption worth writing: a **photograph** fills its box on purpose, so
   every edge is ink; a **wordmark** starts at its first letter. Without those
   two, 9 of 13 findings were correct work. It printed 13, then 4, and 2 of the
   4 were real.

0d. **A screen's name is not evidence.** `39 About you, answering out loud`
   showed a typed answer and an on-screen keyboard. It had been named that for
   days, so every pass over the list read the name, believed it, and moved on.
   The gap it hid was the whole speaking route, which is the route that reaches
   the 79% of active tutors who have never written anything about themselves.

   The check is mechanical: **the name claims a state; the export has to show
   that state.** Any screen whose name says a thing is happening gets looked
   at, not counted.

0e. **A recorded replacement is not an applied one.** `asset-generation.md`
   recorded on 15/09 that the smiling coins were superseded by plain ones.
   On 16/09 the smiling coins were still on four screens, one of them the RM50
   referral reward. A spec that says "superseded" is enforcing nothing. Anything
   a spec retires goes on the banned list the pre-flight already reads for
   retired strings, assets included.

0b. **`malay-check.py` runs in the same breath.** It pairs every Malay screen
   with its English version and reports three things as arithmetic: a string that
   is identical on both screens and is not stored content, a screen holding a
   different number of strings than its reviewer, and a screen a whole card taller
   or shorter. Run it with `/usr/bin/python3 design/scripts/malay-check.py`
   (no arguments checks every flow page).

   The pairing is **declared** in `design/research/malay-pairs.json`, not
   guessed, because most Malay screens are titled in Malay and no name match
   exists. Anything not declared is paired by score and printed as GUESS so it
   gets eyes on it. `design/research/stored-content.json` holds what the app
   renders as stored in both languages, each entry with its reason; subject
   names, level qualification names, the parent's note and a staff-written
   news headline are all correct when identical, and a check that reports
   them is reading `copy-glossary.md` wrong.

   It exists because the same failure happened in four separate rounds: a
   sweep lands on the English screens, the Malay version does not get it, and
   nobody sees it until two screens are read side by side. On its first run it
   found eleven Malay screens holding less than their reviewer, including a Report
   sent screen still drawn to a design replaced a day earlier, a student list
   missing its progress line on all five rows, and a Help screen still carrying
   the block `asking-staff.md` deleted on 15/09. It also found the reverse:
   the **English** Notifications screens showed the word "On" where every other
   row on the same screen showed a switch, and the Malay screen was the one
   that was right.

   **Codex cannot run this step.** `api.figma.com` does not resolve from the
   Codex sandbox. The measure lane is Claude-side only; give Codex the specs
   and the comments instead.

1. `autopilot-reviewer` on Claude and the Codex reviewer run **in parallel and
   blind**, on the same contact sheet and spec. Neither sees the other's
   findings. Neither sees the conversation.
   Both reviewers are told the geometry pass has already run, so they spend
   their round on judgement rather than pixels, and both read every comment
   the CTO has left on the file first, via
   `/usr/bin/python3 design/scripts/comments.figma.py --themes`. A complaint
   he has already made on another flow outranks anything new.

2. `autopilot-verifier` takes both lists and marks each finding CONFIRMED,
   WRONG or UNCHECKABLE, and reports DRIFT between the spec and the screens.
3. The chat fixes every CONFIRMED and every DRIFT. It decides on
   UNCHECKABLE ones and writes the reason. It ignores WRONG ones and logs
   them.
4. Re-export, re-shoot, next round.

Stop when both reviewers return nothing, or at five rounds. Anything still open
at five goes into the decision log as an open question with what each reviewer
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
what hangs on it. The screens affected are named so he can see the blast
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

## One question list, added 15/09/2026

Hafiz, 15/09/2026: "If we go through all the question, why we keep repeating
this? I'm so confused."

He was right and the cause was mechanical. Four spec files each kept their
own "What still needs Hafiz" list. When he answered, the answer was written
into the same file as a "Decided" note and the question was left standing.
By 15/09 those lists held 25 items of which 22 were already answered, so
every read of them looked like a mountain of open work and settled things
came back round.

Two rules now:

1. **`design/OPEN-QUESTIONS.md` is the only question list.** A spec may not
   keep its own. When a question is answered it moves out of that file and
   into the owning spec's Decided section in the same edit. Never both.
2. **Do not interleave asking and drawing.** The other half of the same
   complaint. On 15/09 a hero question was asked, four options drawn, one
   picked, redrawn, then a badge question, redrawn, then an asset question,
   regenerated. Each answer invalidated work that had already been made.
   Questions that touch many screens are answered before anything is drawn;
   the drawing pass then runs uninterrupted.

Order the list by how many screens the answer touches, not by which flow it
came from. A header question that changes eight screens is asked before a
toggle colour that changes one.

## The run got cheaper, 15/09/2026

Hafiz: "make sure make it more efficient and usage saving no ned to have
many rounds if no need. Make sure efficient that previously. Analuze first."

**What the old run cost.** Per flow: 3 research agents, then up to 5 review
rounds, each round being 2 blind reviewers plus a verifier plus a re-export plus
a fresh contact sheet. Up to 18 agent calls and 5 full exports for one flow.

**Where the waste actually was.**

1. **Rounds 3, 4 and 5 almost always returned nothing.** The pre-flight
   script now catches what the reviewers used to catch, and it is free and
   deterministic. The rounds were paying agent tokens to re-confirm a
   passing script.
2. **`autopilot-data` re-read production for flows whose numbers were
   already in the spec.** Two of the three remaining flows already had their
   figures from earlier passes.
3. **Two reviewers on two models plus a verifier reading both**, to find the
   same fault twice and then adjudicate between two agents that agreed.
4. **Per-screen screenshots** instead of one contact sheet.
5. **Interleaved questions**, which invalidated drawn work. Already fixed by
   the one-question-list rule; the cost was real before that.

**The shape now.**

| Step | Then | Now |
|---|---|---|
| Research | 3 agents per flow | 3 agents for **all** remaining flows, one per lens |
| Questions | asked per flow, mid-draw | one batch before any drawing, using the ask tool |
| Drawing | flow by flow, export each | all flows uninterrupted, one contact sheet at the end |
| Pre-flight | per page, per round | per page, once, before the review |
| Review | up to 5 rounds, 2 reviewers + verifier each | **1 round**, one reviewer and one verifier, in parallel across every flow. A second round only if round one confirms a real fault |
| Copy audit | per flow | once, across everything, at the end |

For the last three flows that is about 7 agent calls and 1 export, against
about 54 calls and 15 exports under the old shape.

**What did not change, because it is what catches things.** The pre-flight
still runs on every page and the report must be empty. The visual check by
eye still happens; a screen count is not evidence. Every number on a screen
still has to trace to production or a spec.

**One thing the cheaper run made obvious.** Subagents cannot reach Figma or
Mobbin. The reference agent said so honestly and flagged what it could not
verify rather than filling the gap with plausible detail. Those flagged gaps
were then closed from the main session in two searches. **A research agent
that reports its own blind spots is worth more than one that does not**, and
the prompt should ask for that explicitly.


## Asking him, rewritten 16/09/2026

He said: "why dont we just go one by one use ask tools". Then thirteen Malay
strings went to him one at a time, and he answered all thirteen and redirected
three of them. The same thirteen had been sitting in a file he was asked to
read, and that file got nowhere.

**The shape that works.** One question per message, through the ask tool, and
every question carries:

1. **Where the reader meets it.** Not the screen number. "On the calendar, a
   class that is booked and coming up shows a pill."
2. **What is drawn now, marked as the recommendation**, with the reason it was
   drawn that way.
3. **Two real alternatives**, each with what it costs. Not a straw man. Two of
   the three he picked on 16/09 were alternatives, which only happens if the
   alternatives are genuine.
4. **The objection to my own answer**, when there is one. He picked
   `Belum lengkap` over the drawn `Belum` precisely because the drawback was
   stated.

**Check the answer against the screen before applying it.** He chose
`Hubungan kecemasan` for a sub-line that sits directly under a row titled
`Hubungan kecemasan`. Applying it would have printed the same words twice. The
run reverted it, told him in one sentence, and offered to apply it anyway. An
answer is a decision about intent; whether it fits is still the run's job.

**When he answers with a principle, the fix is structural.** Twice on
16/09:

- "the app is free to download for all, for first time user we need them to
  login > register" and then "like how normal app does!" That was not a copy
  note. An unrecognised number had been drawn as an **error screen** with two
  ways out that both assumed an existing account, so a person who had never
  taught with us was stuck. The fix was to delete the screen, not reword it.
- "package is essitially a predefined class frequency and session duration in
  multi cycle." That settled a package size, which settled the rates, which
  changed a figure on eleven screens.

A one-line answer that restates how the world works is a redirect. Stop and
re-derive, rather than patching the thing that was asked about.

## A word swap never touches an identifier, 16/09/2026

Renaming one invented word across 45 files also rewrote `twins.figma.py` inside
three spec files as `Malay versions.figma.py`, and `twin-pairs.json` as
`Malay version-pairs.json`. Neither file exists under those names, so three
specs pointed at nothing.

A rename sweep skips: anything in backticks, anything with a file extension,
any path, any token name, any variable. Rename the prose; rename the files
separately and deliberately.
