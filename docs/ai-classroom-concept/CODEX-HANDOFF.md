# Claude To Codex Handoff — AI Classroom / Kota Buku Proposal

Written 2026-09-06 by Claude (Fable 5.1) at the end of a single long research session with Hafiz. Follows `docs/agent-playbooks/handoff.md` and `docs/agent-playbooks/templates/claude-to-codex.md`. Read this file first, then the four companion documents (including the data spec) in the order given in "Read first."

---

## Project

`cross-project` — a new product concept with no home repo yet. It draws on engineering *patterns* from `kelas/` and `lls/` but is not an extension of either. Mission Ledger ID: **AI-CLASSROOM-001** in `docs/agent-playbooks/mission-ledger/cross-project.md`.

## Active Task

**LATEST OVERRIDE, 2026-09-07 (deck handoff, written by Claude):** Hafiz handed the Kota Buku deck to Codex to continue. Read the last §13 entry, "Claude to Codex: complete deck handoff", first: it holds every decision (including D11 on tiers and the "student" and real-names copy rules), every produced file, the rebuild pipeline in `production/visual-samples/claude/build/`, the review outcomes and the ordered next actions. The deck is complete at fifteen slides with all check suites clean; Hafiz is sharing `production/visual-samples/claude/share/` with his partner. "Do not edit deck files" below is now historical: Codex owns the deck.

**Compilation entry point, 2026-09-07:** Hafiz requested all documents compiled. Open `START-HERE.html` (governed index `START-HERE.md`): current external/internal v0.2 editions, Claude's full deck, source specs, planning/review records, restricted partner references and historical artifacts. Searchable catalogue covers62 local reader-document files including formats/history, not62 separate deliverables. No files moved or merged; no ZIP/publication. Index QA and inventory scope recorded in latest §13 entry.

**Latest refinement, 2026-09-07 (REC-09):** Hafiz approved strengthening the teaching-assistant story beyond generation. Both external/internal masters and EN/BM HTML/PDF/DOCX are v0.2 local reading drafts. External §§1/5 and internal §§1/5/12 foreground understand → support → follow up for pupils/groups/class, with teacher-selected personal attention. Release tiers unchanged. Targeted independent review: zero Blocking/Material/Minor; regenerated output checks pass. See §13 latest entry and both acceptance records. Next: owner reading feedback on chapter 5, not new scope or publication.

**Latest checkpoint, internal sourcebook drafted and checked (2026-09-07):** Hafiz's “Yes” approved the six-part internal walkthrough (REC-08), retaining sixteen chapters and seven appendices. Read `production/internal-team-sourcebook-acceptance.md`: complete EN/BM master, offline switcher, two 26-page PDFs and editable Word editions. Independent content correction review confirms zero remaining Blocking/Material/Minor findings; local content/browser checks passed, PDF contact sheets inspected. Exact Word-app appearance remains unverified. Both external and internal documents now await owner reading feedback, not another structure approval. No final-copy/circulation approval inferred; all protected-file and fixed-decision boundaries remain.

**Current work, reconciled document blueprints:** Hafiz prefers Claude's design and is refining the deck with Claude; Codex does not edit it. Hafiz approved both interest-building and later commercial support, the proposed Kota Buku programme-partner role, benefit-first narrative, preserved full vision/readiness and proposed support split. These supplement D1-D10/C4 without changing them. Read `production/document-reconciliation-and-coverage.md` for REC-01 to REC-06 and `production/external-kota-buku-blueprint.md` / `production/internal-team-sourcebook-blueprint.md` for the chapter structures awaiting Hafiz's review before full prose. Commercial figures remain partner-owned; counterpart agreement, capacity and contract details remain unverified. The downloaded framework is reference methodology, not mandatory seven-artifact scope. Earlier sample/deck next actions below are historical.

**Historical visual checkpoint:** Hafiz rejected the crowded one-slide sample and approved continuing with Apple-inspired multi-slide pacing. The review target then was `production/visual-samples/codex/sequence.html`, three slides with English/BM switcher. He subsequently preferred Claude's direction. Both Codex samples are design history, not the current review target.

**Historical frame correction, 2026-09-07:** Hafiz rejected the thick dark device border. The sample iteration replaced it with a fine light outline and restrained shadow; no heavy hardware bezel. Claude's common brief carries the same instruction. Language switching remains unchanged.

**Historical language correction, still-binding preference, 2026-09-07:** Hafiz rejected simultaneous BM/English on one slide. `production/visual-samples/codex/sample.html` was updated with an English / BM switcher for the entire slide and concept UI. Source Markdown translation pairs are not a layout instruction. Claude's comparison brief has the same correction.

**Historical single-sample checkpoint, 2026-09-07:** Hafiz approved producing one finished lesson-plan/exercise visual sample using the Kelasapp-inspired direction, and requested an independent Claude Fable 5.1 version of the same assignment. See `production/visual-sample-brief.md` and `production/visual-samples/codex/README.md`. The Codex sample was locally rendered and checked; the Fable model probe failed and no fallback was substituted. Later Hafiz worked directly with Claude and selected its direction; do not restart the probe or sample task.

- Task id: AI-CLASSROOM-001 (Mission Ledger; no `.claude/tasks/active.json` — this is not a code project yet)
- Route: local bilingual document production, authorised by Hafiz after the completed research/specification review. No software build or publication.
- Historical reading-draft step (2026-09-07): `production/deck-reading-draft.md` records the twelve-beat bilingual story including parent and pupil sections. Its complete-experience/plain-language principles remain relevant; subsequent blueprint work and Claude deck ownership are in the current Active Task above. D1-D10 and blended C4 remain fixed.
- Task file: none (see Mission Ledger entry)

## Goal

Produce a credible, evidence-backed proposal to Perbadanan Kota Buku positioning the Kota Buku app, delivered by Sifututor, powered by Learnest Lab, as the complete software solution (device + application + content) for the "Kota Buku Application" slot in redONE Mobile's Teacher Digital Empowerment Programme — an iPad + 300GB data + insurance + app bundle for up to 182,757 KPM teachers, pending MCMC USP Fund approval.

---

## 1. What we are trying to do, and why (plain language)

