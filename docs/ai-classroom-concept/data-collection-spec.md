# AI Classroom — Data Collection Specification (the "national education data asset")

**Requirement this answers (Hafiz, 2026-09-06):** *"make sure we collect every data we have from the student/teacher throughout the journey so that later the gov can use it for themselves for the better of the country and education."*

**D8–D10 alignment, 2026-09-06:** co-branded Kota Buku app, delivered by Sifututor, powered by Learnest Lab; Hafiz must confirm the exact contracting legal entity and processing-party schedule. Teacher devices only does not cancel existing parent/pupil web access. Programme commercial figures belong solely in the [partner pack](partner/SEPADU-v1.0-Founder-Briefing.md); this spec stays figure-free. **C4 decided by Hafiz, 2026-09-06: blend teacher-workload reduction with AI-classroom capability** (handoff §7 C4). Reporting remains bounded by D7 and the evidence limits; no proven outcome is implied. [Review §2/§10](partner/SEPADU-review.md).

**Decisions that frame it (all Hafiz, 2026-09-06 — see `CODEX-HANDOFF.md` §7):** build the capture and governance fully; the written proposal calls it "reporting and analytics," not a national data asset (the data-asset value is raised in conversation). KPM (via Kota Buku) is the data controller and owner; Learnest Lab is the PDPA processor; data is Malaysia-resident.

**Research basis:** 8 targeted agents on 2026-09-06 covering what Malaysian teachers already record system by system; the Standard 1 to Form 5 journey at every transition; KPM's own KPIs and acknowledged data gaps; and how the UK, Australia, Estonia, Singapore and the US govern national education datasets (plus Korea NEIS and India DIKSHA from earlier research). Same evidence discipline as the companion docs: **[P]** = read from a primary/official document; **[N]** = reputable news reporting an official statement; **[S]** = secondary/SEO/blog or document-mirror only — treat as unverified. A consolidated verification list is in §10.

Companion documents: [research-findings.md](research-findings.md) (why), [technical-build-blueprint.md](technical-build-blueprint.md) (how), [product-feature-spec.md](product-feature-spec.md) (what). This document defines *what data*, *from whom*, *when*, *what to read vs. add*, *what not to collect*, and *how it is governed*.

---

## Table of contents

