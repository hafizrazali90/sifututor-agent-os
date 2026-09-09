# AI Classroom — Product & Feature Specification (Kota Buku Proposal)

**Authority, 2026-09-06:** co-branded Kota Buku app, delivered by Sifututor, powered by Learnest Lab; exact legal entity to be confirmed by Hafiz. D8 supplies teacher devices only, without cancelling Pillar 6. D10 puts all programme commercial figures in the [partner pack](partner/SEPADU-v1.0-Founder-Briefing.md); these specifications stay figure-free. [Review §2/§10](partner/SEPADU-review.md). **C4 decided by Hafiz, 2026-09-06: blend teacher-workload reduction with AI-classroom capability** (handoff §7 C4). The six pillars below explain both intended benefits; scope, tiers and evidence limits are unchanged.

**What this is:** the actual product definition — what to build — synthesized from [research-findings.md](research-findings.md) (pedagogy evidence, Malaysia market/policy context) and [technical-build-blueprint.md](technical-build-blueprint.md) (architecture, cost, and deployment constraints). Those two docs cover *why* and *how*; this one covers *what*.

**Framing constraint that shapes everything below:** in the redONE/Kota Buku programme, the iPad goes to the **teacher**, not the student or parent. There are ~30 students per teacher and none of them get a device through this programme. That means:
- Everything in Pillars 1–5 is a **teacher-operated tool**, even where it produces something a student experiences (e.g. a worksheet a teacher generates and prints/projects, not a student logging into their own app).
- Pillar 6 (parent/student access) **cannot live on the teacher's iPad** — it needs a separate, lightweight surface parents and students reach on their own phones. This is a second, smaller product, not a screen inside the teacher app.

---

## Table of contents

