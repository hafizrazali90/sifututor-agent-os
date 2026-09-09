# AI Classroom — Technical Build Blueprint (Kota Buku Proposal)

**Context:** Perbadanan Kota Buku reached out to Sifututor with an open, unspecified invitation to propose a solution — they have no existing spec. This document is the technical/architecture research foundation for that proposal, done in parallel with (and building on) [research-findings.md](research-findings.md), the earlier Malaysia/global market research.

**The deal this slots into:** redONE Mobile's "Teacher Digital Empowerment Programme" proposal to MCMC's Universal Service Provision (USP) Fund — an iPad + 300GB mobile data + device insurance + "Kota Buku Application" bundle for up to 182,757 KPM teachers. Currently pending MCMC/USP approval (Phase 1 of 4). The "Kota Buku Application" line item is commercially defined in the partner pack (D10) and originally described as an e-book/reference content subscription — Kota Buku wants Sifututor to propose something much more complete to occupy that slot: device + application + content, not just content.

**Commercial boundary (D10), 2026-09-06:** programme prices, support allocations and cost estimates belong only in the [partner pack](partner/SEPADU-v1.0-Founder-Briefing.md), with unresolved corrections in its [read-only review](partner/SEPADU-review.md). This blueprint retains technical cost drivers and verification flags, not a competing price model. Teacher devices only (D8); the existing parent/student web surface remains. **C4 decided by Hafiz, 2026-09-06: blended workload reduction and AI-classroom capability**, with the six pillars and scope unchanged (handoff §7 C4). This is intended value, not proven savings or learning gains.

**Deal structure DECIDED by Hafiz, 2026-09-06:** co-branded Kota Buku app, delivered by Sifututor, powered by Learnest Lab; exact legal entity name to be confirmed by Hafiz; our IP/code, processor-only role, no exclusivity beyond KPM, and rights to the Learnest Lab private/international-school version. All ten decisions in CODEX-HANDOFF.md §7 govern this research; the review does not reopen them.

**Platform:** native iPadOS app (confirmed decision). Device model is unresolved in redONE's own deck (inconsistent between "iPad Air M4" and "iPad A16" across slides) — this ambiguity turns out to be architecturally load-bearing (see §3).

**Research date:** 2026-09-06, compiled from 4 parallel top-level research agents (one of which split into 5 sub-agents on AI infrastructure), ~830K additional tokens of raw findings. Same sourcing standard as the companion document: every claim is dated and sourced; flagged items need verification before going into a client-facing proposal.

---

## Table of contents

