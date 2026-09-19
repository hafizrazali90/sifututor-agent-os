# UI/UX autopilot: decisions taken with Hafiz

Live record. Every decision here was made by Hafiz in chat, dated.

## 14/09/2026

| # | Decision | His words |
|---|---|---|
| 1 | Full autopilot. Agents decide, including product and money rules, drawing on the specs and production data. Nothing stops to ask him mid-run. | "full autopilot, because i will review everyting every decision later once complete" |
| 2 | The reviewers are not a gate. The chat and the agents work together; no agent approves or blocks. He reviews when the work is done. | "they should be working with each other, the chat and the agent. I will review when the work is done and ready for review." |
| 3 | One reviewer per model, all available LLMs. Today that is Codex and Claude. Kilo (GLM 5.3) joins when its metered Z.AI key exists. | "reviewer using all available llm, for now we have kilo (glm5.3), claude and codex" + "Start with two reviewers" |
| 4 | Review pack per flow: one contact sheet of every screen, plus a decision log. Written to be read by him, not by an engineer. | "follow rec, but make sure its easy tounderstand" |
| 5 | Review depth: keep going until every reviewer is clean, maximum five rounds. Anything unresolved at five becomes an open question in the log, with what each reviewer said. | chose the five-round option |
| 6 | Scope is NOT yet decided. Before any autopilot run, research and analyse the full flow inventory of the app and design the flow list with him. | "this is another task to discuss on full implementation (research, analyze and help me to design the full available flow first. We discuss this next before the work start." |

## Open

- Which flows the autopilot designs, and in what order. Waiting on the inventory.
- Kilo reviewer, waiting on `ZAI_API_KEY` in `~/.config/sifututor/zai.env`.

## 14/09/2026, later

| # | Decision | His words |
|---|---|---|
| 7 | The agents must be grounded in everything the workspace already holds, not just the design specs: Koda memory, the local memory files, `working-with-hafiz.md`, the mission ledgers, and the decision docs under `Sifututor`. | "also use all info u cna to create this agent for our agentic agent os such as memory, and decision doc u found under sifututor and so on." |

## Parallel flows, decided 14/09/2026

Hafiz asked whether several flows can run at once. Yes, two at a time, each
with its own team and its own Figma page; the one desktop connection means
drawing steps interleave while research and reviews run fully in parallel.
Not seven at once: the costliest faults so far were rules fixed on one flow
and missed on its sibling, and that check only holds with two side by side.
Opening the app runs last because Home is built from the other flows' cards.

Order agreed: Getting work with Settings and account; Reporting on a student
with Getting told; Getting in with Bringing another tutor; Opening the app
alone; then the cross-flow loading, empty and failure pass. Each flow's pack
goes to him the moment it closes.

A runner that is itself a subagent launches its lanes, reviewers and verifier
blocking (`run_in_background: false`), because a subagent's background
children notify the main session, not the subagent; the first parallel
runner stalled waiting for a notice that could never reach it (14/09/2026).

## Missing backend, decided 14/09/2026

The runs so far treated a dead column as a reason not to draw (Being worth
picking decision 8). Hafiz reversed that on the intro video: the redesign
exists to make the app better, and a missing route or column is a ticket
to build. From now on a feature that serves the tutor is drawn and its
table row names the backend work; the system section still records what
exists today, and copy never promises what is not built (B21). Rule E9.

## Closing passes, decided 14/09/2026

Hafiz: once every flow is drawn, three passes run before build, in this
order.

1. **Consistency.** One name per thing, one component per job, every rule
   applied on every sibling (the fold, the checklist tones, the pay line,
   the glossary), across all flow pages. The pre-flight runs on every page;
   the reviewers review the whole app as one sheet.
2. **Interaction and motion, like Me+.** A motion spec per pattern (sheet,
   coloured page, checklist, card open, toast, the Chosen celebration, the
   request stack if adopted) drawn from Me+'s measured behaviour, and a
   short list of the screens that adopt an interactive concept. Not every
   screen; the ones where a gesture or a transition carries meaning.