1. [Build status: what Kelasapp actually gives us](#1-build-status-what-kelasapp-actually-gives-us)
2. [MVP philosophy — why this isn't "build all 6 pillars at once"](#2-mvp-philosophy)
3. [Pillar 1 — Teacher data collection on students](#3-pillar-1--teacher-data-collection-on-students)
4. [Pillar 2 — Conducting class and activities](#4-pillar-2--conducting-class-and-activities)
5. [Pillar 3 — AI content generation](#5-pillar-3--ai-content-generation)
6. [Pillar 4 — AI teaching assistant / personalization](#6-pillar-4--ai-teaching-assistant--personalization)
7. [Pillar 5 — Adjacent efficiency features](#7-pillar-5--adjacent-efficiency-features)
8. [Pillar 6 — Parent/student access (separate surface)](#8-pillar-6--parentstudent-access-separate-surface)
9. [Data collection & AI-advice workflow — the actual mechanics](#9-data-collection--ai-advice-workflow--the-actual-mechanics)
10. [Kota Buku content integration — a specific feature, not a footnote](#10-kota-buku-content-integration--a-specific-feature-not-a-footnote)
11. [Competitive feature benchmark — what already exists elsewhere](#11-competitive-feature-benchmark--what-already-exists-elsewhere)
12. [MVP scope recommendation](#12-mvp-scope-recommendation)
13. [What NOT to build first](#13-what-not-to-build-first)

---

## 1. Build status: what Kelasapp actually gives us

A direct codebase survey of `kelas/` (2026-09-06) corrects an earlier assumption. Kelasapp is **not** a foundation this product extends — it's a mature, separate web SaaS whose *patterns* are worth referencing but whose *code* carries over nowhere.

**What Kelasapp actually is**: Next.js 16 + React 19 + TypeScript, PostgreSQL/Drizzle, Better Auth — a fully web-based, always-online tuition-centre billing and attendance system. No `ios/`, no Swift, no native mobile code of any kind exists in the repo.

**Confirmed absent — 100% greenfield regardless of Kelasapp's existence:**
- **Native iPadOS app**: zero existing code. Everything in Swift/SwiftUI starts from nothing.
- **Offline-first architecture**: no service worker, no local cache, no sync engine, no PWA config — nothing. This is new architecture work end to end.
- **AI/RAG integration**: no LLM SDK, no vector DB, no AI API calls anywhere in the codebase today. Every AI feature in Pillars 3–4 is new work with nothing to inherit, not even an API-calling convention.
- **Curriculum/DSKP modeling**: Kelasapp's "taxonomy" feature (`programs`/`levels`) is free-text labels an operator types in ("Iqra' 3", "SPM") — not a structured subject/form/TP1-6 hierarchy. There is no lesson-plan, RPH, worksheet, or quiz feature anywhere.
- **Real messaging/notifications**: the only "messaging" is a manual WhatsApp click-to-chat link generator (`src/features/messaging/wa.ts`) — the operator taps it to open WhatsApp with a prefilled message. No push notifications, no in-app chat, no automated sends.
- **Multi-tenant data model fit**: `orgSettings`, `classes`, `enrollments`, and `teachers` all have billing/payout fields (monthly fee, discount, per-class teacher rate via `classes.teacherRatePerSession` + `payModel`; `teachers.grade` is a manual A/B/C quality rating, not a pay grade — wording corrected after adversarial review) baked directly into the core tables — this is billing-centric by construction, not a loosely-coupled org/class/student model. A KPM school hierarchy (school → form → subject → DSKP standard) doesn't map onto it without discarding most of the schema.

**What's genuinely reusable — as design patterns, not code:**
- `src/features/attendance/service.ts` — the lazy-session-materialization pattern (a concrete `sessions` row is only created when attendance is actually taken, not pre-generated for every calendar date) plus one-attendance-row-per-student-per-session modeling is a sound reference for the new attendance feature's schema design.
- `src/features/parent/service.ts` — the cross-tenant guardian-identity-by-verified-email linking pattern is a useful reference for how the separate parent/student web portal should handle identity.
- General engineering discipline (E2E test coverage, org-scoping conventions, i18n setup) as process reference, not code.

**What this means for the proposal**: Kelasapp gives Sifututor team credibility and two proven design patterns to point to — it does not reduce the actual build scope for anything that differentiates this product. The pitch should be honest about this: strong engineering track record, genuinely new build for this specific product.

### LLS (Learnest LMS) — closer, but still not a foundation

A direct codebase survey of `lls/` (Laravel 11 backend) and `lls-frontend/` (React SPA), live at lms-sifu.tutorla.tech, found genuinely more relevant assets than Kelasapp — LLS already runs an OpenAI-powered "AI tutor" and BigBlueButton live classes — but the honest picture is still "valuable engineering patterns, not a product foundation."

**The AI tutor is not a hidden RAG asset.** It's a well-guardrailed prompt-to-OpenAI wrapper (`AiChatController` + `TutorPromptService`, gpt-4o-mini) whose only content-grounding is pasting a single lesson's video-caption transcript into the system prompt — no chunking, no embeddings, no similarity search, no curriculum-standard tagging. Building real DSKP-grounded RAG (per doc 2 §10) is still 100% new work.

**What's genuinely reusable — as patterns, not code:**
- **The AI engineering discipline in `app/Services/Adaptive/`** (`StudyPlanGenerator`, `WeaknessReportGenerator`, `AiQuizGeneratorService`): structured-JSON-output + retry + a **hallucination guard that validates every AI-generated ID against the real database** + a `DeterministicFallbackReportBuilder` for when AI calls fail. This is the single most valuable transferable pattern found across both codebases — directly applicable to grounding AI-generated lesson plans/worksheets against a real DSKP content ID list.
- **`AiCostRecorder`** — per-call token/cost logging (hardcoded gpt-4o-mini pricing). Essential pattern at 182,000-teacher scale, not much code to port.
- **`BBBService.php`** — a clean timeout/auth/typed-exception wrapper around BigBlueButton, and the underlying `LiveClass`/`LiveClassController` pattern (one teacher as moderator, all enrolled students as attendees) is genuinely **teacher-led, one-to-many** — the right shape for a "conduct a live class" feature, even though a native iPad app would use BBB's native SDK, not this web join-URL flow.
- **`Topic` tree + `StudentTopicMastery`** (continuous 0-100 mastery score per topic): directionally similar to a mastery model, but would need real remodeling into DSKP's discrete TP1-6 bands and Subject→Form→Content-Standard hierarchy — a starting schema shape, not a reusable one.
- **`ParentDashboardController`**: a real, working read-only parent view (magic-link + authenticated modes, per-child progress/quiz summaries) — useful as an API-surface reference for the separate parent/student portal in Pillar 6.

**Confirmed absent, same as Kelasapp:**
- No native mobile/offline capability anywhere (confirmed: no Capacitor/Cordova/React Native/service worker in `lls-frontend`; the only "offline" reference in the whole frontend is a marketing copy string).
- **No School/Class/Teacher-roster concept at all.** LLS has no `Organization`, `Tenant`, `School`, or `Class` model — it's a flat two-sided tutor marketplace (individual tutors own courses, individual students self-enroll). This is the single biggest structural mismatch for a KPM-schools deployment, where the natural unit is School → Class → Teacher → Students provisioned in bulk, not self-enrollment into a course catalogue.
- Grading is exact-match MCQ/true-false only — no free-response/essay auto-grading exists, which the new product needs for worksheet grading.
- No teacher-to-parent messaging — only one-way, read-only parent dashboards.

**What this means for the proposal**: LLS is the stronger of the two existing systems to point to for AI/live-class engineering credibility, but neither it nor Kelasapp reduces the actual build scope for the school/class/roster model, curriculum grounding, or offline-first architecture that differentiate this product. The pitch's honest framing is: Sifututor has shipped production AI-cost-governance and live-classroom infrastructure before (LLS) and production attendance/guardian-identity systems before (Kelasapp) — this proposal combines that engineering maturity into a new, purpose-built product, not a repackaging of either.

**Readiness correction, 2026-09-06:** the partner readiness-map claim that an AI-enabled RPH generator already exists is **withdrawn as a claim for this package**. The audits above of `kelas/`, `lls/` and `lls-frontend/` found no existing RPH generator; quiz/study-plan generation is not RPH generation. The module is new work. D4 still requires a shared backend at launch, Level 1 for all teachers and Level 2 full AI-drafted RPH as a guided pilot beta **at launch**, not a later build. Source: this §1 audit and [partner review §8.3](partner/SEPADU-review.md#83-does-the-rph-generator-do-what-we-told-kpm-it-does-pack-113). Partner files themselves are unchanged.

## 2. MVP philosophy

Two research findings directly determine how ambitious the first build should be:

- **Every failed national device programme researched (Turkey, Indonesia, Kenya, Rwanda) shipped hardware before software/content/training was ready** — devices arrived, meaningful use never materialized. The inverse failure mode also matters: trying to ship all 6 pillars, fully realized, in v1, without a validated delivery budget, is how a proposal becomes a FATIH-style "building the muscle, not the soul."
- **Uruguay's Plan Ceibal (the one clear success case) won on continuous iteration over years, not a big-bang launch** — it started narrower and kept adding teacher-facing tools after observing real usage.

So the feature list below is written in three tiers per pillar: **Core (MVP)**, **Fast-follow (v1.x)**, **Later (needs more budget/maturity)** — not because the vision should be small, but because the pitch and the build should both be honest about sequencing. D11 (Hafiz, 2026-09-07; handoff §13) adds same-launch selected-teacher guided trials for plain-language AI analysis, assistant conversation and AI-written admin drafts alongside D4 full-RPH beta. Core class views/flags remain rule-based, not predictive or diagnostic.

---

### 2.1 Cross-cutting Core requirements — adopted 2026-09-06

- **Accessibility:** WCAG 2.2 AA target for the web surface and applicable native-app interactions; native iPad accessibility testing (VoiceOver, text scaling, contrast and input alternatives) complements the web standard. This is an acceptance requirement, not a compliance claim. [W3C WCAG 2.2](https://www.w3.org/TR/WCAG22/); partner G9 / review §10 C12.
- **First-week onboarding and in-app coaching**, with BM, English, Mandarin and Tamil parity: guide the teacher through first attendance, first mark and first RPH. Keep school-level champions and ongoing coaching in the Core adoption plan; IPGM/IAB are potential endorsement channels, not confirmed delivery capacity. Measure completed workflows and quality, not just logins, in the partner’s first two evidence gates; thresholds and resourcing need agreement. [Review §8.2](partner/SEPADU-review.md#82-can-182757-teachers-be-trained-in-eight-months-pack-112); blueprint §8.1.
- **Phase 1 has no KPM system integration.** Standalone register and generic CSV/PDF exports remain Core; idMe/APDM/SPPB connectors are later, permission-dependent, separately priced items in the partner pack. Do not promise removal of re-keying.

## 3. Pillar 1 — Teacher data collection on students

*Longitudinal data on each student's learning, so patterns emerge over the year, not just at exam time.*

| Feature | Tier | Basis |
|---|---|---|
| **Formative check-ins** (exit tickets, quick quizzes, bell-ringers tied to a specific DSKP learning standard) | Core | Doc 1: Edulastic/Formative/i-Ready pattern — i-Ready has the strongest independent evidence in the whole pedagogy research (0.14–0.24 SD, ESSA Tier 2/3) |
| **MCQ auto-grading** (ticked/bubbled answers, in-app live quizzes, or scanned answer sheets) | Core | Doc 2 §3: deterministic exact-match logic, not generative AI — near-zero cost, runs on the cheapest device tier, no accuracy gap vs. cloud. Scan-based capture of *bubble/tick* MCQ is the proven paper-to-digital path (ZipGrade-style). |
| **Handwritten fill-in-blank / numeric answer auto-grading from scanned paper** | Fast-follow (re-tiered after adversarial review) | Grading logic is still deterministic, but the *capture* depends on OCR of children's handwriting in Bahasa Malaysia. Verified 2026-09-06: Malay is absent from Apple's developer Vision OCR API in every runtime dump found (present only in consumer Live Text), and no independent handwriting benchmark includes Apple Vision or covers Malay/children's handwriting at all. Realistic engine is cloud OCR with Malay support (Google/Azure) — an unresolved Malaysia-resident processing requirement under D7 for images of student work; foreign inference is not authorised. See §9.1. Ship after a real classroom pilot measures accuracy and time-per-class-set on the chosen engine. |
| **Attendance — standalone in-app register first** | Core | The register itself has no external dependency. Doc 1 §1.2/§8: APDM exists and is disliked for duplicate entry, so the design goal is to *not* add a third parallel entry. Fallback if no APDM path exists: standalone register + generic CSV/PDF export for review. APDM-compatible import/export and any reduction in re-keying remain conditional on a KPM-approved format and channel. |
| **APDM sync** (read/write integration with KPM's system) | Fast-follow, dependent on KPM (re-tiered after adversarial review) | Neither research doc found any evidence an APDM integration API or export mechanism exists (Doc 1 §1.2, §3.5, §7.1 — no documented vendor pathway into KPM systems at all). This is a question to put to KPM directly, not an assumption to build on. |
| **Per-student mastery tracking against DSKP's TP1–6 scale** | Core | Doc 1 §2.2/§2.4; Doc 2 §4 — TP levels are what KPM already uses (PBD), so this isn't a new taxonomy for teachers to learn, it's digitizing one they already work in |
| **Class-level dashboard** (recorded learning evidence by topic/standard, not a diagnosis or overall grade alone) | Core — D11, 2026-09-07 | Doc 1 §6.1 — Star/i-Ready pattern: growth/mastery views, not just raw scores |
| **Essay/free-text grading assist** | Later | Doc 1 §6.5, Doc 2 §3: genuinely needs cloud AI, has a documented central-tendency bias (AI graders under-reward excellent work, under-penalize weak work) — should launch as a *teacher-reviewed suggestion*, never auto-final |
| **Early-warning/at-risk flagging** | Later | Doc 1 §6.5: prediction accuracy is well-studied but evidence that flagging *actually reduces* absenteeism/dropout is thin — build this once there's a real intervention workflow behind it, not just a red flag with nowhere to route it |

---

## 4. Pillar 2 — Conducting class and activities

*Live tools for the actual lesson, not just planning before or grading after.*

| Feature | Tier | Basis |
|---|---|---|
| **Live poll/quiz during class** (project from iPad or students answer via their own phones if available) | Core | Doc 1 §6.2: Kahoot! has the strongest evidence of anything researched — an independent meta-analysis found 0.72 SD in the cited study; **source/measure needs verification before external use**, and SD cannot be converted into a universal letter-grade gain |
| **Simple gamified activity templates** (points, streaks — kept intentionally simple) | Fast-follow | Doc 1 §6.2 flags ClassDojo-style behavior tracking as **genuinely mixed evidence** — a 2025 paper explicitly critiques it. Keep this light-touch and optional, don't lead with it |
| **Interactive lesson delivery from Kota Buku content** (turn a static e-textbook page into a poll/discussion prompt) | Fast-follow | Ties Pillar 2 directly to §10 (Kota Buku content integration) — this is likely the single most distinctive feature vs. any generic classroom tool, because it's grounded in content Kota Buku already owns |
| **Offline core: downloaded content, register and local grading; new cloud AI and networked live responses require connectivity** | Core, non-negotiable | Doc 2 §2: rural connectivity is a documented, recurring failure point across every case study researched (Rwanda's charging/connectivity issues, Kenya's high data costs, Malaysia's own teacher pain-point research on DELIMa/connectivity). This can't be an afterthought feature — it's an architecture requirement from day one |

---

## 5. Pillar 3 — AI content generation

*Producing material for the whole class or differentiated per student.*

| Feature | Tier | Basis |
|---|---|---|
| **AI worksheet/quiz (checkable-item) generation, grounded in the public DSKP documents** — teacher picks subject/form/learning standard, app generates MCQ/short-answer items and a printable worksheet | Core (with honest evidence framing) | This is the AI-generation task with the *closest* Malaysian evidence: the 2025 paper (Doc 2 §10) generated Form 1 Math MCQs in Bahasa Melayu and found 92-96% retrieval-validity grounded vs. 12-15% ungrounded — but that study used one chapter's teacher notes (not DSKP), an automated and self-referential validity metric, and **no human validation**. So the evidence supports "grounding matters a lot for checkable items," not "this is proven with teachers." It stays Core because it is the *least* risky AI task (checkable output a teacher can eyeball), DSKP documents are public (bpk.moe.gov.my) so it needs **no Kota Buku content licence**, and it is the natural first RAG workload to prove in the field. Still requires the RAG pipeline to be built (new work, Doc 2 §10). **A teacher-validation pilot on generated items is a pre-launch requirement, not optional.** |
| **Lesson plan (RPH) authoring — template-assisted, with the shared RPH library** | Core | RPH is a real, recognised teacher workflow (SMAP's RPH module and CikguAI both prove demand, Doc 1 §4). A structured RPH template (13-section format) that the teacher fills, with DSKP standards selectable from the taxonomy and links to textbook references, plus the Pillar 5 sharing library — **no AI generation or content-licence dependency**, so it can ship day one. |
| **AI-drafted lesson plan (RPH) generation, RAG-grounded in DSKP (+ Kota Buku textbook content as it arrives)** | **Core backend, staged release — DECIDED by Hafiz 2026-09-06 ("Level 2, guided beta at launch")** | Doc 1 §6.3 (MagicSchool/Curipod/Khanmigo pattern) shows the category is real. The adversarial reviewer's three concerns — (1) no Kota Buku content licence yet (Doc 2 §1); (2) a production RAG + validation pipeline that is 100% new work; (3) the Malaysian paper evaluated *MCQ* generation using automated metrics, not teacher-validated correctness or long-form plans — are handled by **exposure, not deferral**: this runs on the *same* grounding pipeline as the checkable-item row above (it is a second output mode, not a second system), so it is built from day one; it starts on the public DSKP documents (no licence dependency); and at launch it is switched on as a **guided beta for pilot teachers**, with quality measured before general release. The template-assisted RPH row above is what every teacher gets on day one. |
| **Worksheet generation grounded in Kota Buku's own textbook pages** (select a page/chapter → generate) | Fast-follow, dependent on Kota Buku content access | The most distinctive Kota-Buku-specific feature (§10), but it cannot ship until their content is licensed and ingestible — an open question, not a given. Doc 1 §6.3 (Diffit pattern: 96% of surveyed teachers said it saves time, 93% said it helps differentiate). |
| **Reading-level differentiation** (same content, adjusted for a weaker/stronger student) | Core | Doc 2 §3: this is one of the *better* on-device-feasible tasks (small quality gap vs. cloud on text-simplification specifically, per the benchmark cited) — a good candidate to run cheaply even on lower-tier hardware |
| **Language parity: BM, English, Mandarin and Tamil from day one**, including UI, generated output and onboarding | Core | Adopted requirement from partner G8 / review §10 C11, 2026-09-06; not proof of translation/AI quality. Validate each language and curriculum; DLP rules remain school/subject-specific, not a universal legal language mandate. |
| **Per-student differentiated material at scale** (not just "easier/harder" but genuinely tailored to that student's tracked weak topics from Pillar 1) | Fast-follow | This is where Pillar 3 and Pillar 4 connect — differentiation quality depends on Pillar 1's data existing first, which is why it's sequenced after core content generation, not before |
| **Grading rubric generation** | Fast-follow | Doc 1 §6.3 — standard MagicSchool/Khanmigo feature, lower complexity than content generation itself |

---

## 6. Pillar 4 — AI teaching assistant / personalization

*This is the "customize learning, track progress/strengths/weaknesses, recommend a plan" pillar — the most evidence-contested one, and the one to be most honest about in the pitch.*

| Feature | Tier | Basis |
|---|---|---|
| **Per-student strength/weakness summary** (derived from Pillar 1 data, presented to the teacher, not auto-acted-on) | Core | Doc 1 §6.4: the strongest evidence found anywhere (Carnegie Learning/MATHia, DoE-funded RCT, nearly doubled year-2 math growth) is for **teacher-mediated, blended** use — not an autonomous AI making decisions. This should be built as a **teacher decision-support tool**, not an autonomous recommender |
| **Simple rule-based remediation suggestions** ("recommend worksheet on topic X because score < threshold on the last 2 assessments") | Core | Doc 2 §3: this is deterministic logic again — cheap, explainable, no hallucination risk, and directly matches the TEAS paper's "Verifiability" pillar (a recommendation the teacher can trace back to specific data, not a black box) |
| **AI-generated learning-plan narrative** ("here's why, in plain language, and what to try next") | Same-launch guided trial, selected teachers — D11 | Doc 1 §6.4: Khanmigo's own RCT found the AI layer's measured effect (≈0.06–0.08 SD/year as recorded in research-findings §6.4; 0.14 SD is a hypothetical full-engagement estimate, not the measured result; NBER primary fetch unavailable in this review) "resembles gains from Khan Academy practice *without* AI" — the generative narrative layer is a real feature but shouldn't be oversold as the source of impact; the underlying data/practice loop is |
| **Chat-based teaching assistant for the teacher** ("how do I explain fractions to a struggling Year 4 student") | Same-launch guided trial, selected teachers — D11 | Doc 1 §6.3/§6.4 — this is a genuinely well-evidenced category (Khanmigo for Teachers, SchoolAI) but Doc 2 §3 confirms it **requires cloud, always** — no device tier makes this feasible on-device |
| **Rule-based class-wide patterns and flags** (shared difficulty in recorded assessments; teacher chooses whether to reteach) | Core — D11 | Natural extension of Pillar 1's mastery tracking; higher value than per-student narrative because it changes what the *whole class* does next, not just one student |
| **Fully autonomous adaptive learning path** (the AI decides what a student does next with no teacher step) | **Do not build this as MVP or possibly at all in v1** | Doc 1 §6.7 (RAND: "evidence of efficacy for blended instructional models is mixed"; EEF: technology should supplement, not replace, teacher-led interaction) — the evidence base does not support removing the teacher from the loop, and doing so would also be the single biggest PDPA/child-safety exposure in the whole product (per Doc 1 §3) |

---

## 7. Pillar 5 — Adjacent efficiency features

*Everything that isn't core teaching but saves real teacher time — and per doc 1's teacher-pain-points research, time is the actual bottleneck, not lack of tools.*

| Feature | Tier | Basis |
|---|---|---|
| **Parent communication templates/automation** (absence notices, homework reminders, progress summaries — pre-drafted, teacher approves/sends) | Core | Doc 1 §6.5: vendor case studies report meaningful time savings here, and it directly addresses the documented Malaysian teacher-workload/burnout finding (admin/paperwork flagged as the primary exhaustion source) |
| **AI-written administrative drafts** (notices, reminders and summaries from authorised records; teacher reviews/edits before sending) | Same-launch guided trial, selected teachers — D11, 2026-09-07 | Owner-approved proposed scope, not evidence of readiness. Template-based notices/reminders and curated parent digest remain Core for all teachers; no autonomous sending. |
| **APDM-aware attendance sync** (see Pillar 1) | Fast-follow, dependent on KPM | Same rationale — reduce duplicate entry, the single most concrete, quotable Malaysian teacher pain point found (the 47.5%/32.6% duplication-agreement statistic, pending primary-source verification per doc 1) |
| **RPH/lesson-plan library and sharing between teachers** (SMAP's own RPH module already proves teachers want this — "staff-created templates other teachers reuse") | Core | Doc 1 §4.1: this is a proven, non-AI feature already validated by a real competitor's usage pattern |
| **Auto-grading for handwritten work (OCR-based)** | Fast-follow | Doc 1 §6.5, Doc 2 §3: Vision framework OCR is mature for printed text, but **Malay is not in the developer OCR API's supported list per every runtime dump found (verified 2026-09-06)** — it appears only in the consumer Live Text feature. Plan on a cloud OCR engine with Malay support for this feature, subject to validated Malaysian processing under D7; foreign inference is not authorised; confirm the iOS 26 Vision language list in Xcode before ruling Apple's engine in or out. Not a headline feature until piloted. |
| **SEL/behavior tracking** | Later, and cautiously | Doc 1 §6.5: the pedagogy (CASEL) is well-evidenced, but **tracking tools specifically lag the research**, and doc 1's competitor research found a 2025 paper explicitly critiquing ClassDojo-style tools for this exact category. Don't lead with this |

---

## 8. Pillar 6 — Parent/student access (separate surface)

*Since parents and students don't get an iPad through this programme, this is architecturally a second, lighter product — most realistically a mobile-optimized web app (matching the pattern already used for Sifututor/Nakngaji assessment delivery, which avoided building duplicate native screens).*

| Feature | Tier | Basis |
|---|---|---|
| **View-only progress summary, teacher-curated** (not raw data dump) | Core | Doc 1 §6.6: research explicitly favors the Seesaw model (teacher-approved content only) over the PowerSchool model (raw SIS data) as the safer default, especially for younger children |
| **Attendance and announcement visibility** | Core | Standard, low-risk, already-expected feature (per SMAP's own parent app, which does exactly this) |
| **Age-gated data visibility** (a Std 1 parent sees less/different data than a Form 5 parent or the Form 5 student themself) | Core, and a genuine design decision | Doc 1 §6.6: **no existing research prescribes this** — this is an open design question the product has to answer itself, not something to copy from a competitor. Recommend: younger bands (Std 1–3) show curated highlights only to parents, no student login at all; older bands (Form 4–5) give the student their own limited login alongside the parent's, given documented research on adolescent autonomy/overprotection tension |
| **Time-boxed/digest visibility rather than continuous real-time tracking** | Core | Doc 1 §6.6: this is the one concrete compromise pattern the research actually found evidence for ("limiting access to designated times can preserve student independence while keeping parents informed") |
| **Direct messaging with teacher** | Fast-follow | Standard in every competitor researched (Seesaw, ClassDojo, SMAP) |
| **Full raw gradebook/assessment history access** | Later | Higher PDPA/consent complexity (doc 1 §3), and not clearly better for younger students per the age-appropriateness research — build the curated version first, add raw access only if actually requested |

---

## 9. Data collection & AI-advice workflow — the actual mechanics

**Non-punitive by contract (G1/G2, adopted 2026-09-06):** individual teacher telemetry is visible only to that teacher and their immediate school leader; above-school teacher reporting must be aggregated/anonymised, without individual drill-down. AI advice must not feed appraisal, disciplinary decisions or rankings. Put these restrictions in the contract and access controls, not just interface wording. Exceptional service/security access is minimised and audited, not a teacher-performance reporting route. Student-record access follows the separate controller-authorised tiers in data spec §7. [Partner review §10 item 6 / pack G1–G2](partner/SEPADU-review.md).

> **Field-level specification lives in [data-collection-spec.md](data-collection-spec.md)** (added 2026-09-06 after Hafiz's requirement to capture every learning data point for later government use): the Std 1–Form 5 data timeline, what each KPM system already holds (read, don't duplicate), what no system captures (the app's unique layer), the event model, what is deliberately *not* collected, and the governance layer (KPM controller, processor-only operation under the confirmed Sifututor contracting entity with Learnest Lab visible as technology (legal schedule pending; data §7.1), access tiers, consent channel, audit). This section stays the workflow narrative.

*This section exists because "collect data on students" and "AI gives the teacher advice" (Pillars 1 and 4) are meaningless without a concrete answer to: how does data actually get INTO the app, and how does it actually turn INTO advice? The single constraint that shapes every answer below: only the teacher holds a device. Students don't. So this is a teacher-mediated capture problem, not a self-service one — the app must make it fast for one adult to capture data on ~30 students, not wait for each student to log in somewhere.*

### 9.1 Three collection channels, by data type

**1. In-class formative checks (fastest, richest data)**
- Live MCQ/quiz polls run from the teacher's iPad during the lesson (Pillar 2). **Open capture gap (2026-09-06):** students have no device, so the fast, student-attributed response route is not specified. Once a response is reliably captured, answer-key grading is deterministic; do not promise instant per-student capture before validating that route.
- Every question is tagged to a specific DSKP learning standard **at creation time** (whether teacher-authored or AI-generated per Pillar 3), so each answer becomes a timestamped, standard-tagged data point: *this student, this standard, right/wrong, this date.*

**2. Homework and paper tests (the harder, more common case, given no per-student device)**

*Calibrated after adversarial review: the earlier draft presented handheld photo capture + handwriting OCR as a proven workflow. It is not — it is plausible but unvalidated, and the Gradescope citation was a mismatch. The honest breakdown by tier:*

- **[MVP] Bubble/tick MCQ answer sheets, captured by iPad camera**: the teacher photographs each answer sheet (or the app's own printed answer template). Mark detection on printed bubbles/boxes is the *proven* paper-to-digital path — this is what ZipGrade-style tools do with a phone camera at classroom speed. Grading is exact-match, zero AI cost (doc 2 §3). This is the reliable Core capture channel.
- **[Fast-follow — needs a real pilot first, and almost certainly needs cloud OCR, not Apple Vision] Handwritten fill-in-blank / numeric answers via OCR**: Apple's Vision framework is mature for *printed* text (doc 2 §5). But a targeted verification (2026-09-06) found that **Malay ("ms") does not appear in the developer-facing `VNRecognizeTextRequest` supported-language list in any runtime dump located** (the most recent found — macOS 14.4-era, `.accurate` mode — lists 16 languages, none Southeast Asian Latin-script; `.fast` mode only six), and passing an unsupported code throws rather than degrading. Malay *is* listed for Apple's consumer **Live Text** feature (24 languages, iOS/iPadOS 26) — a different surface that apps cannot call — and a developer building on Vision confirms his app trails Live Text's list. Whether the iOS 26 revision has since added Malay is unverified; whether an `en-US` hint "works anyway" for Latin-script Malay at the glyph level is developer folklore, not documented. Separately, **no independent handwriting-OCR benchmark found includes Apple Vision at all**, and none anywhere covers children's handwriting or Malay/Indonesian (an earlier draft cited a "~72% vs 91%" figure that could not be located and has been removed). **Practical implication:** the realistic engine for BM handwriting is a cloud OCR service that supports Malay (Google Cloud Vision / Document AI, Azure AI Vision) — which requires a verified Malaysia-resident deployment for identifiable worksheet images under D7 (data spec §7.1); neither a TIA nor a vendor’s language-support list authorises foreign processing. Do not tier this as Core until a teacher has photographed a real class set of ~30 BM worksheets and the accuracy and time-per-set have been measured on the chosen engine.
- **[Later] Free-response/essay items**: AI drafts a suggested score and feedback, but a teacher must approve it before it counts — never auto-final. AI graders show a measurable central-tendency bias, under-rewarding excellent work and under-penalizing weak work (doc 1 §6.5). Tiered Later in Pillar 1; described here only so the full pipeline is visible.
- **Capture-method reality check** (corrected twice — the second verification refined the first): handheld-camera capture of paper *is* proven practice — Gradescope's own mobile app supports it (auto-capture on a green overlay, no scanner needed) alongside flatbed/sheet-fed scanning, and ZipGrade is phone-camera-only at K-12 scale. **What is not proven anywhere is full free-text handwriting transcription from a handheld photo.** Gradescope does not OCR free responses: it diffs each scan against the blank template PDF to isolate the handwritten region, clusters visually similar answers for a human grader, and documents free-response boxes as "must be graded by hand." ZipGrade is bubble-sheet MCQ only. Products marketing handwriting transcription (EssayGrader, Class Companion, GradingPal's "95% accuracy") do so on vendor claims alone — no independent benchmark or non-vendor time-per-class figure was found for any of them. What Gradescope genuinely validates for this product is the **student-matching pattern** (printed name/ID or QR code per sheet) and the **template-diff approach** to isolating handwritten regions — both worth adopting rather than inventing.

**3. Attendance and participation**
- Captured directly in-app per session, APDM sync only in Fast-follow if KPM grants a channel rather than duplicating a second parallel entry (directly addressing the documented Malaysian teacher pain point of duplicate data entry across systems, doc 1 §1.2/§8).

### 9.2 From raw data to "advice" — two layers, deliberately separated by cost and trust level

**Layer 1 — rule-based, cheap, always-on, fully explainable.**
Only assessment evidence updates the running mastery estimate for a student against a DSKP standard. Attendance and participation remain contextual signals, not evidence of attainment. An internal score is not interchangeable with official TP1–6: the teacher makes and confirms the PBD judgement (doc 2 §4). A simple threshold rule flags it: *"this student has missed this standard on the last 2-3 assessments."* No AI/LLM call needed. This shares a rules-based differentiation idea with Canvas's "Mastery Paths," but does not establish an identical workflow (doc 3 §11.4) — and it's the version the strongest pedagogy evidence actually supports: Carnegie Learning's best-evidenced results come from exactly this kind of teacher-facing, data-driven flag, not autonomous AI (doc 1 §6.4).

**Layer 2 — AI narrative, built on top of Layer 1, cloud-based. [D11, 2026-09-07: same-launch guided trial with selected teachers, not general access.]**
When a teacher opens a student's or the class's profile, an LLM turns the raw Layer-1 flags into plain language: *"Aiman Hakim has struggled with fraction subtraction in the last three checks. Consider revisiting that concept before the next topic."* (fictional illustration, not a validated curriculum mapping) This must be grounded against authorised learning records and verified curriculum references; Kota Buku textbook grounding additionally depends on content rights/access — a design motivated, not validated, by the Malaysian MCQ preprint ([paper §§3, 6.3](https://arxiv.org/html/2508.04442v1), checked 2026-09-06; doc 2 §10) — and every standard or lesson it references must be validated against the real curriculum database before being shown to the teacher, using the same hallucination-guard pattern already working in production inside Sifututor's own LLS codebase (`validateLessonIds()`, doc 3 §1).

**Class-level aggregation, not just per-student.**
The same underlying data, rolled up across a whole class, answers a different and often more actionable question: *"60% of the class missed this standard — reteach before moving on"* rather than intervening student-by-student. Collection/aggregation is designed from day one; the teacher-facing class dashboard and rule-based flags are Core at launch under D11 as tiered in §3 — no new AI capability, but a separate delivery surface (doc 3 Pillar 4).

### 9.3 The non-negotiable rule underneath all of this

The teacher always acts; the AI never does. The AI drafts a suggested grade, flags a pattern, or suggests a next step — it never finalizes a grade, never moves a student to a different learning path, and never sends anything to a parent on its own. This isn't just a safety posture — it's what the evidence actually supports: teacher-mediated AI use has the strongest results found anywhere in this research (Carnegie Learning), while fully autonomous AI has the weakest and the least evidence (doc 1 §6.7, doc 3 §13).

---

## 10. Kota Buku content integration — a specific feature, not a footnote

This deserves its own section because it's the single most distinctive thing this proposal can offer that a generic classroom app cannot: turning Kota Buku's own content into an active teaching tool rather than a passive PDF/EPUB reader.

- **Ingest Kota Buku's existing BTDA (PDF) and BTDI (EPUB3) textbook content** as the seed corpus for the RAG-grounded content generation in Pillar 3 — this remains conditional on content rights and ingestion validation; the Malaysian preprint tested teacher notes and an RPT, not Kota Buku PDFs/EPUBs (doc 2 §10).
- **Replace the passive reader experience** with one where a teacher can select a textbook page/chapter and generate a worksheet, quiz, or simplified version directly from it — turning Kota Buku's content library into the input for Pillar 3, not a separate app teachers have to switch to.
- **This directly answers the brief's own framing** ("device + application + content... not just providing the device") — Kota Buku's content becomes more actively used through this app than it currently is through their own 2.3-star reader.
- **Practical build note** (doc 2 §1): confirm whether Kota Buku's content can be licensed/ingested via a real API/export, since none was found publicly — this is a concrete first conversation to have with them directly, now that they've opened the door.

---

## 11. Competitive feature benchmark — what already exists elsewhere

Researched 2026-09-06 across three categories: national government LMS platforms, commercial K-12 LMS/SIS systems, and AI-native "complete teacher platform" products. The goal was to stress-test the feature list above against what mature systems already consider standard, and find genuine gaps to win on.

### 11.1 National government platforms — no one has built the whole thing

| Platform | Strongest at | Missing/weak |
|---|---|---|
| Singapore SLS | Pedagogy/AI (LEA chatbot, SAFA auto-marking, DAT natural-language class-data queries) | No native gradebook/attendance — relies on separate school admin systems |
| Estonia eKool/Stuudium | Day-to-day admin + real-time parent transparency (grades/attendance/homework all live for parents) | No AI features built in; separate national "AI Leap" programme trains teachers on existing tools instead |
| Korea NEIS | Records/HR administration (20+ years in production) | No teaching/content layer at all — purely administrative; **serious cautionary history** (see 11.3) |
| China's National Smart Education Platform | Real-time in-class learning analytics, massive scale (164M+ registered users claimed) | Independent academic critique: risk of "teaching-innovation degradation," algorithmic black-box concerns |
| India DIKSHA | Content repository + teacher CPD | **No attendance or gradebook at all** — independently documented as causing real teacher burden (see 11.2) |

**No national system combines gradebook + attendance + content + AI + parent portal in one product.** This directly validates Sifututor's "complete solution" positioning — it's not a redundant feature set, it's filling a gap every researched national system has left open.

### 11.2 The India lesson: fragmentation is a documented, independently-verified failure mode

Careers360 (investigative journalism, not government PR) documents Indian teachers logging into DIKSHA (content) + UDISE+ (attendance/enrollment) + a mid-day-meal app + state-specific apps, re-entering the same data in different formats across all of them — described as teachers "teaching through logins." This is a strong, independently-sourced argument *for* Sifututor's single-app consolidation pitch, not just a nice-to-have talking point — it's evidence a comparable government chose fragmentation and is now facing documented criticism for it.

### 11.3 The Korea lesson: two serious risk patterns to plan around

- **NEIS's privacy fight has run for over 20 years.** Centralizing student data (health, religion, family background) into one national database nearly triggered a teachers' strike in 2002-2003; the resolution kept data school-local rather than centrally accessible, and Korea was *still* tightening data collection (dropping national ID number collection) as recently as 2023. This is the strongest cautionary precedent found anywhere in this research for a programme centralizing data on 182,000 teachers and their students — data architecture and consent design need to anticipate this exact fight, not react to it after launch.
- **Korea's 2025 AI Digital Textbook initiative was politically rolled back** after a change of administration — reclassified from mandatory core material to "supplementary," with only 13 of 17 regional education offices opting in as of Jan 2025. A comparable East Asian government-mandated AI rollout hit real political and parent-screen-time resistance mid-course. The January participation figure and later rollback must not be conflated chronologically. **Decision 6 controls:** leave mandatory/optional framing to Kota Buku/KPM; present capability neutrally with staged pilot exposure and per-school/per-teacher switches. This evidence is a talking point, not an unsolicited opt-in recommendation.

### 11.4 Commercial LMS feature checklist — concrete design references

- **Google Classroom has no native attendance feature at all** (confirmed 2026) — teachers work around this with Forms or third-party add-ons. This is a genuine, beatable gap for a product built attendance-first.
- **Seesaw's Standards & Curriculum Alignment Tool is the most mature standards-tagging system found anywhere**: teachers tag activities against searchable curriculum standards (including custom-uploaded standard sets, not just Common Core), and the gradebook has a dedicated "Standards View" rolling up which standards are under-addressed per student/class. This is a strong, concrete UI/UX reference for how DSKP/TP1-6 tagging should actually work in the product, not just a data-model concept.
- **Canvas's "Mastery Paths" is Pillar 4's "rule-based remediation" feature, already shipped at real scale**: a teacher sets a scoring-range rule on a graded item, and Canvas automatically branches each student to matching follow-up content — explicitly rule-based branching, not ML-driven, per Instructure's own positioning ("true adaptive learning requires third-party integration"). This validates that a deterministic, explainable version of this feature is a legitimate product on its own, not a compromise.
- **Microsoft Teams' Insights dashboard** combines SEL check-in data + engagement + assignment performance + Reading Progress fluency in one teacher view, with a "create challenge assignment" action button generated directly from a student's error pattern — a good reference for how Pillar 1's data collection should surface actionably to a teacher, not just as a report.
- **PowerSchool is confirmed as the pure "system of record" layer** (scheduling, state compliance, IEP/504 case management) that no LMS/classroom tool (Google, Microsoft, Canvas, Seesaw) competes with. This clarifies scope: Sifututor's app is a classroom tool in this same category, not a school-administration system of record — worth being explicit about in the proposal so Kota Buku/KPM don't expect it to replace APDM/SPS-level administrative infrastructure.

### 11.5 AI-native "complete platform" competitors — closest analogs, none an exact match

- **Kira Learning ("Kira 2.0", launched March 2026)** — the closest match on data+content integration: a longitudinal "Student Atlas" profile, conversational query of student data, auto-generated personalized materials, all standards/Bloom's-tagged automatically. **No parent-facing component found** — teacher/curriculum-centric only, unlike Sifututor's required Pillar 6.
- **ibl.ai's "Agentic OS for K-12"** — explicitly includes parent communication as a workflow alongside tutoring, grading, and attendance automation, and is LLM-agnostic/district-ownable (full source code, no lock-in) — a genuinely relevant structural reference, though with no independent adoption evidence found (early-stage, enterprise-sales model).
- **iFlytek (China)** and **Huawei Smart Classroom 3.0** show the most mature full-loop (content generation + grading + live analytics) integration of anything researched, but both require proprietary hardware and are China-market-anchored — not a model Sifututor can replicate without a hardware partner, though iFlytek's claimed grading-time reduction (90 minutes → 5 minutes per class) is a strong efficacy benchmark to cite if a similar feature is built.
- **Jio Shiksha (Reliance Jio, India, 2026)** — the single closest structural match found anywhere to redONE/Kota Buku's exact bundle shape: teacher-facing smart board + student e-book device, cloud-synced, bundling textbooks/videos/quizzes/homework with an AI tutor and progress reports visible to teachers **and** parents/principals. Explicitly described as "early stage, limited number of schools" as of the 2026 announcement — not yet proven at scale, but validates that the "device + connectivity + app + content + parent visibility" bundle shape Sifututor is proposing is a real, currently-being-attempted model elsewhere, not a novel or unprecedented structure.
- **No platform researched — national, commercial, or AI-native — combines Sifututor's full scope** (data collection + class conduct + AI content generation + AI personalization + adjacent efficiency + parent/student access, in one teacher-facing app) with independently verified adoption at meaningful scale. Nuance added after adversarial review: this does *not* mean no competitor has any parent-facing element — SchoolAI, for instance, markets a parent-visibility feature (parents can see what their child asked the AI). The precise claim is that no one combines parent access **plus** attendance **plus** the full pillar set in one product. This is either a genuine market gap or a genuinely hard integration problem nobody has fully solved yet — likely both, which argues for the phased MVP approach in §12 rather than promising the complete vision as a day-one deliverable.

### 11.6 Sources for this section

*Added after adversarial review, which correctly noted this section had no retained source trail unlike the rest of the proposal. All fetched 2026-09-06; government/vendor pages are self-descriptions unless marked independent.*

- **Singapore SLS**: [MOE SLS](https://www.moe.gov.sg/education-in-sg/student-learning-space); [GovTech — AI in SLS](https://www.tech.gov.sg/technews/ai-in-education-transforming-singapore-education-system-with-student-learning-space/); [SLS AI-enabled features](https://www.learning.moe.edu.sg/teachers/teaching-and-learning-on-sls/aied-features/). Rollout dates per AI tool not published by MOE.
- **Estonia**: [e-Estonia e-education](https://e-estonia.com/what-is-e-education/) (state promotional site); [eKool — Wikipedia](https://en.wikipedia.org/wiki/EKool); [AI Leap — EU Digital Skills](https://digital-skills-jobs.europa.eu/en/inspiration/good-practices/ai-leap-estonia); [ERR — AI grading pilot](https://news.err.ee/1609942145/estonia-looking-into-ai-grading-for-native-language-exams).
- **Korea NEIS**: [Australian Privacy Foundation case study](https://privacy.org.au/resources/additional-resources/korean-neis/) (independent); [NEIS — Wikipedia](https://en.wikipedia.org/wiki/National_Education_Information_System); [OECD Korea digital-education governance](https://www.oecd.org/en/publications/country-digital-education-ecosystems-and-governance_906134d4-en/full-report/component-21.html); [IDB — lessons from Korea](https://www.iadb.org/en/blog/education/implementing-edtech-scale-3-lessons-korea-digital-transformation). AI-textbook rollback: reported Jan 2025 (13 of 17 offices opted in).
- **China National Smart Education Platform**: [MOE China press release, Apr 2024](http://en.moe.gov.cn/news/press_releases/202404/t20240401_1123431.html); [gov.cn — 164M users, May 2025](https://english.www.gov.cn/archive/statistics/202505/17/content_WS6828769cc6d0868f4e8f29e4.html); [SAGE Open academic study](https://journals.sagepub.com/doi/full/10.1177/21582440241239471) (independent critique).
- **India DIKSHA**: [Careers360 — "teaching through logins"](https://news.careers360.com/school-teacher-data-entry-burden-udiseplus-midday-meal-diksha-attendance-nishtha-ullas-portal-apps-login-monitoring-education) (independent journalism, Sep 2026); [DIKSHA official](https://diksha.gov.in/); [ORF — protecting teaching time](https://www.orfonline.org/research/using-ai-to-protect-teaching-time-and-improve-learning-quality-in-indian-schools).
- **Google Classroom**: [product page](https://edu.google.com/intl/ALL_us/workspace-for-education/products/classroom/); [learning standards feature, May 2026](https://workspaceupdates.googleblog.com/2026/05/keep-track-of-student-progress-with-learning-standards-and-skills-in-Google-Classroom.html); [attendance gap — TEQ](https://www.teq.com/attendance-google-classroom/). Re-verified after review: still no native Classroom attendance in 2026 (Google Meet has a separate meeting-attendance report on higher tiers — not classroom roll call).
- **Microsoft Education**: [Teams for Education](https://www.microsoft.com/en-us/education/products/teams); [Reading Progress guide](https://learn.microsoft.com/en-us/training/educator-center/product-guides/reading-progress/); [Attendance app](https://techcommunity.microsoft.com/blog/microsoftteamsblog/taking-class-attendance-on-teams-for-education/1472549); [Parent Connection retirement notice](https://support.microsoft.com/en-us/topic/communicate-with-guardians-in-microsoft-teams-01471ecd-eb5d-4eda-9c5d-0064d672960e).
- **PowerSchool**: [SIS features](https://www.powerschool.com/solutions/student-information/powerschool-sis-unused/features/); [Special Programs](https://www.powerschool.com/products/student-information/special-programs/).
- **Canvas**: [Canvas K-12](https://www.instructure.com/k12/products/canvas/canvas-lms); [Mastery Paths](https://support.smsd.us/support/solutions/articles/44002549000-canvas-mastery-paths); [Roll Call attendance](https://community.instructure.com/en/kb/articles/662770-what-is-the-roll-call-attendance-tool).
- **Seesaw**: [Standards alignment tool](https://seesaw.com/alignment/); [Standards View in Gradebook](https://help.seesaw.me/hc/en-us/articles/360060064332-Using-the-Standards-View-in-the-Gradebook).
- **AI-native platforms**: [Kira 2.0](https://www.kira-learning.com/blog/kira-2.0) (Mar 2026; "no parent component" re-verified after review); [ibl.ai Agentic OS K-12](https://ibl.ai/product/agentic-os/k12); [iFlytek, 2026 WDEC](https://www.iflytek.com/en/news-events/news/330.html); [Jio Shiksha](https://www.jio.com/ai-classroom/); [Huawei Smart Classroom 3.0](https://e.huawei.com/en/news/2024/industries/education/accelerate-education-intelligence); [Alef Education](https://www.alefeducation.com/). SchoolAI parent-visibility feature: noted by the adversarial reviewer from SchoolAI's marketing; URL not retained — verify before citing.
- **Not independently re-verified in this pass**: the Estonia, Korea, and China rows rest on the sources above without a second check; Kira, Google Classroom attendance, and the 6-pillar claim were re-verified.

---

## 12. MVP scope recommendation

The cross-cutting Core requirements in §2.1 are part of this MVP: four-language parity, WCAG 2.2 AA, first-week coaching and school champions. D8 does not remove the separate parent/student web surface; no student hardware or always-connected student device may be assumed.

Pulling every "Core" row from Pillars 1–6 above into one MVP feature list:

*Revised after adversarial review and Hafiz's decisions of 2026-09-06. Items that depended on unconfirmed external access (Kota Buku textbook content, an APDM integration path) or an unvalidated capture workflow (handwriting OCR) are Fast-follow. AI lesson-plan generation is **built at launch on the same backend as item 5 and released in stages** (Level 1 for all, Level 2 as a guided teacher beta) — Hafiz's call, superseding the reviewer's "defer it" recommendation.*

**Teacher app (iPad, offline-first):**
1. Attendance — standalone in-app register with generic export; APDM-compatible formats require KPM confirmation (APDM sync itself is Fast-follow, pending KPM)
2. Formative check-ins + MCQ auto-grading (live in-app, or bubble/tick answer sheets captured by camera)
3. Per-student TP1-6 mastery tracking
4. Live poll/quiz for class activities
5. AI worksheet/quiz (checkable-item) generation grounded in the public DSKP documents — the least-risky AI task and the one with the closest Malaysian evidence (automated-metric, single-chapter, not teacher-validated — see Pillar 3); no Kota Buku licence needed; teacher-validation pilot required before launch
6. Reading-level differentiation and language parity in BM, English, Mandarin and Tamil, with per-language quality validation
7. Template-assisted RPH (lesson plan) authoring with DSKP standard selection
8. Per-student strength/weakness summary (teacher-facing, not autonomous — Layer 1 rules only)
9. Rule-based remediation suggestions
10. Parent communication templates
11. RPH/lesson-plan sharing library

12. Class view, rule-based class flags and suggestions — Core for all teachers under D11; recorded evidence remains visible and the teacher decides.
13. Plain-language AI analysis, teacher assistant conversation and AI-written admin drafts — guided trial with selected teachers at the same launch under D11; teacher review before use or sending, no autonomous assignment. Notice/reminder templates and the curated parent digest remain Core. This trial does not promote automatic history-based material generation at scale or other Fast-follow features.

14. **AI-drafted full RPH text (Level 2) — same backend as item 5, live at launch as a guided beta for pilot teachers only**, general release after quality is measured; grounded on public DSKP first, Kota Buku textbooks as they arrive.

**Fast-follow (not in the launch build):** worksheet generation from Kota Buku textbook pages (needs their content licence); handwritten fill-in-blank OCR grading (cloud OCR, pilot first); APDM read/write sync (pending KPM).

**Separate parent/student web surface:**
1. Curated, age-gated progress view
2. Attendance/announcement visibility
3. Time-boxed digest, not continuous tracking

This list is deliberately still substantial — it's not a "just do the minimum" MVP, it's "do the pillars where the evidence is strongest and the technical cost is lowest first," which is a different filter than "do the least possible."

---

## 13. What NOT to build first

**Scope check, 2026-09-06:** full Standard 1–Form 5 and government plus private/international schools remain Hafiz’s approved scope. Any phased year/subject recommendation below is not approval to narrow that scope. The package lacks a year × subject × language × curriculum coverage/validation matrix, a private/international-school operating/governance mapping, a complete age-gate policy for the middle years, and a validated device-free response-capture route (§9.1). These are existing-scope gaps for Hafiz to prioritise later, not new research or build work authorised by this review. Public DSKP availability also does not by itself establish unrestricted reuse rights; the no-Kota-Buku-licence launch dependency remains decided, while exact source licences need verification.

Explicit, because every case study in doc 2 §12 shows programmes that failed by trying to do too much, too fast, with too little teacher-support infrastructure behind it:

- **Not** a fully autonomous adaptive-learning engine that removes the teacher from decisions (§6 — evidence doesn't support it, and it's the single biggest compliance/trust risk).
- **Not** essay/free-text auto-grading as a final grade — only as a teacher-reviewed suggestion, given the documented AI-grader bias.
- **Not** SEL/behavior-point tracking as a headline feature — the tooling evidence is genuinely weaker than the pedagogy it's based on.
- **Not** raw, continuous, real-time parent tracking — start curated and time-boxed, expand only if asked.
- **Not** trying to cover all subjects/all forms (Std 1–Form 5) at full depth on day one — given DSKP's own subject-by-subject structure and the KP2027 transition already underway, a phased subject/grade rollout (mirroring how Kota Buku's own BTDI only covers ~4 subjects for Form 3 today) is both more credible and lower-risk than promising full national curriculum coverage immediately.

---

*Companion to [research-findings.md](research-findings.md) and [technical-build-blueprint.md](technical-build-blueprint.md). This document defines product scope; it does not re-derive the evidence behind each decision — see the cited sections in the two research docs for sourcing.*
