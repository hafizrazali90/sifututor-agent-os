# UI/UX autopilot: decisions taken with Hafiz

Live record. Every decision here was made by Hafiz in chat, dated.

## 14/09/2026

| # | Decision | His words |
|---|---|---|
| 1 | Full autopilot. Agents decide, including product and money rules, drawing on the specs and production data. Nothing stops to ask him mid-run. | "full autopilot, because i will review everyting every decision later once complete" |
| 2 | The twins are not a gate. The chat and the agents work together; no agent approves or blocks. He reviews when the work is done. | "they should be working with each other, the chat and the agent. I will review when the work is done and ready for review." |
| 3 | One twin per model, all available LLMs. Today that is Codex and Claude. Kilo (GLM 5.3) joins when its metered Z.AI key exists. | "twin using all available llm, for now we have kilo (glm5.3), claude and codex" + "Start with two twins" |
| 4 | Review pack per flow: one contact sheet of every board, plus a decision log. Written to be read by him, not by an engineer. | "follow rec, but make sure its easy tounderstand" |
| 5 | Review depth: keep going until every twin is clean, maximum five rounds. Anything unresolved at five becomes an open question in the log, with what each twin said. | chose the five-round option |
| 6 | Scope is NOT yet decided. Before any autopilot run, research and analyse the full flow inventory of the app and design the flow list with him. | "this is another task to discuss on full implementation (research, analyze and help me to design the full available flow first. We discuss this next before the work start." |

## Open

- Which flows the autopilot designs, and in what order. Waiting on the inventory.
- Kilo twin, waiting on `ZAI_API_KEY` in `~/.config/sifututor/zai.env`.

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

A runner that is itself a subagent launches its lanes, twins and verifier
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
   the twins review the whole app as one sheet.
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
   to the boards it belongs on, applied there properly, and nowhere it does
   not belong. His words: never overdo. A rule sprinkled everywhere is as
   wrong as a rule missed.

## What we refuse to build, 14/09/2026

From the engagement reference pass, with sources: no points or badges
without cash meaning, which is the exact thing Uber drivers resented in the
2017 New York Times investigation; no leaderboard against other tutors,
given Human Rights Watch's and the FTC's findings on opaque gig scoring; no
confetti on money moving; no streak that punishes a week a tutor did not
control; no fake urgency. A tutor is earning a living, not playing.