3. **Copy audit, the whole app, last.** Hafiz, 14/09/2026: "make sure to
   audit all copy with the writer agent once all finish". So the writer
   (`autopilot-copy`) runs once more at the end across EVERY page in the
   library, both languages, after the last flow and after every addendum,
   even pages it has already audited, because late decisions change strings
   on pages that were signed off earlier. It returns one copy table per
   page, and the run is not finished until every table is applied or its
   rows are answered. Per-flow audits during the run do not replace it.

   Audited so far, and needing the final pass again: Becoming verified,
   Being worth picking, Getting work. Never audited yet: Teaching a class,
   Getting paid, Asking staff, Settings and account, and every addendum.
4. **Decision audit.** Every decision he made in the walk-throughs traced
   to the screens it belongs on, applied there properly, and nowhere it does
   not belong. His words: never overdo. A rule sprinkled everywhere is as
   wrong as a rule missed.

## What we refuse to build, 14/09/2026

From the engagement reference pass, with sources: no points or badges
without cash meaning, which is the exact thing Uber drivers resented in the
2017 New York Times investigation; no leaderboard against other tutors,
given Human Rights Watch's and the FTC's findings on opaque gig scoring; no
confetti on money moving; no streak that punishes a week a tutor did not
control; no fake urgency. A tutor is earning a living, not playing.

## 16/09/2026

| # | Decision | His words |
|---|---|---|
| 8 | **Never invent a word.** A word goes in a reply only if it is on a screen or in the code, or he has used it himself, or a stranger would understand it with no explanation. 45 files were renamed the same day; `board` became `screen` on his instruction | "Why u use the word twin so fucking confusing your choice of word is so bad!" and "Rename alao audit your claude and agent os related to how u talk to me so that u improve." and "Yes use screen." |
| 9 | **Stop asking permission to continue.** Work through to the end and bring him the result | "Why not u just proceed until all is done? Why need my permission everytime?" |
| 10 | **Questions go one at a time through the ask tool**, each with what is drawn now as the recommendation, two real alternatives, and the reason for each. A file of questions to read does not work; the same thirteen items went over one at a time and all thirteen came back | "why dont we just go one by one use ask tools" and, earlier, "lets go one by one witu your suggestion and justification" |
| 11 | **The grey surface stays at 1.12:1** (`#E9EAEF` on `#FAF9FF`). It was 1.05:1, which is below the point an edge resolves, and that is what made it tiring to read | "the top banner color is too subtle vs the background. This create eye strain to the reader" and then "Keep it at 1.12" |
| 12 | **Four empty screens keep four different objects**, not one repeated, so screens that appear one tap apart cannot be mistaken for each other | picked "Keep all four" |
| 13 | **A package is a predefined class frequency and session duration across several cycles.** That settled the Nakngaji package size at 24 sessions, which is exactly three cycles at 8 classes a month, which settled every rate on the commission sheet | "package is essitially a predefined class frequency and session duration in multi cycle." |
| 14 | **Anyone can download the app; a first-time user logs in and then registers.** An unrecognised number is a new tutor, not an error. The error screen was deleted | "the app is free to download for all, for first time user we need them to login > register." and "like how normal app does!" |
| 15 | **A button names what the tutor gets, not the form they are about to fill.** `Start with your details` became `Get verified to start teaching`, in both languages | "why not be direct like Sahkan profile anda untuk mula mengajar. something like this?" |
| 16 | **The thirteen flagged Malay strings are locked.** Nine as drawn, four changed. `terdahulu` over `dulu`, `Belum lengkap` over `Belum`, `IC` over `kad pengenalan`, and a shorter calendar banner line | answered one at a time through the ask tool |
| 17 | **Build the app itself is not part of this run** without his word. The redesign touches nearly every screen in the live tutor app, so it does not land in one release | raised in the finishing plan, 16/09/2026 |

## Still open

Nothing. `design/OPEN-QUESTIONS.md` is empty for the first time since it was
created on 15/09/2026.