1. [Kota Buku's actual current technology — the starting point](#1-kota-bukus-actual-current-technology--the-starting-point)
2. [Offline-first architecture patterns](#2-offline-first-architecture-patterns)
3. [On-device vs. cloud AI — the device-model decision is load-bearing](#3-on-device-vs-cloud-ai--the-device-model-decision-is-load-bearing)
4. [Curriculum-aligned content data modeling](#4-curriculum-aligned-content-data-modeling)
5. [Native iPadOS-specific considerations](#5-native-ipados-specific-considerations)
6. [Enterprise deployment at 182,000-device scale](#6-enterprise-deployment-at-182000-device-scale)
7. [App distribution model — a hard constraint, not a choice](#7-app-distribution-model--a-hard-constraint-not-a-choice)
8. [Running it after launch](#8-running-it-after-launch)
9. [AI infrastructure and cost modeling](#9-ai-infrastructure-and-cost-modeling)
10. [RAG / content-grounding architecture for curriculum AI](#10-rag--content-grounding-architecture-for-curriculum-ai)
11. [Non-AI infrastructure validation](#11-non-ai-infrastructure-validation--commercial-figures-in-the-partner-pack)
12. [Case studies: national device+app+content programmes](#12-case-studies-national-deviceappcontent-programmes)
13. [Synthesis: what this means for the proposal](#13-synthesis-what-this-means-for-the-proposal)
14. [Master list of gaps and follow-ups needed](#14-master-list-of-gaps-and-follow-ups-needed)
15. [Regulatory and contracting checks](#15-regulatory-and-contracting-checks--2026-09-06)

---

## 1. Kota Buku's actual current technology — the starting point

- **textbook.moe.gov.my**: functions as a download/landing page linking to app-store listings, distinct from DELIMa's Google Workspace portal. Live status unverified this session (fetch failed) — confirm directly before citing.
- **KPM eTextbook Reader app**: App Store ID 889928729, developer "Perbadanan Kota Buku." **Last updated 2 November 2021, rated 2.3/5 from only 3 ratings.** Google Play listing (`com.kotabuku.kpm`) returned 404 — possibly delisted. This establishes sparse public rating/update evidence, not measured engagement or backend quality.
- **Likely white-labeled, not bespoke**: package-name history (`com.esentral.kpm` → `com.kotabuku.kpm`) plus a claim that "Book Capital and eSentral now use the same publisher panel/DRM reader" suggests the reader is a licensed instance of **eSentral** (a pre-existing commercial Malaysian ebook platform run by Xentral Methods Sdn Bhd, proprietary in-house DRM) — an inference chain, not a confirmed vendor relationship, but a plausible one.
- **Format — two parallel tiers, and this matters a lot**:
  - **BTDA (Buku Teks Digital Asas)** — plain **PDF**, distributed via Google Drive under DELIMa accounts, **no app, no DRM**.
  - **BTDI (Buku Teks Digital Interaktif)** — **EPUB3**, requires the KPM eTextbook Reader app, multimedia-enhanced, offline-capable — but only **~4 subjects for Form 3** were confirmed live.
  - **Implication**: the EPUB/app experience is a narrow subset. Most textbook distribution today is likely plain PDF with no app or DRM at all. This is a materially different starting point than "upgrading a working product with real usage" — it's closer to "the existing solution barely exists in practice."
- **No public API/SDK/licensing documentation found anywhere** for third-party integration with Kota Buku's content. Government e-tender portals (eperolehan.gov.my) were not searchable with available tools this session — **genuine gap, recommend a manual check before asserting no integration pathway exists.**
- **Corporate structure**: the reader's privacy-policy link points to `bookcapital.my`, not kotabuku.my — Book Capital appears to be Kota Buku's commercial digital-platform brand (launched by PM Anwar Ibrahim, 27 May 2023) — relationship to PKB not fully confirmed.
- **No evidence of any existing Kota Buku + telco device/SIM/app bundle programme.** This looks like a genuine white space — the device+connectivity+app bundle is a new initiative to propose into, not one with a known prior template (unless Kota Buku's actual enquiry says otherwise).
- **DELIMa's broader infrastructure** runs on Google Cloud, with Awantec Systems (MDM) and Matrix Connexion (analytics) as named partners — neither confirmed to touch the textbook app specifically.

**Strategic read (updated 2026-09-06):** broader teacher workflows may add value beyond the reader. Sparse app-store ratings and update history do not establish adoption, backend quality, or replacement feasibility. The approved structure is co-branded white-label, not an open choice between replacement and white-label.

---

## 2. Offline-first architecture patterns

Relevant even with a 300GB/month data allowance, because Malaysian rural school connectivity has documented reliability problems independent of data quota (established in the companion research doc's teacher-pain-points section).

- **Khan Academy's own mobile app**: offline mode is narrow (video-only download, no offline exercises/articles) — no published engineering detail on sync architecture. The more architecturally relevant Khan-lineage precedent is the now-superseded **KA Lite** (self-hosted, zero-connectivity).
- **Google Classroom**: pre-downloaded attachments viewable/editable offline, background refresh every 24h when online — **conflict-resolution behavior is undocumented by Google even in their own docs.**
- **Kolibri (Learning Equality) — the strongest documented precedent found**: 3M+ learners claimed across 220+ countries/territories, purpose-built for low-connectivity settings.
  - Runs as a **local server on-device**, can serve other devices over local WiFi with zero internet (classroom "hub" mode).
  - Custom open-source sync engine **Morango**: does **delta sync** (change-tracking, not full resync), supports peer-to-peer and hub-and-spoke topology, certificate-based auth.
  - Content packaged into self-contained "channels" (topic tree + zipped HTML5/EPUB-like bundles), authored centrally via a toolkit called Ricecooker on "Kolibri Studio."
  - **This is the single closest technical precedent found for a capped-data-allowance, low-connectivity-tolerant education platform at scale** — worth a deeper technical read of Morango's actual source before finalizing a sync design.
- **General industry patterns** (local-first DBs: WatermelonDB/SQLite, PouchDB/CouchDB, RxDB, Realm; CRDT libraries: Automerge, Yjs) are commonly cited, but **no researched national-scale edtech deployment was confirmed to actually use CRDTs** for grades/attendance sync — Kolibri uses its own custom engine instead. Treat CRDTs as an option to evaluate, not a validated precedent to copy blindly.
- **iOS-specific mechanisms**: `BGTaskScheduler` (periodic background work) and Background URLSession (OS-managed large-file transfer surviving app suspension) are the relevant Apple APIs — sourced from third-party engineering explainers, not independently re-verified against Apple's primary docs this session.
- **Apple Content Caching** (native macOS service): a local Mac on a school network can cache App Store apps/OS updates/iCloud data for other devices on the same network — an infrastructure-layer complement worth considering alongside app-level offline design.
- **DIKSHA/Sunbird** (India's national teacher platform) — the closest real precedent of a government building an open-source, offline-first, teacher-facing platform at scale. Deep-read completed 2026-09-06 (technote v5.0A, 23 Dec 2022, all 134 pages, supplemented by Sunbird docs/GitHub and 2025 news). Findings below are tagged [technote], [Sunbird docs/GitHub], or [news].

### 2.1 DIKSHA/Sunbird — what the technote actually shows

**Caveat up front [technote pp.132-133]:** the deep-technical content — telemetry schema, API reference, dataset design, RCA findings, release notes — lives in Appendices A-U, which are referenced by title only and **not published** at that URL or anywhere found. So the architecture below is confirmed; implementation parameters and lessons-learned are not.

- **Architecture [technote pp.36-66]:** ~12 independent MIT-licensed "building blocks," not a monolith: **Knowlg** (content management + a Taxonomy/Framework service), **Lern** (identity, User-Org-Location registries, roles, batches/cohorts, Groups, notifications), **Obsrv** (telemetry ingestion/aggregation), **inQuiry** (question banks, QuML spec), **Telemetry**, **RC** (registries + verifiable credentials), **UCI** (WhatsApp/Telegram/SMS conversations), **Saral** (OCR/handwriting recognition for scanning paper test scoresheets — note the direct relevance to our capture pillar), **cQube** (state-level analytics). Stores: Cassandra, MongoDB, PostgreSQL, Redis, Elasticsearch, **Neo4j** (the graph store behind the taxonomy), Kafka, RabbitMQ, Druid; Kubernetes microservices, originally Azure Central India, migrated to Oracle Cloud (announced Aug 2023; "DIKSHA 2.0," Sep 2025, cites OCI) [news].
- **Mobile client [Sunbird docs/GitHub]:** a Cordova hybrid app over `sunbird-mobile-sdk` (TypeScript) — "all the business logic … from API access to offline data management" lives in the SDK, the app is a thin shell over the same APIs the web portal uses. *Not a native app; a different choice from ours, but the SDK-owns-offline-logic pattern is the transferable idea.*
- **Offline design [technote pp.78, 106-107; Sunbird docs]:** three delivery modes — Portal, Mobile, Offline Desktop. The offline unit is the **ECAR** package (zip: `manifest.json` + thumbnail + artifact) in three variants: **FULL** (everything incl. nested children — fully offline), **SPINE** (structure/metadata only, children stream on demand — partially offline), **ONLINE** (streaming only). Downloads must be initiated online; once downloaded, content is searchable and playable fully offline. Telemetry is queued on-device and synced opportunistically — batch size/retry parameters could not be confirmed. **No documented conflict-resolution strategy exists anywhere** (technote, docs, GitHub) — a genuine gap, which means any implementer, including us, designs that from scratch. **The Offline Desktop app is still "Coming soon"** on diksha.gov.in/get-app today despite being a named deployment target in the 2022 technote — a real sign that component stalled.
- **Curriculum taxonomy [technote pp.37-38, 113; Knowlg docs]:** content is tagged against a **Framework** — a hierarchical taxonomy with **Categories** (`board`, `medium`, `gradeLevel`, `subject`, `topic`, …) each holding **Terms** (e.g. gradeLevel = Class 5). Served by a dedicated Framework/Taxonomy service with CRUD APIs — a structured graph, not free-text tags. **Federation:** each state/board runs its own **Channel** (tenant) and defines its own Framework under it, so 36 states maintain distinct board→medium→grade→subject vocabularies on one platform without collision. *Maps naturally onto our need to run KSSR/KSSM and KP2027 side by side (§4): one channel, one framework per curriculum version.*
- **Energized Textbook [technote pp.109-111]:** every printed textbook chapter carries a QR/DIAL code resolving to curriculum-tagged digital content for that chapter — 35 states/CBSE/NCERT, 60 crore (600M) textbook copies, 90,000+ linked items. *This is the closest existing analogue to the "select a Kota Buku textbook page → get worksheet/quiz" feature in the feature spec §10, and it is proven at national scale.*
- **Telemetry [technote pp.71-72, 88-104; telemetry.sunbird.org]:** "Full" tier telemetry on a common envelope (`eid`, `ets`, `mid`, `actor`, `object`, `edata`, `context`, `tags`); spec v3.1 defines **17 event types** (START, END, IMPRESSION, INTERACT, ASSESS, RESPONSE, …). Pipeline: Kafka → Flink/Samza stream jobs → Druid (OLAP) → Superset, packaged as the in-house "Hawk Eye" reporting layer with public and admin dashboard tiers. *A ready-made, open reference for our Pillar 1 event model.*
- **Identity and roles [technote p.38, 114; Sunbird-Lern GitHub]:** Keycloak auth (password, Google, SSO, SMS-OTP reset); User, Organization, Location as three related registries; five personas (learner, teacher, admin, parent, community). Guest access and **multiple profiles per device** (households sharing one phone) are explicit. **No formal class/section roster entity exists** — only an ad hoc Groups feature; per the technote's decentralisation principle, rosters live in state systems, if anywhere. *The same gap we found in LLS and Kelasapp: a School→Class→Teacher→Students roster is something we must build; no reference platform hands it to us.*
- **AI [technote p.130; news]:** as of Dec 2022, aspirational — one paragraph plus a navigation/FAQ chatbot ("TARA"). **DIKSHA 2.0 (1 Sep 2025)** added **Ask DIKSHA** (a RAG-style assistant grounded in NCERT textbooks), Read Aloud, Closed Captioning, and a "Personalized Adaptive Learning" layer — repositioning from content management toward a full LMS. No technical documentation of Ask DIKSHA's model, RAG pipeline, or hosting was found. Google's "Sahayak" is confirmed separate from the Sunbird stack.
- **Licence and reusability [technote pp.7, 36, 123-129]:** MIT, confirmed twice in the text; recognised Digital Public Good; the technote explicitly invites global adoption "with sovereign control." The **infrastructure layer** (auth, framework/taxonomy engine, ECAR packaging, telemetry, registries) is genuinely reusable or at least referenceable; the **content layer** (Energized Textbooks, VidyaDaan, question banks) is deeply coupled to NCERT/CBSE/state boards and Indian languages.
- **Lessons learned:** essentially **none documented**. The technote is an operations manual (release cycle, QA gates, S1/S2 incident classes) with an RCA *process* but no RCA *findings*. The incident-qualification list (Azure region impact, DB unreachable, pipeline lag >8h, TPS spikes) implicitly records failure modes hit at scale, without narrative. Real lessons would be in the unpublished Appendix K (RCA) and Appendix E (release notes).

**What transfers to our design (factual mapping, decisions remain open):** the ECAR FULL/SPINE split for offline content; a per-curriculum-version Framework under one Channel; the QR-per-textbook-chapter link pattern for Kota Buku content; the 17-event telemetry envelope; Keycloak-style identity with multiple profiles per device. **What DIKSHA does not solve for us:** offline conflict resolution, a class roster model, and any published lessons from running it — all three are ours to design and prove.

**Applied:** the Sunbird telemetry envelope and the Framework-per-curriculum-version pattern are adopted as the data model in [data-collection-spec.md](data-collection-spec.md) §5 and §8, together with the data-residency and controller/processor requirements (§7 there) that constrain the hosting choices in §10–§11 of this document.

---

## 3. On-device vs. cloud AI — the device-model decision is load-bearing

**Codex evidence note, 2026-09-06:** [Apple Intelligence requirements](https://support.apple.com/en-us/121115) govern that product, not all local machine learning. [Core ML](https://developer.apple.com/documentation/coreml) supports app models on-device. The fixed M1+ recommendation / A16 minimum is preserved; its rationale in handoff §7 needs Hafiz’s attention because deterministic grading and compatible printed OCR are not M1-exclusive. RAM/TOPS figures, language support and model context limits below are not a device acceptance test.

This is the single most consequential technical finding in the whole research set, because it directly resolves (or exposes) the ambiguity in redONE's own deck.

- **Confirmed hardware fact** (independently re-verified against Apple's own support page, support.apple.com/121115, after adversarial review): the **base iPad A16 is not eligible for Apple Intelligence**. This does not exclude ordinary local code, Vision or suitable Core ML models; framework/task compatibility must be tested separately. Apple Intelligence requires an iPad mini (A17 Pro) or **any iPad with an M1 chip or later** — so M1/M2/M3 iPad Airs and iPad Pros qualify too, not only the M4 Air named in redONE's deck. The **iPad Air M4** (12GB RAM, 38 TOPS Neural Engine) qualifies fully; the base A16 (6GB RAM, ~17 TOPS) does not qualify for **Apple Intelligence**. Precision note: Apple gates by chip model, not by a published RAM figure — the "~8GB floor" sometimes cited (including in an earlier draft of this document) is an inferred proxy, not Apple's stated mechanism.
- **This is an unpriced hardware/inference trade-off requiring validation**: the cheapest iPad Apple sells (base A16; redONE’s unit prices are internally inconsistent, and commercial figures belong in the partner pack) is the unit a cost-sensitive government tender is most likely to specify — and it cannot run Apple Intelligence. Saving on cloud inference cost by pushing work on-device would require spending *more* upfront on hardware (Air/Pro/A17-Pro-mini) than the cheapest compliant iPad would cost. **Any technical proposal to Kota Buku needs to present this explicitly as a trade-off/decision point** — it cannot be assumed away, and it directly resolves which of redONE's two named device models the numbers actually support.
- **Apple Intelligence is not the whole on-device capability set.** A16 remains supported for local deterministic work and compatible app-supplied models; cloud-first is the approved product direction, not proof that all local processing is impossible. The app cannot be architected "on-device-first" — it must be cloud-capable by default, with on-device treated as an optional cost-optimization for whichever subset of the fleet ends up on qualifying hardware.
- **Apple's on-device model specs** (Foundation Models framework, shipped iOS/iPadOS 26): ~3B parameters, 2-bit quantized, and — critically — an **8,192-token context window** (started at 4,096). This is a hard ceiling that rules out feeding large curriculum documents or long chat history into the on-device model directly; it's explicitly designed by Apple for summarization/extraction/classification, "not designed for world knowledge or advanced reasoning." Complex reasoning routes to Apple's Private Cloud Compute, which does not have exact published latency numbers or routing thresholds.
- **What's genuinely well-suited to on-device (deterministic logic, not even needing an LLM)**: MCQ/fill-in-blank grading (exact-match comparison against an answer key — near-zero marginal cost, no accuracy gap vs. cloud, because it isn't generative AI at all) and simple rule-based recommendation logic (e.g., "recommend remedial worksheet on topic X because score < threshold"). These should be explicitly separated from "AI features" in the pitch, since they don't carry AI inference cost regardless of device tier.
- **What shows a real, measured quality gap on-device**: a 2026 benchmark study found small on-device-class models (Gemma 2B) scored ~25 GLEU on grammar correction vs. GPT-3.5 Turbo's ~75 GLEU — roughly a 3x gap, with the paper's explicit conclusion that "LLMs are currently not replaceable" for this task on-device. Text simplification/rewriting showed a much smaller gap (~55 vs ~59 SARI) — simplification is far more tractable on-device than grammar correction.
- **Cloud-first tasks in this design:** open-ended lesson plans, nuanced feedback and curriculum chat. Their quality and latency need evaluation. A large retrieval corpus does not itself require a large context window: RAG retrieves selected passages rather than loading the whole corpus. Model/runtime/language limits must be checked before promising an on-device alternative.
- **Engineering gotchas documented in the literature** (2026 mobile-SLM engineering paper): on-device inference creates real battery/thermal load unsuited to *continuous* use (better for short bursty tasks); model behavior is inconsistent across processor generations/RAM/device age, complicating QA across a mixed 182,000-device fleet bought across different procurement cycles; and offline-to-cloud sync reconciliation when local and cloud outputs disagree is "intricate."
- **Industry validation**: every major AI-in-education competitor researched (MagicSchool AI, SchoolAI, Khanmigo, Curipod, Diffit) is **cloud-backed in the reviewed descriptions** — no on-device component was documented in this search. This supports cloud-first as a practical pattern, not proof that the entire category lacks local processing, not a compromise unique to this proposal.

**Bottom line**: on-device AI is a real, available cost lever, but task-specific: deterministic grading/recommendations can run on both supported tiers; OCR depends on language/runtime; generative simplification depends on the chosen model. Apple Intelligence eligibility is a separate restriction. It is not a substitute for a cloud-capable core architecture, and the specific iPad model chosen materially changes what's even possible — this should be raised as an explicit decision point with Kota Buku/redONE, not assumed.

---

## 4. Curriculum-aligned content data modeling

- **Khan Academy** (from their own 2015/2016 engineering blog): content modeled as Video/Exercise/Article/Topic entities in a hierarchical tree, served via an immutable, versioned "Frozen Model Store," with a separate human-curated country/curriculum-alignment overlay maintained by local "language advocates." Their actual mastery algorithm is not publicly documented (a commonly-attributed "halflife regression" technique is actually **Duolingo's**, not Khan Academy's — worth not repeating that mix-up).
- **IXL's SmartScore**: a per-skill 0-100 proficiency meter with asymmetric adjustment near mastery (small gains, larger penalties above 90, to prevent lucky-guess false mastery) — but **no public documentation of IXL's actual multi-curriculum data model exists** — this is exactly Sifututor's "many curricula → one skill graph" problem, and it simply isn't publicly documented anywhere by IXL either.
- **The most directly reusable, verified reference pattern: CASE (Competencies and Academic Standards Exchange)**, maintained by 1EdTech Consortium, latest version **CASE 1.1, released 24 January 2025**. Its data model maps almost exactly onto DSKP's subject → year/form → content-standard → learning-standard → performance-level hierarchy:
  - `CFDocument` (one standards framework), `CFItem` (one taxonomy node with a human-readable code, item type, education level), `CFAssociation` (edges including `isChildOf` and `exactMatchOf` for cross-walking standard versions — directly useful for the KSSR/KSSM → KP2027 transition documented in the companion research doc — and `isTranslationOf`, new in 1.1, useful for BM/English bilingual content), and `CFRubric`/`CFRubricCriterionLevel` (built-in ordinal performance-level modeling, structurally close to DSKP's own TP1-6 band system).
  - **Real adoption**: 21 US states publish standards in CASE format as of 2026 (up from 7 in 2023) — a concrete precedent for "government curriculum → machine-readable taxonomy."
  - **Recommendation**: this is a strong candidate as the underlying schema for a DSKP content graph, rather than inventing a bespoke taxonomy format from scratch.
- **Mastery modeling — two dominant, well-established academic patterns**:
  - **Bayesian Knowledge Tracing** (Corbett & Anderson, 1995) — a per-skill Hidden Markov Model producing a continuously-updating binary mastery estimate ("mastery grows with practice").
  - **Item Response Theory** (Lord & Novick, 1968) — a continuous latent-ability estimate calibrated against item difficulty, powers computerized adaptive testing (i-Ready/PISA/TIMSS-style diagnostics).
  - Industry pattern: platforms typically show teachers a **simple ordinal field** (what IXL/i-Ready display) computed internally by one of these more complex probabilistic engines. No vendor researched has unified both approaches into one universal formula — pick one, don't try to build both.

---

## 5. Native iPadOS-specific considerations

- **ClassKit + Apple Classroom**: a thin publication layer (Contexts/Activities/Handouts) letting the Schoolwork app browse an education app's content and view reported progress — does not replace the app's own data storage. **Critical constraint**: production use requires **Managed Apple IDs issued via Apple School Manager**, tying it architecturally to Apple's own institutional identity system. No dedicated ClassKit WWDC session since 2020 (6-year gap, not marked deprecated — treat as "maintained but not actively evolved"). **Guideline 5.1.2(vi) explicitly restricts ClassKit-derived data from marketing/advertising/data-mining use.**
- **Schoolwork app**: actively updated (v3.2.1, 27 Jan 2025), requires iPadOS 18.2+, is the teacher-facing consumer of ClassKit data.
- **Shared iPad**: solves a different problem (multiple students sharing one device via Managed Apple IDs) — **confirmed not relevant** to a one-iPad-per-teacher deployment.
- **SwiftUI vs UIKit**: Apple positions SwiftUI as complementary, not a UIKit replacement. Industry commentary (not individually source-verified — flagged as a follow-up) suggests UIKit remains stronger for complex document/text rendering, annotation surfaces, and large custom scrolling views — directly relevant to an EPUB-rendering, form-heavy, annotation-capable app. A hybrid SwiftUI-shell + UIKit-for-heavy-screens pattern is commonly reported as pragmatic for this category.
- **App Store Review Guidelines** (full text checked): no dedicated "education apps" section exists — education is referenced only in scattered clauses (1.5 developer contact, 2.5.2 code-teaching exception, 5.1.2(vi) ClassKit restriction). **Guideline 5.1.4 (Kids)**: apps collecting/transmitting minors' personal data must have a privacy policy and comply with COPPA/GDPR/etc. — Apple does **not** itself spell out a "school as consent proxy" exception the way COPPA's own regulatory text does. **This needs direct confirmation from Apple's separate privacy documentation or legal counsel before relying on it** — it's load-bearing for a government-schools student-data-collection design (and connects directly to the companion doc's finding that Malaysia itself has no codified parental-consent-verification mechanism either).
- **No lighter-touch review track for institutional/Custom Apps** — a private Custom App distributed via ASM/ABM still goes through the same App Review guidelines as a public App Store app.

---

## 6. Enterprise deployment at 182,000-device scale

**Primary correction, 2026-09-06:** Apple’s [24 March 2026 announcement](https://www.apple.com/uk/newsroom/2026/03/introducing-apple-business/) says Apple Business replaces Apple Business Manager/Essentials/Connect from 14 April, with a free service and built-in management; features vary by region. Historical ABM references below describe the deployment pattern, not a current paid tier. Do not infer that its built-in management meets this fleet’s needs or replace the MDM evaluation. The teacher-only ASM-versus-business eligibility question remains for Hafiz/Apple.

- **Zero-touch enrollment (ADE)**: a device bought via an ADE-participating channel registers itself to the buyer's Apple Business Manager (ABM) / Apple School Manager (ASM) account at purchase; on first boot it pulls its MDM enrollment profile automatically. Apple syncs devices to an MDM at roughly **3,000 devices/minute** (Microsoft's figure, not Apple's own). Microsoft's Intune caps at **200,000 ADE devices per token** — 182,000 sits under this ceiling but close to it. **No Apple-published hard device ceiling per ABM/ASM tenant was found anywhere** — this Intune figure is an implementation limit inferred from Apple's undisclosed throttling, not an Apple document.
- **ASM vs. ABM**: ASM adds education-only features (Managed Apple Accounts, Classroom app, Shared iPad, SIS roster sync) and is free for eligible institutions; ABM is the business/government equivalent with no education features. **Open question, unresolved in any Apple documentation found**: whether a national *teacher-only* (not student) programme qualifies for ASM or should use the business route (eligibility still unresolved; not a free-versus-paid ABM distinction) — worth a direct question to Apple's education/enterprise channel.
- **No confirmed Apple engagement with MCMC, the USP Fund, or this specific programme was found anywhere public** — an absence-of-evidence result, not a denial; the procurement may simply not be public yet or may run through a reseller intermediary.
- **MDM platform comparison** (published list/SMB rates — every vendor's 100,000+ pricing is "custom quote," none publish enterprise-scale rates):

| Platform | Commercial verification | Notes |
|---|---|---|
| Jamf School | Enterprise quote required | Education-focused, strong ASM/VPP integration |
| Jamf Pro | Enterprise quote required | Cross-platform enterprise tier |
| Mosyle | Enterprise quote required | Apple-only; no programme-scale quote established |
| Microsoft Intune | Confirm existing entitlement and quote | Do not assume the programme already holds the required M365 Education licence |
| Cisco Meraki Systems Manager | Custom quote | 3-year minimum term |

- **No confirmed incumbent MDM vendor or government panel** tied to MCMC/DELIMa/PADU device programmes was found — genuinely unknown, worth asking directly rather than assuming a clean slate.
- **What breaks at six-figure scale — real precedents**:
  - **LAUSD (~650,000 targeted, 2013)**: ~340 students removed the MDM profile within days, stripping the web filter; the district froze off-campus device use fleet-wide. Failure mode was policy-removal, not infrastructure load.
  - **UK DfE "Get Help with Technology" (1.3M+ devices, COVID-era)**: largest verified national deployment found, Intune + Cisco Umbrella pre-installed. No public throughput/ticket-volume data found.
  - **Haryana e-Adhigam, India (~500,000 tablets, 2022)**: students bypassed the MDM's education-only restriction; separately, lapsed SIM/connectivity funding left many devices unused. **Closest precedent to this programme in both scale and government-run nature.**
  - No 100,000+ device vendor-published MDM case study exists for education, for any vendor — Jamf's largest public case study is ~50,000 devices (El Paso ISD).

---

## 7. App distribution model — a hard constraint, not a choice

**Review qualification, 2026-09-06:** the account-ownership statements below apply to the proposed managed Custom App route. The public App Store row does not by itself require every customer to hold an organisation-management account. Kota Buku/its designated ministry entity is the approved fleet-side partner, but technical administration/delegation and eligibility still need confirmation. Handoff §7 decision 1 is unchanged; its “regardless” rationale is flagged for Hafiz, not silently rewritten.

| Model | Who needs an account | Fits 182,000 external teachers? |
|---|---|---|
| Public App Store | Sifututor: standard developer account; confirm current terms | **Fits** |
| ABM/ASM Custom Apps | Sifututor: same standard developer account, naming Kota Buku's Organization ID | **Fits** |
| Developer Enterprise Program | Restricted to internal employees only | **Disqualified** |

- **Confirmed fact, not inference**: Apple's own guide states the Enterprise Program is "only for the internal use and distribution of proprietary apps... to their employees," and explicitly says it's the wrong vehicle when a public App Store app or Custom App could serve the need instead. The License Agreement defines an "Internal Use Application" as one built solely for the organization's own employees, explicitly excluding any app made available to "vendors, resellers, end-users or members of the general public."
- **Enforcement precedent**: Apple revoked Facebook's (30 Jan 2019) and Google's (31 Jan 2019) enterprise certificates after both used enterprise provisioning to distribute apps to non-employee consumers via paid panels — breaking each company's internal tooling for roughly a day. This is Apple's clearest public demonstration that it actively enforces the employee-only limit, even against major partners. **The disqualification on the terms themselves is settled** (re-verified against the current License Agreement, dated 8 Oct 2025). One fairness note added after adversarial review: the 2019 case was an extreme data-collection/privacy scandal (Facebook paying teenagers to install a traffic-harvesting VPN), i.e. the severe end of the precedent spectrum — enforcement for a milder violation might be less swift or public. That nuance does not change the conclusion: distributing to 182,000 external teachers is squarely outside the licence's "Internal Use Application" definition regardless of how aggressively Apple would police it.
- **Critical structural implication**: Apple confirms the **publisher** (Sifututor) never needs its own ABM/ASM account — only a standard App Store Connect developer account. The **purchasing/using organization** (Kota Buku or its designated ministry entity) must hold the ABM/ASM account, run the MDM, and grant Sifututor's account permission to target its Organization ID. **Sifututor cannot unilaterally control distribution — Kota Buku has to stand up and administer the ABM/ASM instance itself.** This needs to be explicit in any proposal's division of responsibilities.
- **No verified example was found of a national education ministry deploying a vendor-built Custom App via ASM/ABM at six-figure device scale anywhere in the world** — this looks under-documented rather than untried, but it means there's no template to point to reassuringly; Sifututor/Kota Buku would be establishing a new precedent, not following one.

---

### Same-launch exposure and evidence controls — D11, 2026-09-07

Owner-approved proposal scope, not implemented capability ([handoff §13](CODEX-HANDOFF.md)): class view, rule-based learning flags and suggestions, notice/reminder templates and the curated parent digest are planned for all teachers at launch. Plain-language AI analysis, teacher assistant conversation and AI-written administrative drafts enter a guided trial with selected teachers at that same launch, alongside the full AI-drafted RPH beta.

Keep recorded evidence and deterministic aggregation separate from generated interpretation. The trial needs selected-teacher access controls, authorised-record retrieval, visible evidence and missing-data handling, teacher review before use/sending, and a measured quality review before wider access. Identifiable inference, logs and backups must meet D7; no foreign fallback is authorised. Connectivity-dependent generation is not an offline promise. Validate bilingual proposal wording against all four product-language requirements, not just the English demo. Formal assessment, teaching actions and family sharing remain teacher-controlled. Textbook rights, handwriting validation, direct messaging and automatic history-based differentiation at scale retain their existing dependencies/tiers; D11 does not move them into general launch.

## 8. Running it after launch

- **Fleet monitoring**: Jamf Pro's Device Compliance module, Mosyle's "Device Scout" (real-time per-device status "regardless of how many devices"), and Apple's Declarative Device Management (iOS/iPadOS 17.2+, near-real-time compliance reporting instead of polling) are the relevant capabilities — but **no vendor page or case study demonstrates any of this specifically at 100,000-200,000-device scale.**
- **Remote troubleshooting — the "no full remote control" claim, checked**: confirmed that `EraseDevice` and `DeviceLock` MDM commands work on iPadOS, and that Jamf's Remote Assist (full interactive screen-share) is **macOS-only** — partially confirming that iPadOS blocks desktop-style remote takeover. Mosyle has announced a "Screen View" feature that would complicate this, but the primary source 404'd on fetch — **needs re-verification before citing either way.**
- **Support staffing benchmarks** (general K-12 data, mostly US, Chromebook-weighted — treat as rough proxy only): IT-staff-per-1,000-students ratios shrink sharply with scale (5.0 at 1,000 students → 0.4 at 50,000). The commonly-quoted "1 technician per 1,000 devices" rule is explicitly flagged by the source itself as unvalidated folklore. iPad/laptop fleets reportedly need roughly 2-3x the support density of an equivalent Chromebook fleet. 58% of US districts describe themselves as understaffed for instructional-technology support. **No published benchmark exists at 182,000-device, government-fleet, iPad-specific scale.**
- **Update cadence**: the standard pattern separates periodic content-package sync (delta/differential patching, only changed assets) from app-binary updates (App Store/MDM). **Kolibri is again the most directly relevant precedent** — architected around one-time bulk content download plus fully offline daily use, syncing only opportunistically.
- **Bandwidth against the 300GB/month allowance**: general (non-education-specific) proxies — SD video ≈1-2GB/2-hour session, HD ≈3-6GB, typical fully-downloaded offline education apps run 200MB-1GB of device storage. **No education-app-specific benchmark exists mapping onto a 300GB/month capped scenario** — the allowance reads as generous against these proxies, but this is one of the least-evidenced areas in the whole research set and would benefit from Sifututor's own instrumentation once a pilot runs, rather than more external research.

---

### 8.1 Adoption, training and Phase 1 interfaces — adopted 2026-09-06

First-week guided setup and in-app coaching are Core, with BM, English, Mandarin and Tamil parity and accessible workflows (product §2.1). Resource school-level champions for ongoing support; IPGM/IAB remain potential endorsement channels, not verified training throughput. Instrument first attendance, first mark and first RPH completion/quality for the partner’s first two evidence gates, not logins alone. Thresholds, staffing and timetable require agreement; activity is not proof of total workload saved. Teacher analytics are non-punitive by contract and aggregated/anonymised above school (data §7). Source: [review §8.2](partner/SEPADU-review.md).

**Phase 1 has no KPM system integration.** The standalone register and generic export remain Core. idMe, APDM, SPPB and other connectors are later, separately priced in the partner pack, and depend on approval, a data-sharing agreement and verified interfaces. No promise of eliminating duplicate entry. Support ownership/allocations are recorded in the partner pack; these documents do not reproduce them.

## 9. AI infrastructure and cost modeling

### 9.1 What the closest real competitors actually disclose (thin, but real)

Public technical disclosure from MagicSchool AI, SchoolAI, Khanmigo, Curipod, and Diffit is genuinely thin — none has a real engineering blog, conference talk, or funding-diligence document disclosing architecture or unit economics.

- **MagicSchool AI**: company FAQ explicitly states it "uses multiple large language models, including models from OpenAI, Anthropic, and Google, depending on the task... routed to models best suited for educational use cases" — a real multi-model-router claim, but from a support FAQ, not an engineering writeup. Commercial benchmark amounts omitted under D10; public subscriptions are not this programme’s unit costs.
- **SchoolAI**: no engineering content of any kind found — absence of evidence, not evidence of a specific architecture. 1M classrooms, 80+ countries, 400+ districts in two years. Commercial benchmark amounts omitted under D10.
- **Khanmigo (Khan Academy)** — the most information-rich, because it's a nonprofit and discloses more than VC-backed peers:
  - Model: GPT-4, developed jointly with OpenAI, launched March 2023.
  - **The real cost war story**: Sal Khan’s original pilot subscription covered development expenses and OpenAI fees. The individual price later dropped — but only after **Microsoft donated free Azure OpenAI infrastructure/credits in May 2024** specifically to remove the cost barrier gating free teacher access. That subscription price included development expenses; it is not a measured inference cost per user, and the subsidy does not establish this app’s unit economics.
  - **Evidence limit:** a subsidised competitor subscription is not evidence of our all-in inference cost or run-fee feasibility. No commercial comparison is carried forward under D10.
- **Curipod**: the most transparent on model choice — explicitly lists using both cheap/fast and frontier model variants from OpenAI and Google depending on task, showing real cost-tiering in practice.
- **The one genuinely quantified adjacent finding**: Chegg (public company, SEC filings) explicitly told investors it's training proprietary models on 100M+ proprietary Q&A pairs specifically to reduce reliance on costlier third-party AI providers, and disclosed gross-margin compression (57% vs 68% YoY) tied to its AI-era cost shift. This is a **verifiable, SEC-disclosed cost pressure signal** from an adjacent (not identical) edtech business model.

### 9.2 AI cost validation — no competing commercial figures

**D10 supersession, 2026-09-06:** the historical model-price/light-heavy cost table and slot-fit conclusions are removed. Commercial ownership sits in the [partner pack](partner/SEPADU-v1.0-Founder-Briefing.md), not this blueprint. This is not an endorsement of the pack’s inference assumptions.

- **Usage remains unverified:** the earlier token/activity volumes were modeled, not telemetry. A pilot must measure task mix, context/output length, images/OCR, retries and teacher-validation overhead before costing.
- **Pricing remains unverified for procurement:** the first pass reopened only selected [OpenAI pricing](https://developers.openai.com/api/docs/pricing) and [deprecation](https://developers.openai.com/api/docs/deprecations) entries; it did not re-audit every provider or region. The earlier warning about December 2026 retirement of dated GPT-5 snapshots remains a verification lead. No model price, retirement date or replacement can be relied on at contracting without a fresh official check. Do not quote the removed table from an old artifact.
- **Caching and batch work are conditional options**, not promised savings: validate stable prefixes, hit rates, cache writes/expiry and latency suitability. Enterprise discounts remain unnegotiated. Use replaceable capability tiers, not a multi-year dependency on one named model.
- **Regional availability is a separate gate:** as checked 2026-09-06, [AWS’s EC2 table](https://docs.aws.amazon.com/ec2/latest/instancetypes/ec2-instance-regions.html) lists Malaysia G6/Gr6 GPU instances. [Bedrock’s inspected Malaysia model rows](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html) use Global routing, not in-region inference; [Microsoft’s inspected managed-model region table](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure-region-availability) does not establish Malaysian in-region deployment. This is a finding about these services, **not proof no Malaysian inference option exists**. Malaysian endpoints/GPU capacity alone do not prove local processing or model quality. Self-managed inference is an option to validate, not a completed design.
- **Decision 7 stays fixed:** identifiable data, prompts, inference, logs and backups must stay in Malaysia. Model/OCR quality, capacity, security and residency remain unresolved per-service checks. Neither foreign Global routing nor a TIA overrides residency.
- **All-in validation is still missing:** add infrastructure, RAG, support, moderation, MDM, training, development, taxes and exchange-rate exposure when the partner costs the service. On-device offload is not assumed to make the economics work.

---

## 10. RAG / content-grounding architecture for curriculum AI

- **Direct Malaysian precedent exists, and the effect is large — but its scope is narrow** (calibrated after adversarial review, which retrieved the paper's actual results table): a 2025 arXiv preprint by Malaysian researchers (peer-review status not established here) ("Automated Generation of Curriculum-Aligned MCQs for Malaysian Secondary Mathematics," arXiv 2508.04442, Aug 2025) built four pipelines generating Form 1 Mathematics MCQs in Bahasa Melayu using GPT-4o, from non-grounded prompting to full RAG grounded in the study’s teacher notes and lesson-plan reference (not official DSKP documents). **Table 2 results (100 MCQs per method, 400 total):** non-grounded basic/structured prompting scored STS 0.55/0.58 with RAG-QA validity of only **12%/15%**; grounded LangChain/manual RAG scored STS 0.86/0.89 with validity **92%/96%**. These are automated source-grounding metrics, not teacher-validated factual-correctness rates; see the limitations below. Primary: [paper §§3–4 and 6.3](https://arxiv.org/html/2508.04442v1), checked 2026-09-06.
  - **What this does and does not prove — further narrowed after a methodology read of the full paper (2026-09-06).** Three findings weaken it beyond the first calibration: **(1) No human validation at all** — evaluation was fully automated; the authors themselves list "a crucial human-in-the-loop validation study" as future work and admit the framework "is unable to reliably assess the cognitive level of a question." **(2) The "RAG-QA validity" metric is circular** — a separate retrieval-QA pipeline built over the *same* grounding PDF checks whether each generated question's stem can find relevant context in that PDF; "valid" means the source text is findable, not that the question is factually or pedagogically correct. The 92-96% vs 12-15% gap is real but measures grounding/retrievability, not correctness. **(3) The grounding corpus was one chapter** — "Nombor Nisbah" (Rational Numbers), Form 1 Math — using an 84-page set of teacher-prepared notes plus a 1-page official yearly teaching plan (RPT). **No DSKP document and no textbook were used**, so "DSKP-aligned" overstates what was tested. Embedding model: "OpenAI's embedding models" (unspecified); vector store: FAISS. **Honest citation:** early, automated-metric evidence from a single-chapter proof of concept that grounding dramatically improves retrieval-validity of generated Malay-language math MCQs — not teacher-validated, not DSKP-tested, not evidence about lesson planning, chat, essay feedback, other subjects, or other forms. The broader case for RAG rests on the general literature in this section (RAGTruth, TEAS); this paper is a local anchor, not a foundation.
- **TEAS (Trusted Educational AI Standard)**, a peer-reviewed AAAI 2026 paper, is the most directly relevant framework found for educational-AI trustworthiness architecture specifically:
  - Documents a taxonomy of failure modes: confident hallucination in STEM, "vaporized learning" (short-term scores improve while long-term retention degrades), non-deterministic outputs breaking curriculum standardization, black-box opacity preventing institutional auditing.
  - Proposes four pillars: **Verifiability** (grounding with citation to specific curriculum sections), **Stability** (deterministic core-curriculum knowledge across sessions), **Auditability** (institutions can independently inspect the knowledge base), **Pedagogical Soundness** (Socratic scaffolding, not answer-dumping).
  - **Empirical case study**: a knowledge-grounded **8B-parameter model** outperformed ungrounded models up to **15x larger** (including a 120B model) on trustworthiness criteria, at **42-88% lower inference cost**. Central finding: **"Architecture > Scale."** This is a strong, quotable framing for a budget-conscious government pitch.
  - **Important limitation the paper itself flags**: its case study used prompt-based grounding (a knowledge graph pasted into the system prompt), which it explicitly calls **not secure** (vulnerable to prompt injection) and **not enforced** — it recommends proper RAG architecture plus a "separate validation layer that rejects any response lacking valid source citations" for production-grade systems, which is exactly the scale DSKP's full corpus would require.
- **Vector database and data residency**: for a corpus this size (likely low single-digit millions of chunks across DSKP + textbooks), **pgvector on managed Postgres is the 2026 default choice** — and critically, **Azure now has a Malaysia West region** and **Pinecone launched a Singapore region in May 2026**, but Singapore is outside Malaysia. Decision 7 excludes foreign processing/storage of student-identifiable data; curriculum-only public material is a different case. Confirm Malaysian availability for every selected service, including inference, logs and backups.
- **Embedding models**: Google's Gemini Embedding-001 explicitly supports Malay among 100+ languages and tops the MTEB Multilingual leaderboard; BGE-M3 (open-weight) natively does dense+sparse+multi-vector retrieval in one model and supports 100+ languages — a strong self-hosted option if data sovereignty is a hard requirement (keeping curriculum embeddings from ever leaving Malaysian/organization-controlled infrastructure, likely a real KPM/Kota Buku procurement concern).
- **Hybrid search (dense + BM25/sparse) matters specifically for DSKP's structure**: DSKP content is full of exact-match identifiers (Standard Kandungan/Pembelajaran numbering, TP-level labels) that dense embeddings handle poorly but sparse/keyword search handles well. Benchmarks show hybrid fusion improving NDCG by ~7.4% and Recall@10 by up to 5.8x over dense-only. **Metadata pre-filtering keyed to Subject/Form/Topic/TP-level before running search** is the standard pattern for hierarchically-structured content and maps directly onto DSKP's own hierarchy.
- **Measured hallucination reduction from RAG**: RAGTruth (ACL 2024, peer-reviewed) found retrieval grounding reduced hallucination rates by 21.6-63.2% depending on model; a separate industry meta-analysis cites retrieval grounding alone as the single most effective mitigation at -75 to -90% (vendor/aggregator-sourced, treat as directional).
- **Architecture recommendation synthesis** (combining the above): a proper vector-store-backed RAG pipeline (not prompt-stuffing, which DSKP's full size rules out) + hybrid search with DSKP-hierarchy metadata pre-filtering + a hard validation/enforcement layer rejecting ungrounded output is the pattern the evidence converges on. A structured curriculum knowledge graph layered alongside vector retrieval (the TEAS/KAG approach) appears to be the emerging best practice specifically for standards-grounded generation, though the one controlled study found used a small corpus and flagged its own results as needing validation at curriculum scale.

---

## 11. Non-AI infrastructure validation — commercial figures in the partner pack

**D10 supersession, 2026-09-06:** removed the planning-estimate cost table and revenue/headroom arithmetic. No reproducible workload model, regional bill of materials or capacity test supported those estimates. This evidence gap remains open; removing figures does not settle it.

| Cost driver | Evidence required before the partner prices it |
|---|---|
| API/app compute and database | Peak concurrent teachers, school-day bursts, offline sync/retries, storage growth, HA and restore targets |
| Content delivery and bandwidth | Licensed corpus/media sizes, cache behaviour, real download/egress volumes; video is not a negligible addition |
| Malaysian hosting and backups | Exact regional service availability, processing/storage paths, tested capacity, security and recovery |
| Observability and operations | Log retention/volume, incident response, monitoring and support tooling |
| MDM, training and support | Teacher-only fleet baseline; multilingual first-week and ongoing demand, staffed escalation and school-champion resourcing |

The [partner pack](partner/SEPADU-v1.0-Founder-Briefing.md) owns support allocation and commercial numbers. Its [review §§3.4/7/8.2](partner/SEPADU-review.md) flags device-base, workload and training assumptions; no revised quote or support commitment is made here. Residency is a decided constraint, not an optional premium. Procurement/tax applicability checks are in §15.

---

## 12. Case studies: national device+app+content programmes

The clearest, most consistent finding across every case researched: **hardware gets delivered, software/content/teacher-training lags behind, and devices end up "dumped"** — high distribution numbers, low actual classroom usage. This shows up in every failed programme researched.

| Programme | Scale | Headline outcome |
|---|---|---|
| Turkey — FATIH | ~18M devices planned | Only 84,921 of 620,000 planned smartboards installed; tenders cancelled over corruption claims |
| Indonesia — Chromebooks | 1.1-1.2M units | Ministry's own pilot found devices unsuitable for low-connectivity regions, procured anyway; **ex-Minister sentenced 10 years** for rigging the evaluation in Google's favor |
| Kenya — Digital Literacy Programme | 1.17M tablets | Independent M&E found only **64.67% utilisation**; devices later resold across the border; programme scaled back |
| Thailand — One Tablet Per Child | ~860,000 units | Auditor-General reported ~30% broken; the ICT Ministry disputed this at 0.62% — government and its own auditor never reconciled the figure |
| Philippines — DepEd laptops | 68,500 targeted | Unit price rose 66%; only 39,583 delivered; ~70% of allotted units undistributed, some resold at retail |
| USA — LAUSD iPads | 650,000 targeted | Bid specs found to favor Apple/Pearson; superintendent and CTO resigned; settlements recovered funds (historical amount omitted under D10) |
| Rwanda — OLPC | ~274,000 laptops | 96% of schools had no electricity; 939 laptops reported stolen in 2018 alone |
| India — DIKSHA | 180M+ enrolled (claimed) | Independent survey found 24.6% of teachers "rarely" and 15.1% "never" use it, despite headline enrollment numbers |
| Uruguay — Plan Ceibal | ~400,000 laptops | The clear **success** case — built on sustained teacher training and built-in M&E from day one |

- **Indonesia's Chromebook scandal is the starkest cautionary tale for this specific proposal**: it shows that even documented technical unsuitability (the ministry's own pilot said so) doesn't stop procurement decisions driven by other factors — and that the legal consequences of a rigged evaluation can be severe (10-year sentence). **Any proposal process here should be scrupulously transparent about genuine trade-offs (like the iPad model/on-device-AI tension in §3) rather than glossing over them.**
- **Balance notes added after adversarial review** (three of the nine cases were re-checked against primary/contemporary sources and held up; no cherry-picking was found): (1) Google publicly disputes the conflict-of-interest characterization in the Indonesia case, stating its Gojek-related investments predated Makarim's ministerial appointment — the procurement-unsuitability finding (the ministry's own pilot) is undisputed, but the corruption narrative has a contested element. (2) Kenya's 64.67% utilisation figure comes from the ICT Authority's own 2019 M&E study (15 counties) — a government self-report, if anything a conservative source — and that report mentioned a follow-up study "in progress"; whether newer Kenyan data exists showing improvement was not established. Check before citing as current state.
- **DIKSHA (India)** is architecturally the closest "another government already built this" precedent: government-owned/branded platform, built on **Sunbird**, a fully open-source MIT-licensed stack created by a non-profit foundation (EkStep), with commercial vendors contracted for specific pieces (mobile client, cloud infra) — a "public platform, plural contractors" hybrid model. Its real adoption growth was triggered by the COVID-19 crisis, not by the 2017 launch itself, and independent surveys show meaningfully lower actual engagement than headline enrollment numbers suggest.
- **Cross-cutting failure patterns** (recurring across 3+ cases): hardware-first/pedagogy-later sequencing; no implementation model or theory of change at launch (Turkey's own Ministry official: "we are trying to make education fit the given technology" rather than the reverse); teacher training treated as a one-time event, not sustained support; procurement/governance risk materializing as scandal or delay; connectivity/infrastructure assumptions not holding in the field; device-dumping (high distribution, low real usage).
- **Cross-cutting success patterns**: local-language, curriculum-aligned, teacher-contributed content; not making adoption mandatory or adding administrative burden (Indonesia's PMM explicitly designed around this); purpose-built monitoring & evaluation from day one rather than device-count as the sole KPI; offline-first/low-connectivity-tolerant technical design; continuous post-launch iteration on teacher-facing tools, not a single content drop.
- **On "who builds the software" — a genuinely useful finding**: comparing DIKSHA (hybrid public-platform-plural-contractors), Turkey's FATIH (multi-vendor hardware, explicitly to avoid lock-in), and Saudi Arabia's Tatweer (single dedicated vendor entity, TETCO) — **vendor-count structure did not correlate with success or failure** in any case found. What correlated consistently with better outcomes was the presence (or absence) of a genuine implementation model, sustained teacher support, and independent monitoring — governance and pedagogy design factors, not how many vendors were in the stack. **This directly informs how Sifututor should think about its own role**: being the sole vendor or one of several doesn't predict success on its own — what would need to be built into the proposal is the sustained-support and monitoring model itself.

---

## 13. Synthesis: what this means for the proposal

Research synthesis subject to the ten decisions already made by Hafiz (CODEX-HANDOFF.md §7); unresolved evidence is not authority to change those decisions.

1. **Co-branded white-label is decided.** The reader’s documented scope motivates broader teaching workflows; sparse ratings do not prove an easy replacement or lack of adoption (§1).

2. **The device-model ambiguity in redONE's deck is not cosmetic — it's an architecture decision.** iPad A16 (the cheaper model named in some slides) is not eligible for Apple Intelligence; iPad Air M4 (named in other slides) can. This should be surfaced explicitly to Kota Buku/redONE as a real trade-off with a cost consequence, not silently resolved either way.

3. **Cloud-first is a proposed architecture supported by the cloud-backed descriptions reviewed, not validated by universal competitor absence.** No local component was documented in those descriptions (MagicSchool, SchoolAI, Khanmigo, Curipod, Diffit); that does not prove none exists. Local processing is task-specific: deterministic grading works on both supported tiers; OCR and generative simplification require separate runtime/language checks — not a foundation to build the whole product on.

4. **Commercial feasibility is unproven; the partner owns the numbers (D10).** The earlier slot-fit scenarios are superseded, not approved prices. Validate actual usage, caching, current replacement-tier pricing, Malaysian processing and the full support/training/infrastructure burden before any commitment (§§9.2/11).

5. **The Malaysian preprint provides limited local evidence for source-grounded MCQs, not validation of this platform.** Its automated metric is not a correctness rate; DSKP, textbooks and teacher evaluation were not tested (§10). The teacher-validation pilot remains necessary.

6. **The distribution and account-ownership structure has a hard constraint that shapes the whole partnership model**: Apple's Enterprise Program is disqualified by Apple's own terms (with enforcement precedent against Facebook/Google). Kota Buku, not Sifututor, must hold and administer the Apple Business/School Manager account. This needs to be an explicit, early conversation in any deal structuring — it affects who "owns" the relationship with the device fleet regardless of who builds the software.

7. **Every documented failure case shows the same pattern: hardware first, software/content/training later, and it doesn't work.** Sifututor's pitch is structurally well-positioned against this exact failure mode — the whole point of the proposal (per Hafiz's own framing) is "device + application + content, not just device." That framing should be made explicit and load-bearing in the pitch, citing Indonesia/Kenya/Turkey/Rwanda as the pattern being avoided.

8. **Vendor-count doesn't predict success — sustained support and monitoring does.** Within the approved Kota Buku app, delivered by Sifututor, powered by Learnest Lab structure, the proposal should build in a genuine implementation and teacher-support model, and monitoring/evaluation from day one — not just device/app/content delivery.

9. **DIKSHA/Sunbird’s dedicated read is complete in §2.1**; unpublished operational lessons remain a gap before finalizing architecture — it's the closest real "another government built this" precedent found, open-source and technically documented, unlike every commercial competitor researched.

---

## 14. Master list of gaps and follow-ups needed

**Needs direct verification before proposal finalization:**
- Whether a national teacher-only (non-student) programme qualifies for ASM or the business route (eligibility unresolved; see §6 dated Apple Business correction) — needs a direct question to Apple's education/enterprise channel.
- Whether Kota Buku has any existing tender/vendor record for its textbook platform on eperolehan.gov.my (not searchable with available tools this session).
- Live status of textbook.moe.gov.my (fetch failed this session).
- Guideline 5.1.4's "school as consent proxy" question for minors' data — needs Apple's separate privacy documentation or legal counsel, not just the App Store Review Guidelines text.
- **Unresolved:** exact Malaysian inference/OCR service, model quality, capacity and all-in hosting economics (§9.2). AWS Global routing is not Malaysian processing; GPU availability is not a validated service. Residency remains mandatory under D7.
- Whether Mosyle's "Screen View" feature is view-only or full remote input control (source blog post 404'd).

**Genuine research gaps (no source exists, may need direct outreach or Sifututor's own instrumentation):**
- No education-app-specific bandwidth benchmark exists to validate the 300GB/month data allowance against realistic app usage.
- No help-desk staffing ratio or ticket-per-device benchmark exists at anything close to 182,000-device, iPad-specific, government-fleet scale.
- No verified example exists anywhere of a national ministry deploying a vendor-built Custom App via ASM/ABM at six-figure scale — this would be a new precedent, not a followed one.
- IXL's and i-Ready's actual multi-curriculum data models are not publicly documented anywhere (their technical manuals are paywalled/blocked) — CASE (§4) is the best available substitute reference, not a confirmed match to what they actually do internally.

**High-value follow-up reading identified but not completed this session:**
- ~~DIKSHA/Sunbird's technical note PDF — not deep-read.~~ **Resolved (2026-09-06): read in full, see §2.1.** New gaps it exposed: the technote's Appendices A-U (telemetry schema, API reference, RCA findings, release notes) are unpublished; no conflict-resolution strategy is documented anywhere in Sunbird; the Offline Desktop app is still "Coming soon" on the live site; Ask DIKSHA (Sep 2025) has no published technical documentation.
- Morango's (Kolibri's sync engine) actual source-level conflict-resolution algorithm — described at a high level only.
- ~~The full text of the Malaysian DSKP MCQ-generation paper (arXiv 2508.04442) — specific quantitative figures were not retrievable.~~ **Fully resolved (2026-09-06)**: Table 2 results and the full methodology read are in §10. Confirmed: no human validation, circular validity metric, single-chapter non-DSKP corpus. The paper is weaker evidence than first cited; §10 and §13 point 5 now reflect that.

---

*Compiled by Claude Code from research spanning 4 top-level agents (one split into 5 sub-agents), 2026-09-06. Companion document: [research-findings.md](research-findings.md) (market/policy/competitive research). Next session on this proposal should start by re-reading both files rather than re-researching any of the above.*

## 15. Regulatory and contracting checks — 2026-09-06

This is a sourced applicability checklist, not legal advice, an executed contract or permission for outreach. Exact entities, procurement route, designation and contractual flow-down remain unverified.

### 15.1 Cyber Security Act 2024 (Act 854)

If an operator is designated as a national critical information infrastructure (NCII) entity, known/suspected incidents require immediate notification to the NACSA Chief Executive and sector lead, prescribed particulars within **six hours of entity knowledge**, and supplementary information within **fourteen days after immediate notification**. Contractual vendor escalation must be fast enough to support these duties, separate from PDPA reporting. Designation can cover an owner/operator, not only KPM; vendor exemption cannot be assumed. Applicable cybersecurity-service licensing also needs a service-specific check, not a blanket “not our licence” conclusion. [Act 854 §§17/23](https://lom.agc.gov.my/ilims/upload/portal/akta/outputaktap/2177706_BI/Act%20854.pdf); [notification regulations reg. 2](https://www.nacsa.gov.my/doc/CYBER%20SECURITY%20%28NOTIFICATION%20OF%20CYBER%20SECURITY%20INCIDENT%29.pdf). Covered entities also face annual risk assessment and at-least-biennial audit; applicability remains unestablished. [Risk/audit regulations](https://www.nacsa.gov.my/doc/CYBER%20SECURITY%20%28PERIOD%20FOR%20CYBER%20SECURITY%20RISK%20ASSESSMENT%20AND%20AUDIT%29.pdf).

### 15.2 Procurement and the proposed contracting chain

**Correction to review §6.2:** the official enactment is the **Government Procurement Act 2026 (Act 882)**. Section 35 addresses unapproved transfer, assignment and novation; it is not an express blanket subcontracting prohibition. Section 1 leaves commencement to Gazette notification; no commencement notice was established in this check. Section 93(7) preserves the prior regime for already-commenced procurements. Do not claim automatic mid-delivery criminal exposure merely because the Act commences. [Official Act §§1/35/93](https://lom.agc.gov.my/ilims/upload/portal/akta/outputaktap/3522709_BI/Act%20882%20-%20GOVERNMENT%20PROCUREMENT%20ACT%202026.pdf).

For the proposed KPM → redONE → Kota Buku → Sifututor chain, establish the actual procurement/payer and start date, confirm Treasury and contract applicability at each link, disclose proposed subcontracting, and secure required approvals. The chain itself is not an executed arrangement.

| Contract issue | Carry forward from review §6.3 — verification still required |
|---|---|
| Advance payment | Confirm applicable Treasury ceiling and guarantee requirements; do not assume the pack’s schedule is permitted |
| Retention / performance security | Confirm whether service-contract performance security rather than works retention applies; exact threshold/basis unresolved |
| Delay damages (LAD) | Verify applicable ICT contract formula, cap position and relief for dependencies; no unverified formula adopted |
| Payment timing | Check AP 103(a), complete-document requirements and each intermediary’s terms; a government payment target is not an end-to-end cash-receipt guarantee |

**Primary Treasury circular/ICT terms not verified here.** This preserves review §6.3’s evidence flag without converting secondary summaries into binding norms or duplicating commercial figures.

### 15.3 Tax and AI governance

- **Service tax:** RMCD confirms the standard **8%** rate from March 2024. Exact IT-service classification, registration and exemptions for this supplier/recipient/contract remain open; KPM affiliation alone is not proof of exemption. The indexed current IT-guide PDF could not be retrieved. Calculations belong in the partner pack. [RMCD FAQ](https://mysst.customs.gov.my/faq-services-tax/); [official guide index](https://mysst.customs.gov.my/industry-guides/).
- **AIGE:** carry the national ethics/governance principles as guidance, not statute; minor-specific provisions remain unverified. [MOSTI announcement](https://www.mosti.gov.my/en/berita/garis-panduan-tadbir-urus-dan-etika-kecerdasan-buatan-negara-aige/).
- **KPM Circular Bil. 2/2026 and AI literacy guide:** published by KPM; inspect the signed instrument and scope before asserting vendor obligations. The official index date conflicts with the review’s June issue-date attribution, so exact date remains unverified. Do not call it the sole binding AI instrument. [KPM publication](https://www.moe.gov.my/surat-pekeliling-ikhtisas-kpm-ai).
- **AI Malaysia Berhad / AI Governance Bill:** the Ministry’s announcement records the institution and then-drafting Bill; the consultation is not enacted law. Later legislative status must be monitored, not presumed. No engagement is authorised by this review. [Digital Ministry](https://www.digital.gov.my/siaran/AI-Malaysia-Pemacu-Utama-Menuju-Negara-AI-2030); [official consultation](https://upc.mpc.gov.my/view-consultation/264).