Hafiz (CTO, Sifututor) received an **inbound enquiry from Perbadanan Kota Buku** (Malaysia's national book / digital-textbook corporation) asking Sifututor to propose what software should be installed on the iPads in redONE Mobile's proposed national teacher-device programme. Kota Buku's own slot in that programme is currently just an e-book subscription with commercial terms now owned by the partner pack (D10). Hafiz's framing, verbatim in spirit: *"We have the device + application + content for the teacher to actually use the device, rather than supply the device only."* Kota Buku has no spec and no idea what can be built — **"we are the expert here."**

The product vision (Hafiz's original six pillars) is a **teacher-centric** iPad app for Standard 1 to Form 5:
1. Collect student data throughout the whole learning journey
2. Help the teacher conduct class and activities
3. Produce learning material for the whole class or per student
4. Act as the teacher's AI assistant — personalise learning, track progress/weakness/strength, recommend plans — so the teacher focuses on teaching
5. Adjacent features that make teaching efficient
6. Parent and student logins to view what the data supports

The session's job was **research and documentation only** — no build, no outreach — so that (a) the proposal can be drafted from evidence, and (b) nothing has to be re-researched later.

## 2. Hafiz's inputs and decisions — the record

Every choice below was Hafiz's, given in answer to explicit questions. Do not re-litigate these. The original seven decisions and D8–D10 are settled in §7. Hafiz subsequently settled C4 as a mix of workload reduction and AI-classroom capability (see §7 C4); partner alignment is not assumed.

| # | Question asked | Hafiz's answer | Status |
|---|---|---|---|
| 1 | How does this relate to Kelasapp-for-School / existing Sifututor work? | **Concept/pitch only for now** — not yet tied to any existing product | Decided |
| 2 | Who is the buyer/deployment target? | **Government national schools (MOE/KPM)** and **private/international schools**. Not madrasah/tahfiz, not tuition centres. | Decided |
| 3 | Is "Standard 1 to Form 5" the real scope? | **Yes, full Std 1 to Form 5** | Decided |
| 4 | Research focus — Malaysia-first vs global-first? | **Both, equal depth** ("1 and 2") | Decided |
| 5 | How are we reaching Kota Buku? | **They reached us** — inbound enquiry to propose the solution for inclusion on the device | Fact |
| 6 | Deal structure to pitch? | **DECIDED 2026-09-06: co-branded white-label** — Kota Buku's name on the app, **delivered by Sifututor, powered by Learnest Lab** (D9 refines the original product-brand wording; Learnest Lab remains the product technology). We own the platform IP and codebase, act as PDPA processor, no exclusivity beyond the KPM programme, and keep the right to sell the Learnest-Lab-branded version to private/international schools. | Decided |
| 7 | What can we credibly say we already have? | "Kelasapp is a real foundation to extend" — **later corrected by a codebase audit** (see §4): neither Kelasapp nor LLS is a foundation; only engineering patterns reuse. Hafiz has seen this correction. | Corrected |
| 8 | Target platform? | **Native iPad / iPadOS** | Decided |
| 9 | Scope of the "how to build" research? | **Everything**: technical architecture, enterprise deployment at scale, AI infrastructure and cost, case studies of similar national programmes, *and* what features the app should have — "everything about the system/app that should help during our dev later once accepted or for proposal building later" | Decided |
| 10 | What did Kota Buku actually ask for? | **Nothing specific** — "they have no idea what to build, what can be built, we are the expert here" | Fact |
| 11 | Also check the LMS? | **Yes** — LLS (`lls/`, live at lms-sifu.tutorla.tech) was audited | Done |
| 12 | Benchmark features against other countries' and private systems? | **Yes** — done, see feature spec §11 | Done |
| 13 | How should data collection and AI advice actually work? | Asked for the "modus operandi" — see feature spec §9 | Done |
| 14 | Adversarial review + more research where weak + Codex handoff? | **Yes** — this document is the result | Done |
| 15 | *(Requirement added after the first six decisions; the seventh decision settled its framing)* Collect every data point from students and teachers throughout the journey so the government can later use it for the country and for education | **STATED REQUIREMENT (Hafiz, 2026-09-06)**: comprehensive, structured capture of learning activity — not just attendance and scores — designed from day one as a **government-owned national education data asset** (KPM/Kota Buku = data controller and owner; Learnest Lab = PDPA processor; data resident in Malaysia). Must ship with a governance layer (stated purposes, anonymised/aggregated views for policy use, controller-gated individual-level access, audit logs) — the Korea NEIS precedent shows comprehensive capture without governance triggers political backlash. Precedent to follow: DIKSHA/Sunbird's published telemetry spec and Obsrv open-data layer (blueprint §2.1). Pitch framing DECIDED: build fully, present as "reporting and analytics" (see §7 item 7). Specified in `data-collection-spec.md`. | Requirement — specified |

| 16 | Partner’s SEPADU pack and reconciliation, 2026-09-06 | **D8: “Teachers only.” D9: “Sifututor is the main (contracting, fronting) entity”; “Learnest Lab must remain visible”. D10: “The partner’s pack owns the numbers.”** Do not mix commercial figures into these documents; both partner files remain read-only. C4 was open at this point; subsequently settled in §7 C4. [Review §2/§9](partner/SEPADU-review.md) | Decided; C4 subsequently settled below |

Working-style instructions Hafiz gave during the session that Codex should keep honouring: document everything so nothing is re-researched; check the whole conversation for misses before claiming done ("I don't want to tell you twice"); short scannable replies.

## 3. What Claude already did

**Files created** (all under `docs/ai-classroom-concept/`, all **local-only** — see §6):
- `research-findings.md` — Malaysia market/policy/competitive research + global pedagogy evidence. 10 sections + master gap list.
- `technical-build-blueprint.md` — Kota Buku's current tech, offline-first patterns, on-device vs cloud AI, content data modeling, iPadOS specifics, deployment at 182k scale, app distribution constraints, AI cost modeling, RAG architecture, non-AI infra cost, national case studies, synthesis, gaps.
- `product-feature-spec.md` — build status vs Kelasapp/LLS, MVP philosophy, six pillars with Core/Fast-follow/Later tiers, data-collection and AI-advice mechanics (§9), Kota Buku content integration, competitive benchmark with sources (§11), MVP list (§12), what not to build first (§13).
- `data-collection-spec.md` — **added last, after the seven decisions**: the Std 1–Form 5 data timeline, what every KPM system already records (read, never re-key), what no system captures (the app's unique layer), the field-level collection spec by moment and role, the bounded "do not collect" list, the governance layer (KPM controller / Learnest Lab processor / Malaysia residency / access tiers / consent channel / audit / two firewalls), KPM interface sequencing, what it gives KPM (for conversation only), and a verification table. Built from 8 research agents on the Malaysian school system and 5 national data-governance models.
- `sources/` — primary documents recovered from the research session so they outlive the session scratchpad: `rpm.txt` (full extracted text of the 375-page RPM 2026-2035), `pajsk_guideline.pdf` (MOE PAJSK guideline), `pekeliling_spm_2627.pdf` (KPT/UPU 2026/27 admissions circular — the source of the 90/10 merit formula), `kpm-panduan-pentadbiran-pentaksiran-psikometrik.pdf`, `diksha-technote.pdf` + `technote_flow.txt` (DIKSHA/Sunbird v5.0A technote and its text). Quote from these, not from memory.
- `CODEX-HANDOFF.md` — this file.

**Reading versions (private Claude artifacts, plain-language, published 06/09/2026; the markdown files remain the sourced reference):**
- Market and Policy Findings — https://claude.ai/code/artifact/4ceeee25-bd7e-4aed-af74-53e0741bc5aa
- Build Blueprint — https://claude.ai/code/artifact/dd28cfa8-f47b-44b4-92dc-6605d0128d78
- Feature Specification — https://claude.ai/code/artifact/aad9ba08-e1db-41b6-89f4-80bf1c9b7ef9
- Data Collection Spec — https://claude.ai/code/artifact/6ed6d98e-c639-4b3b-b4fd-a10f58738164
- Codex Handoff — https://claude.ai/code/artifact/e73a202a-fcb1-4bfb-a91c-7cb88651f0a2

**Files modified (tracked):**
- `docs/agent-playbooks/mission-ledger/cross-project.md` — added mission `AI-CLASSROOM-001`. `python3 scripts/agent-checks/mission-ledger-check.py` → `ok (128 items)`.

**Research executed:** ~20 web-research agents across four waves (market/policy; technical build; feature benchmark; adversarial review + targeted verification), plus two codebase audits (`kelas/`, `lls/` + `lls-frontend/`). Source input read: `~/Downloads/Teacher-Digital-Empowerment-Programme.pptx` (redONE's USP Fund deck, 12 slides — all text extracted and summarised in the blueprint's header).

**Commands run:** file reads/greps of `kelas/` and `lls/`; `git status`/`check-ignore`; `mission-ledger-check.py`. No builds, no tests (not a code task), no commits, no pushes.

**Koda memories stored** (project tag `sifututor`; search `ai-classroom` or `kota-buku`):
- `mem_5d3b07184852` — market/policy research pointer + headline findings
- `mem_8f0201fd75af` — technical build research pointer + headline findings
- `mem_da43b33d5d8e` — Kelasapp/LLS codebase reuse audit (patterns, not foundation)
- `mem_d869a836a22a` — feature benchmark vs national/commercial/AI-native systems
- (a lessons memory from the adversarial review is stored alongside this handoff — search `adversarial review` under `sifututor`)

## 4. Adversarial review — what changed and why it matters

Three reviewers (one per doc) re-verified the load-bearing claims against fresh sources; five targeted follow-up agents then closed the gaps they found. Net result: **the facts mostly held; the overreach was in synthesis and tiering.** What changed:

**Claims corrected (were wrong or stale):**
- The PCG school-finance circular cited (SPK 8/2012) was **superseded in 2021** by SPK Bil. 1/2021. Figures appear to carry over; citation fixed; figures still secondary-sourced.
- The "64.1 hrs/week" teacher-workload statistic **traces to a 2006 one-district conference paper** (274 primary teachers, Kedah). Do not cite. TALIS 2013 is the citable alternative.
- Khanmigo's RCT effect is **0.06-0.08 SD/year measured**, not 0.14 (that was a hypothetical full-engagement figure).
- DELIMa 3.0 launched **21 July 2026**, not 20.
- "RPM 2026-2035" is the school sub-plan; the umbrella is **RPN 2026-2035**. Use the terms precisely in anything KPM-facing.
- Kelasapp `teachers.grade` is a quality rating, not a pay grade (pay is per-class rate).

**Claims narrowed (were overstated):**
- "No Malaysian edtech startup has won a KPM contract" → **"none has won KPM *software-procurement* or *DELIMa-vendor* status."** Pandai has an official Ministry of Digital/MDEC pilot partnership (Sarawak, Feb 2026 press release); Sasbadi holds KPM *textbook-print* contracts. Neither is the software route.
- The Malaysian RAG paper (arXiv 2508.04442) is **weaker than first cited**: no human validation, a circular "validity" metric (RAG checking RAG against the same source), grounding corpus = one chapter's teacher notes + a 1-page plan — **not DSKP, not a textbook**. It shows grounding matters for checkable-item generation; it does not validate the platform.
- "No platform combines our full scope" → **"none combines parent access + attendance + the full pillar set"** (SchoolAI has parent visibility).
- The original budget-fit conclusion was narrowed because token volumes were modeled, not telemetry. **D10 now supersedes that cost table and any slot-fit conclusion:** the partner owns commercial figures; actual usage, regional availability and all-in delivery costs remain unverified. No affordability is established, and the case cannot assume on-device AI savings.
- iPad qualification → **any M1+ iPad** qualifies for on-device AI (not only the M4 Air); Apple gates by chip, not a published RAM floor. Base A16 does not qualify for Apple Intelligence; this does not exclude local deterministic grading or compatible Vision/Core ML work (Codex correction, 2026-09-06; blueprint §3).

**New facts from verification:**
- **Historical model-retirement warning:** the first pass recorded a December 2026 shutdown for dated GPT-5 snapshots. Blueprint §9.2 retains the need to recheck official lifecycles; replacement price comparisons are no longer reproduced under D10. Rule retained: **use a replaceable capability tier, not a fixed model, in a multi-year commitment.**
- **Malay is absent from Apple's developer Vision OCR API** in every runtime dump found (present only in consumer Live Text). On-device BM handwriting OCR is contradicted by the best evidence; cloud OCR with Malay support is the realistic path, with a PDPA cross-border implication.
- **PDP child-consent verification amendments reported still in consultation as of the cited March 2026 commentary; later enactment not independently settled** (Public Consultation Paper No. 4/2025; Chambers, 10 Mar 2026). Not law.
- **Sarawak MDEC PoC and KPM's 27→260-school national pilot**: no official cross-reference either way — treat as two distinct, unreconciled initiatives. National school counts are inconsistent across reports; the ministerial Parliament reply (18 Dec 2025) is the authoritative set.

**Tiering changed in the feature spec (recommendations pending Hafiz):**
- **AI-drafted RPH (lesson-plan) generation: built day one, staged switch-on** (Hafiz's decision, §7 item 4 — supersedes the reviewer's "move to Fast-follow"). The reviewer's three concerns (no Kota Buku licence yet, RAG pipeline 100% new, MCQ evidence doesn't cover long-form plans) are answered by exposure, not by deferral: Level 1 (template + AI practice items) is general availability at launch; Level 2 (AI-written plan text) ships on the same backend as a guided beta for pilot teachers first, grounded on public DSKP until Kota Buku content arrives.
- **AI checkable-item (worksheet/quiz) generation stays Core** — the least-risky AI task, grounded in *public* DSKP documents (no licence needed), with a **teacher-validation pilot as a pre-launch requirement**.
- **Attendance = standalone register (Core); APDM sync = Fast-follow pending KPM** — no evidence any APDM integration path exists.
- **Handwritten fill-in-blank OCR grading → Fast-follow**, cloud-OCR path, pilot first. Bubble/tick MCQ capture by camera stays Core (proven practice).
- Feature spec §9 now marks inline which mechanics are MVP vs later; §11 gained a full source list (it previously had none).

## 5. Current state

- Branch: `main` (`ahead 2, behind 6` vs `origin/main` at session start — unrelated to this work)
- Active task next step: **independent review and improvement of the whole package (Hafiz's instruction, 06/09/2026): read everything, verify what can be verified, fix what is weak, report findings. Do NOT derive the next deliverable — no proposal outline, no drafting.**
- Known failures: none. No checks failed. Checks not run: `scripts/agent-checks/pre-commit-guard.sh` (no commit was requested); no test suites (not a code change).
- Uncommitted changes that are intentional: (1) the modified `docs/agent-playbooks/mission-ledger/cross-project.md` (tracked, commit-able, not committed); (2) the five `docs/ai-classroom-concept/*.md` files (including this handoff) (gitignored — see §6).
- Highest proven state: **changed locally**. Nothing committed or pushed; private reading artifacts were published as listed in §3, but no external stakeholder distribution is recorded.
- All research agents have returned. The DIKSHA/Sunbird deep-read (full 134-page technote) landed after the first draft of this handoff and is in `technical-build-blueprint.md` §2.1. **Nothing is in flight.**

## 6. Constraints

- **Critical lane:** none technically (no code, no production, no data). Commercially sensitive: this is a live inbound government-linked opportunity.
- **Human review required:** everything below before it leaves the building.
- **Do not do, under any circumstances, without Hafiz's explicit instruction:** contact Kota Buku, redONE Mobile, MCMC, KPM, Apple, or any school; start any build; commit or un-ignore the `docs/ai-classroom-concept/` files; send anything externally.
- **Files/paths not to touch:** `live/**`, `.workflow-rollout/**`; do not modify `kelas/` or `lls/` (they were read-only audited).
- **Repo convention to respect:** `.gitignore` has `docs/*` with allow-lists only for `docs/agent-playbooks/` and `docs/onboarding/`. Every prior research doc (KESUMA, hosting comparison, competitive gap analysis) is likewise local-only. The concept docs follow that convention. They are readable by Codex on this Mac; they will **not** travel via git to another machine. Hafiz decided (2026-09-06) they stay local-only — see §7 item 3.
- **Naming:** write `Sifututor` in prose; `SifuTutor` only where it is an existing literal identifier. Use `RPN` for the 2026-2035 umbrella plan and `RPM` for the school plan.
- **Evidence discipline the docs use — keep it:** every claim dated and sourced; anything unverified is flagged inline; synthesis sections must not drop hedges present in body sections (that was the single most common review finding).

## 7. The ten decisions — ALL DECIDED by Hafiz on 2026-09-06 (Codex: apply, do not reopen)

1. ~~Deal structure~~ **DECIDED (Hafiz, 2026-09-06): co-branded Kota Buku app, delivered by Sifututor, powered by Learnest Lab; exact legal entity name to be confirmed by Hafiz.** Rationale accepted: Kota Buku already white-labels (its reader is a rebadged eSentral instance), Kota Buku must hold the Apple Business/School Manager account regardless, and the inbound came because they own the slot. Contract non-negotiables to carry into the proposal: platform IP and code owned by us; PDPA processor/controller split explicit; no exclusivity beyond the KPM programme; right to sell the Learnest-Lab-branded version to private/international schools. **Learnest Lab remains visible as the product technology; Sifututor is the contracting/fronting face (D9).**
2. ~~Device-model stance~~ **DECIDED (Hafiz, 2026-09-06): recommended + minimum spec, delta shown.** The proposal states **"M1 or later" as the recommended spec** with concrete reasons (on-device MCQ grading, printed-text OCR, text simplification; RAM headroom for the offline content cache; longer software support life), states the **base A16 as the minimum the app fully supports** (cloud-first architecture works on both), and shows the per-unit cost delta. The hardware decision stays with redONE/Kota Buku. This is the transparent-trade-off posture the Indonesia case study argues for; do not bury the gap and do not dictate their line item.
3. ~~Un-ignore the concept docs?~~ **DECIDED (Hafiz, 2026-09-06): keep local-only**, matching the KESUMA/competitive-gap research convention. **Consequence for Codex:** run on this Mac, or copy `docs/ai-classroom-concept/` by hand to wherever you work — a fresh clone or a cloud session will not have these files. Do not commit them.
4. ~~Accept the re-tiering?~~ **DECIDED (Hafiz, 2026-09-06): one backend, staged switch-on ("option D").** Both modes are built on the same grounding pipeline from day one. At launch: **Level 1** (form pre-filled from the DSKP taxonomy + AI-generated practice items) for every teacher. **Level 2** (AI-drafted full RPH text) is live on the same backend but exposed as a **guided beta to pilot teachers**, quality measured, then general release. Grounding starts on the public DSKP documents and improves as Kota Buku textbook content arrives — so no launch dependency on their licence. **Pitch wording:** "AI-assisted lesson planning for all teachers from day one; full AI-drafted plans rolling out through a teacher pilot." Hafiz's framing that resolved it: it was never two backends, only a question of what is switched on and promised at launch.
5. ~~Commercial terms~~ **DECIDED (Hafiz, 2026-09-06; refined by D10): commercial figures live in the partner’s SEPADU pack (partner owns the numbers); our documents stay figure-free.** The build/setup plus per-teacher run-fee structure remains the technical context, not an independently priced offer. The original disclosure timing (after the first Kota Buku meeting) is not changed by this reconciliation. See [partner pack](partner/SEPADU-v1.0-Founder-Briefing.md) and its [read-only review](partner/SEPADU-review.md) for commercial assumptions and unresolved corrections. No affordability, margin or acceptance of the pack’s estimates is established here. Sifututor fronts/contracts; Hafiz must confirm the exact legal entity. Blueprint §§9/11 retain validation inputs, not competing cost tables.

6. ~~The Korea lesson~~ **DECIDED (Hafiz, 2026-09-06): let Kota Buku / KPM set the mandatory-vs-optional framing.** The proposal presents AI capability neutrally and does not take a position on whether schools must adopt it. What the proposal *does* carry: the staged rollout from decision 4 (Level 1 for all, Level 2 via teacher pilot) as the delivery mechanism, and per-school/per-teacher switchability as a technical capability. The Korea 2025 rollback and KPM's own 27→260→2030 phasing stay in the evidence base as talking points if they ask — not as a recommendation we volunteer. (Claude's recommendation was "opt-in and phased, never mandatory"; overridden.)

7. **National education data asset — how to pitch it. DECIDED (Hafiz, 2026-09-06): build it fully, pitch it quietly.** The app captures every student and teacher data point across the journey and ships with the governance layer (controller = KPM/Kota Buku, processor = Learnest Lab, Malaysia-resident, stated purposes, anonymised/aggregated policy views, controller-gated individual access, audit logs). The *proposal document* presents this as **"reporting and analytics"** for teachers and schools — not as a headline "national data asset" pillar. The government-data-asset value is for Hafiz to raise in conversation with Kota Buku/KPM, not for the written pitch. (Claude recommended a headline seventh pillar; overridden.) **Follow-up research completed** on how Malaysian schooling works end to end; the result is `docs/ai-classroom-concept/data-collection-spec.md`. Headline facts Codex must carry: no KPM system exposes an API (integration = data-sharing agreement + export formats first); KPM itself built Matriks Pembelajaran because UASA gave it no comparable mastery data — the app's continuous per-standard data is that gap; KPM's SiPKPM already scores dropout risk on income, marital status and disability, so the app must *not* re-collect those (inBloom lesson) and should instead supply learning-engagement signals; the durable governance pattern is Estonia's (vendor captures, state owns the register).

8. **Devices — DECIDED (Hafiz, 2026-09-06): “Teachers only.”** No pupil devices are supplied. This does not cancel the existing parent/pupil web surface on their own devices (product §8).
9. **Contracting and brand — DECIDED (Hafiz, 2026-09-06): “Sifututor is the main (contracting, fronting) entity”; “Learnest Lab must remain visible”.** Co-branded Kota Buku app, delivered by Sifututor, powered by Learnest Lab. Exact legal name/registration and inter-entity IP arrangements remain Hafiz’s to confirm.
10. **Commercial ownership — DECIDED (Hafiz, 2026-09-06): “The partner’s pack owns the numbers.”** Our five documents contain no programme commercial figures or competing cost model; point to the read-only partner pack. Dated public-policy/evaluation statistics are evidence, not programme prices. D2’s device delta belongs in the partner-owned costing when validated, not a new table here. Source: [partner review §2](partner/SEPADU-review.md#2-hafizs-three-answers-today).

### C4. Positioning — DECIDED by Hafiz, 2026-09-06

**Hafiz’s wording: “lets do mix of both”.** Combine teacher-workload reduction with the AI-classroom vision: help teachers prepare, mark and record more efficiently while supporting classroom delivery, differentiated material and pupil-progress understanding through the existing six pillars. Both strands belong in the framing; this is not an admin-only product or an AI feature list disconnected from teacher value.

This records **approved strategic direction**, not a measured time saving, guaranteed learning improvement, new product scope or proposal draft. D1–D10 remain unchanged, including staged full-RPH beta at launch, teacher-only supplied devices, separate parent/pupil web access, partner-owned commercial figures and D7’s quiet reporting/analytics treatment. No admin modules are imported from the pack by implication. The partner files retain their historical framing and C4-open wording as read-only source material; Hafiz’s later decision here supersedes that status for our masters, without asserting Faiz’s agreement. Koda: `mem_48f135a53201`.

## 8. Next exact action

REC-09: read chapter 5 in both v0.2 editions for teacher assistance and personal attention. All earlier next-action prose is subordinate to latest Active Task and §13. No release-tier or product-scope change; no deck/publication action.

**Latest next action:** Hafiz reads the internal sourcebook through `production/internal-team-sourcebook-editions/internal-team-sourcebook.html`, starting with chapters 1–5 and 10–12; the external draft remains available separately. Apply scoped reading feedback to its governed master and regenerate/check editions. Do not ask for either chapter structure approval again. No publication, partner-source edit or Claude deck edit. See each acceptance record for its distinct review/Word-check limits.

**Current checkpoint after owner reconciliation, 2026-09-07:** review the new external and internal chapter blueprints with Hafiz; see Active Task and §13's latest entry. Full prose awaits blueprint approval. Approved direction is REC-01 to REC-05 in `production/document-reconciliation-and-coverage.md`; do not repeat those questions. Claude owns deck refinement with Hafiz. No partner/source-file changes, new commercial figures, publication, software build or commit. Older instructions below are retained only as historical workflow records.

**Historical production instruction, 2026-09-07:** use `production/document-direction-and-storyboard.md` for the authorised local production contract, audience boundaries and proposed bilingual assertion sequence. Present the titles to Hafiz for approval, then create the finished visual sample. Do not wait for Claude's reading-version republication. Legal registered entity disclosure remains deferred. All outputs concern Kota Buku; naming the intended recipient does not imply appointment or endorsement. Preserve outstanding evidence flags and protected inputs; the newer blueprint checkpoint now controls the next action.

**Historical reading-draft checkpoint, same date:** Hafiz approved preparing the slide-by-slide reading draft and explicitly added pupils and parents. `production/deck-reading-draft.md` preserves that review copy. Keep the ambitious full experience, simple wording, independent BM/English comprehension, and visible material delivery boundaries. Its former story/sample approval sequence is historical; do not restart it in Codex's current long-form document lane.

**Completion update, 2026-09-06:** the second-pass steps below are retained as the brief/audit trail, not instructions to repeat completed work. The result and all deviations justified by evidence are in §13 under “Second-pass SEPADU reconciliation”. Next is Claude’s reading-version reconciliation when Hafiz instructs; C4 is now decided as blended positioning (§7 C4); existing owner checks remain open. No new deliverable is inferred.

**Hafiz's instruction (06/09/2026): Codex continues by previewing all of the work and improving it where needed. Codex does not derive the next step.** That means no proposal outline, no drafting, no build, no new research scope unless Hafiz asks.

**Second pass added 06/09/2026 (after the first review in §13).** Hafiz's partner (Faiz Samion, CSO) prepared a commercial and programme pack for the same opportunity, "SEPADU v1.0 Founder Briefing", filed verbatim at `partner/SEPADU-v1.0-Founder-Briefing.md`. Claude reviewed and verified it and wrote `partner/SEPADU-review.md`. Hafiz's rule: **Claude does not merge; Codex applies the findings.** Hafiz decided three new points today (review §2): D8 teachers only, no pupil devices; D9 Sifututor is the contracting face with Learnest Lab visible as the product technology; D10 the partner's pack owns the commercial numbers, our documents stay figure-free.

**For Codex, in order:**
0. **Step 0 (do this first):** read `partner/SEPADU-review.md` in full, then apply its §10 list to the five documents. Do not edit the two files under `partner/`. Record every edit in §13 below under a new dated heading. Where the review marks something "open for Hafiz and Faiz" (positioning, C4), leave both documents as they are and list it in your findings.
1. Read all five documents in `docs/ai-classroom-concept/` in the order in §11, skim `sources/`, and open the five reading-version artifacts linked in §3.
2. Review for: (a) internal consistency across documents — dates, figures, and the seven decisions applied identically everywhere; (b) claims that overreach their evidence, especially in synthesis sections; (c) flagged or unverified items that a reachable primary source can settle; (d) gaps against Hafiz's recorded inputs in §2; (e) plain-language clarity, since the reading versions must be easy to understand.
3. Apply low-risk improvements directly: typos, inconsistencies, clearer wording, corrected or added citations. Keep every claim dated and sourced. Keep every verification flag unless you have settled it from a primary source, in which case record the source.
4. Append a dated **Change log** section to the end of this file listing every edit (file, section, what changed, why).
5. Report to Hafiz a ranked findings list: what was wrong or weak, what you changed, what needs his decision. Reference file and section for each item.
6. If a reading-version artifact needs changes, list them for Claude to republish. Codex does not publish artifacts.
7. Leave these tracked but untouched: the four Kota Buku questions in `data-collection-spec.md` §11 and the human-only verifications (a teacher photographing a real class set of worksheets; the content-licence conversation; the APDM integration question; Apple's ASM-vs-ABM answer; a browser check of bpk.moe.gov.my links). They are Hafiz's to schedule.

## 9. Required verification before "done"

Not a delegated code build, so the runner/watchdog fields do not apply:
- Delegation evidence JSON / Markdown, worker handback, watchdog state, stall events, usage counters: **not applicable** (interactive research session, no delegation runner).
- Gate 2A / QA / regression: **not applicable** (no code).
- Guard command: `pre-commit-guard.sh` **not run** — nothing was committed. Run it if/when the ledger change is committed.
- Ledger check: `mission-ledger-check.py` → **passed**.

## 10. Independent Codex review checklist

- Acceptance wording vs implementation: the deliverable was research + docs; compare against Hafiz's request in §2 row 14 and the six pillars in §1.
- Diff and scope: the original handoff expected one modified tracked file; the Codex check on 2026-09-06 found many unrelated existing changes, preserved untouched by this document pass. Five concept markdown files remain gitignored. Review the docs, not a code diff.
- Test strength / human-journey proof: none required; the "proof" is the source trail inside each doc. Spot-check any claim by following its citation — the docs are designed for that.
- Forbidden actions / approval boundary: none crossed. No outreach, no build, no commit, no push.
- Highest safe next state: **reviewed and improved package, with a change log and a findings report to Hafiz**. Not a proposal draft, not sent, not build.
- Decisions still needed from Hafiz: none of the seven gating ones (§7, all decided 2026-09-06), and D8 to D10 are decided (review §2). C4 is now decided by Hafiz as blended workload-reduction and AI-classroom positioning (§7 C4). Still his call later: partner alignment, when to start the proposal outline, and approval of any outline before full prose. RM figures now live in the partner's pack (D10), not in our documents.

## 11. Read first

1. This file.
2. `docs/ai-classroom-concept/product-feature-spec.md` — the *what*. Start at §1 (build status) and §12 (MVP list).
3. `docs/ai-classroom-concept/technical-build-blueprint.md` — the *how*. §3 (device model), §7 (distribution constraint), §9 (cost), §13 (synthesis).
4. `docs/ai-classroom-concept/research-findings.md` — the *why*. §9 (cross-cutting observations) then dip into sections as cited.
5. `docs/ai-classroom-concept/data-collection-spec.md` — the *data*. Read §1 (one-paragraph answer), §6 (what not to collect), §7 (governance) before touching any data-model or proposal-analytics work.
6. `docs/agent-playbooks/mission-ledger/cross-project.md` → `AI-CLASSROOM-001`.
7. `~/Downloads/Teacher-Digital-Empowerment-Programme.pptx` — the redONE deck (source of the programme facts; note its internal inconsistencies on device model and unit price).

## 12. Watchouts

**Codex review status, 2026-09-06:** the local review and low-risk improvement pass is recorded in §13 below. Existing verification flags remain open unless a primary source is explicitly recorded there. Five private reading versions could not be opened; their contents and visual parity remain unverified. Nothing in this review authorises a proposal outline, drafting, build or publication.

- **The docs are local-only.** If Hafiz opens Codex on another machine, they are not there. Confirm the files exist before relying on them.
- **Pricing and model names decay fast.** The historical model-retirement warning remains a verification lead (blueprint §9.2); the old cost table is removed under D10. Recheck official model lifecycles, regional availability and prices before any partner-owned costing.
- **Every "no vendor pathway into KPM exists" claim is an absence-of-evidence finding.** It was narrowed once already (Pandai). Treat it as a strong but rebuttable thesis, not a fact.
- **The redONE deck itself is inconsistent** (iPad Air M4 vs A16; conflicting unit prices and insurance charges). Do not quote its numbers as authoritative.
- **Do not present the RAG paper as validation of the platform.** It is single-chapter, automated-metric, not teacher-validated.

---

## Continuation prompt (paste into Codex)

Deck handoff, 2026-09-07: Codex now owns the Kota Buku deck as well as the documents. Use this prompt; the older prompt beneath it is historical.

```text
Continue from /Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/CODEX-HANDOFF.md (read fully first, then the last section 13 entry "Claude to Codex: complete deck handoff").
Main goal: an evidence-backed, honest proposal to Perbadanan Kota Buku (AI-CLASSROOM-001), delivered by Sifututor, powered by Learnest Lab; local-only until Hafiz says otherwise.
Current position: Claude's fifteen-slide bilingual deck is complete with desktop, phone and PDF check suites clean (production/visual-samples/claude/, README.md there is the record; share/ holds the partner files). Codex's external and internal documents are v0.2 reading drafts.
Next action: apply decision D11 (class view, flags, suggestions, templates and parent digest at launch for all teachers; plain-language AI analysis, the assistant and AI-written admin drafts as a guided trial with selected teachers at the same launch) and the two copy rules ("student" never "pupil" in English; real-looking fictional names instead of placeholders) to product-feature-spec.md, technical-build-blueprint.md, production/deck-reading-draft.md and both v0.2 documents; then refresh the START-HERE index for the deck; then continue Hafiz's one-by-one deck review using build/runall.sh with the reference-first process (show Mobbin references, he picks, one slide at a time).
Check first: git status; the deck README; review-codex-2026-09-07.md; the build/ folder runs with `zsh build/runall.sh all` from production/visual-samples/claude.
Do not change: D1 to D11 and C4; both partner files (read-only); commercial figures stay in the partner pack; no publication, commit, un-ignore, outreach, software build, or edits under live/ or .workflow-rollout/; do not hand-edit kota-buku-deck.template.html (regenerate it); keep the honesty line, the delivery-slide boundary and the i-card texts.
```

Historical prompt (superseded 2026-09-07 by the deck handoff above):

```text
Continue from /Users/hafizrazali/Projects/Sifututor/docs/ai-classroom-concept/CODEX-HANDOFF.md (read fully first).
LATEST OVERRIDE: REC-08 approves the internal six-part structure with sixteen chapters and seven appendices. Both document masters and local editions now exist. Read production/internal-team-sourcebook-acceptance.md and internal-team-sourcebook-evidence.md, then internal-team-sourcebook.md. Internal HTML/PDF/DOCX text and browser checks pass; both PDFs26pages; independent content follow-up confirms zero remaining Blocking/Material/Minor findings. Exact Word/Pages visuals remain unverified. External acceptance retains its separate review limits. Next is Hafiz reading feedback, not another blueprint approval or new deliverable. No publication/build/partner-source/Claude-deck edits. The following earlier checkpoint is historical.
AI-CLASSROOM-001 current checkpoint: two long-form chapter blueprints prepared for Hafiz's review before full drafting. Read section 13's latest entry, production/document-reconciliation-and-coverage.md, production/external-kota-buku-blueprint.md and production/internal-team-sourcebook-blueprint.md. Hafiz is refining Claude's preferred deck with Claude; do not edit deck files. REC-01 to REC-05 record approved direction: interest-building plus later partner-owned commercial package; proposed Kota Buku programme/delivery role and Sifututor product/technology lead powered by Learnest Lab; benefits-first connected teacher/pupil/parent narrative; full vision with honest launch/beta/later stages; proposed enablement/support split and joint adoption review. These are our approved proposals, not Kota Buku acceptance or agreed staff/service levels. No automatic seven-artifact expansion. Chapter approval is not yet granted. Do not restart old slide-sample or research-review tasks.
The five markdown masters now apply SEPADU-review section 10 with evidence-qualified disagreements recorded: Act 882 is the Government Procurement Act 2026, section 35 is not a blanket subcontract offence, commencement/transition applicability remains open; RPM 80:20 is printed p179; early LKAN year/edition needs primary reconciliation. D8 does not cancel pupil/parent web access; D4's full-RPH guided beta remains at launch.
Decisions 1 and 5 were refined with Hafiz's explicit approval, D8-D10 added; D2-D4/D6-D7 remain unchanged. Commercial figures stay in the read-only partner pack. Both partner files and sources are untouched; all concept files remain local-only. C4 is decided by Hafiz as a mix of workload reduction and AI-classroom capability (section7 C4); do not infer Faiz approval.
If instructed to republish reading versions, Claude should apply section 13's artifact list to all five and verify parity/flags. Codex does not publish. Mission Ledger decisions match but its current/next-action and law-year text are stale; section 13 lists the exact refresh for Claude. No ledger edit was made in this second pass.
Local document planning/authoring is now authorised within those checkpoints. No outreach, software build, publication, commit, un-ignore, or changes under live/ or .workflow-rollout/. Preserve the four questions in data spec section 11 and all unresolved verification flags. Legal identity disclosure is deferred. Ask Hafiz only for the agreed creative checkpoints or genuinely new scope or decisions. Older review-only statements are historical, not current production authority.
```

## 13. Change log — independent Codex review, 2026-09-06

**Historical first-pass record below:** statements about seven decisions being verbatim, retained cost tables and the then-next action describe the first pass only. The later second-pass heading supersedes current status and records Hafiz-authorised D1/D5 refinements plus D8–D10; it does not erase the audit trail.

### Review result and limits

Reviewed the five markdown masters, AI-CLASSROOM-001 ledger entry, preserved source files and redONE deck text. A separate read-only reviewer challenged governance and measurement claims; Codex reconciled the findings and made the edits below. This follows document-production evidence discipline, with Hafiz’s review-only boundary overriding new authoring/rendering/publication steps.

**Highest proven state: reviewed and improved locally, with material evidence and owner-verification gaps still visible. Not cleared for external use.** All seven decisions in §7 and the four conversations in data spec §11 were compared with the pre-edit copies and remain verbatim. No software work, new research topic, outreach, commit, un-ignore or artifact publication was performed in this review.

All five private Claude URLs in §3 were attempted; the available fetch route rejected them. No reading-version text or visual QA is claimed. Local markdown corrections do not automatically update those artifacts.

### Ranked findings for Hafiz

| Rank | What was wrong or weak | What changed | What remains / owner attention |
|---|---|---|---|
| 1 — material | **Hardware rationale overreached.** Blueprint §3/§13 and handoff §4 confused Apple Intelligence with all local processing. Handoff §7 decision 2 lists grading/OCR as reasons for M1+. | Distinguished Apple Intelligence eligibility from local code/Core ML/Vision; removed the claim that corpus size alone makes on-device RAG impossible. | **Hafiz:** keep the decided M1+ recommendation/A16 minimum, but acknowledge that grading and compatible OCR are not exclusive upgrade benefits. Exact hardware/language/performance and support-life claims need evidence before the delta is presented. Decision 2 text is untouched. |
| 2 — material | **Governance contradicted itself.** Data §7 allowed vendor-own improvement and foreign inference despite processor-only/Malaysia-resident decisions; called pseudonymous research data non-identifiable; treated legal basis as settled. | Aligned uses with controller instructions; kept identifiable processing in Malaysia; distinguished anonymity from pseudonymisation; clarified legal/contract status, logged access and retention. Research §3 now cites existing parental consent and the government exclusion directly. | No new policy choice made. Actual legal entity/controller, lawful authority, Malaysian inference/OCR availability, DPA, retention and breach obligations need the existing human/legal checks. A TIA is not permission to override decision 7. |
| 3 — material | **Learning evidence was overstated.** Product §9/§10 and blueprint §10/§13 still said the Malaysian paper validated the architecture/textbooks; attendance could update mastery. Data §9 promised national comparability and intervention effectiveness from activity logs. | Narrowed the preprint to its tested source-grounded MCQ setting; kept teacher validation; separated assessment estimates from teacher-confirmed TP; kept attendance contextual; changed causal/comparability/workload claims to qualified evidence/proxies. | No product effect size, national comparability or workload saving is proven. Device-free per-pupil response capture is still unspecified; later worksheet photos cannot recover pupil response times. These are validation gaps, not permission to invent a capture feature. |
| 4 — material | **The seven decisions had drifted between documents.** White-label was still “open”; APDM sync was both Core and Fast-follow; exports were promised despite unknown formats; ledger still deferred full RPH; Korea text recommended opt-in. | Applied the approved brand/deal, Level 1/Level 2 launch posture, neutral adoption framing and conditional APDM integration. | Seven decisions remain settled. Apple account ownership wording applies to the managed Custom App route, not universally to public App Store distribution; handoff decision 1’s “regardless” rationale is flagged, unchanged. Apple eligibility remains a human question. |
| 5 — material | **A primary-source number contradicts itself.** Data §2/§10 repeated RPM’s 11% beside 122,062 / 448,113 (2024). | Preserved both the reported figure and counts with an explicit inconsistency flag; arithmetic gives 27.24%, not 11%. | Do not substitute 27.24% or the secondary 27.5% as the official rate. The original source/extraction/denominator needs reconciliation. Also flagged current UASA reporting and institution-specific admission rules. |
| 6 — material | **Scope breadth exceeds demonstrated specification depth.** Full Std 1–Form 5 and private/international schools are decided, but the coverage and operating details are predominantly KPM/DSKP. | Added an explicit existing-scope gap note in product §13; no new research or delivery scope added. | **Hafiz, later:** prioritise coverage/validation across years, subjects, languages and curricula; private/international governance; middle-year age gates; capture feasibility. Any narrower launch coverage needs a separate explicit choice, not an inference from MVP advice. Public availability also does not automatically establish DSKP reuse rights. |
| 7 — evidence | **Cost and market synthesis was too confident.** Blueprint §9 contradicted its own scenarios, assumed cache savings/discounts, and lacked a reproducible non-AI bill of materials; market claims turned “not found” into “does not exist.” | Qualified modeled costs, cache assumptions, additional costs and missing regional evidence; narrowed absence-of-evidence claims. Reopened official OpenAI pricing/deprecations without certifying other providers’ rows. | Recheck every selected current model/region/service-tier rate before quoting any cost table. No fee amount or margin is approved. Exact studies, national case outcomes and several vendor figures still lack claim-level primary references. |
| 8 — editorial / access | **Several references and status statements were stale or wrong.** Consent “inferred practice,” Gradescope acquisition year, TALIS denominator, age-6 entry, source scratchpad paths, file count, and ledger state. | Corrected or flagged them; verified the MOE budget figure from the speech rather than guessing from a URL slug. | Claude must republish/check all five reading versions when instructed. This review could not inspect them. Existing classroom-photo, licence, APDM, Apple and BPK-browser checks remain Hafiz’s to schedule. |

### Edit register (every changed area)

All edits below are dated 2026-09-06. The register groups related line edits; no source file was modified.

| File / section | Edit and reason |
|---|---|
| Handoff opening, Goal, §5, §10, §11 | Corrected four-companion/five-total file counts, product-brand wording, private-artifact versus external-sharing status, actual dirty-worktree observation and duplicate reading-order number. |
| Handoff §4, §12, §13 | Corrected A16 summary and dated consultation-status caveat; added review status, ranked findings, this edit register, evidence trail, preservation checks and Claude republication list. §7 unchanged. |
| Blueprint header, §1, §13 items 1/8 | Replaced undecided/replacement deal language with the co-branded Learnest Lab decision; narrowed conclusions from sparse ratings and update history. |
| Blueprint §3, §13 items 2/3 | Distinguished Apple Intelligence from local deterministic code, Vision and Core ML; removed universal “no local AI” and corpus-size/context-window inference; made task/runtime/language validation explicit; narrowed cloud-only market inference. |
| Blueprint §6, §14 | Replaced “paid ABM” premise and added Apple Business’s dated replacement/free-service announcement, while retaining the exact teacher-only eligibility question as unresolved. Historical ABM terminology is explained, not silently treated as current pricing. |
| Blueprint §7 | Added a route-specific qualification to account ownership/administration; public App Store distribution differs from managed Custom Apps. Flagged fixed decision 1’s supporting rationale without editing it. |
| Blueprint §9.1–§9.2 | Distinguished Khanmigo subscription/development price from inference cost; qualified light/heavy budget interpretation, caching hit-rate assumptions, unnegotiated discounts, extra costs and the boundary of this review’s price recheck. Existing cost table retained, not newly certified. |
| Blueprint §10, §13 item 5 | Replaced unsupported peer-review/platform-validation and factual-correctness claims with the preprint’s narrower automated-metric interpretation; added primary link; kept methodological limitations and teacher-pilot requirement. |
| Blueprint §10–§11 | Made Singapore incompatible with identifiable Malaysia-resident processing; flagged service-by-service inference/log/backup residency and missing reproducible non-AI cost/capacity assumptions. |
| Blueprint §13 opening/item 9 | Recognised that seven decisions are already made and DIKSHA deep-read already completed; retained unpublished operations/conflict-resolution gaps. |
| Product §3, §7, §9.1, §12 | APDM sync consistently Fast-follow/conditional; Core register has generic export, not an unverified “upload once” promise or assumed APDM format. |
| Product §4 | Removed unsupported letter-grade conversion; flagged study measure/source; limited offline promise to local/downloaded workflows; fixed content-integration cross-reference from §8 to §10. |
| Product §5 | Clarified language choice versus DLP legal applicability; changed “validated MCQ” to automated evaluation, preserving day-one full-RPH backend/guided-beta decision. |
| Product §6 | Aligned Khanmigo measured versus hypothetical estimate with research §6.4; explicitly retained independent-primary-fetch limitation. |
| Product §8 | Corrected Sifututor prose capitalisation. |
| Product §9.1–§9.2 | Flagged unspecified device-free live-response attribution; excluded attendance/participation from attainment; separated internal estimates from teacher PBD judgement; narrowed Canvas architectural analogy; class-dashboard surface remains Fast-follow despite day-one data design. |
| Product §9.2, §10 | Removed “exact architecture validated” and “textbook ingestion proved” synthesis; retained content rights/ingestion conditions and linked the primary preprint. |
| Product §11 | Removed unsolicited opt-in recommendation; applied neutral framing and flagged January participation versus later rollback chronology. |
| Product §13 | Added coverage, private/international, age-gate, capture and public-source-rights gaps without reducing approved scope or adding a new deliverable. |
| Data introduction, §1 | Corrected verification-list reference to §10; changed universal API/learning-record absence claims to reviewed-public-evidence limits; narrowed single-factor Estonia/inBloom causal framing. |
| Data §2, §9, §10 | Flagged RPM percentage/count inconsistency at all uses; retained the separate secondary 27.5% and original reconciliation flag. No replacement official rate selected. |
| Data §2 | Corrected UPU formula being labelled matriculation; scoped yearly PAJSK to Year 4–Form 5 within this product; stopped generalising income rules to BAP; added current-UASA-format verification caution. |
| Data §3, §8 | Made APDM/BPK/SPPB formats, idMe federation and upload capability conditional; teacher owns the TP judgement, not an automatic export algorithm. |
| Data §5, §5.5, §9 | Added observable-event/missing-data limits; differentiated item targets, estimates and official TP; changed workload proof to proxies and national/causal claims to validation requirements. |
| Data §6 | Removed accidental ethnicity/religion roster exception; language medium is a distinct field, not a justification for sensitive data retention. |
| Data §7 opening, §7.1–§7.2 | Clarified proposed legal/contract status; enforced existing processor-only purposes and Malaysia residency, including inference/logs/backups; no TIA override. |
| Data §7.3, §7.8 | Corrected pseudonymised ≠ anonymous; logged documented KPM individual access; added linkage/differencing risks; “no differential privacy found” instead of universal absence. |
| Data §7.5–§7.7 | Made statutory-basis confirmation explicit; separated audit-log retention from breach-record minimum; changed predicted NUTP opposition into an unverified adoption risk. Breach-rule details remain for legal verification, not silently cleared. |
| Data §10–§11 | Clarified [P] provenance versus current applicability; replaced expired scratchpad references with six preserved source links; marked downstream product/proposal notes historical and not authorised. Four human questions unchanged. |
| Research §1.1, §1.6 | Corrected Apple-in-2020 chronology conflict and voluntary age-6 entry wording. |
| Research §1.7 | Added government-hosted budget speech paragraph 187 for 2026 MOE allocation; retained other budget amounts as explicit verification leads. |
| Research §3.2–§3.5, §9 item 5 | Replaced “inferred” child-consent claim with regulation 3; dated the later consultation uncertainty; cited express Federal/State exclusion; narrowed missing-template/vendor-route claims. |
| Research §6, §6.5 | Added claim-level source/measurement cautions, NBER fetch limitation and cross-study comparison limits; corrected Gradescope acquisition to 2018 with primary citation. |
| Research §7.4 | Narrowed procurement absence claim and removed inference that inbound contact bypasses an established closed route; preserved Pandai/Sasbadi qualifications. |
| Research §8.1 | Removed misleading weekly teaching/admin conversion from TALIS; preserved all workload-statistic warnings and required exact Malaysia table/denominator before quotation. |
| Mission Ledger AI-CLASSROOM-001 only | Updated brand, current five-document state, approved staged-RPH launch, review outcome, owner attention and next action; removed stale scope/commit ambiguity. Other missions preserved. |

### Evidence checked or still open

- **Primary checked:** [Apple eligibility](https://support.apple.com/en-us/121115), [Core ML](https://developer.apple.com/documentation/coreml), [Apple Business announcement, 24 Mar 2026](https://www.apple.com/uk/newsroom/2026/03/introducing-apple-business/), [Malaysian preprint §§3–4/6.3](https://arxiv.org/html/2508.04442v1), [PDP Regulations 2013 regulation 3, p.14](https://www.pdp.gov.my/ppdpv1/wp-content/uploads/2024/06/PERATURAN-PERLINDUGAN-DATA-PERIBADI-2013.pdf), [JPDP applicability](https://www.pdp.gov.my/ppdpv1/en/akta/application-and-non-application-of-the-act/), [Turnitin acquisition announcement](https://www.turnitin.co.uk/press/turnitin-acquires-gradescope), [Budget 2026 speech ¶187](https://www.investmalaysia.gov.my/media/pipcspid/prime-minister-s-parliamentary-speech-on-budget-2026-english-translation.pdf), and [OpenAI pricing](https://developers.openai.com/api/docs/pricing)/[deprecations](https://developers.openai.com/api/docs/deprecations). Checked 2026-09-06; each settles only the associated point, not the entire paragraph or system design.
- **Preserved-source checks:** PAJSK cover explicitly scopes Year 4–6 / Form 1–5 (plus STAM outside this product); UPU circular §5.4 carries the 90/10 formula; RPM text contains the contradictory percentage/counts and voluntary-entry wording; DIKSHA cover identifies v5.0A as a December 2022 draft, not a current 2026 deployment attestation. Psychometric guide skimmed; no current policy inferred solely from its existence.
- **Deck caution:** text confirms proposed scale/bundle and pending approvals, not an awarded programme. It also mixes 182,000 with 182,757 and conflicting first-year totals/device costs. Do not treat deck arithmetic as an approved budget. No procurement numbers were changed or proposed by this review.
- **Not settled:** NBER w35620 page returned 403 and PDF fetch failed; exact TALIS Malaysia table not recovered; JPDP breach-guideline PDF exceeded fetch size; post-March child-verification amendment status not established; live Apple Vision Malay runtime support still unverified. These are not removed from the evidence debt.
- **Additional retained gaps:** source URLs/editions for many study effects and policy/programme counts; current SAPS versus SPPB status; current UASA reporting; admission routes by institution/cohort; public DSKP reuse rights; exact legal judgments in national failure case studies; service-level Malaysian inference/OCR availability. No new research programme initiated to fill these.

### Claude reading-version republication list — do not publish from Codex

| Artifact in §3 | Changes to carry from the corrected master |
|---|---|
| Market and Policy Findings | Consent/applicability, dates, budget citation, TALIS denominator, Gradescope year, source/market-absence caveats. |
| Build Blueprint | Decided white-label brand, A16/local processing distinction, current Apple Business note, conditional distribution/residency, narrow RAG evidence, cost-model limits. Do not repeat unrechecked table figures. |
| Feature Specification | APDM tier/export conditions, staged RPH, neutral Korea framing, mastery versus attendance, device-free capture gap, offline boundary, limited RAG claims and scope gaps. |
| Data Collection Spec | RPM discrepancy, UPU/PAJSK scope, conditional interfaces, measurement limits, processor/residency/anonymisation/legal caveats and preserved-source links. |
| Codex Handoff | Corrected counts/status plus this complete ranked review/change log; retain §7 decisions verbatim and all human-only checks. |

After any republication, Claude must check wording against the masters and confirm all flags survive. Because the artifacts were inaccessible here, this list is a required reconciliation list, not a claim about their current exact contents.

### Local verification

- Pre-edit copies retained in a task-specific temporary directory for diff/preservation checks; concept documents remain local-only and gitignored.
- Exact section comparison: handoff §7 unchanged; data §11 four human questions unchanged.
- `git check-ignore docs/ai-classroom-concept/*.md`: all five remain ignored.
- `python3 scripts/agent-checks/mission-ledger-check.py`: **passed, 129 items**. Count differs from the original handoff because the workspace has other existing mission changes.
- No software tests/build/commit guards run: not a code or commit task. No claim of artifact rendering/visual QA.
- Recommended next: Hafiz reviews the ranked findings; Claude reconciles/republishes reading versions only when instructed. No proposal outline or drafting started.

### Second-pass SEPADU reconciliation — 2026-09-06

**Scope and authority:** applied partner review §10 items 1–7 to the five markdown masters, following Hafiz’s explicit “please proceed to fix all” approval of the D1/D5 wording refinements. Used document-production’s source/claim discipline and independent read-only legal/consistency critique; no new proposal, research programme, build or publication. The two partner files remain verbatim/read-only. Dates use ISO format; no decision was reopened.

#### Ranked findings and disagreements

| Rank | Weakness / disagreement | Fix and reference | Still needing attention |
|---|---|---|---|
| 1 — legal | Review §6.2 calls the law “Procurement Act 2025”, treats s35 as a blanket subcontract offence, and predicts automatic exposure on commencement. | Blueprint §15.2 uses primary **Government Procurement Act 2026 (Act 882)** §§1/35/93: transfer/assignment/novation; Gazette commencement and prior-procurement transition matter. Contract-chain disclosure/approval remains a prudent applicability check, not a categorical offence finding. | Legal review of actual procuring entity, start date, terms and each link; no commencement notice established. Claude’s review and ledger need this correction, but were not edited. |
| 2 — commercial / identity | D9/D10 conflicted with old Learnest-only contracting language, old slot-fit claims and our independent cost tables. | All five identify **Kota Buku app, delivered by Sifututor, powered by Learnest Lab**; handoff §2 row16 and §7 D1/D5/D8–D10 reconcile authority. Blueprint §§9/11 replace figures with validation inputs. Other monetary amounts/benchmarks removed to keep the five masters figure-free; citations and unresolved thresholds remain. | Hafiz confirms legal entity/registration and inter-entity IP/processing schedule. Partner owns/rebases its figures; removal of ours is not approval of theirs. Original disclosure timing remains. |
| 3 — scope / readiness | Review §8.1 wrongly treats D8 as removing all pupil-client work and D4 as not shipping full RPH at launch. | Product §§1/2.1/8/12 retain the separate parent/pupil web surface without supplied pupil devices; full-RPH shared backend and guided beta remain **at launch**. Existing-generator claim explicitly withdrawn using the earlier audit. Phase 1 has no KPM integration; generic exports are not APDM integration. | Faiz must reconcile pack readiness/scope and the content-supply assumption. No additional audit/build was authorised; this pass relies on the recorded codebase audit. |
| 4 — governance / operations | Review §6.1 overstates vendor exclusion; cloud service presence was being mistaken for Malaysian inference. G1/G2 and adoption requirements were incomplete. | Blueprint §§8.1/9.2/15.1, product §§2.1/9 and data §§5.5/7/8: designated-NCII incident timeline, conditional contractual escalation, explicit Malaysia-only identifiable processing, teacher/immediate-leader visibility, above-school aggregates, non-punitive contract restrictions, four-language Core, WCAG 2.2 AA, onboarding/champions. | Designation, licensing, signed flow-down/DPA, service capacity/residency/quality, native accessibility acceptance and training resourcing remain unverified. IPGM/IAB are not assumed to supply throughput. |
| 5 — evidence | Review’s RPM page is wrong; early audit “2014” may conflate publication and report year; EEF/Korea findings can be overgeneralised. | Research §§1.4.1/1.6.1/1.6.2/6.6.1/6.6.2: RPM printed **p179**, phased policy not achieved workload; distinct audit samples/metrics; EEF’s English secondary-science preparation task and limited quality assessment; Korea’s dated adoption figures without a single cause; enabling e-RPH mirror remains [S]. | Contemporary reports identify **LKAN 2013 Series 3 published in 2014**. Primary cover/edition and steering-committee detail still need verification; archive retrieval failed. The three population/facilities figures remain explicit DO NOT QUOTE leads. |
| 6 — policy precision | Review §6.3 Treasury norms are not primary-verified; §6.4 treats this exact supply as certainly taxable; §6.5 overstates circular scope/date and future law. | Blueprint §15 preserves Treasury applicability/threshold/LAD flags, confirms standard tax rate without deciding the contract’s liability, distinguishes AIGE guidance, KPM circular, AI Malaysia Berhad and draft/consultation-stage Bill. | Current IT guide retrieval failed; exemptions/classification unresolved. KPM index conflicts with review’s issue date; signed instrument not inspected. Future enactment/commencement not assumed. No outreach. |
| 7 — open positioning / publication | C4 is a human choice, not an editorial inconsistency to “fix”. Reading artifacts and ledger can drift from corrected masters. | Both AI-classroom and partner workload framings preserved; no headline choice made. Five-artifact reconciliation list below. Ledger checked read-only. | **Hafiz + Faiz:** decide C4 when ready. Claude: refresh artifacts when instructed and ledger status/legal-year note; no new proposal deliverable authorised. |

#### Edit register — every changed area in this pass

| File / section | Edits and reason |
|---|---|
| Handoff Active Task, Goal, §§1–2 | Mark local second-pass status; add delivery/technology brand distinction; replace old slot figure with partner reference; update settled-decision count, preserve C4 exception; add row16 with three answers and do-not-mix rule. |
| Handoff §§4/7/12 | Remove historical slot/price comparisons and device/insurance amounts; preserve lifecycle, inconsistent-deck and economic-validation flags. Refine D1/D5 with explicit approval; append D8–D10 with Hafiz’s wording, parent/pupil-access guard and D2 delta’s partner-owned costing boundary. D2–D4/D6–D7 unchanged. |
| Handoff §§8/13 and continuation prompt | Mark original brief as historical/completed; prevent repeating the pass or starting a proposal; retain prior review as dated history; add this ranked report, complete edit register, evidence/verification and republication instructions. |
| Research introduction, §§1.4.1/1.6.1/1.6.2 | Apply D8–D10 brand/commercial/scope boundary; add audit failure table with separate rounds, denominators and Unicliq duty; flag early year/edition disagreement; add exact RPM quote with corrected printed page/phases; add enabling e-RPH nuance with mirror/primary-copy caveat. |
| Research §§6.6.1/6.6.2 and final evidence-debt block | Add EEF population/time/quality limits, Korea chronology and neutral causation; explicit do-not-quote flags for Sabah/Sarawak, SEN and facilities figures. No promise of Malaysian workload/learning gains. |
| Research §§1.4/1.7/3/5/6.3/7.2/7.4/9 | Omit monetary contract, budget, penalty, funding, subscription and threshold amounts under D10 while retaining source links and verification caveats; preserve school-level procurement as conditional, not a verified delegated ceiling. Non-monetary policy/evaluation statistics remain. |
| Blueprint header, §§3/6/7/9.1/12 | Apply brand, teachers-only and commercial ownership; remove programme device and monetary MDM/developer/competitor/case-study comparisons without removing vendor/eligibility/quote gaps. |
| Blueprint §§8.1/9.2/11/13/14 | Add Core onboarding/coaching/four-language/school-champion approach, no assumed IPGM/IAB capacity, workflow adoption measures, no Phase-1 KPM integration and later separately priced connectors; partner owns support figures. Replace AI/non-AI cost tables and slot/headroom synthesis with unresolved validation inputs. Narrow Malaysian GPU versus managed inference evidence; preserve service/lifecycle/pricing/capacity checks. |
| Blueprint §§10/13 | Remove residual “official curriculum documents”/“cloud-only competitors” contradictions; align with teacher-note/RPT study corpus and bounded cloud-backed evidence already in the text. Update ten-decision reference. |
| Blueprint §15 and contents | Add sourced Act 854 timeline/applicability; correct Act 882 title and s35/transition reading; qualified contract-norms table; tax applicability, AIGE/KPM/Bill/institution distinctions. Add navigation link. |
| Product header, §§1/2/2.1/5/12 | Apply brand/D8/D10; explicitly withdraw existing-RPH claim against recorded audit without cancelling guided beta at launch; remove old price-slot reference; add four-language parity, WCAG target, in-app first-week coaching and champions as Core in body and MVP summary; state no Phase-1 KPM connectors. |
| Product §§3/7/9/9.1 | Enforce Malaysia residency in all cloud-OCR suggestions rather than implying TIA/foreign processing suffices; add G1/G2 non-punitive contractual rule and separate pupil tiers; clarify functional processor brand versus pending legal schedule. |
| Data introduction, §§3/5.5/7.1/7.3/7.6/7.7/8 | Apply brand/legal-schedule caveat/D8/D10; align all interface wording to generic Core export/no Phase-1 KPM integration; add teacher/immediate-leader-only rule, label pupil-access tiers separately, prevent above-school teacher drill-down and make non-punitive use contractual. Preserve PDPA verification debt and add primary-supported conditional NCII incident flow-down. Four owner questions in §11 unchanged. |

#### Evidence and remaining limits

Primary sources for new legal/cloud claims are linked at blueprint §§9.2/15 and data §7.6; the independent reviewer read the official instruments/tables. Main reviewer checked preserved RPM text, W3C WCAG 2.2 and EEF’s primary project/evaluation page. New audit/Korea reporting is labelled [N]; the e-RPH mirror and unverified audit detail are not upgraded to primary evidence. No original source file was edited. No assertion of new full codebase audit, full provider price audit, legal sign-off, school pilot or artifact visual parity.

**Ledger reconciliation (read-only item 7):** AI-CLASSROOM-001’s D8–D10, staged-RPH launch and C4 status match. Its current/next-action text still says the second pass is pending and repeats “Procurement Act 2025”; its historical “all seven verbatim” claim now needs the D1/D5-authorised-refinement qualification. Claude should update those status/evidence lines to this section, preserve decisions, and keep the mission active (proposal itself is not done). No ledger mutation was authorised by the check-only instruction, so none was made.

#### Claude reading-version republication — all five, when instructed

| Artifact from §3 | Required changes from the current master |
|---|---|
| Market and Policy Findings | Delivery/technology brand, figure-free monetary policy, 80:20 quote/page/phases, split audit table and early-year flag, EEF population limits, neutral Korea chronology, enabling e-RPH/source flag, three do-not-quote statistics. |
| Build Blueprint | Brand/D8/D10; remove old cost tables, device/MDM/account prices and slot-fit claims; carry validation caveats, Malaysian processing distinction, Core adoption model, no Phase-1 KPM integration and qualified regulatory checklist. |
| Feature Specification | Brand and RPH-readiness withdrawal; retain full-RPH guided beta at launch and parent/pupil web access; four-language/accessibility/onboarding/champion Core requirements; G1/G2; Malaysia-only OCR; generic export/later connector distinction. |
| Data Collection Spec | Delivery/legal-role clarification, G1 teacher restrictions separate from pupil tiers, non-punitive contract, conditional immediate/six-hour NCII escalation, no Phase-1 integrations, unchanged owner questions. |
| Codex Handoff | Ten decisions with authorised D1/D5 refinements, completed local status, this full dated change log/disagreements, remaining C4/owner/evidence gaps and updated continuation prompt. Preserve first-pass record as historical. |

The private artifacts were inaccessible in the first pass and remain unverified here; this is a reconciliation list, not a claim of their current contents. Claude must check all five against the masters after republication and preserve every unresolved flag. Codex has not published them.

#### Verification and finish state

- Required mission-ledger check: **passed, 129 items**; semantic status differences are disclosed above, not hidden by a green structural check.
- `git check-ignore`: all five masters, both partner files and all preserved source files remain ignored.
- Final comparison **passed:** both partner SHA-256 hashes match the pre-pass record; D2–D4/D6–D7 and the complete data §11 section are unchanged. All five masters have balanced fences and consistent table columns; currency-literal scan found no monetary figures. Local contents links checked; repaired blueprint §11’s renamed anchor and added §15 navigation. Pre-pass copies remain at `/tmp/sepadu-reconcile.jRlzMF/` (temporary, not durable archival storage).
- No code tests, build or commit guard required/run; no code, commit, push, external messages or artifact publication.
- **Highest proven state:** reconciled and improved locally, not externally approved. Planned document edits are complete; owner/legal/evidence checks and reading-version reconciliation remain intentionally open.
- **Recommended next:** Claude reconciles/republishes the five reading versions when instructed, using this list; Hafiz/Faiz retain C4 and existing owner decisions. No proposal outline or drafting is implied.

### C4 positioning decision recorded — 2026-09-06

**Owner instruction:** after the second-pass review, Hafiz chose “lets do mix of both” when asked about workload-first versus AI-classroom-first positioning. This supersedes earlier C4-open statements in the historical review above; no other decision is reopened.

**Every edit in this update:** handoff §2/§7 C4/§8/§10 and continuation prompt now distinguish the decided mixed framing from still-open partner/owner checks; §13 adds this record. Research introduction and §1.6.1, blueprint commercial-boundary introduction, product authority introduction and data alignment introduction now point to the same blended direction. No pillar, feature tier, commercial assumption, source claim or verification flag was changed. Both original framings remain available as source history; neither is used to silently narrow the scope.

**Checks:** compared D1–D10 and data §11 with pre-update text; checked that only the listed passages changed, the five masters remain ignored, and both partner hashes remain unchanged. No new factual research, independent re-review, render, artifact publication or code test was needed for this narrow owner-decision record. Koda decision saved as `mem_48f135a53201`.

**Claude follow-through:** carry the blended direction into all five reading versions when instructed; retain evidence caveats and the prior reconciliation list. Refresh the ledger’s C4 status using this owner decision, without claiming Faiz approval. Ledger and Session Map remain untouched in this scoped update; their older C4/status summaries do not supersede this handoff.

**Finish point:** recorded locally only. Remaining owner/legal/source checks persist; no proposal outline, drafting, build or external sharing is authorised by the positioning decision.

### Kota Buku document direction and storyboard — 2026-09-07

**Later owner authority:** Hafiz requested three BM-English outputs, reuse of the ecosystem/TEKUN production method, and visual explanation of teacher benefits. His latest direction: “ok proceed all kota buku no need agreement as we will present this to them, we need to convince them as they are not the product expert we are.” This authorises local production subject to the agreed story and visual checkpoints; it does not imply an existing Kota Buku appointment or authorise external publication. Legal registered entity disclosure is deferred. D1-D10 and C4 are unchanged.

**Every edit:** created `production/document-direction-and-storyboard.md` §§1-7 with owner direction, consolidated contract, three-audience disclosure matrix, twelve bilingual assertion titles with source-section boundaries, external/internal structures, visual-sample and QA plan, and source/acceptance rules. Updated this handoff's Active Task, §8 current instruction and continuation prompt to remove stale review-only routing from the current next action; appended this record. The four companion masters, both partner files, sources, Mission Ledger and Session Map were not edited in this update. Older review records remain historical.

**Review and limits:** checked storyboard source-section references and prior-process links locally. The plan distinguishes illustrative workflows from validated outcomes, preserves launch beta and later-feature boundaries, and excludes commercial figures. No new factual research, empirical validation, independent critique or rendered visual QA is claimed for this planning step. Those checks remain required for the produced outputs. Koda owner correction: `mem_732e5baa5ba5`.

**Current next:** approve or adjust the assertion storyboard in chat, then produce a finished bilingual visual sample. No HTML deck or full prose has been produced. Claude may later reconcile the old reading versions using the existing §13 list and this current-state update; that is not a prerequisite for local production. Nothing has been published, committed or sent externally.

### Reading-draft revision: full experience, pupils and parents — 2026-09-07

**Owner direction:** following the read-only plan challenge, Hafiz requested discussion one point at a time. He clarified a future-facing, persuasive full-platform vision with practical alternatives, without lying or shrinking the offer to one or two tasks. Present the proposed experience and delivery journey, not a readiness assessment. Ordinary non-technical readers must understand either language without a presenter. His approval of the offered next step was “ok but make sure to include the student and parents too”. This approves creating a reading draft; story and visual-sample review checkpoints remain.

**Every edit in this update:**

- Created `production/deck-reading-draft.md`: production/reading contract; twelve BM-English story beats with visual directions and P01-P12 source/status notes; dedicated parent (§07) and age-appropriate pupil (§08) stories; classroom pupil benefits (§§04-06); Kota Buku content value (§09); practical use and safeguards (§10); general-launch/guided-trial/expansion journey (§11); concrete recommendation (§12); acceptance checklist and source key.
- Updated `production/document-direction-and-storyboard.md`: status; subsequent owner authority in §1; audience, standalone-reading and future-facing rules in §2; §4 links the current draft and marks the old title table historical; §5 external-document argument follows the revised family-inclusive story; §7 updates proposition IDs and current acceptance.
- Updated this handoff: Active Task, §8 latest checkpoint, continuation prompt and this dated §13 record. The four companion research/specification masters, both partner files, sources, Mission Ledger and Session Map are untouched by this update.

**Scope and evidence:** proposed/illustrative copy is traceable to the existing 2026-09-06 masters. No new research scope, monetary figures, current vendor claims, measured savings, legal certifications or automatic expansion promises were introduced. Teacher-only hardware, age-gated family access, full-RPH guided beta at launch, conditional textbook integration, structured rather than handwritten launch capture, and Malaysia residency remain explicit. Existing verification flags and owner questions are preserved in the unchanged masters.

**Next and publication boundary:** present the reading draft for Hafiz's story review, then create finished bilingual visual samples. No rendered deck, full external/internal prose, upload, publication, outreach, software build or commit. Claude's older reading-version parity is not a prerequisite and is not newly claimed here.

**Independent reading review and refinements:** a separate read-only Astra reviewer compared the reading draft with the fixed decisions and specifications. No material scope, stage or bilingual-meaning errors were reported. All three minor findings were corrected: §11 launch marking now explicitly means marked multiple-choice answers; §11 adds the practical use of shared teaching materials and teacher-reviewed notice/reminder templates to both languages; §10 corrects the BM identifiable-information phrase and replaces “aggregated”/“secara agregat” in the visible teacher-data caption with understandable group-summary wording. These corrections preserve the original permissions and tiers. This was a document comparison, not fresh external research, classroom validation or rendered visual QA.

**Local checks:** twelve numbered story beats, twelve BM/English copy pairs, twelve proposition/source notes, relative links and scans for monetary literals/em dashes passed. The new draft and existing concept documents remain gitignored. SHA-256 comparison confirms the four companion masters and both partner files are unchanged from the start of this reading-draft update. No code tests or commit guard were run because no software or commit was involved. Highest proven state: locally checked reading draft with independent critique addressed, awaiting Hafiz's story review; layout and actual audience comprehension remain untested.

### Online deck-direction and copy research — 2026-09-07

**User request:** research online how comparable education/AI offerings use decks, including direction and copy. This is communication research and critique, not a new product-research scope or permission to rewrite the reading draft automatically.

**Every edit:** created `production/deck-reference-research.md` with the question, eight classified references, exact inspection/access limits, recommendations for the current reading draft and one illustrative bilingual copy example; appended this dated handoff record. Existing reading draft, direction contract, four companion masters, partner files, sources, Mission Ledger and Session Map are unchanged in this research step.

**Evidence:** inspected public Microsoft education PDFs, Apple's historical Singapore parent brochure, current MagicSchool/Seesaw product-story pages and Duarte/Penn State presentation guidance. Selected PDF pages were rendered and visually inspected locally. Distinguish brochures, a one-slide PowerPoint export, sales-enablement material and websites from full sales decks. Access-restricted full decks are expressly excluded from conclusions. No claim that a reference won a contract, that vendor marketing outcomes are independently proved, or that source layouts meet our bilingual requirements. Temporary PDFs/images are under `/tmp/kota-buku-deck-references.rjxaA0/`, not a durable archive.

**Next:** discuss the research-backed copy/story recommendations with Hafiz, then apply agreed refinements before visual samples. Reading-story acceptance and visual approval are still pending. No deck design, build, commit, outreach or publication occurred.

### First visual sample and requested Fable comparison — 2026-09-07

**Authority:** Hafiz approved the offered single slide showing a lesson-plan template and resulting practice options, after discussing Kelasapp marketing UI versus its implementation and other visual references. He also asked Claude Fable 5.1 to independently produce the same sample. Earlier no-HTML checkpoint language is superseded only for this sample; the complete deck still needs visual approval.

**Every edit:** created `production/visual-sample-brief.md` (shared content, style, truth boundaries, independent-comparison rules and dispatch limit); created `production/visual-samples/codex/sample.template.html` (one bilingual, synthetic fractions slide), generated `sample.html` (embedded house fonts, offline), created `check.cjs` and generated desktop/small/phone screenshots; created the accompanying `README.md` with governed sample copy, provenance, review, checks and limits. Updated this handoff's Active Task with the latest checkpoint and appended this record. Existing production reading draft/contract, four companion masters, partner files, sources, ledger and other workspace changes were not edited.

**Review and corrections:** initial screenshot exposed crowded introduction and clipped mock-screen content; corrected layout spacing. Independent Codex content review found no material issue and two minor translation issues; matched activity verbs and made the selected-teacher/full-generated-plan guided trial explicit in both languages. Kelasapp style informs presentation, not claims of inherited functionality. All teaching examples are synthetic and no commercial figures were copied.

**Checks:** existing house font builder passed without unresolved tokens; installed Chrome via existing Playwright used for 1920 x 1080, 1280 x 720 and 390 x 844 screenshot/overflow/offline/keyboard/edit-toggle checks. Screenshots inspected. Fixed-stage phone portrait is an overview, not a comfortably readable full slide; desktop or zoomable PNG is recommended. No application build/tests, commit guard, PDF, outreach, publication or artifact republication was performed.

**Fable status:** Claude Code was present, but its no-tool `fable-5.1` model probe failed as unavailable or inaccessible. No substitute model selected and no Claude design generated. The common brief is prepared, not successfully dispatched to a working Fable session. Hafiz can provide its configured model ID or run the brief in his existing Fable session. Independent Codex review must not be confused with Fable authorship.

**Next:** Hafiz reviews the Codex sample's look and readability; finish the independent Fable sample when the requested model is reachable, then compare before full deck production. Highest proven state: local single-slide design sample, not a completed deck or a completed two-model comparison. Both partner files remain read-only and all concept outputs remain local-only.

### Language-switcher correction — 2026-09-07

**Hafiz's correction:** “why we have 2 language in one slide!!!! Why not we can have a html slide like we did with tekun and just add the switcher!” Codex incorrectly interpreted bilingual support as simultaneous translated text. The required experience is one language at a time, with an English / BM control. Koda correction stored as `mem_5dc2e2bdc1db`.

**Every edit:** updated the sample template with complete language dictionaries, a persistent accessible switcher, language-specific review edits and larger single-language typography; regenerated `sample.html`. Updated `check.cjs` to test both languages at all three viewport sizes, producing six language-suffixed screenshots. Updated sample README, common Claude comparison brief, reading-draft production contract, document direction contract, this Active Task and this log. Old unsuffixed screenshots are explicitly historical. Research/specification masters and partner files remain unchanged.

**Checks and limits:** font build and all six browser checks passed (language selection/parity, bounds, offline resources, navigation, edit toggle and no script errors). English/BM desktop and phone English screenshots inspected. The TEKUN files found in the local derivative folders did not expose a matching language-switch implementation in the targeted search; this implements Hafiz's explicitly requested behavior rather than claiming to have copied a verified TEKUN component. No deployment or publication. The Fable model-access issue is unchanged; its brief now requires the same switcher. Next is Hafiz's visual review of the corrected sample, not full deck production.

### Remove heavy device frame — 2026-09-07

This frame-only iteration was subsequently rejected as still dated and crowded; see the later three-slide redesign record.

Hafiz rejected the deep, thick border. Changed only the sample's presentation treatment: removed dark padded bezel and camera decoration, added a fine light panel outline, reduced shadows. Updated the common Claude brief, sample README and this handoff's current state/log; regenerated HTML and the six language-specific screenshots. Language-switch behavior, copy, delivery qualifications, decisions and research sources are unchanged. This is a local design correction, not app work or full-deck approval. Fable comparison remains pending model access.

### Three-slide visual redesign — 2026-09-07

Owner instruction: the sample looked dated and cramped; spread it across pages with proper Apple-inspired presentation pacing. Later “continue” authorised this redesign. Koda correction `mem_37f9afb17395`.

Every edit: created `production/visual-samples/codex/sequence.template.html`, generated offline `sequence.html`, added `check-sequence.cjs` and 18 language/viewport/slide screenshots; updated sample README, shared comparison brief and this Active Task/log. The old single-slide sample is retained but marked superseded. No other masters or partner files edited.

Design: a spacious goal-led opening, one large modern teacher-workspace concept, and a separate exercise comparison. English/BM switcher covers the complete story. Teacher authority, synthetic examples and full-plan guided trial at launch remain explicit. App navigation is illustrative, not proof of implemented software. No new evidence claims or commercial figures.

Checks: house-font build passed; all 18 render/bounds/language tests and forward/back navigation passed without page errors. All six desktop slides and the smaller English app view inspected. No claim of audience acceptance, Apple-brand endorsement, classroom validation or Fable authorship. Nothing published or committed. Next: Hafiz reviews this three-slide direction before full-deck work; Fable comparison remains pending his manual run.

### Partner proposal-framework intake — 2026-09-07

**Authority and current lane:** Hafiz supplied the partner's framework from Downloads for analysis, safe updates and discussion of contradictions. He is refining the external deck with Claude; Codex's current document lane is the non-technical external Kota Buku explanation and detailed whole-team internal sourcebook. Earlier sample-review next actions above are historical.

**Every edit:** created `production/partner-framework-review.md` with source inventory, twelve ranked findings, recommended coverage improvements, technical evidence and a one-at-a-time discussion queue. Updated this handoff's Active Task to reflect the current division of work and added this dated record. No research/specification master, partner source or Claude deck was changed.

**Checks and findings:** read all eleven substantive files in `/Users/hafizrazali/Downloads/sepadu-proposal-framework/`. The package is a generic method with templates and worked examples, not seven completed deal documents or new agreed programme facts. A read-only synthetic test demonstrated that its share stripper leaves restricted paragraphs and script-held dummy content; a second assertion disproved the example regex's claimed whitespace tolerance in one direction. Other asset findings are source-inspection findings, not full browser/print QA or proof of a leak in any actual Claude artifact. No external factual verification or production share build was performed.

**Preserved boundaries:** D1-D10/C4 and verification flags remain unchanged. No commercial figures imported, framework installed, source folder migrated, new research scope started, artifact published or commit made. Downloads and both existing partner files remain read-only.

**Next discussion:** recommend using the framework as a completeness checklist inside the agreed deck plus two main documents, rather than automatically creating its seven-artifact package. Confirm that package boundary with Hafiz before changing blueprints; walk through remaining material questions one at a time. No existing reading-version republication is required by this intake alone.

### Claude full deck built from the reading draft — 2026-09-07 (written by Claude)

**Authority:** Hafiz reviewed Claude's three-slide sample point by point and then instructed Claude to build the full deck on autopilot with adversarial and visual review until done, answering the clarifying questions in chat: all twelve beats of `production/deck-reading-draft.md`; the sample's density (headline verbatim from the draft, one sentence, an "i" button opening the draft's full context for that beat); a live demo on every proposed-screen slide; generated people including pupils, disclosed once; HTML plus a static PDF in both languages; one quiet persistent honesty line instead of per-panel tags, with the launch boundary only where relevant; extra slides allowed where they explain better ("later we can have a slimmer version if needed"). He also asked that the decisions be recorded here for Codex once the deck was done.

**Every edit (all under `production/visual-samples/claude/`, local-only, nothing published or committed):** `kota-buku-deck.html` (sixteen slides: title, agenda, beats 01 to 12 with the sample's three slides carrying beats 03 and 04, beat 10 split into practical use and data protection), `kota-buku-deck-share.html` (partner copy without the presenter hint), `kota-buku-deck-en.pdf` and `kota-buku-deck-bm.pdf` (19 pages each, three appendix pages carry the "i" notes), `kota-buku-deck.template.html`, four generated supporting images in `assets/` (pupils on paper, parent with phone, older pupil, wide classroom; fal.ai text prompts only, no personal data), `screenshots/deck/`, and the `README.md` section "Full deck" with the slide list, decisions, checks, the adversarial-review change log and limitations. Koda: `mem_c567806edfa4`. Mission Ledger AI-CLASSROOM-001 updated the same day. No research or specification master, partner file, reading draft or Codex sample was edited.

**Checks:** house font build; desktop suite in both languages on every slide and every interacted state (bounds, clipping, escaping children, text below 13 px, text overlap, 6 px proximity for pills and buttons, thread crossings, dictionary completeness, console errors, EN/BM difference); interaction suite for every demo, the info cards and reset; navigation and persistence; phone suite on an iPhone 13 viewport; PDF suite (page size, overflow, chrome hidden, credits per page, return to normal). A separate adversarial review agent compared the deck with the reading draft and the rules and returned 3 blocking, 9 material and 19 minor findings; all blocking and material findings were fixed (notably: beat 10 keys had overwritten the sample's lesson goals; the plan slide had shown AI drafting the whole plan for all teachers, now "From template" rows with AI drafting practice only; Continue on the goal picker pointed at the agenda; invented onboarding items removed; the progress suggestion is labelled rule-based; offline wording as design intent; residency pill as design requirement; larger credits and honesty lines; PDF shows completed demo states; BM "Dilaksanakan oleh Sifututor"). One material point was kept by design and is explained in the README (continuation slides use a verbatim body sentence as headline). All twelve beat headlines verified verbatim in both languages by script; no em dashes, no commercial figures, no curriculum codes, no pupil names, no award wording.

**Limits:** concept illustration only; synthetic examples not reviewed by a teacher; Malay copy written by the model, native review still needed before external use; the PDF is a static export; no audience test. Not a Fable comparison of the Codex sample: this is Claude's own deliverable in the approved direction.

**Next:** Hafiz reviews the deck (English and BM, desktop and phone) and decides what to trim for a slimmer version; Codex's document lane (non-technical external explanation and the internal sourcebook) can reference the deck's slide list and the decisions above. Nothing published, committed or sent.

### Claude deck, second build after Hafiz's review — 2026-09-07 (written by Claude)

**Hafiz's direction, one point at a time:** keep Claude's layout system but adopt the cool grey ground and light chrome of Codex's `visual-samples/codex/sequence.html` (he opened it for comparison); make the cover like Codex's opening slide (big left headline, tilted card); add the analytics and assistant story, which he called one of the most important features ("AI assistant for the teacher to do all the admin and analytic work based on data that teacher input or collected"); trim the deck so everything fits, and give every non-sample slide real visual hierarchy ("the other page looks like rush job"). He chose a fourteen-slide merge.

**Every edit (still under `production/visual-samples/claude/`, local-only):** rebuilt `kota-buku-deck.html`, the share copy, both PDFs (17 pages), the template and the screenshots. Slides: cover, who it serves, one topic through the lesson, the three sample slides, pupils on paper, class view and assistant (beat 06 merged with the new analytics story), admin assistant (new), families (beats 07 and 08 merged), Kota Buku content, practical and protected (beat 10 in one slide), delivery, recommendation. README section "Full deck" rewritten with the slide list and the decisions. No master, partner file, reading draft or Codex sample edited.

**New decision for Hafiz to confirm and Codex to carry into the masters and the reading draft:** the deck presents the class view, rule-based flags and suggestions, and the notice and reminder templates as planned for all teachers at launch (consistent with the feature specification's core tier), and the plain-language AI analysis, the assistant conversation and AI-written admin drafts as a guided trial with selected teachers at the same launch, the same framing as the full AI-drafted lesson plans (D-level: the specification tiers these as fast-follow; the reading draft placed deeper class analysis in expansion). Hafiz did not choose a lane when asked; he restated the assistant concept as central. Claude applied the guided-trial framing as the honest way to present it prominently; if Hafiz prefers "soon after launch" or "expansion", the two launch notes and the delivery slide change.

**Checks:** desktop, phone and PDF suites clean in both languages after the rebuild; all twelve beat headlines verified verbatim by script; no em dashes, figures, curriculum codes, pupil names or award wording. A second adversarial review has not been run on the rebuilt deck yet.

**Third build, Hafiz's ten-point review the same day (written by Claude):** Hafiz found the non-sample slides overlapping, unhierarchical and "lazy", asked for proper website-section layouts with Mobbin references shown before approval, and added a missing data story. Every non-sample slide was rebuilt against a reference he chose (Clockwise cards, Function step section, Apple Mail scan, SchoolAI dashboard, PayPal device cards, Wise roadmap, Runner workflow snapshot); a data slide was added (fifteen slides now). Two copy rules from Hafiz that the masters and the reading draft should adopt: the English word is "student", never "pupil" (BM "murid" stays), and mockups carry real-looking fictional names and data instead of placeholders. "Head teacher" became "principal" on Claude's judgement. The data slide's "could stand in for the printed report card" is worded as later and subject to the school's and the ministry's approval, and its i-card places targeted AI practice in the guided trial. README section "The third build" has the reference table.

**Tier decision, Hafiz, 07/09/2026 (D11, recorded by Claude):** Codex's adversarial review of the deck (run through the Codex CLI in a read-only sandbox from `visual-samples/claude/review-brief-codex.md`) flagged that the masters tier the class-level dashboard, the plain-language AI narrative and the teacher assistant as fast-follow while the deck shows the class view at launch for all teachers and the assistant as a guided trial at launch. Asked to choose, Hafiz chose "deck stands, update the masters". Codex is to carry this into `product-feature-spec.md` (Pillar 4 tiers: class view, flags and rule-based suggestions core at launch; plain-language analysis, the assistant conversation and AI-written admin drafts as a guided trial with selected teachers at the same launch, alongside the full AI-drafted RPH beta), `technical-build-blueprint.md`, and `production/deck-reading-draft.md` (beat 06 visual note and beat 11 lanes). Both partner files stay read-only. The other Codex findings and the second Claude review's findings were fixed in the deck the same day; the README section "Third-build reviews and fixes" lists them.

**Disclosure placement, Hafiz's decision the same day:** asked "why we even need to disclose this?", Hafiz chose to keep the launch boundary on the delivery slide (launch / guided trial / expansion lanes) and in the "i" context cards only. The purple launch notes under the plan, class-view and admin panels, the guided-trial box on the plan slide and the trial tag beside AI drafts were removed; slide faces now show the full proposed experience. The boundary itself is unchanged and still appears in the appendix of both PDFs.

### Approved reconciliation and two document blueprints — 2026-09-07

**Owner authority:** Hafiz approved preparing both the interest-building explanation and later commercial discussion; the proposed Kota Buku programme/delivery role with Sifututor leading product and technology delivery powered by Learnest Lab; benefit-first narrative; full six-pillar vision with honest readiness; and the proposed enablement/support split. His “ok proceed” authorised recording these approvals and preparing the two chapter blueprints, stopping before full prose for structure review. These are our proposed roles, not Kota Buku acceptance or agreed staffing/service levels. D1-D10/C4 remain unchanged.

**Every edit:**

- Created `production/document-reconciliation-and-coverage.md` §§1-8: reading-stage package map, REC-01 to REC-06 owner record, shared contract, source authority, framework-to-chapter coverage, F01-F12 dispositions, verification backlog and next checkpoint. Retains a separate later commercial stage without assuming the internal founder briefing is ready to send or accepting its figures.
- Created `production/external-kota-buku-blueprint.md` §§1-7: twelve external chapters, reader outcomes, source pointers, visual owners, reader paths, language/format plan, disclosure/evidence checks and pending owner approval. E05/E06 wording corrected after review to preserve Fast-follow dashboards/narratives and Core age-appropriate family access.
- Created `production/internal-team-sourcebook-blueprint.md` §§1-7: sixteen chapters and seven appendices, full research/decision/feature/workflow/delivery/governance/commercial-interface coverage, role reading paths, evidence and sensitive-content boundaries, visuals and acceptance requirements. No commercial figures or sensitive raw partner issues copied.
- Updated `production/document-direction-and-storyboard.md`: current status; one-language-at-a-time rule; proposed support split superseding the old blanket exclusion; commercial-stage connection; latest owner authority and detailed blueprint links; accurate current acceptance. Historical story tables remain intact.
- Updated `production/partner-framework-review.md`: current disposition notice and §5 discussion completion, preserving the original findings and technical evidence. No downloaded framework asset changed.
- Updated this handoff: Active Task, §8 current checkpoint and continuation prompt; clearly marked superseded sample/reading-draft instructions historical; appended this dated record. Older audit entries retained.

**Reconciliation result:** no outstanding direction question requires reopening existing decisions before blueprint review. Partner agreement/resources, content/source rights, middle-year age rules, curriculum/year/language coverage validation, controller/legal/IP schedules, device/distribution/residency/capture evidence, official formats and final commercial reconciliation remain open. Their verification status has not been promoted by owner approval. Keep the four data-spec §11 questions and human-only checks intact.

**Checks:** sequential chapter IDs (E01-E12, I01-I16), duplicate headings, local Markdown file-link existence, conflict markers and commercial-amount scan passed for the three new files. New files remain gitignored. Both existing partner files match the hashes recorded before this work. Independent read-only blueprint review found zero blocking, zero material and three minor findings; all three were corrected (release-tier precision, age/access timing, historical checkpoint labels). This is blueprint quality review, not current-source reverification, software verification, rendered visual/accessibility QA or proof of external readiness.

**Targeted review confirmation:** the independent reviewer re-read the corrections and confirmed zero remaining blocking, material or minor findings at blueprint level. This does not replace Hafiz's chapter-structure approval.

**Memory:** updated `mem_732e5baa5ba5` through Koda to preserve reference-first recommendations, the reconciled sharing stages, approved proposed roles, support split and no repeated direction questions. Source `correction`; project tag `sifututor`.

**Untouched and publication boundary:** four research/specification companion masters, both partner files, sources, downloaded framework, Claude deck files, Mission Ledger and unrelated worktree edits. No full draft, generated HTML/PDF/DOCX, new research scope, software build, outreach, commit, un-ignore or publication. No application tests or commit guard needed for this local planning-only packet.

**Claude artifact implications:** no automatic republication is needed for the original five reading versions because their source masters were not changed. Future deck/external copy should reflect the benefit-first order, proposed programme/support roles, same-launch beta and separate commercial stage, using the reconciliation record; no claim that Claude's current deck was reviewed or updated. Do not send the internal founder briefing as the commercial edition without reconciliation and disclosure approval.

**Next:** Hafiz reviews the external chapter structure and internal completeness. Full drafting begins only after blueprint approval; all current direction approvals remain recorded and need not be asked again.

### External structure approved; bilingual draft and local editions — 2026-09-07

**Authority:** Hafiz said “ok proceed” after the twelve external chapters were explained, then repeated “ok proceed” during export verification. Recorded as REC-07: external blueprint approved, not internal blueprint or final-copy/distribution approval. Codex continued through local drafting and export checks. Claude's deck lane is unchanged.

**Every edit/output:** created `production/external-kota-buku-document.md` (full BM/English twelve-chapter master and three appendices); `external-kota-buku-evidence.md` (18 bounded claim entries, sources, visual map and verification limits); `external-kota-buku-acceptance.md` (reading links, executed checks and outstanding limits); `render-external-document.cjs`, `render-document-docx.cjs`, `external-document.css` and `check-external-document.cjs` (local rendering/checks, no new installed dependencies). Generated `external-kota-buku-editions/`: bilingual offline HTML, EN/MS single-language HTML, two 17-page A4 PDFs, two editable DOCX, editable-content HTML intermediates, build hash manifest and sixteen desktop/phone screenshots. Updated external blueprint approval, reconciliation record/current state/REC-07, and this handoff's latest status/next action/continuation override/log. Other blueprint/production references that still describe the prior packet are historical; REC-07 and acceptance govern current state.

**Review and corrections:** independent source-grounded content review found 0 blocking, 0 material and 6 minor issues; primary corrected England wording, standalone attendance BM, telemetry jargon, BM branding, exceptional service/security access, and release-condition BM. Targeted independent follow-up failed due reviewer usage availability; do not claim its confirmation. Primary checked corrections. Replaced native Word conversion because it flattened tables; local OOXML export preserves ten editable tables, chapter heading semantics, lists and source hyperlinks. Corrected encoded apostrophes and the first renderer's mistaken expected-table count. E08 PDF break now deliberately separates release matrix from Core scope instead of leaving a trailing paragraph on a mostly empty continuation page.

**Evidence:** re-opened Kota Buku's primary About page, EEF/NFER December 2024 PDF executive summary and W3C WCAG 2.2. Uses only narrow remit, dated preparation-study and chosen-accessibility-target statements. EEF page metadata's later completion date is not substituted for the report date. No fresh pricing, legal conclusion, competitor survey or source-right settlement. Product/roles remain proposed; internal audit experience dated 2026-09-06, not current code re-audit.

**Checks:** renderer and checker passed; BM/EN desktop/phone language/navigation/overflow/offline checks; per-paragraph/heading/table-cell PDF/DOCX completeness; source/output hashes; private-string/amount checks; editable table and heading counts. Both PDFs are 17 A4 pages with tagged output, not certified accessible. PDF contact sheets and representative HTML screenshots inspected; changed E08 pages inspected at larger size. DOCX exact visual pagination in Word/Pages remains unverified. No application tests or commit guard performed for this document-only local work.

**Preserved:** no partner files, downloaded framework, sources, four research/specification companions, internal blueprint, Claude deck, ledger, live files or unrelated worktree edits changed. No proposal commercial figures duplicated; no commercial edition sent or created from the internal founder pack. No outreach, upload, publication, commit or un-ignore.

**Next:** Hafiz reads the external draft, preferably the offline HTML switcher. Internal chapter approval still awaits review; do not infer it from external approval. Final circulation requires owner approval of actual files and material evidence/disclosure refresh. Outstanding operational/legal/rights/classroom validations remain visible and are not settled by this draft.

### Internal structure approved; complete bilingual sourcebook and checked local editions — 2026-09-07

**Authority:** Hafiz's latest “Yes” followed the six-part internal reading walkthrough: opportunity; research/reasoning/decisions; complete six-pillar teacher/pupil/parent experience; architecture/data/AI/governance; delivery/support/evaluation/commercial interface; assumptions/sources/maintenance. Recorded REC-08, retaining I01–I16 and appendices A–G. Approval covers local drafting/checks, not final text, publication, commercial-figure duplication or software implementation.

**Every edit/output:** created `production/internal-team-sourcebook.md` (complete English/BM sixteen-chapter/seven-appendix master); `internal-team-sourcebook-evidence.md` (IS01–IS19 claim register, source dates/limits, visual/coverage map, correction record); `internal-team-sourcebook-acceptance.md` (reading links, exact checks, boundaries and next action); `render-internal-sourcebook.cjs`, `check-internal-sourcebook.cjs` and `internal-sourcebook.css`. Generated `internal-team-sourcebook-editions/`: bilingual offline HTML, two single-language HTML, two 26-page A4 PDFs, two editable DOCX, two editable-content HTML intermediates, source/output build manifest, twenty desktop/phone screenshots and two full-PDF contact sheets. Updated internal blueprint approval, reconciliation current status/REC-08/next checkpoint and this handoff's Active Task, §8, continuation override and dated §13 log. Existing shared document CSS, external renderer/checker, DOCX helper and external editions were reused read-only, not modified. No new dependencies installed.

**Ranked review and corrections:** initial independent content review found 0 Blocking, 2 Material, 3 Minor. (1) Material I08/I09: governance detail omitted explicit pupil access, research Five Safes, controller-directed/no-independent-reuse constraints and no-public-school/class-ranking firewall. Added bilingual pupil-access matrix and purpose/research/ranking rules, retaining separate teacher G1 restrictions and unresolved legal agreement. (2) Material I08/Appendix B: lifecycle, transfer/portable record, class-specific retention, short-lived prompts/telemetry, controller deletion/return/audit and AI usage provenance too thin. Added lifecycle and purpose/provenance explanation and six-family Appendix B index; exact periods remain open. (3–4) Minor I08/I10: split misleading combined citations into their two actual source destinations in both languages. (5) Minor I15/Appendix D: added governing decision index and dated differentiated approval/acceptance/validation status. Targeted independent re-read confirms all five resolved: zero remaining Blocking/Material/Minor within content scope.

**Other source reconciliation:** carried forward qualified absence-of-public-evidence findings instead of old absolute “no government system” claims; historical programme cases are not a causal league table; no legal deadlines/prices reproduced. P's Later SEL possibilities versus D's data exclusion remain explicitly research-only until authorised scope/governance decision (I15/A), not a silently resolved contradiction. No disagreement with the independent review remains. Original verification flags and four D §11 human questions are unchanged.

**Research:** used the existing corpus, approved decisions and previous external primary verification. Reopened the narrow Malaysian Form-1 BM MCQ preprint and CASE primary page within existing scope; retained automated-metric/single-chapter/no-teacher-validation caveats and standards-reference-not-certification treatment. EEF December2024, Kota Buku remit and WCAG primary checks from same-day external work remain dated and limited in the evidence register. Current Core ML page yielded JavaScript-only content; no new compatibility fact claimed. No new research programme, legal/pricing conclusion or rights settlement.

**Checks:** internal renderer/checker passed; both languages desktop1440×1000/phone390×844, single visible language, navigation targets, no horizontal overflow, no external runtime requests/errors; master source links exist; every paragraph/heading/table-cell preserved in PDF/DOCX; DOCX semantic chapter/table counts; master/renderer/shared CSS/internal CSS/output hashes current; amount/credential-path scan. Both final PDFs26 A4 pages and tagged output. Inspected final PDF contact sheets, representative desktop/phone tables and dense I15 enlarged PDF. Print-only fixes removed short orphan continuation pages in I02/I03/I15 and split I05 three pillars per page. Exact Word/Pages appearance/pagination remains unverified; these checks do not certify accessibility or software readiness. No application tests/commit guard required for local document-only work without commit.

**Preservation:** both partner hashes match baseline (`f25b4002…`, `c92b2615…`); new files remain gitignored. No four companion research/spec master, sources, downloaded framework, partner file, Claude deck, ledger, live file, credentials or unrelated worktree edits changed. No outreach, upload, publication, commercial figures, commit or un-ignore.

**Claude/artifact implications:** no automatic republication of the original five reading artifacts; companion masters unchanged. Claude may consult the internal sourcebook for decision/release-tier/teacher-pupil-parent/support consistency, but this is not authority to edit or republish his deck. Internal editions are not safe external payloads. External document remains separately governed.

**Next:** owner reading feedback on internal chapters1–5 and10–12 (then role-specific detail), not another direction approval. Apply feedback locally and regenerate. No settled D/REC decision needs reopening now. Existing rights/legal/controller/age/curriculum/capture/residency/distribution/partner-capacity/official-interface checks still require their recorded evidence before commitment.

**Final continuity check:** reran both internal and existing external document checkers successfully; external checker refreshed its diagnostic browser screenshots only, not its master or HTML/PDF/DOCX. Internal master/evidence/acceptance local-link and conflict-marker checks passed. Stored durable synthesis/governance completeness lesson and approved-structure reminder in Koda `mem_2dfeb0f83612` (source auto-captured, sifututor project tag).

### Teacher assistance and personal attention foregrounded — 2026-09-07

**Authority:** Hafiz clarified that the assistant must help teachers evaluate learning for individual pupils and groups/class so teachers can provide personal attention, not merely generate content. “Yes proceed all” approved the recommended understand → support → follow up narrative throughout both documents. Recorded REC-09; this is editorial emphasis within product §6, not expanded launch scope.

**Every edit:** external master English/BM §§1/5 and version0.2: stronger opening purpose, evidence-evaluation role, individual conversation/explanation/follow-up and group/class illustration. Internal master English/BM §§1/5/12 and version0.2: central purpose, fuller teaching-support profile, and evaluation of teacher-selected action rather than output count. Both blueprints gain REC-09 refinement notices; both evidence registers map the changed passages to existing claim IDs/source product §6 and preserve earlier verification dates; both acceptance records record v0.2 checks/limits. Reconciliation gains REC-09; direction/storyboard gains current editorial authority. This handoff updates Active Task/§8/continuation notice and appends this log.

**Generated outputs:** regenerated both sets of bilingual/single-language HTML, separate EN/BM PDFs and DOCX, editable-content HTML and manifests; checkers regenerated diagnostic browser screenshots. Added four `check-assistant-v02-{en,ms}.png` changed-page contact images across the two edition folders. External PDFs remain17pages each; internal remain26pages each. Older full-PDF contact sheets are historical v0.1 evidence, explicitly labelled in acceptance records. No renderer/CSS/code changes needed.

**Review and proof:** independent targeted content review of external1/5 and internal1/5/12 in both languages against product §6 found zero Blocking, Material or Minor findings. Core summaries/rule-based suggestions remain distinct from Fast-follow class patterns, AI narratives and teacher chat. No automatic grouping, fixed ability labels, diagnosis, autonomous TP or causal outcome promise. Both render/check scripts passed paragraph/heading/table-cell PDF/DOCX completeness, semantic structure, hashes, language/navigation/overflow/offline checks. Visually inspected changed external PDF pages2/6 and internal pages2/7/15 in both languages; no page overflow or short orphan created. Exact Word-app appearance still unverified. This is document QA, not application tests or accessibility certification.

**Evidence and preservation:** existing source product §6 plus owner editorial authority; no new empirical/current technical/legal/pricing claims, no new research scope, no verification date advanced. Partner hashes match baseline; masters remain gitignored. Four research/spec masters, partner sources, downloaded framework, Claude deck and unrelated worktree changes untouched. No commercial figures, outreach, publication, commit or un-ignore. Stored owner correction in Koda `mem_748ec005aa4f`, source correction, sifututor tag.

**Next / Claude implications:** Hafiz reviews chapter5 in both v0.2 reading editions. No decision reopening required. Claude should carry the same teaching-assistant emphasis into future deck copy if Hafiz requests; we did not edit or republish his deck. Original five source-reading artifacts need no automatic republication because their companion masters did not change. Actual external circulation still requires owner approval and remaining source/operational checks.

### Existing document collection compiled into one reading index — 2026-09-07

**Authority/scope:** Hafiz asked to compile all documents produced so far. Implemented a local owner-only navigation pack over the existing originals, not a combined external document, duplicated commercial pack or portable archive. The document-production skill's audience separation shaped the catalogue; no new research/content claims required. Latest memory search supplied no relevant additional authority; current local records and REC-09 governed.

**Every edit/output:** created root `START-HERE.md` with seven sections: current external/internal/full Claude deck, editable masters/Word, research/specifications, decisions/QA, restricted partner references, older samples/private artifact links and inventory maintenance. Created `production/compile-document-index.cjs`; generated `START-HERE.html` and `DOCUMENT-INVENTORY.json` with62 reader files, supporting-file counts and hashes, plus search by path/category. Generated `production/check-document-pack-desktop.png` and `check-document-pack-phone.png`. Updated this Active Task and appended this log. No existing source/master/deck/partner file changed. Catalogue includes format variants/history, not62 independent deliverables. External downloaded framework is linked outside the folder, not copied/installed. Five Claude artifact URLs are historical unverified links from §3.

**Checks:** compiler validates index local links and current external/internal master/output hashes. Browser checked desktop1440×1000 and phone390×844 with no horizontal overflow/errors; search returns the two restricted partner files, zero for unmatched text and62 when cleared. All generated local HTML links resolve. Both viewport screenshots visually inspected. No remote artifact access/parity, new deck audit, Word-app QA or legal/source refresh claimed. No application tests/commit guard needed for this local index-only task. Index/renderer and source docs remain gitignored; no commit, upload, publication, outreach, partner figures copied, duplicate masters or file moves.

**Next:** Hafiz opens `START-HERE.html` and reads the intended document, rather than forwarding the complete index. Owner index contains restricted links and is not a Kota Buku distribution package. Current two documents remain owner-review drafts; Claude deck is separately maintained; commercial offer remains a later reconciled deliverable. No direction decision needed for this compilation.

**Visual correction:** phone inspection revealed narrow table columns breaking document names awkwardly. Updated only the index renderer to stack document rows as readable cards on small screens; reran phone overflow/search and re-inspected screenshot successfully. Rebuilt catalogue after final records/screenshots so inventory hashes describe the final files. Supporting files total183 at this compilation;62 reader-document entries unchanged.

### Claude to Codex: complete deck handoff — 2026-09-07 (written by Claude, supersedes the deck records above)

**Ownership:** Hafiz asked for a full handoff so Codex continues the deck work. From this record on, Codex owns `production/visual-samples/claude/` too. Claude's deck sessions end here; everything below is the state to continue from.

**Where things are (all local-only, gitignored, nothing published, committed or sent):**

- Deck: `production/visual-samples/claude/kota-buku-deck.html` (15 slides, English / Bahasa Melayu switcher, demos on every proposed-screen slide, "i" context card per slide, R resets). Partner copy without the presenter hint: `kota-buku-deck-share.html`. Clean-named copies for sending: `share/Kota-Buku-App-Proposal.html`, `share/Kota-Buku-App-Proposal-EN.pdf`, `share/Kota-Buku-App-Proposal-BM.pdf` (Hafiz is passing these to his partner).
- Source of truth for the deck: `build/deck_content.py` and `build/deck2_content.py` (EN and BM strings; the second overrides the first) and `build/builddeck2.py` (slides, CSS, JS). `kota-buku-deck.template.html` is generated; never hand-edit it. The three-slide sample template `kota-buku-sequence.template.html` is the base the builder rewrites (sample slides 1 to 3 of the deck come from it verbatim, with dictionary corrections applied in the builder).
- Rebuild and check everything: `zsh production/visual-samples/claude/build/runall.sh all` (uses `.claude/skills/doc-design/scripts/build.py` for font embedding and Playwright from `kelas/node_modules` with the installed Chrome; `desktop`, `phone` or `pdf` run one suite). `build/verify_copy.py` checks beat headlines verbatim against the reading draft and scans for forbidden content. `build/offline.js` proves the share copy loads with the network off.
- Records: `README.md` in the deck folder (slide list, the decisions, the reference table, the review change logs, limitations), `review-brief-codex.md` (the brief the Codex review ran from), `review-codex-2026-09-07.md` (Codex's report), `screenshots/deck/` (every slide, both languages, desktop, phone, interacted states, PDF pages), `assets/` (generated images; fal.ai lane 26 in the access map, key file never printed).

**Decisions that shape the deck (all Hafiz, 07/09/2026 unless noted):**

1. Claude's layout system on Codex's cool grey ground (`#f5f5f7`) with light chrome: KOTA BUKU wordmark, centred switcher, plain "Proposed solution", honesty line left, navigation pill with Full screen centre, credits right.
2. Cover in the style of Codex's opening slide: three-line headline "Kota Buku app. More attention to teaching.", teal eyebrow, Teacher / Students / Parents step row, tilted lesson-goal card.
3. Fifteen slides (fourteen merged from eighteen, then the data slide added): cover; who it serves; one topic through the lesson; goal picker; plan; worksheets; students on paper; class view and assistant; admin assistant; data; families; Kota Buku content; practical and protected; delivery; recommendation.
4. Every non-sample slide rebuilt against a Mobbin reference Hafiz chose after the tabs were opened in his browser: Clockwise (who it serves), Function (step section), Apple Mail and Google Drive scan (students on paper), SchoolAI dashboard (class view), PayPal device cards (families, whole phone visible), Wise roadmap (delivery), Runner workflow snapshot (data). Process rule for further design changes: show references first, one slide at a time, Hafiz approves each.
5. Colour rule: step numbers in dark ink circles; teal only for a selection; yellow only for AI drafts.
6. Disclosure placement: the launch boundary lives only on the delivery slide (launch / guided trial / expansion) and in the "i" cards; slide faces show the full proposed experience. One persistent honesty line in the bottom bar.
7. Copy rules for every Kota Buku document: English says "student", never "pupil" (BM "murid" stays); mockups use real-looking fictional data (class 4 Bestari, Cikgu Farah, Aiman Hakim, Nurul Aisyah, Haziq Iskandar, Tan Wei Jie, Priya Devi, Amirah Zulaikha, Adam Firdaus in Form 2 Amanah), never placeholders. "Principal", not "head teacher" (Claude's judgement, not yet confirmed).
8. D11, tiers: the deck stands and the masters follow. Class view, rule-based flags and suggestions, notice and reminder templates and the parent digest are planned for all teachers at launch; plain-language AI analysis, the teacher assistant and AI-written admin drafts are a guided trial with selected teachers at the same launch, the same framing as the full AI-drafted RPH beta. Codex applies this to `product-feature-spec.md` Pillar 4 and 5 tiers, `technical-build-blueprint.md`, `production/deck-reading-draft.md` (beat 06 visual note, beat 11 lanes) and the v0.2 external and internal documents where they state tiers.
9. The reading draft's beat headlines are used verbatim (with the student substitution) on the beat slides; four slides carry non-draft headlines by instruction: the plan slide (a beat 03 body sentence), the class view, the admin assistant and the data slide. Beats 07 and 08 share one slide; beat 10 is one slide; the "i" cards carry the draft's full text for each.

**Reviews run today and what was done:** first Claude adversarial review of the first build (3 blocking, 9 material, 19 minor; all blocking and material fixed); Hafiz's own ten-point design review (all ten addressed, see README "The third build"); Codex adversarial review through the Codex CLI in a read-only sandbox (10 blocking, 8 material, 1 minor: four blocking were the tier conflict, closed by D11; the rest fixed); second Claude adversarial review (1 blocking, 19 material, 15 minor; all blocking and material fixed, minors fixed where cheap); a first-glance test by a fresh agent on screenshots only (its top asks applied: class table simplified at rest, plan sub-line, data slide badges, internet shown as Limited, badge 2 on the shutter, teacher photo recrop). README section "Third-build reviews and fixes" lists each fix and the items deliberately left.

**Checks passed at handoff:** desktop suite (both languages, every slide and interacted state: bounds, clipping, escapes, text below 13 px, overlaps, 6 px proximity, thread crossings, dictionary completeness, console errors, EN/BM difference); phone suite (iPhone 13 viewport, both languages); PDF suite (page size, overflow, chrome hidden, credits per page, appendix packed by height, return to normal); offline load with all five font faces; headline-verbatim script (28 of 28); no em dashes, figures, curriculum codes or award wording. Not done: a native Bahasa Melayu read before external use; a projection test in a real room; any audience test.

**Known limitations to keep stating:** concept illustration, no working app; synthetic examples not reviewed by a teacher; BM written by the model; the PDF is a static export; aria labels are English only; the plan slide keeps its three body callouts and the worksheet tray by Hafiz's earlier choice.

**Next actions for Codex, in order:**

1. Apply D11 and the two copy rules ("student", real-looking names) to the masters, the reading draft and the v0.2 external and internal documents; record the edits in this file.
2. Refresh the compiled index (`START-HERE`) entry for the deck: fifteen slides, the `share/` folder, the build pipeline, the two review reports.
3. Continue Hafiz's one-by-one review of the deck when he raises the next point, using `build/runall.sh` and the reference-first process in decision 4; keep every suite clean before showing him a slide.
4. Arrange the native BM read.
5. No publication, commit, un-ignore, outreach or partner-file edit; both partner files stay read-only; commercial figures stay in the partner pack.

### Codex: D11 document alignment and local package refresh — 2026-09-07

**Scope completed:** latest handoff actions 1–2, plus the requested full existing deck check run. D1–D11/C4 unchanged. This is local document production, not application implementation or distribution approval.

**Every source/edit group:**

- `product-feature-spec.md` §§2/3/6/7/9.2/12: class dashboard and rule-based class flags/patterns are Core; narrative/teacher assistant/admin drafts are same-launch selected-teacher trials. Added explicit AI-admin row and consolidated launch entries. Replaced the synthetic numbered curriculum reference with fictional Aiman Hakim and a non-coded concept; grounding still requires verified authorised sources. Automatic history-based material at scale, handwriting, messaging, textbook and official-interface dependencies are not promoted.
- `technical-build-blueprint.md`, new “Same-launch exposure and evidence controls” subsection before §8: D11 availability, trial access, evidence traceability, teacher approval, missing data, quality review, D7 processing and connectivity requirements. No deployment/readiness assertion.
- `production/deck-reading-draft.md`: English student terminology throughout; realistic fictional-name instruction; beat 06 class-view/assistant visual; beat 11 English/BM launch/trial/expansion copy; opening and beat 03 disclosure instructions now follow protected delivery-slide/i-card placement. D11 source references updated.
- `production/external-kota-buku-document.md`: v0.3 English/BM; chapter 5 D11 individual/group teaching support, chapter 8 tiers/Core summary, Appendix A tier index and Appendix B trial glossary; chapter 3 Cikgu Farah/4 Bestari and chapter 5 Aiman Hakim are explicitly fictional. English student terminology throughout.
- `production/internal-team-sourcebook.md`: v0.3 English/BM; chapters 1/3/4/5/11/12/13 plus feature/decision/acceptance/glossary appendices aligned to D11. Added D11 decision rows, Core versus selected-teacher evaluation checks, all-four-trial acceptance guard and fictional lesson names; English student terminology throughout.
- Both `*-blueprint.md` and `*-evidence.md` records: dated D11/v0.3 override preserving historical approval/research dates; external EXT-07 explicitly corrected. No fresh empirical claim or pricing research.
- `START-HERE.md`: v0.3 editions, fifteen-slide deck, current Codex ownership, partner-copy links, pipeline and review reference; removed stale page counts. `production/compile-document-index.cjs`: recognise clean-named partner deck files as current deck rather than sample history. Regenerated index HTML/inventory.
- Deck `README.md`: current fifteen-slide heading and authoritative current-state guide above historical build records; subsequent dated check note records current PDF counts.
- Deck `build/verify_copy.py`: compare owner-approved final student terminology; exclude font/image base64 from financial-string scanning; accept actual BM credit wording. Six apparent headline misses and base64 price matches were checker artefacts, not deck-copy failures.
- Regenerated both documents' HTML/PDF/DOCX/intermediate/manifests and checker screenshots; deck template/HTML/share variant/PDF and suite screenshots regenerated only through the established pipeline. Refreshed the three clean-named `share/` copies from regenerated outputs. Added diagnostic D11 PDF images and English deck montage. No hand edit to generated template, dictionaries, protected i-card text, honesty line or delivery layout.
- Both document acceptance files receive this run's evidence and remaining limits.

**Ranked findings and disposition:**

1. Material: older sources contradicted D11 by deferring class views, analysis and teacher assistant. Corrected as above; D11 is owner-approved proposal scope, not readiness evidence.
2. Material: independent review caught remaining English/BM evaluation and trial-acceptance mismatch, plus beat 03 preview-label placement. Corrected; targeted reviewer recheck found 0 blocking / 0 material. Its remaining minor BM evaluation elaboration was also matched and the internal editions regenerated/rechecked.
3. Maintenance: deck README mixed build generations and START-HERE still sent the owner back to Claude. Added explicit current authority and maintained historical records rather than rewriting history.
4. Maintenance: `runall.sh all` does not copy regenerated outputs into clean-named `share/` files. Copies refreshed explicitly. Also, script exit 0 alone is not sufficient QA proof: inspect actual suite finding/error payloads.
5. Still for human review: native BM reading, real projection/audience comprehension, “principal” terminology confirmation. Existing source rights, age policy, residency/capture/curriculum validation and legal/controller schedules remain open. No decision reopened.

**Fresh evidence:** external/internal check scripts passed desktop and phone EN/BM language/navigation/overflow, source/output freshness and PDF/DOCX text/table/heading completeness. External PDFs remain 17 pages per language; internal PDFs are now 27 per language. Representative changed browser tables and PDF pages visually inspected. Full deck `zsh build/runall.sh all`: desktop findings 0, errors []; phone results [], errors [], context card fits; PDF bad [] in both languages, errors [], 18 EN pages / 19 BM pages including context appendices. Offline share check: zero failed requests/errors, five font faces loaded, navigation 1/15 to 15/15, BM switch and no presenter hint. Source-headline checks 28/28, no financial/code/award matches after excluding embedded assets, both credit/honesty strings present. English 15-slide montage and class-view/delivery slides inspected. These are document/concept checks, not software validation or complete renewed native-language/projection QA.

**Integrity:** both partner source hashes unchanged from prior record. Concept docs remain gitignored; unrelated tracked changes untouched. No publish, commit, un-ignore, outreach, app build, secret/live/.workflow-rollout access.

**Artifact refresh for Claude, only if Hafiz later requests republication:** feature-spec reading artifact needs revised §§2/3/6/7/9.2/12 and student wording; blueprint artifact needs D11 exposure subsection and student wording; handoff artifact needs this log. Research/data masters unchanged by this pass, so no new content-driven republication request for those two. Existing remote artifacts were not opened, edited or claimed current. Local v0.3 document editions and deck share files are already regenerated; Claude is not a prerequisite.

**Next:** continue Hafiz's one-by-one deck review when he raises the next point. Show reference options first, let him choose, then edit one slide through the dictionaries/builder and rerun checks. No new slide design was selected on his behalf in this pass.

### Codex: cover supporting copy, two desktop lines — 2026-09-07

Hafiz approved replacing the cover's company-description sentence with the assistant proposition, required no em dash, and requested two rows. The long discussed sentence measured four lines at the existing 28px/780px; tightened it without shrinking type or changing layout.

- `build/deck2_content.py`, `t0s` English: “An AI assistant to prepare lessons, understand students, handle daily tasks and keep parents informed.” BM: “Pembantu AI untuk menyediakan pelajaran, memahami murid, mengurus tugas harian dan memaklumkan ibu bapa.” Sifututor/Learnest Lab credits, headline, fractions card, honesty line, i cards and delivery boundary unchanged.
- Added `build/check-cover-copy.cjs`: exact bilingual copy, no em dash, exactly two lines at 1920×1080 and 1280×720, unchanged desktop 28px type, no overflow/clipping. At 390×844 both languages naturally use three lines at existing 17px mobile type. All six cases pass; screenshots saved under `screenshots/cover-copy-*` and desktop/BM plus phone/EN inspected.
- Regeneration uses `zsh build/runall.sh all`, never hand-edits the generated template. No next-slide edit, publication, commit, application build or partner-source edit. Next remains Hafiz's cover acceptance or next slide comment.

Cover-copy check completed 2026-09-07: desktop findings 0/errors []; phone results []/errors []; PDF bad []/errors [], 18 EN and 19 BM pages. Offline check clean. The new English/BM cover subheading is exactly two desktop lines at unchanged 28px, three natural phone lines; `build/check-cover-copy.cjs` checks all six language/viewport cases. Clean-named HTML/PDF share copies refreshed after generation. Index/inventory refreshed. Other slides unchanged; no publication or commit.

### Codex: slide 2 role previews and deck-wide rules, 2026-09-07

Hafiz approved short optional click-to-explore experiences after the Genially/Storylane references. His comments now govern the whole deck: specific plain benefit-plus-feature copy, no em dashes, no added icons/logos, teacher insights from recorded work, paper/online practice, teacher-reviewed parent insights, meaningful clicks, readable static/PDF content and realistically filled photo screens. Significant redesign remains reference-first, one slide at a time. Rules stored in Koda.

Implemented: slide 2 captions/subline and paper-plus-online label in build/deck2_content.py, English/BM, with explicit device-free classroom participation and permitted own-device access. New build/role-previews.html provides teacher rule-based record reveal, paper/online fraction practice with corrective feedback, and parent progress/next-practice tabs. All examples fictional; teacher authority retained. No new backend feature, universal generative-assistant access or measured benefit implied.

build/builddeck2.py injects the editable partial and opens it from role cards. Keyboard activation, native modal focus containment, Back/Escape focus restoration, R preview reset, navigation isolation and PDF closure implemented. PDF omits the click-only instruction; benefit captions remain. Generated template is regenerated, not hand-edited. Original i cards, honesty, delivery boundary, photos and other slide content unchanged.

Added build/check-role-previews.cjs for all roles/actions, EN/BM, desktop/phone, answer correction, keyboard/Back/Escape/reset, overflow and PDF closure. Updated shotdeck.js/shotdeckm.js to check modal opening and close it before continuing. Focused tests pass all four language/viewport combinations. Full desktop/phone/PDF run zero findings/errors; focused role/PDF checks rerun after modal-centering/PDF-copy refinements. Screenshots/roles-* preserve overview and interacted states; teacher desktop and student phone inspected. Share copies and inventory refreshed after final exports.

Still pending: realistic device-screen photo composites and applying the same rules to the remaining slides through owner review. No image edits in this slice. Native BM reading, subject validation and projection/audience judgement remain open. No publication, commit, outreach, partner edit, app build or secret access.