1. [The one-paragraph answer](#1-the-one-paragraph-answer)
2. [The Malaysian school journey as a data timeline](#2-the-malaysian-school-journey-as-a-data-timeline)
3. [What teachers already record, system by system — read, do not duplicate](#3-what-teachers-already-record-system-by-system)
4. [What no system captures — the app's unique contribution](#4-what-no-system-captures)
5. [The collection specification, by moment and role](#5-the-collection-specification-by-moment-and-role)
6. [What NOT to collect — bounded scope](#6-what-not-to-collect)
7. [Governance layer — the quiet part that makes it survivable](#7-governance-layer)
8. [Interfaces with KPM systems and the curriculum](#8-interfaces-with-kpm-systems-and-the-curriculum)
9. [What this gives KPM (for the conversation, not the document)](#9-what-this-gives-kpm)
10. [Verification status and open items](#10-verification-status-and-open-items)
11. [Next actions](#11-next-actions)

---

## 1. The one-paragraph answer

Malaysia already records a great deal about each pupil — attendance, biodata, aid status, health, discipline, co-curricular scores, psychometric inventories, and a consolidated mastery level (TP1–6) per learning standard at reporting points — across APDM, SPPB, SSDM, e-RKM and SiPKPM. **No approved third-party API route or equivalent end-to-end learning-process dataset was found in the reviewed public material as of 2026-09-06. This is an evidence limit, not proof that no internal API or learning records exist.** PBD records one TP level per standard at a checkpoint; the reviewed public sources do not establish an end-to-end record of which standards a class actually spent time on, how each pupil answered each item, what the teacher tried when it didn't work, or the trajectory that produced the TP. KPM has diagnosed this gap itself: the new centralised Matriks Pembelajaran (Year 4 in Oct 2026, Form 3 in 2027) exists because school-set UASA gave the ministry no nationally comparable mastery data. **The app should therefore (a) read what KPM already holds, through a data-sharing agreement rather than re-keying; (b) capture, comprehensively and continuously, the proposed learning-process layer (absence elsewhere is not proven); and (c) never re-collect the sensitive welfare and family fields that already feed KPM's own risk system.** Every event is tagged to the DSKP standard and curriculum version, stored in Malaysia, owned by KPM, and governed by written purposes, tiered access, audit logs and a live consent channel — a governance design informed by the Estonia and inBloom cases, not proof that one factor alone explains either outcome.

---

## 2. The Malaysian school journey as a data timeline

| Stage | What happens | Record produced | Held today in | Used downstream for | Gap the app can fill |
|---|---|---|---|---|---|
| **Entry to Year 1** | Compulsory from age 6 on 1 Jan of the school year (Education Act 1996 s.29A; cohort popularly labelled "7") **[P]**. RPM 2026-2035: age-6 entry from 2027 is **voluntary**; mandatory preschool from 2031 via new legislation **[P, RPM pp.94-95]**. | Enrolment, biodata, guardian, address | APDM | Placement, aid, planning | Baseline learning profile at entry does not exist |
| **Year 1, month 3** | **Saringan Murid Tahun 1 / Program Intervensi Tahun 1 (PIT1)**: literacy (BM or SJKC/SJKT medium) and numeracy screening; Phase 1 intervention Jul–Sep, Phase 2 Oct–Dec **[S, KPM slide deck]**. Official dataset "Saringan Murid Tahun 1 Malaysia" cited in RPM: **RPM prints 11% beside 122,062 of 448,113 (2024), an internal arithmetic inconsistency: those counts imply 27.24%** **[P, preserved RPM text, pp.73-74; checked 2026-09-06]**. A conflicting 27.5% figure exists **[S]**. **Open:** reconcile the source/denominator; no percentage is cleared for quoting. | Screening result, intervention list | **APDM: Pemulihan Khas module** (remedial teacher) **[S, two KPM-linked sources]** | Remedial placement; RPM literacy targets | Whether the intervention *worked*, week by week, is not recorded anywhere |
| **Years 1–3 (Tahap 1)** | PBD continuous; no mid/year-end exams since 2019 **[S]**. KKM health screening at Year 1 (RKM1/e-RKM) **[P, MOH]**. | TP per learning standard, twice-yearly report | SPPB (PBD module) via BPK Excel templates **[P, UASA guideline cl.7.1]** | Reporting to parents; moderation | Per-item and per-lesson evidence behind each TP |
| **Years 4–6 (Tahap 2)** | PBD + **UASA** (school-set papers on LP-supplied instruments; BM, BI, Maths, Science, Sejarah; TP1–6 only, no raw scores shown) **[P; historical guideline, current marks/grade reporting format still needs verification]**. **Matriks Pembelajaran Tahun 4 (MPT4)**, centrally set by Lembaga Peperiksaan, first sitting **6–8 Oct 2026**, diagnostic not ranking **[N, dates S]**. Psychometric inventories extended to Years 4–6 from 2023/24 **[S, moe-dl site]**. SEGAK fitness twice yearly from Year 4 **[S]**. KKM screening at Year 6 **[P, MOH]**. Pemulihan Khas placement (reported <50% BM/Maths, IPP2M/IKAM instruments) **[S]**. | TP per standard; UASA TP; MPT4 result; PAJSK yearly; SEGAK; PPsi | SPPB; LP (MPT4); SPPB-PAJSK; idMe (SEGAK, reported) | Intervention in Years 5–6; SBP/MRSM selection inputs | Everything between the two snapshots (PBD checkpoints and MPT4) |
| **Year 6 → Form 1** | Ordinary placement by **address/zone** via APDM eDaftar Menengah (BPPS form) — not academic **[S, moe-dl district site]**. SJKC/SJKT leavers with **TP1–2 in BM** go to Kelas Peralihan (appeal via a BM literacy test, name inconsistent UPLBM/UPKP) **[S]**. **SBP/MRSM/SMKA/SMT/KV** via the centralised **PKSK** test on spskt1.moe.gov.my **[P, portal exists]** plus PBD, PAJSK, PPsi, and socioeconomic status (reported SBP weights PKSK 40 / PAJSK 25 / SES 20 / PBD 10 / leadership 5) **[S]**; MRSM confirms PBD, co-curricular and B40 priority **[P, MARA FAQ]**. | Placement; PKSK score; Peralihan decision | APDM; LP/BPSBP; MARA | School allocation; selective admission | A pupil's Year 6 learning profile does not travel with them to Form 1 in any usable form |
| **Forms 1–3** | PBD + UASA (Forms 1–3). **No central Form 3 exam** since PT3 was abolished (2 Jun 2022) **[N]** until **MPT3 in 2027** (adds Sejarah) **[N]**. PPsi Inventori Minat Kerjaya at Form 1 and Form 3 **[S, moe-dl site]**; KKM screening at Form 1 and Form 3 **[P, MOH]**. SSDM records misconduct only (positive-conduct logging removed Nov 2025) **[N]**. | TP per standard; UASA; PPsi; SSDM cases | SPPB; LP (PPsi); SSDM | Form 4 package decision | Same as primary: the process layer |
| **Form 3 → Form 4** | Streaming replaced by **subject packages** (STEM A/B/C; Kemanusiaan & Sastera Ikhtisas) from 2020 **[N]**. Selection is multi-factor: UASA (esp. Science/Maths), PBD (reported **TP4** threshold for STEM), PPsi, attendance/conduct, counsellor and parent discussion **[S]**. KV/SMT/MRSM entry via PKSK **[P, portal]**. | Package assignment; PKSK | School; SPPB; LP | Determines SPM subject set | The evidence trail behind a package decision is not structured anywhere |
| **Forms 4–5** | PBD; **SPM** (≥6 compulsory subjects; **BM and Sejarah must be passed**; from Jan 2026 mandatory for international/religious/UEC streams too, mechanics still under study as of May 2026) **[N]**. PPsi at Form 5 **[S]**. PAJSK cumulative CGPA closes **[P]**. | SPM grades; PAJSK CGPA | LP; SPPB-PAJSK | UPU admissions (90% academic / 10% co-curricular in the 2026/27 UPU circular §5.4) **[P]**; matriculation criteria require a separate source; STPM; TVET; JPA/MARA (academics + co-curricular + interview + B40) **[S]** | Continuous mastery evidence for the two years before SPM |
| **Recurring records (age-specific eligibility below)** | Daily attendance (APDM; categories present/late/absent-with/without reason; escalation letters) **[S]**. **PAJSK** assessed yearly for Year 4–Form 5 within this product’s scope (not Years 1–3), GPA + running CGPA, recorded in SPPB, slip verified with parents, disputes to BSKK within 15 days **[P, PAJSK guideline]**. **SEGAK** twice yearly Year 4–Form 5 **[S]**. Aid eligibility is programme-specific: RMT/KWAPM income rules must not be generalised to BAP **[P, MOE/MOF pages in original research; exact current programme criteria require linked primary verification]**. **SiPKPM** dropout-risk tracking with an AI intervention module from 2026, scoring 7 indicators: attendance, academic results, discipline, distance to school, household income, parental marital status, disability **[N, partially verified]**. Teacher: RPH daily (reported simplification to Objektif/Aktiviti/Refleksi) **[N]**, Buku Rekod Mengajar, PBPPP appraisal via e-Prestasi/HRMIS **[S]**; SPLKPM training log **abolished from 2026** **[N]**; manual co-curricular recording abolished **[N]**. | Attendance; PAJSK; SEGAK; aid flags; risk band; RPH | APDM; SPPB; SSDM; SiPKPM; e-Prestasi; paper/eRPH | Aid, risk intervention, appraisal, university merit | Attendance and risk are recorded; *engagement in lessons* is not. RPH is planned, never linked to outcomes. |

**Cohort note for architecture (see blueprint §1.6/§4):** KSSR/KSSM and Kurikulum Persekolahan 2027 coexist from 2027 to ~2031, one cohort at a time. Every record below carries a curriculum-version tag.

---

## 3. What teachers already record, system by system

The rule: **read or sync; never make a teacher enter it twice.** An academic study found ~80% of teachers agree APDM/SMM duplicate their work (three entries of the same data: Kad 001(M), SMM, APDM) — the app must not become the fourth **[S, ResearchGate; metadata unverified]**. In 2024 teachers reported losing entered marks when idMe/MOEIS failed to autosave **[N, Scoop.my via NUTP]** — a direct argument for the offline-first, local-persist design in the blueprint.

| System | Official name | Who enters | What | Access today | App posture |
|---|---|---|---|---|---|
| **APDM** | Aplikasi Pangkalan Data Murid | Class teacher; school APDM admin | Biodata, guardian, address, transport, **daily attendance**, health flags, **household income (PIR)**, aid status (KWAPM, RMT, SPBT, PSS, SBT), Form 1 placement (eDaftar), **Pemulihan Khas module** (Year 1 intervention list) | Portal only (apdm.moe.gov.my), via idMe. **No API or export documented.** | **Read** roster, attendance, remedial/intervention flags under a DSA. **Write** attendance back only if KPM grants a path; otherwise provide a generic export; APDM-compatible formats/import remain unconfirmed. Never store income/aid detail. |
| **SPPB KPM** | Sistem Pengurusan Pentaksiran Bersepadu (successor to SAPS; 13 modules reported) | Subject teacher (PBD, UASA); co-curricular teacher (PAJSK) | **TP1–6 per learning standard** and TP Keseluruhan per subject (mid-year, year-end); UASA TP; **PAJSK** yearly marks (each co-curricular category 110 marks: involvement 50, participation 40, achievement 20; best 2 of 3 count) **[P]** | Portal, module within idMe/MOEIS. Reporting also via **BPK Excel templates**. No API found. | **Support the teacher’s PBD TP judgement** from evidence; compatible export/upload is conditional on obtaining and validating the current BPK template and SPPB import route. **Read** PAJSK and UASA as context. The TP Keseluruhan aggregation rule is unverified — obtain the template. |
| **Matriks Pembelajaran (MPT4 / MPT3)** | Lembaga Peperiksaan | LP | Centralised diagnostic result, Year 4 (2026), Form 3 (2027) | LP-held; too new for any access path | **Read** when LP allows; the app's continuous data is the bridge *between* these snapshots. |
| **SSDM** | Sistem Sahsiah Diri Murid | Discipline teacher | Misconduct cases and actions (positive-conduct logging removed Nov 2025) | Portal | **Read** case counts only if KPM grants it for at-risk context. **Do not** log behaviour in the app (feature spec: SEL/behaviour points deliberately not a headline). |
| **SiPKPM** | Sistem Pengesanan Murid KPM | KPM (AI module from 2026) | Dropout-risk band from 7 indicators | KPM-internal | **Supply** learning-engagement signals to it; **read** risk flags for the teacher if permitted. Never re-derive risk from welfare fields. |
| **e-RKM / RKM1** | Buku Rekod Kesihatan Murid (KKM) | School health team / KKM | Consent, allergies, immunisation, BMI (Years 1, 6; Forms 1, 3) | erkm.moe.gov.my; MOH-held | **Do not touch.** Health data is out of scope. |
| **LP psychometrics (PPsi)** | Inventori Personaliti, Inventori Minat Kerjaya, aptitude | Counsellor / LP | Personality, career-interest, aptitude profiles (Years 4–6; Forms 1, 3, 5) | LP-held | **Pointer only** (that a profile exists) for the counsellor's own view; never copy results. |
| **e-Prestasi / HRMIS** | PBPPP teacher appraisal | Admin | Teacher performance scores | Portal | **Firewall.** No app telemetry ever feeds appraisal (§7.7). |
| **RPH / Buku Rekod Mengajar** | Daily lesson plan; eRPH | Every teacher | Objectives, activities, reflection (+ success criteria, resources, TP reference in fuller formats) | Paper, file, or eRPH (teacher's choice); admin checks | **Replace** the paper artefact: the app *is* the RPH, and the plan becomes a structured lesson event (§5.1). Export/print in the accepted format. |
| **SPBT** | Textbook loans | SPBT teacher | Loan records (Borang SPBT G) | Paper/school | Out of scope. |
| **idMe / MOEIS** | KPM identity layer | — | SSO across DELIMa, eRPH, APDM, SPPB | The real integration surface | **Authenticate teachers via idMe** if KPM allows federation; this is the one technical hook that demonstrably exists. |

**Finding that shapes everything:** no approved public API/bulk-export route was established by this review. Phase 1 has no KPM integration: Core is the standalone register plus generic export. Later APDM-compatible formats and sync are conditional on a data-sharing agreement, permission and verified receiving interfaces, and separately priced in the partner pack (§8).

---

## 4. What no system captures

This is the asset. Each item below is confirmed absent from every KPM system found:

1. **Per-item, per-attempt results** — PBD holds one TP per standard per checkpoint; no raw responses, no attempt history, no misconception pattern.
2. **Actual instructional coverage** — which learning standards a class spent time on, for how long, and how far behind the yearly scheme (RPT) it is. RPH records the *plan*; nothing records the *actual*.
3. **In-lesson comprehension signals** — formative checks, hands-up/response rates, re-teach triggers.
4. **The trajectory behind a TP** — the sequence of attempts and interventions between "TP2 in March" and "TP4 in October."
5. **Objective-to-outcome linkage** — RPH objectives and PBD results live in different documents with no join.
6. **Structured teacher adaptations** — what differentiation or intervention was tried and with what observed effect; "refleksi" today is free text and unaggregatable.
7. **Intervention effectiveness** — PIT1 and Pemulihan Khas record *who* was placed, not whether they progressed week to week.
8. **Cross-system pupil view** — attendance dips, discipline, health and results are siloed; KPM's own SiPKPM is the first attempt at a join, and it lacks learning signals.
9. **A learning profile that travels** — Year 6 → Form 1 and Form 3 → Form 4 decisions are made without a structured evidence trail.
10. **Nationally comparable classroom-level mastery** — KPM built MPT4/MPT3 because UASA is school-set; nothing exists at the granularity of a lesson or a week.

---

## 5. The collection specification, by moment and role

**Measurement boundary, 2026-09-06:** capture only events actually observable through the approved teacher/pupil workflow. A later photo scan does not reveal a pupil’s original response time, hint use or learning process. Missing data stays missing; it must not become a zero score or an inferred event. Assessment estimates, item target TP and teacher-confirmed PBD judgements are different fields/concepts. Common curriculum IDs do not establish cross-school score equivalence (§9). These qualifications preserve comprehensive learning capture without pretending every proposed field is currently observable.

Event model: adopt the **Sunbird telemetry pattern** (blueprint §2.1) — one envelope (`event id, timestamp, message id, actor, object, event data, context {school, class, subject, curriculum version, device, session, offline flag}, tags`) and a small set of event types (START/END, IMPRESSION, INTERACT, ASSESS, RESPONSE, FEEDBACK, AUDIT, ERROR, SUMMARY). Every learning event carries the **DSKP identifier** (subject → year/form → content standard → learning standard) and the **curriculum version** (KSSR-2017 / KSSM / KP2027), using the CASE-style taxonomy in blueprint §4. Events are written locally first and synced opportunistically (offline-first, blueprint §2).

### 5.1 Per lesson (teacher, on the iPad)

| Data | Captured how | Why it matters |
|---|---|---|
| Lesson identity: class, subject, date, period, curriculum version | Automatic from timetable/roster | Joins everything else |
| **Standards planned vs. standards actually taught** (DSKP ids) with time on each | Teacher selects at planning; confirms/edits at lesson end (one tap) | Fills gap §4.2; feeds pacing vs. RPT |
| Objectives and success criteria | From the RPH template (Level 1); AI-drafted in Level 2 beta | Enables §4.5 linkage |
| Activities run, resources used (incl. Kota Buku textbook page/chapter ids), teaching aids | Selected from the plan; usage logged automatically when opened in-app | Content-effectiveness analysis for KPM and Kota Buku |
| **Formative check results** — per pupil, per item, response, correct/incorrect, time | Live in-app quiz/poll; bubble/tick sheets by camera (MVP); handwritten OCR later | Fills §4.1 and §4.3 |
| Participation signals | Response rate to polls, pupils who responded, teacher-tapped observations ("needs help", "absent from activity") | Fills §4.3; supplies SiPKPM an engagement signal it lacks |
| Differentiation and intervention applied | Structured pick-list (re-taught, paired, extra worksheet, referred to remedial) + optional note | Fills §4.6 |
| **Reflection** | Two structured fields (what worked / what to change) + free text; ties to next lesson's plan | Replaces RPH refleksi with something aggregatable |
| Attendance for the session | Register (Core), APDM sync/export (Fast-follow) | Required anyway; do not duplicate |

### 5.2 Per assessment item and attempt

| Data | Notes |
|---|---|
| Item bank metadata: DSKP standard, target TP band, item type, Bloom level, language (BM/EN/other), source (teacher / AI-generated with model+prompt version / Kota Buku page), teacher approval state | Provenance of AI-generated items is itself a governance record |
| Per pupil per attempt: response, score, time, attempt number, mode (live / paper-scanned / homework) | The unit of the asset |
| Teacher overrides of any auto-score, with reason | Audit trail; the "teacher always acts" rule (feature spec §9.3) |
| Worksheet/test instance: which items, which pupils, when set, when returned | Turns homework into structured data for the first time |

### 5.3 Per pupil, longitudinal (the learning record)

| Data | Source | Notes |
|---|---|---|
| Mastery estimate per DSKP standard — TP band, continuous internal score, confidence, last evidence date | Derived from 5.1/5.2 | The trajectory in §4.4; feeds the PBD export |
| PBD reporting outputs (mid-year, year-end TP per standard; TP Keseluruhan) | Produced by the app in BPK template format | Aggregation rule to be confirmed against the actual template |
| Attendance summary | Register / APDM | Read-only context |
| Intervention history: remedial/PIT1 status (read from APDM: Pemulihan Khas if permitted), in-app interventions and their measured effect | Read + app | Fills §4.7 |
| Contextual pointers only: PAJSK status, PPsi profile exists, SiPKPM risk band (if granted) | Read-only | Never copied into app tables beyond a flag |
| Consent state, notice acknowledged, portal access grants | App | Required by §7 |
| Transfer record: on school change, the learning record moves with the pupil (KPM-controlled) | App via controller | Fills §4.9 |

### 5.4 Per class and school

| Data | Notes |
|---|---|
| Standards coverage and pacing vs. the yearly plan | Answers "is this class behind, and where" |
| Mastery distribution per standard; re-teach events; class-level flags ("60% missed standard X") | Feature spec Pillar 4 class-level view |
| Content usage: which Kota Buku pages, which generated items, with outcome | The evidence Kota Buku has never had about its own textbooks |
| School aggregates for the head teacher: coverage, mastery, attendance, intervention load | Access-tiered (§7.3) |

### 5.5 Per teacher (workflow telemetry — purpose-bound)

| Data | Purpose | Hard rule |
|---|---|---|
| Feature usage, time-on-task proxies (planning, marking, reporting), offline/online sessions, errors | Controller-instructed service improvement; **workflow proxies, not proof of the 80:20 teaching-time split** (announced 24 Mar 2026) | **Never** exported to e-Prestasi/PBPPP or any appraisal; individual teacher data visible only to that teacher and the immediate school leader; aggregated/anonymised only above school; **non-punitive by contract** (§7.7) |
| AI usage: prompts category, model tier, tokens, cost, acceptance/edit rate of AI drafts | Cost governance (blueprint §9); quality monitoring for the Level 2 beta | Prompt *text* retained only as needed for quality review, short retention |
| RPH authoring events, template use, sharing library contributions | Measures the workload relief the pitch promises | Same firewall |

### 5.6 Parent/student surface (separate web app — feature spec Pillar 6)

| Data | Notes |
|---|---|
| Views of the curated, age-gated digest; message threads (Fast-follow) | Minimal; time-boxed digest, not continuous tracking |
| Consent/notice acknowledgements; complaint or objection submissions | The live channel whose absence sank inBloom and drove the UK campaign |

---

## 6. What NOT to collect

"Every data point about **learning**" is the requirement; "every field about the **child**" is the inBloom failure mode (~400 fields including health, discipline and welfare, no consent, a commercial intermediary — shut down in a year with no breach ever occurring). The bounded scope:

| Excluded | Why | Where it lives instead |
|---|---|---|
| Household income, aid eligibility detail, eKasih/PGK status | Already in APDM and feeds SiPKPM; no learning purpose; maximum political and PDPA exposure | APDM (read a flag only if the controller grants it) |
| Parental marital status, family circumstances, disability status | SiPKPM indicators; sensitive; no learning purpose | APDM / SiPKPM |
| Health, immunisation, allergies, BMI | MOH/KKM domain | e-RKM |
| Religion and ethnicity (language/teaching medium is a separate field; roster import is not authority to retain these) | Korea NEIS's flashpoint | APDM |
| Biometrics of any kind (face/fingerprint attendance) | "Sensitive personal data" under the 2024 PDPA amendment | — |
| Psychometric results | LP-held; profile *pointer* only | LP |
| Behaviour/merit points, SEL scoring | Evidence for the tooling is weak (research-findings §6.5); SSDM already logs misconduct | SSDM |
| Location or device tracking, continuous parent-facing monitoring | Adolescent-autonomy research; NEIS/inBloom | — |
| Free-text notes about a pupil's home life | Unstructured sensitive data with no governance | — |
| Teacher telemetry for appraisal | Destroys teacher trust (NUTP); see §7.7 | — |

---

## 7. Governance layer

**Status, 2026-09-06:** this is the approved proposed governance direction, not an executed DPA or a legal opinion. Actual controller identity, statutory authority, each party’s PDPA applicability, breach duties and retention schedules require confirmation; the four owner questions in §11 remain unchanged. Research §3.2 now cites the existing under-18 parental-consent rule directly; the status of later verification amendments beyond the March 2026 commentary remains unverified.

Design distilled from what the durable systems share (Estonia EHIS, UK's research-access tier, Singapore's public-sector framework) and the failed ones lack (inBloom; UK's Home Office data-sharing episode; the original Australian schools-USI proposal).

### 7.1 Ownership and roles
- **Contracting identity clarification (D9):** Sifututor fronts and contracts, with Learnest Lab visible as product technology. The processor role described below is functional; do not treat a product brand as a verified legal entity or infer two independent processing companies. Hafiz must name the signing entity and any approved sub-processor relationship in the DPA. No change to D7’s ownership, processor-only purposes or residency.
- **Controller and owner: KPM** (via Perbadanan Kota Buku as the contracting body — confirm which entity signs). **Processor: Learnest Lab**, under a written data-processing agreement in the GDPR-Article-28 style: process only on documented instructions, no independent use, sub-processor approval, deletion/return on exit. Under the 2024 PDPA amendment the processor carries direct security duties and criminal exposure, so the agreement protects both sides.
- **Estonia pattern:** the app captures; the authoritative register is the state's. Learnest Lab never becomes a second copy-holder of the canonical record beyond the operational database needed to run the service, and that database is contractually KPM's.
- **Malaysia residency** for all pupil-identifiable data (AWS Malaysia region or an approved Malaysian cloud; Azure Malaysia West for any vector store — blueprint §10/§11). Decision 7 is stricter than a possible legal transfer route: pupil-identifiable processing, including inference, prompts, logs and backups, stays in Malaysia. A TIA alone does not override it. Foreign calls may use public curriculum or demonstrably anonymous content only; pseudonymisation alone is not anonymity. Unavailable Malaysian OCR/inference is an unresolved delivery constraint, not permission to transfer.

### 7.2 Purpose register (written, published to schools and parents)
1. Support the pupil's own teacher in teaching, assessing and reporting (PBD).
2. Support the school's improvement and intervention decisions.
3. Support KPM/JPN/PPD policy, planning and intervention (SiPKPM enrichment, RPM targets, curriculum evaluation) on **aggregated or controller-authorised** views.
4. Approved research, through the gate in §7.4.
5. Controller-instructed service operation and improvement only; no independent vendor use of pupil data. Any separately used anonymous statistics require demonstrated anonymisation and contractual permission.
Any new purpose requires the controller's written approval and, where it goes beyond education, fresh notice/consent. **The UK lesson:** collection under one legal basis, then repurposing (immigration enforcement) without a new gate, is what triggered the ICO finding and a decade of campaigning.

### 7.3 Access tiers — pupil records and the teacher-specific restriction

**Teacher-specific G1 restriction (adopted 2026-09-06):** individual teacher data is visible only to the teacher and the immediate school leader. Above-school teacher reporting is aggregated/anonymised only: the pupil-record authorisation routes in the table do **not** permit PPD/JPN/KPM or researchers to drill into individual teacher telemetry. Suppression and linkage-risk checks apply (§7.8). Minimised, logged emergency service/security access is not a teacher-performance reporting tier. [Partner G1/G2 and review §10](partner/SEPADU-review.md).

**Pupil-record access tiers (not permission to bypass teacher G1 above):**

| Who | Sees | Individual-level? |
|---|---|---|
| Subject/class teacher | Own classes | Yes, own pupils |
| Head teacher / GPK | Own school | Yes, for a documented duty (intervention, moderation) — logged |
| PPD / JPN officers | District/state aggregates; drill-down only under a controller policy | Only via controller authorisation, logged |
| KPM HQ | National aggregates; individual access via controller process | Only for a documented authorised purpose, logged |
| Parent / pupil | Own child's curated digest (age-gated, feature spec Pillar 6) | Own only |
| Researchers | Pseudonymised extracts in a controlled environment | Potentially re-identifiable personal data; no direct identifiers, controlled access, no re-identification |
| Public | Suppressed, rounded statistics | No |
| Learnest Lab staff | Operational access on a break-glass basis, logged and reviewed | Minimised |

### 7.4 Research and secondary use — "Five Safes"
Safe people (vetted, trained), safe projects (approved public-good purpose), safe settings (controlled environment, no download), safe data (pseudonymised, small cells suppressed), safe outputs (checked before release). Re-identification attempts are a contractual breach and, following Singapore's 2026 public-sector amendment pattern, should be a penalty in the DSA.

### 7.5 Consent and notice
- Proposed basis for the core learning record: KPM’s education function, subject to confirmation of the actual controller, statutory authority and applicable legal regime (not established merely by foreign precedent), with **clear notice** to parents and pupils at enrolment and in the portal — what is collected, why, who sees it, how to object.
- **Explicit consent** for anything beyond purposes 1–3 (e.g., named research, any commercial use — which this design excludes).
- Minors: consent/notice via parent or guardian under current PDPA; **build for verification** now, because JPDP's Public Consultation Paper No. 4/2025 would require it (still in consultation as of Mar 2026).
- **A live channel**: parents can see who accessed what, raise an objection or complaint, and get a response within a defined time. Its absence — "too busy compiling data to respond" — is the documented proximate trigger in both the inBloom and UK cases.

### 7.6 Audit, retention, breach, portability
- **Audit log** of every individual-level read and export, visible to the controller (Estonia's X-Road pattern). Tamper-evident with a controller-approved retention schedule. A breach-record retention minimum does not by itself establish the retention period for every access log.
- **Retention** per data class, set by the controller: learning record follows the pupil through Form 5 plus a defined period; raw prompt text and telemetry short-lived; deletion on the controller's instruction.
- **Breach**: the existing PDPA notification/DPO summary remains subject to the legal-verification flag above and in handoff §13; confirm the triggering conditions and time anchors from current JPDP guidance rather than treating every incident as identical. A named incident owner and escalation route are required by the proposed design.
- **Act 854 flow-down possibility (checked 2026-09-06):** if the relevant operator is a designated NCII entity, known/suspected incidents require immediate notice to the NACSA Chief Executive and sector lead, prescribed particulars within **six hours of entity knowledge**, and supplementary information within **fourteen days after immediate notice**. A vendor’s contractual escalation must support these deadlines; this is separate from PDPA notification. No designation or signed flow-down is established here, and a vendor owning/operating NCII is not categorically excluded. [Act 854 §§17/23](https://lom.agc.gov.my/ilims/upload/portal/akta/outputaktap/2177706_BI/Act%20854.pdf); [notification regulations reg. 2](https://www.nacsa.gov.my/doc/CYBER%20SECURITY%20%28NOTIFICATION%20OF%20CYBER%20SECURITY%20INCIDENT%29.pdf); blueprint §15.1.
- **Portability**: a pupil's learning record exportable in a documented format (PDPA right; also how the record travels on transfer).

### 7.7 Two firewalls that protect the programme politically
- **Teacher telemetry is non-punitive by contract (G2), not just by interface design.** Individual teacher data is visible only to that teacher and their immediate school leader (G1); above-school views are aggregated/anonymised only. Contractually prohibit appraisal, disciplinary use and individual teacher ranking; enforce with access controls, export restrictions and audit. No e-Prestasi/PBPPP feed. Without this, adoption faces a credible teacher-trust risk; NUTP’s position on this specific app has not been established.
- **No public ranking of schools or classes.** MPT4 is explicitly "diagnostic, not ranking"; Australia's My School shows that publishing school aggregates without that rule becomes league tables in the press regardless of the publisher's intent.

### 7.8 Anonymisation practice
Deterministic and documented, not marketing: suppress cells under a threshold (UK DfE: counts of 1–2 suppressed, totals rounded to 5), pseudonymous ids in research extracts, no free-text in extracts. Pseudonymous ids and small-cell suppression alone do not guarantee anonymity: linkage and differencing risks need assessment. No claim of formal differential privacy — no verified example was found in the systems reviewed.

---

## 8. Interfaces with KPM systems and the curriculum

**Phase 1: no KPM system integration (review C5, adopted 2026-09-06).** No approved public API route was established; this is not proof no internal API exists. Later integrations are separately priced in the partner pack and depend on permission and verified interfaces. Sequence the dependencies honestly:

1. **Post-Phase-1 interface candidates (not a delivery promise):** idMe federation, APDM roster import, APDM-compatible attendance export and BPK/SPPB upload depend on KPM permission and verified formats/channels. Core is the standalone register and generic export. Do not claim “upload once” or elimination of re-keying until the receiving workflow is demonstrated; the four questions in §11 remain open.
2. **Data-sharing agreement (first KPM conversation):** read access to APDM roster/attendance/Pemulihan flags, SPPB PBD/PAJSK/UASA, MPT4/MPT3 results, SiPKPM risk bands; write-back of attendance and PBD when KPM provides a channel. Named counterpart: Bahagian Pengurusan Maklumat/BTP for systems, BPK for templates, LP for MPT/PPsi.
3. **Later:** APIs under the DSA. Do not design around their existence.

**Curriculum reference data:** ingest the public DSKP documents (bpk.moe.gov.my; deep links need a manual browser check) into a Framework per curriculum version — Subject → Year/Form → Content Standard → Learning Standard → TP descriptors — using the CASE-style schema (blueprint §4), with `exactMatchOf` cross-walks between KSSR/KSSM and KP2027 standards as KP2027 rolls out. Kota Buku textbook pages are tagged to the same standards (the DIKSHA "Energized Textbook" QR-per-chapter pattern, proven at 600M copies). Yearly teaching plans (RPT) are the pacing reference.

---

## 9. What this gives KPM

For Hafiz's conversation, not the written proposal (decision 7):

- **Continuous, standard-tagged classroom evidence** between assessment checkpoints. National comparability is not established by shared standard IDs alone: different questions, teacher judgements and capture coverage need calibration/moderation before cross-school comparisons.
- **Intervention follow-up** for PIT1 and Pemulihan Khas — the app could show recorded progress; causal effectiveness needs an evaluation design. RPM’s Year 1 percentage is internally inconsistent (see §10), so do not use 11% as a settled baseline.
- **Learning-loss measurement capability** KPM never had (the COVID estimates came from academics and think tanks, not KPM data).
- **RPM 2026-2035 mandatory-target tracking** (minimum Grade C in BM, English, Maths, Sejarah; digital competency) tracked continuously instead of at exam time.
- **Teacher-workflow proxies** relevant to the 80:20 policy. App logs do not measure total teaching/admin time: a baseline and independent teacher-time validation are needed. Avoiding duplicate submission remains conditional on confirmed KPM interfaces.
- **SiPKPM enrichment** with the one signal it lacks: learning engagement.
- **Content evidence for Kota Buku itself**: which textbook pages are used, and with what outcomes.
- **A learning profile that travels** across the Year 6 and Form 3 transitions where high-stakes selection currently uses PBD/PAJSK/PPsi without an evidence trail.

---

## 10. Verification status and open items

**Review caution, 2026-09-06:** [P] means an identified primary source was read in the original research, not that every inference or its current applicability is verified. Several rows lack a direct URL, edition/date or exact clause. In particular, current UASA marks/grade reporting versus historical TP-only wording, admission-route applicability by institution/year, and the exact SPPB import workflow remain unverified. Preserve those distinctions before external quotation; a live portal alone does not prove an admissions rule or API contract.

| Item | Status |
|---|---|
| PBD definition, continuity, TP1–6 reporting; UASA scope, subjects, school-set papers, SPPB as system of record | **Verified [P]** — 2019 PBD guideline (BPK), UASA administration guideline (moe.gov.my) |
| PAJSK components, 110-mark structure, yearly GPA/CGPA, SPPB recording, 2005 Cabinet origin of the 10% | **Verified [P]** — MOE PAJSK guideline PDF |
| UPU 90/10 merit formula, 2026/27 | **Verified [P]** — KPT/UPU circular; Parliament 25 Nov 2025 |
| RPM 2026-2035: voluntary age-6 entry 2027, mandatory preschool 2031, Year 1 3M baseline, 3-phase timeline | **[P] source read; baseline inconsistent** — [preserved RPM text](sources/rpm.txt), passage “pengesanan awal literasi dan numerasi”: prints 11% beside 122,062 / 448,113 (2024), which calculates to 27.24%. Source/extraction or denominator reconciliation remains **Open**; do not select either percentage as authoritative. |
| KWAPM, RMT, BAP eligibility and legal basis; eKasih ownership (ICU JPM) | **Verified [P]** — moe.gov.my, manfaat.mof.gov.my, malaysia.gov.my |
| Education Act s.29A entry rule; SPI 10/1998 early-entry exception | **Verified [P]** — MOE policy pages |
| MPT4 existence, LP administration, Year 4 subjects, Form 3 in 2027, diagnostic framing | **[N]** Bernama/RTM; exact 6–8 Oct dates **[S]** |
| SiPKPM name and function; AI module from 2026; 7 indicators | **[N]** Bernama/RTM/Parliament; indicator list partially verified |
| PT3 abolition (2 Jun 2022); SSDM reversion (Nov 2025); SPLKPM abolition (from 2026); manual co-curricular recording abolished; 80:20 policy (24 Mar 2026) | **[N]** multiple outlets |
| PBD TP Keseluruhan aggregation formula | **Open** — download and open an actual BPK template |
| APDM attendance cut-off (9am vs 10am), escalation triggers, exact field list | **[S]** conflicting — confirm with KPM |
| SSDM points scheme (if any) | **Open** — none found |
| RPH reduced to 3 mandatory elements; SPI 3/1999; Surat Siaran 2/2025 e-RPH | **[N]/[S]** — confirm circulars |
| PIT1 announcement date and screening cadence; LINUS end date (2019); 11% vs 27.5% discrepancy | **[S]** — reconcile against the named KPM dataset |
| Kelas Peralihan TP1/2 rule and test name (UPLBM vs UPKP) | **[S]** — no circular located |
| SBP weighting percentages; MRSM interview step | **[S]** — BPSBP/MARA primary needed |
| Form 4 package criteria (TP4 threshold) and weighting | **[S]** — BPK primary needed |
| Pemulihan Khas thresholds (IPP2M/IKAM, <50%); PPKI process; DLP circulars (SPI 8/2018, 3/2020) and criteria | **[S]** — official PDFs blocked; request from KPM |
| SPM grade cut points | **[S]** — LP primary needed |
| KV/SMT entry thresholds | **[S]** — one stale school page |
| idMe as a SEGAK data-entry surface; HRMIS/SiPP as SPLKPM successors; PADU–KPM integration | **Unresolved** |
| Any Auditor-General or Hansard finding on KPM data-system quality/duplication | **Not found** — direct archive search needed |
| Singapore/Estonia published research-access pathways; EHIS parental access; use of formal differential privacy anywhere | **Absence of evidence** |

Preserved local sources (checked 2026-09-06): [RPM text](sources/rpm.txt), [PAJSK guideline](sources/pajsk_guideline.pdf), [UPU 2026/27 circular](sources/pekeliling_spm_2627.pdf), [psychometric guide](sources/kpm-panduan-pentadbiran-pentaksiran-psikometrik.pdf), [DIKSHA technote](sources/diksha-technote.pdf) and [its text](sources/technote_flow.txt). Source age and scope still matter; preservation does not settle the remaining flags.

---

## 11. Next actions

**Conversations (Hafiz / Kota Buku / KPM):**
1. Ask KPM which unit signs a data-sharing agreement and which entity is the controller of record (KPM vs. Kota Buku) — this shapes the DPA.
2. Request export/import formats for APDM (roster, attendance) and SPPB (PBD templates, PAJSK) and whether idMe federation is available to a third party.
3. Ask whether SiPKPM risk bands can be surfaced to the class teacher through a partner app, and whether learning-engagement signals can be supplied to it.
4. Obtain the current BPK PBD Excel templates, SPK Bil. 1/2021 (school finance), and the Pemulihan Khas / PPKI / DLP guidelines directly.

**Historical downstream notes — not authorised by the current review-only instruction:**
5. Feature spec: Pillar 1 and §9 now reference this spec for field-level detail; the MVP list is unchanged (standalone register, live MCQ, TP tracking, DSKP-grounded items, template RPH).
6. Blueprint: the telemetry envelope and Framework-per-curriculum-version design here become the data model section of the build; add the DPA/residency requirements to §11 cost and §13 synthesis.
7. Proposal outline (decision 7): the "reporting and analytics" section describes §5.1–5.4 outputs and §7.3 tiers in plain language; §9 stays out of the document.

**Verification before anything is quoted externally:** every **[S]** and **Open** row in §10.
