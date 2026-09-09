# AI Classroom for Malaysian Schools — Research Findings

**Status:** Concept/pitch-stage research only. Not yet a committed build, not yet tied to Kelasapp-for-School or any existing Sifututor product.
**Scope requested:** Teacher-centric app, Standard 1 to Form 5 (full national primary + secondary), targeting both government/MOE schools and private/international schools. Six pillars: (1) longitudinal student data collection, (2) conducting class/activities, (3) AI content generation for whole-class or per-student material, (4) AI teaching-assistant personalization + progress/strength/weakness tracking + recommendations, (5) adjacent efficiency features, (6) parent/student portals.
**Research date:** 2026-09-06. Compiled from 9 parallel research agents (~830K tokens of raw findings, ~300 web searches/fetches). Every claim below carries its source; anything not independently verified is explicitly flagged as such — treat flagged items as leads to re-check, not facts to quote externally.
**Why this file exists:** so none of this has to be re-researched before the next working session on this concept.

---

**Programme decisions, 2026-09-06:** co-branded Kota Buku app, delivered by Sifututor, powered by Learnest Lab; exact legal entity to be confirmed by Hafiz. D8 supplies devices to teachers only, not pupils; existing parent/pupil web access remains. D10 puts programme commercial figures exclusively in the [partner pack](partner/SEPADU-v1.0-Founder-Briefing.md); no competing costing is offered here. Dated public-policy/evaluation statistics below are evidence, not programme prices. **C4 decided by Hafiz, 2026-09-06: blend workload reduction with the six-pillar AI-classroom framing** (handoff §7 C4). Neither intended benefit is a proven product outcome. [Partner review §2/§9/§10](partner/SEPADU-review.md).

## Table of contents

1. [Malaysia government/MOE digital education landscape](#1-malaysia-governmentmoe-digital-education-landscape)
2. [DSKP curriculum structure + the KP2027 reform](#2-dskp-curriculum-structure--the-kp2027-reform)
3. [Legal & compliance: PDPA and KPM data governance](#3-legal--compliance-pdpa-and-kpm-data-governance)
4. [Malaysian local competitors and market](#4-malaysian-local-competitors-and-market)
5. [Regional APAC/SEA competitors](#5-regional-apacsea-competitors)
6. [Global best-in-class platforms and pedagogy evidence (mapped to the 6 pillars)](#6-global-best-in-class-platforms-and-pedagogy-evidence)
7. [Go-to-market reality: B2G procurement vs. private/international schools](#7-go-to-market-reality-b2g-procurement-vs-privateinternational-schools)
8. [Teacher pain points in Malaysia](#8-teacher-pain-points-in-malaysia)
9. [Cross-cutting strategic observations](#9-cross-cutting-strategic-observations)
10. [Master list of dead ends, unverified items, and follow-ups needed](#10-master-list-of-dead-ends-unverified-items-and-follow-ups-needed)

---

## 1. Malaysia government/MOE digital education landscape

### 1.1 DELIMa (Digital Educational Learning Initiative Malaysia)

- Three-way partnership: Google Workspace for Education (from 1 Jul 2019), Microsoft (joined 1 Jan 2020), Apple (named in the linked June 2020 launch announcement; the previous “joined Mar 2022” date contradicted that source). Officially launched/rebranded **15 June 2020**. Replaced VLE Frog after the 1BestariNet contract ended 30 June 2019. [Microsoft News Center, 15 Jun 2020](https://news.microsoft.com/en-my/2020/06/15/ministry-of-education-launches-new-digital-learning-platform-with-participation-from-google-microsoft-and-apple/); [SoyaCincau, 16 Jun 2020](https://soyacincau.com/2020/06/16/education-ministry-relaunches-digital-learning-platform-with-help-from-apple-google-and-microsoft/)
- **Adoption figures conflict across years/sources — do not quote a single % without noting this volatility:**
  - Jun 2020 (launch): ~1.7M MAU, 10,000 schools, 370,000 teachers, 2.5M students.
  - Aug 2022: 99% teachers / 85% students "actively using," 5.3M total users, per Dr Wagheeh Shukry Hassan. [Sinar Harian, 24 Aug 2022](https://www.sinarharian.com.my/article/217935/berita/nasional/delima-berwajah-baharu-tingkatkan-kualiti-pdp-guru-dan-murid)
  - Mar 2024: 2.1M pupils / 42% active. [Borneo Post via PressReader, 28 Mar 2024](https://www.pressreader.com/malaysia/the-borneo-post-sabah/20240328/281616720372145)
  - Nov 2023: 53 million cumulative logins as of 9 Nov 2023. [Malay Mail, 27 Nov 2023](https://malaymail.com/news/malaysia/2023/11/27/education-ministry-53-million-users-access-delima-online-learning-platform-as-of-november-9/104499)
  - Google Cloud's own case study (undated, ~2024-2025): 10,230 schools, 4.8M students, 480,000+ teachers, **98% teacher tool adoption**. [Google Cloud MOE case study](https://cloud.google.com/customers/moe-my) — vendor-authored, treat as marketing-inflected.
- **DELIMa 3.0** — launched **21 July 2026** (corrected from an earlier "20 July" after re-checking the Bernama source). Adds **DETa** (Digital Educational Teaching & Learning Assistant, an MOE-branded AI chatbot for teachers/students) and an AI-driven "Digital Learning Pathway" for per-student personalization. 16 specialized AI apps integrated for automated marking, performance analysis, learning-gap detection (exact 16-app list not disclosed). Usage as of 30 Jun 2026: ChatGPT 208,836 uses, Gemini 175,765, NotebookLM 130,099 within-platform. Adoption Jan 1–21 Jul 2026: **teachers 97.73% active, students only 37.32% active** — a large, notable teacher/student engagement gap. [Bernama, 23 Jul 2026](https://bernama.com/en//general/news.php?id=2584910)
- **Implication:** MOE is not a blank slate on AI. An "AI Classroom" pitch to government schools must position against/alongside an official, government-endorsed AI layer already reaching near-100% teacher penetration.

### 1.2 APDM, SMM, eOperasi, SPS, SAPS — the student-data system stack

- **SPS (Sistem Pengurusan Sekolah)** — umbrella single-database platform, launched 1 Jan 2015 (KPM Circular Bil. 21/2014). Three modules: MPS (school), MPG (teacher), MPM (student). Includes a Dashboard/EIS for KPM management. [ecentral.my](https://ecentral.my/sistem-pengurusan-sekolah/)
- **APDM (Aplikasi Pangkalan Data Murid)** — nationwide student database since 2012: personal info, family background, academic/co-curricular records, health/immunization/allergy data, financial-assistance status, e-attendance. Used by class teachers, portal at apdm.moe.gov.my; limited parent view/update access. No AI features. [logmasuk.my](https://logmasuk.my/apdm/), [fuh.my](https://fuh.my/apdm/) — secondary/SEO sources, directionally reliable, not primary-confirmed.
- **SMM (Sistem Maklumat Murid)** — the original, older PPD-level student-data system that APDM was meant to supersede/consolidate.
- **eOperasi** — HR/staff module within SPS: placement, subject assignment, transfer status. No AI features, not classroom/lesson-planning related.
- **SAPS (Sistem Analisis Peperiksaan Sekolah)** — collects/analyzes **internal/school-level** exam data only (not national public exams). Parent portal at sapsnkra.moe.gov.my/ibubapa2 via student IC. Still apparently active (2025/2026 guide pages exist) but **no primary KPM/news source confirms current technical status** — treat as "presumed active, unconfirmed." **Historical note:** in 2018, SAPS was reportedly SQL-injection-vulnerable and taken offline after a breach potentially exposing 4.9 million students' data. [The Star, 10 Jun 2018](https://www.thestar.com.my/news/nation/2018/06/10/details-of-49-million-students-may-have-been-hacked/) — pre-2023, cite only as historical precedent that KPM's centralized student systems have a breach history.
- **"iSTUDENT" — dead end.** No MOE system by this exact name was found across multiple query variants. Likely a misremembering/conflation of SMM, APDM, or **IDME** (idme.moe.gov.my — the current identity/SSO gateway for MOEIS and other MOE portals). Recommend confirming the intended name before citing it anywhere.
- **APDM workload finding (important, quotable):** a paper found via ResearchGate ("Penerimaan Guru dengan Pelaksanaan Sistem Maklumat Murid dan Aplikasi Pangkalan Data Murid...") — full citation metadata unverified (ResearchGate blocked fetch, 403) — reports **47.5% "strongly agree" + 32.6% "agree"** (≈80% combined) that SMM/APDM duplicate teacher data-entry work rather than reduce it, despite APDM's intended purpose of being a single national database. This is a strong "digitalization increased admin burden" data point, but needs primary-source verification before external use.

### 1.3 National "AI-Powered Classroom" pilot — directly competitive/complementary context

- **"Bilik Darjah Dikuasai Kecerdasan Buatan"**: piloted in **27 schools in 2025**, expanding to **260 schools nationwide in 2026** (phased), targeting **full national implementation by 2030**. Framed explicitly as support, not replacement, for teachers — "task automation and learning analytics" for educators, "adaptive learning" for students (Education Minister Fadhlina Sidek). 24 technology partners named broadly, including Google, Microsoft, Apple, Intel, Huawei, Samsung, MDEC. [RTM Berita, 18 Dec 2025](https://berita.rtm.gov.my/nasional/senarai-berita-nasional/senarai-artikel/kpm-perluas-bilik-darjah-dikuasai-kecerdasan-buatan-ke-260-sekolah-pada-2026/)
- **MDEC "AI-Powered Classroom" PoC, Sarawak** — separate/possibly-overlapping reporting: led by Ministry of Digital + MDEC + KPM, at SK St James Quop, Padawan, Sarawak, Phase 1 from Aug 2025, targeting rural/digital-divide. Partners: MyDigital Corp, UNIMAS, UKM, Microsoft, Intel, Dell, Vector InfoTech, **Pandai Education**, Chumbaka, APR Electronic Services. Tied to the "Sekolah Angkat MADANI" program. [MDEC media release](https://www.mdec.my/media-release/news-press-release/416/kementerian-digital-dan-mdec-perkasa-pendidikan-masa-hadapan-melalui-projek-rintis-%E2%80%9Cai-powered-classroom%E2%80%9D-di-sarawak) — **Verification result (targeted follow-up, 2026-09-06): treat as two distinct, unreconciled initiatives.** The official Ministry of Digital/MDEC press release (11-12 Feb 2026) frames the Sarawak PoC as MDEC-led under Sekolah Angkat MADANI; it never references KPM's "Bilik Darjah Dikuasai Kecerdasan Buatan," the 27-school figure, or the national rollout, and the RTM report on the national programme (a Dewan Negara reply by the Minister, 18 Dec 2025) never mentions Sarawak or MDEC's PoC. No official source states whether SK St James Quop is counted among the 27/260. Do not assert "same" or "different" as fact — cite both, flag the possible overlap. **Separate sourcing problem surfaced:** the national programme's school counts are inconsistent across reports (an early "11 schools," then 27 → 260, "800 classrooms by end-2027" in a May 2026 outlet, "all schools by 2030"); quote the 27/260/2030 figures from the ministerial Parliament reply as the authoritative set.
- **Samsung AI-Powered Classroom** — Samsung Malaysia + MOE, launched 10 Jun 2026, pilot schools SMK Nilai Impian (Negeri Sembilan) and SMKA Naim Lil Banat (Kelantan). Galaxy Tab A9+ tablets, digital smartboards. Content/AI layer by **Sasbadi Holdings** (listed MY ed-publisher) via its "**Ace-it**" platform — feature detail unverified. A related/possibly-distinct "first AI-powered classroom in Perlis" (SMK Kuala Perlis) also surfaced — relationship to the Nilai/Kelantan pilots unclear. [The Sun](https://thesun.my/spotlight/samsung-rolls-out-ai-powered-classroom-initiative/), [Samsung Newsroom MY](https://news.samsung.com/my/samsung-strengthens-nation-building-efforts-through-ai-powered-classrooms-for-malaysian-youths)
- **AI Classroom World / SMKDAR-AI** — the single closest existing analog to this concept found anywhere. Malaysian AI strategist Razman Salleh built a generative-AI chatbot for **SMK Dato' Ahmad Razali (SMKDAR)**, a public school in Ampang, Selangor, launched **24 Apr 2024**, bypassing formal MOE lab/policy channels. KSSM-syllabus-aligned Q&A + writing feedback. Usage skewed Science (19%), BM (19%), Maths (18%), Add Maths (18%). Pilot claims: 40% of students reported clearer understanding, "100% survey satisfaction" (self-reported, unverified independently). Evolved into **AI Classroom World**, positioned as a broader "command center" (school management + task automation + AI analytics), ready to scale from Q4 2025, seeking partnerships with public/private schools and international humanitarian networks (OIC, Education Cannot Wait). [aiclassroom.world/smkdar-ai](https://www.aiclassroom.world/smkdar-ai) — **flag prominently as a direct comparable/potential competitor or partner.**

### 1.4 1BestariNet and VLE Frog — history and the 2024 corruption investigation

- **1BestariNet**: 15-year contract awarded **2011** (open tender, 19 companies competed) to YTL Communications for 4G broadband + Frog VLE across 10,000 schools. Effectively delivered ~7.5 years; contract ended **30 June 2019**. From 2013, rural schools already reporting slow/failing connectivity.
- **Frog VLE**: run by FrogAsia (JV of FrogTrade Ltd UK + YTL Group). Discontinued and replaced by Google Classroom → DELIMa from mid-2019/2020. **Not in active use today.**
- **2024 MACC corruption investigation** (highly relevant political context for any government pitch): Sept 2024, MACC raided YTL Communications' offices, probing payment claims within the tender, triggered by a Government Procurement/Finance Governance Investigation Committee finding plus a Public Accounts Committee report (which separately flagged low broadband coverage/poor school infrastructure). [FMT, 4 Sep 2024](https://www.freemalaysiatoday.com/category/nation/2024/09/04/macc-raids-ytl-communications-in-probe-on-1bestarinet-project); [NST, Sep 2024](https://www.nst.com.my/news/crime-courts/2024/09/1101236/updated-macc-probes-rm4bil-1bestarinet-tender-raids-ytl-office)
- **18–19 Dec 2024: MACC concluded — no charges filed, YTL cleared.** [The Malaysian Reserve, 18 Dec 2024](https://themalaysianreserve.com/2024/12/18/ytl-communications-cleared-of-wrongdoing-in-1bestarinet-project-by-macc/); [FMT, 19 Dec 2024](https://www.freemalaysiatoday.com/category/nation/2024/12/19/no-one-will-be-charged-over-1bestarinet-says-macc)
- **Net effect:** 1BestariNet remains a politically sensitive reference point — a nationwide edtech infrastructure project that underdelivered and drew a corruption probe (even though ultimately cleared). Expect this history to color government procurement scrutiny and risk appetite for any new large edtech pitch.

### 1.4.1 Auditor-General failure evidence — years and denominators matter

**Reconciled 2026-09-06.** Do not merge different audit rounds, samples or contractor duties. These findings support readiness/adoption checks, not an allegation that the current proposal repeats past wrongdoing.

| Audit window / provenance | Finding | Limit or implication |
|---|---|---|
| Findings published in 2014; partner review calls this “LKAN 2014” | Requirement study, technical/MAMPU approval, value-management and steering-committee gaps reported in the early audit | **Year-label disagreement remains:** contemporary reporting names **LKAN 2013 Series 3, released November 2014**. The EUROSAI archive’s 2014 folder is not proof of report year. Primary cover/edition must be checked before an external citation. Steering-committee detail remains review-sourced, not independently verified here. |
| Same early audit; survey of 501 schools | 292 schools (58%) reported coverage did not extend across the whole school | This is incomplete campus coverage in that sample, not a national “no internet” rate. |
| LKAN 2018 Series 1, reported July 2019 | 3,698 of 10,185 schools (36.3%) never met the Frog VLE usage KPI in 2018 | A KPI measure, not the proportion of all teachers never logging in. |
| Same audit; 2,222 sampled teachers in 42 schools | 950 (42.8%) never accessed Frog VLE | Sample denominator must travel with the percentage. |
| Same audit | Use constrained to labs/school hours; ineffective parent information; Unicliq had the change-management responsibility | Distinguish adoption evidence from YTL’s connectivity/service obligations and Unicliq’s programme responsibility. Do not assign every shortfall to one contractor. |
| Same audit; 423,566 teachers | Only 0.8% created and published a learning page in Frog Store in 2018 | Content-authoring activity, **not** overall VLE participation or teacher competence. |

Sources: **[N]** [Malay Mail, 10 Nov 2014](https://www.malaymail.com/news/malaysia/2014/11/10/1bestarinets-virtual-learning-usage-less-than-5pc-audit-finds/779927), [The Edge, 18 Mar 2015](https://theedgemalaysia.com/article/ytl%E2%80%99s-1bestarinet-project-continue-despite-shortcomings-says-pac), [The Edge, 16 Jul 2019](https://theedgemalaysia.com/article/1bestarinet-phase-2-not-value-money-project-moe), [Bernama via Malaysiakini, 15 Jul 2019](https://www.malaysiakini.com/news/483884). **Primary verification lead, not cleared:** [EUROSAI-hosted audit chapter](https://egov.nik.gov.pl/MY/2014/BestariNnet/1BESTARINET%20FOR%20EUROSAI%20CUBE.pdf) was indexed but full retrieval failed in this pass; review §5 supplies the steering-committee claim. Keep this evidence debt visible.

### 1.5 PADU (Pangkalan Data Utama) — adjacent, NOT an education system

- Launched 2 Jan 2024 under the **Ministry of Economy** (not KPM) — a whole-of-government socioeconomic/subsidy-targeting database, unrelated to schools/students specifically. [Fulcrum/ISEAS, 7 Jan 2025](https://fulcrum.sg/big-data-bigger-debate-malaysias-padu-system-and-the-future-of-digital-governance/)
- Controversial: lawyers' groups called for suspension pending stronger PDPA (Jan 2024); Sarawak objected and postponed registration in-state (Mar 2024) citing autonomy/data-sovereignty; "tepid" public response attributed to privacy distrust. 2024 PDPA amendments were partly a response to this pressure.
- **No evidence found of any PADU-to-KPM/schools data integration.** Treat as parallel government infrastructure — not a dependency or competitor for an AI Classroom product, but useful context on Malaysian public trust levels around government data systems.

### 1.6 RPM 2026-2035 and Kurikulum Persekolahan 2027 (KP2027) — major finding, architecture-relevant

- PM Anwar Ibrahim launched the umbrella **Rancangan Pendidikan Negara (RPN) 2026-2035** around **20 Jan 2026** — which bundles two sub-plans launched the same day: **Rancangan Pendidikan Malaysia (RPM)** for schools (the K-12-relevant half) and RPTM for higher education. Official PMO/MOHE/MOSTI sources use "RPN" for the umbrella and "RPM" for the school plan; in any KPM/MOHE-facing document, use the terms that way. The launch announced a brand-new curriculum, **Kurikulum Persekolahan 2027 (KP2027)**, that will **replace KSSR and KSSM entirely, in phases**:
  - **2026**: Prasekolah 2026 (preschool) begins first.
  - **2027**: Year 1 and Form 1 move to KP2027.
  - **2028**: Year 2 and Form 2 follow.
  - **Full rollout to all years/forms by ~2031**; other levels continue on KSSR Semakan 2017 & KSSM in the interim.
  - Age-6 entry from 2027 is **voluntary**, per the preserved RPM text and data spec §2; do not describe it as a compulsory standardised entry age. Centralized Year 4 assessment (BM, English, Maths, Science) starts 2026. KP2027 emphasizes literacy/numeracy mastery, digital skills, integrated learning, "Insan Sejahtera" character formation, bilingualism, STEM, TVET from Year 1. [ecentral.my](https://ecentral.my/rancangan-pendidikan-malaysia/), [official RPM doc, updated 04/09/2026](https://www.moe.gov.my/dokumen-penuh-rancangan-pendidikan-malaysia-rpm-2026-2035)
- **BM and History made compulsory across ALL school streams**, including international, religious, and UEC schools — announced same day (20 Jan 2026). All Malaysian-citizen children in international schools must now sit SPM Bahasa Melayu and Malaysian History papers, benchmarked to SPM standards. [The Star, 20 Jan 2026](https://www.thestar.com.my/news/nation/2026/01/20/international-religious-schools-and-uec-stream-must-offer-bm-history-as-subjects-in-spm-says-pm-anwar); [Bernama, 20 Jan 2026](https://www.bernama.com/en/news.php?id=2514712)
  - **Directly widens the addressable market**: DSKP-based BM/History content becomes mandatory even for international-school pupils, strengthening the case for covering private/international schools in this pitch (per your confirmed scope).
  - **Implementation mechanics were still unsettled after the announcement** (added after adversarial review): a later Malaysiakini report ("KPM kaji kemungkinan benarkan hanya ambil BM, Sejarah untuk SPM") shows KPM was still studying whether affected students could register for *only* those two SPM subjects rather than the standard minimum, and was separately negotiating with Dong Zong on how UEC-stream students would be accommodated. The mandate itself is real and multiply confirmed; the exact enforcement timeline and registration mechanics were not fully operational as of that reporting. Treat the market-widening effect as directionally solid but not yet a settled compliance requirement with a fixed date.
- **AI curriculum integration**: AI as a secondary elective subject in Forms 4-5 starting 2027. KPM referenced a "Master Plan for AI in Malaysian Education 2025-2030" and a standalone "AI Education Policy" for 2026 — **not confirmed as formally published** as of Sept 2026, treat as in-development. KPM published a "Buku Panduan Literasi Kecerdasan Buatan (AI)" (AI literacy guidebook) dated 9 Jun 2026. [moe.gov.my PDF](https://www.moe.gov.my/storage/files/shares/Pengumuman/BUKU%20PANDUAN%20LITERASI%20KECERDASAN%20BUATAN%20AI%209.6.26.pdf)
- **Architecture implication (important for any product decision later)**: KSSR/KSSM and KP2027 will coexist system-wide for at least 4-5 years across different year/form cohorts simultaneously. Any content-generation architecture should treat "curriculum standard version" as a swappable schema, not a hardcoded structure.

### 1.6.1 Dasar 80:20 — a phased policy anchor, not today’s measured outcome

**[P, checked 2026-09-06]** RPM’s “Penstrukturan Semula Tugas Guru Melalui Dasar 80:20” states: **“80% masa guru mata pelajaran diperuntukkan untuk aktiviti berkaitan dengan PdP, manakala 20% diperuntukkan untuk tugasan bukan PdP.”** It allocates time to teaching-related work, not solely face-to-face lessons. [Preserved RPM text](sources/rpm.txt), printed **p.179**, Figure 6.4 (text lines 6233–6278). **Correction to review §4/§10:** p.178 is the preceding MySG/support-staff page; the quoted policy and phases are on p.179 in this preserved edition.

- **2026–2027:** policy formulation and initial scope development, alongside expansion of teacher-assistant initiatives.
- **2028–2030:** pilot implementation and effectiveness evaluation.
- **2031–2035:** full implementation and expansion.

This is a policy direction with future phases, not evidence that today’s teacher workload already meets the split or that this app will deliver it. App logs measure workflow proxies only; independent baseline/time-use evaluation remains necessary (data §9). **Positioning C4 decided by Hafiz, 2026-09-06:** combine the workload rationale with AI-assisted teaching and pupil-progress support. The six pillars remain intact; the policy anchor does not establish an achieved time split or measured product effect.

### 1.6.2 e-RPH circular — enabling and flexible, not exclusive procurement authority

**[S, checked 2026-09-06]** the retrieved mirror of **Surat Siaran KPM Bil. 2/2025**, dated 23 April 2025, describes DELIMa e-RPH as an alternative to existing RPH methods (§3), with offline completion/upload when connected in the attached guide. It enables a digital workflow; it does not prove a mandate for this product, a DELIMa integration right, or exclusive adoption. [Circular mirror, §§3–5 and guide](https://www.studocu.com/my/document/sekolah-menengah-kebangsaan-desa-serdang/bahasa-melayu/surat-siaran-kpm-bil-22025-garis-panduan-e-rph-untuk-guru/132295021). **Official signed copy/current applicability still require verification**; the mirror is not upgraded to a first-party source. D6 leaves mandatory/optional framing to Kota Buku/KPM.

### 1.7 Budget context

- **Budget 2025:** education and rural-school internet allocations provide policy context, not funding approval for this programme. Monetary values omitted under D10; historical source retained: [The Vibes](https://www.thevibes.com/articles/news/103792/rm82.1-billion-for-education-in-budget-2025).
- **Budget 2026:** the MOE allocation was checked against the [Budget speech, paragraph 187](https://www.investmalaysia.gov.my/media/pipcspid/prime-minister-s-parliamentary-speech-on-budget-2026-english-translation.pdf), 2026-09-06. Monetary values omitted under D10, not withdrawn as source evidence. **Still unverified:** exact paragraphs and programme scope for smart TVs, the Malaysia Digital Acceleration Grant, targeted support and the “AI Nation by 2030” framing. Do not infer a budget for this deal.

---

## 2. DSKP curriculum structure + the KP2027 reform

### 2.1 What DSKP is

- **DSKP = Dokumen Standard Kurikulum dan Pentaksiran** ("Standard Curriculum and Assessment Document"). Issued by KPM's **Bahagian Pembangunan Kurikulum (BPK)**. One DSKP exists **per subject, per year/form** — not one master document per level. Sits within **KSSR** (primary, Year 1-6) and **KSSM** (secondary, Form 1-5). [Pandai blog, 30 Jan 2026](https://blog.pandai.org/apa-itu-dskp/); [bpk.moe.gov.my](https://bpk.moe.gov.my/)

### 2.2 Three-part structure

- **Standard Kandungan (Content Standard)** — what a pupil should know/do, organized by topic per subject/year.
- **Standard Pembelajaran (Learning Standard)** — measurable, assessable criteria tied to each content standard; this is the granular unit teachers plan lessons against.
- **Standard Prestasi (Performance Standard)** — measures mastery via **Tahap Penguasaan (TP1-TP6)** under **Pentaksiran Bilik Darjah (PBD)**, the classroom-based assessment that replaced UPSR/PMR:
  - TP1 Tahu · TP2 Tahu dan Faham · TP3 Tahu, Faham dan Boleh Buat · TP4 …dengan Beradab · TP5 …dengan Beradab Terpuji · TP6 …dengan Beradab Mithali
  - (Consistent across multiple secondary sources; no single official KPM PDF was directly fetched — treat wording as reliable-by-consensus, not verbatim-official.)
- **KSSM English** is jointly developed with Cambridge English and explicitly **CEFR-aligned** — a notable structural exception (not purely BPK-authored in isolation).
- Teaching-artifact chain: **DSKP → Scheme of Work (SoW) → daily lesson plans (RPH)**.

### 2.3 Where published

- Primary portal: **bpk.moe.gov.my** ("Portal Rasmi Bahagian Pembangunan Kurikulum"), confirmed live, last updated 26 Aug 2026 (fetched 6 Sep 2026). Structure indexed via category paths by year/form (e.g. `.../category/16-dskp-tingkatan-1`), served over **plain HTTP not HTTPS**. Deep-link category pages returned 403/404 on direct fetch this session (likely bot protection, not evidence pages don't exist) — **recommend a human manually verify these URLs in a real browser before citing as clickable links**.
- Secondary mirrors: repositori.bpk.moe-dl.edu.my, state JPN portals (e.g. jpnpp.moe.gov.my).
- Digital textbooks (curriculum-derived, separate from DSKP): textbook.moe.gov.my, "KPM eTextbook Reader" app, EPUB format (built for PdPR/COVID home learning).

### 2.4 Existing edtech DSKP alignment — sets a competitive baseline

- **Pandai** (pandai.org, iOS + Android) explicitly maps content to DSKP's own hierarchy: grade/subject/chapter/topic/subtopic/**TP mastery level**. Covers Year 1-6, Form 1-5, core + elective subjects, bilingual for DLP, Chinese content for vernacular schools. [Pandai Academic page](https://pandai.org/my/academic) — a claimed "Education Alliance Finland" recognition is **unverified marketing claim**, not found on the fetched page itself.
- **imanelit.com** — follows KSSR + KPM programs (LINUS, PAK21, PBD), less explicit DSKP-level mapping than Pandai.
- DELIMa itself is infrastructure/LMS, not a DSKP-mapped content engine — alignment there depends entirely on what individual teachers upload.
- **Takeaway:** DSKP-alignment (down to chapter/topic/TP granularity) is already table-stakes in the Malaysian consumer edtech space — Pandai proves the market expects this. A content generator would need the same granularity just to be credible; the real differentiation would need to come from teacher-workflow value (lesson planning, PBD-compliant reporting, RPH generation), not raw curriculum coverage.

---

## 3. Legal & compliance: PDPA and KPM data governance

### 3.1 PDPA 2010 + 2024 Amendment (Act A1727)

- Base law (Act 709) historically covers only **commercial transactions** — a long-recognized gap that excludes Federal/State Government itself from PDPA's "data user/controller" obligations. [Linklaters](https://www.linklaters.com/insights/data-protected/data-protected---malaysia)
- **Amendment gazetted 17 Oct 2024, rolled out in 3 phases:**
  - **Phase 1 (Jan 2025)**: "data user" → "data controller"; **biometric data explicitly added to "sensitive personal data"**; formal legal definition of "personal data breach."
  - **Phase 2 (Apr 2025)**: new cross-border transfer regime — old unusable "whitelist" scrapped; now permitted if destination has "similar/adequate" protection OR under alternative bases (consent, contract necessity, vital interests, documented due diligence). Formalized via **Cross-Border Personal Data Transfer (CBPDT) Guidelines, 29 Apr 2025** — requires written notice, contractual safeguards, secure transfer methods, documented Transfer Impact Assessment (TIA).
  - **Phase 3 (Jun 2025)**: **mandatory DPO** (threshold: processing 20,000+ individuals' data, OR sensitive financial data of 10,000+, OR regular systematic monitoring — notify Commissioner within 21 days, Malaysian-resident or easily contactable) + **mandatory breach notification** (72-hour Commissioner notification benchmark; 7-day individual notification if "significant harm" or 1,000+ subjects affected; records kept 2+ years). [DLA Piper, 4 Mar 2025](https://privacymatters.dlapiper.com/2025/03/malaysia-guidelines-issued-on-data-breach-notification-and-data-protection-officer-appointment/)
  - **Penalties raised**: maximum fine increased (amount omitted; verify current statutory provision before legal reliance); max imprisonment 2 → **3 years**. **Data portability right** introduced.
- **Relevance**: a national schools rollout will almost certainly cross the 20,000-record DPO threshold — a DPO appointment is a launch-blocking compliance item, not optional. Biometric attendance (face/fingerprint) is now explicitly "sensitive." Any AI inference hosted outside Malaysia triggers the new CBPDT regime (TIA + documented safeguards required as a matter of course).

### 3.2 No Malaysia-specific children's-data law

- **Correction, primary checked 2026-09-06:** parental consent is not merely inferred practice. Regulation 3(3) expressly directs consent for an under-18 data subject to a parent, guardian or person with parental responsibility; regulation 3(5) puts proof on the data user. This is distinct from the later proposed verification amendments. [PDP Regulations 2013, p.14](https://www.pdp.gov.my/ppdpv1/wp-content/uploads/2024/06/PERATURAN-PERLINDUGAN-DATA-PERIBADI-2013.pdf). Application to each contracting party remains a legal question (§3.3).
- Proposed amendments to the subsidiary PDP Regulations 2013 would introduce parental/guardian consent **verification** obligations (organisations must take reasonable steps to verify that consent given on a child's behalf is genuine) — layered on top of the *existing* rule that a minor's consent comes from a parent/guardian. **Status limit (reviewed 2026-09-06): the latest cited commentary, dated 10 Mar 2026, says still in consultation; enactment after that date has not been settled by a primary gazette check.** The instrument is JPDP's **Public Consultation Paper No. 4/2025** (issued 22-25 Aug 2025, feedback closed 8 Sep 2025); Chambers and Partners' *Data Protection & Privacy 2026 — Malaysia* guide (10 Mar 2026) confirms "proposed changes remain in the consultation phase, not yet enacted," and no gazette entry or law-firm enactment alert was found after that date. The existing consent rule has an under-18 threshold; applicability/exemptions must be assessed separately. Nothing in the already-in-force PDPA (Amendment) Act 2024 specifically addresses minors. Re-check pdp.gov.my immediately before any pitch goes out.
- **Online Safety Act 2025 (ONSA)** — MCMC's Child Protection Code + Risk Mitigation Code, effective **1 Jun 2026**: bars under-16 social media registration, mandates age verification, parental controls on **licensed service providers**. Financial penalties apply; exact provision/applicability remains for legal verification. This targets **open platforms**, not closed/school-administered/teacher-supervised tools — an AI Classroom app more likely sits under PDPA + internal KPM governance than ONSA, but **this boundary is untested in enforcement — treat as an open legal question, not a settled exemption.**

### 3.3 The public-sector/vendor gap — the single most important structural fact here

- **Primary clarification, 2026-09-06:** the Federal and State Governments are expressly excluded from Act 709; that exclusion is not merely a grey area. The status of Kota Buku and the commercial processing arrangement must be assessed separately, including amended processor security duties. Do not infer a vendor exemption or a settled statutory basis from the government’s position. [JPDP applicability guidance](https://www.pdp.gov.my/ppdpv1/en/akta/application-and-non-application-of-the-act/).
- **Practical framing for a pitch**: "We are the party PDPA unambiguously covers, even if the school's own status is ambiguous — our compliance posture must be self-sufficient, not dependent on 'the school is responsible.'"

### 3.4 KPM-specific data governance (mostly secondary-sourced — verify before external use)

- "Digital Education Policy" (Dasar Pendidikan Digital) — 4 objectives, 6 pillars, 18 strategies, 41 initiatives. [moe.gov.my](https://www.moe.gov.my/dasarmenu/dasar-pendidikan-digital)
- "Guru Data" appointment circular (reportedly SPI Bil. 7/2018) mandates a designated data teacher per school — **circular number unverified, sourced only from secondary summaries.**
- School Information Management Committee (JR02) feeds Sistem Maklumat Pendidikan (SMP) for PPPM tracking — sourced from a school-produced handbook, not an official KPM circular repository.
- Parental consent required before photographing/recording/uploading pupil media to social media (civil servants explicitly barred from unconsented uploads) — circular reference/date unverified.
- **No standardized, KPM-issued "vendor data-consent form" template was found in the reviewed sources as of 2026-09-06** for third-party edtech apps — this fragmentation means Sifututor would likely need to design its own consent/notice flow reviewed against PDPA directly, rather than adopt an existing KPM template.

### 3.5 Vendor-approval reality — no formal route verified in this review

- **No public "approved vendor list" or formal EdTech onboarding pathway was found anywhere.** No equivalent to Singapore's EdTech vendor pre-approval regime.
- Feb 2025: Education Minister Fadhlina Sidek stated **"KPM tidak pernah benar syarikat swasta masuk ke sekolah"** ("MOE has never allowed private companies to enter schools") — [Bernama, 8 Feb 2025](https://www.bernama.com/bm/am/news.php?id=2390598). **Context matters**: this was specifically in response to MACC's "Op Sky" investigation into loan-syndicates using teachers/schools for financial-product promotion — **not a blanket ban on EdTech vendors**. But the underlying governance signal (external parties need KPM/JPN approval before entering schools or engaging staff/students) applies by extension to any private vendor.
- **This is a real go-to-market risk to flag**: no clear approval funnel exists — this cuts both ways (faster informal grassroots adoption is possible, but there's no official "approved" badge to reassure schools/parents, and KPM has shown willingness to publicly shut down unauthorized private access after the fact).

### 3.6 Breach precedents and the macro data-security climate

- **2018 SAPS breach** (see §1.2) — historical precedent only, pre-2023.
- **Singapore's Mobile Guardian breach (2024)** — the single most relevant *regional* cautionary case study, though **NOT Malaysia** (no evidence Malaysian schools were affected — must be clearly labeled as Singapore if used in a pitch): Apr 2024, unauthorized access exposed 67,000 parents' + 22,000 staff's data across 127 schools; Aug 2024, a hacker remote-wiped **~13,000 student devices** across 26 secondary schools; Singapore's MOE terminated the vendor contract entirely and replaced the platform. [Wikipedia](https://en.wikipedia.org/wiki/2024_Mobile_Guardian_security_breach); [TechCrunch, 9 Aug 2024](https://techcrunch.com/2024/08/09/student-raised-security-concerns-in-mobile-guardian-mdm-weeks-before-cyberattack) — **strongly recommend using this as the "why security posture matters" exhibit** in any pitch.
- **Malaysia's macro breach climate** (context, not school-specific): 646 breaches in 2023 (+1,192% vs 2022's 50); 427 by Sep 2024; 195 in Q1 2025 (+29% vs Q4 2024). Whoscall's 2024 report ranked **Malaysia highest for personal data leaks** among surveyed Asian markets (72.5% of checked users found compromised info). 2024 MyKad leak of 17M records; 2025 hacker claims of mass government-agency data theft. [Lowyat.NET](https://www.lowyat.net/2024/335377/digital-ministry-data-breach-figures/); [FMT, 3 Mar 2025](https://www.freemalaysiatoday.com/category/nation/2025/03/03/msia-tops-asian-nations-for-personal-data-leaks-according-to-survey)
- **No specific 2023-2026 breach tied by name to DELIMa, APDM, or VLE Frog was found.**

### 3.7 International privacy/ethics frameworks (comparison reference — Malaysia is the operative jurisdiction)

- **COPPA (US)**: first major amendments since 2013, effective 23 Jun 2025, full compliance required by **22 Apr 2026**. "COPPA 2.0" (extending to teens, currently only covers under-13) passed the US Senate unanimously 5 Mar 2026 but **not yet law**. US school districts used an average of **2,982 distinct edtech tools** in 2024-25 (+9% YoY) — context for why regulators are revisiting old rules. COPPA's under-13 gate is narrower than the Std 1-Form 5 (ages 7-17) range, but its core principles (minimal collection, parental consent, retention limits) are the de facto global vendor-design baseline.
- **FERPA (US) + generative AI**: no AI-specific amendment; existing guidance layers on: explicit consent before feeding education records into AI tools, minimum-necessary data, verified FERPA-compliant vendor agreements. ~20 US states now reference FERPA/COPPA/CIPA/IDEA as their AI-in-schools baseline.
- **UK DfE AI guidance**: full package released **10 Jun 2025** (leadership materials, staff training, self-audit tool); core principle — AI use "carefully considered and assessed," always with **human oversight**, never autonomous decisions. 13 generative-AI product safety standards, current version **19 Jan 2026**. **KCSIE 2026** now treats AI-enabled harms as mainstream safeguarding, not a niche IT issue. This is the **most operationally detailed** of the four frameworks — potentially a useful structural template.
- **UNESCO**: Guidance for Generative AI in Education and Research (2023), AI Competency Frameworks for Students and Teachers (2024, 9 languages), supporting 58 countries on national AI-in-education frameworks. A 2025 *Oxford Review of Education* critique argues UNESCO's guidance risks "techno-solutionism dressed as ethics" — a caution that international frameworks can be aspirational rather than operationally enforceable.

---

## 4. Malaysian local competitors and market

### 4.1 SMAP.my — the closest incumbent, but NOT the same market segment

- Legal entity: **SMAP Solutions Sdn Bhd** (formerly ADS Web Services), incorporated 2 Mar 2020, Dengkil, Selangor. 5 sub-brands: SMAP Education, Association, Business, Community, Pay. [CTOS report](https://businessreport.ctoscredit.com.my/oneoffreport_api/single-report/malaysia-company/1363778M/SMAP-SOLUTIONS-SDN-BHD-)
- **Full feature list**: student/parent records + online registration; automated fee/billing/invoicing; payment gateways (ToyyibPay, CHIP, Bizappay, Billplz, GO Secure); **e-Invois/LHDN direct integration** (since 27 May 2025); WhatsApp/SMS/email broadcast; HR/payroll (leave, payslips, attendance, claims); **RPH module** (daily lesson plans, teacher-shared templates, activity photos); separate RPH-for-tadika / RPA-for-taska (curriculum-planning acronym, NOT robotic process automation); **Pentaksiran** (assessment — explicitly manual entry, no AI); **Peperiksaan** (exam grading/reports); **RPI** (individualized education plans for special needs); **Pengajian Al-Quran** module; discipline tracking (explicitly manual, no automation); QR attendance for staff/students; parent mobile app.
- **AI capability: NONE FOUND, confirmed as of 6 Sep 2026** across the entire product line, including active 2025-2026 blog posts. Grading, assessment, and discipline modules are explicitly manual. [blog.smap.my](https://blog.smap.my/)
- **Target buyer skews to tadika/taska/tuition centres, NOT MOE government or international schools** — testimonials name only kindergarten/daycare/tuition operators (e.g. Tadika Permata Adwa, Taska Ummu Humaira). Marketed audience list includes "primary/secondary schools" but **zero independent evidence of any government or private/international school customer** was found. This is a genuine gap, not a confirmed absence.
- **Pricing not published** — quote-on-request only, no tiers, no free trial found.
- Parent app: 3.6/5 (39 ratings, thin sample), last updated Aug 2024 (stale); user complaints (low-confidence, snippet-only) describe UI as "not very user-friendly." Staff app: 4.6/5 (14 ratings).
- **Strategic implication: both the AI angle and the government/international-school market are genuinely open — not already owned by the closest local incumbent.**

### 4.2 Other Malaysia school-management SaaS — mostly a different, adjacent market

- **AOneSchools** — MY-made, founded 2018, 2,000+ learning centres across SEA claimed. Targets tuition/preschool/childcare/enrichment centres, not MOE schools. No AI confirmed.
- **EduPilotPro** — brands itself an "AI School Operating System": AI-flagged attendance + parent alerts, automated invoicing/reconciliation. Supports KSSR/KSSM + Cambridge IGCSE/A-Levels/UEC/IB — the one product here explicitly claiming both national AND international curriculum support. "AI" here reads as workflow automation, not generative AI/lesson planning.
- **LittleLives** (Singapore-based, 145+ MY preschools), **Illumine**, **Taidii**, **School2me**, **Twinklinc**, **Oodlins** — all cluster in the **private preschool/tuition/daycare** segment, none target MOE government schools, none confirmed AI features.
- **Google Workspace for Education / Microsoft Education adoption** — the vehicle is DELIMa itself (§1.1); Microsoft's **Reading Progress** (AI-assisted reading fluency) was rolled out in Malaysian schools per a 2022 case study (stale for a 2026 pitch, no more recent update found); no Malaysia-specific Copilot for Education rollout confirmed (only AI-skills-training partnerships with the National AI Office).

### 4.3 Local "AI cikgu" startups — the direct comparables

- **CikguAI** (cikguai.app) — the most directly comparable found: KSSM-aligned AI lesson-plan generator, full 13-section RPH in <5 min vs 30-45 min manual, multi-language output (EN/BM/Chinese/Tamil), PDF/DOCX export. Company background (funding, team, launch date) **not verifiable**.
- **Cikguu** — different, adjacent, seed funding from 1337 Ventures + Amanz (Feb 2023 coverage) — **no more recent activity found, possibly dormant.**
- **AI Classroom World / SMKDAR-AI** — see §1.3, the closest overall analog.
- **Samsung AI-Powered Classroom** — see §1.3.
- **MDEC/MaGIC** — AI-skills-training grants and funding infrastructure (HRD Corp-claimable training, MDAG-AI grant, Malaysia Digital tax incentives, 140 local AI providers and ecosystem revenue claimed (monetary value omitted)) — **none of this is a teacher-facing product**, it's ecosystem/skills infrastructure. No edtech-specific MaGIC accelerator cohort found.

---

## 5. Regional APAC/SEA competitors

Only one player found with a confirmed, currently-operating Malaysia school channel:

| Company | Origin | Teacher-facing AI? | Malaysia presence |
|---|---|---|---|
| **Squirrel AI** | China | Weak — B2C franchise model, human tutors alongside AI, no school-B2B dashboard | None found; expanding to US 2026 |
| **Century Tech** | UK | Yes — AI marking, micro-lessons, real-time alerts | None found ("Century Tech Malaysia" hits are unrelated hardware companies) |
| **Riiid** | South Korea | Pre-rebrand: public-school district licensing (B2G) | None found. **riiid.com now redirects to corp.socra.ai ("Socra AI")** — unconfirmed rebrand, not stated explicitly on the new site |
| **BYJU'S** | India | No (B2C only) | **Unstable — active insolvency proceedings in India as of Jul 2026** (NCLT stayed bidding to 31 Aug 2026); a "Byju's Malaysia" Facebook page exists but appears dormant/unverifiable. Do not treat as a live competitor. |
| **Ruangguru** | Indonesia | Yes — **Ruangkelas** LMS + Ruanguji assessment, partnered with 33/34 Indonesian provinces | Officially Indonesia-only per own info page; one low-confidence aggregator claims ASEAN expansion targeting Vietnam/Thailand specifically (not Malaysia) |
| **Geniebook** | Singapore | No — pure B2C (GenieSmart/GenieClass/GenieAsk) | Unverified claim of a Malaysia office (one AI-search summary, not confirmed on geniebook.com) |
| **KooBits** | Singapore | **Yes** — AI auto-marking + teacher strength/weakness reports, custom assignment builder | **Confirmed, currently operating**: named on koobits.com's regional footprint list, and **SMO Online Malaysia** is the official reseller of "KooBits Online Maths (School Plan)," explicitly "Only available to Schools in Malaysia" |

- **Regional government momentum worth tracking**: Vietnam's MOET piloted AI in schools Dec 2025-May 2026, with a **nationwide compulsory AI curriculum (grades 1-12) from academic year 2026-2027**; Khan Academy's Vietnam Foundation is bringing a **Vietnamese-language Khanmigo for Teachers** from Nov 2025; FPT Schools deploying an "AI-integrated Flipped Classroom" across 8,000+ students from 2026; Microsoft trained **160,000+ Thai educators** under "AI for Teachers." This shows Malaysia is not ahead of regional peers on government-AI-in-education pacing.
- **Dead ends**: "MindValu" does not exist as a company (domain doesn't resolve); a "Samsung AI Classroom Malaysia" article and an "aimentor.asia" product were found but blocked from verification (403); a claim that "Pandai" was AI-search-summarized as relevant turned out to be a hallucinated attribution when the source article was actually checked.

---

## 6. Global best-in-class platforms and pedagogy evidence

**Evidence-quality note, 2026-09-06:** multiple study effects, vendor counts and national-programme figures below lack an exact study/report URL, date and outcome definition. They remain research leads, not cleared external claims. “Strongest” rankings across different studies/designs and transfer of foreign effect sizes to this app are not established. The Khanmigo measured-versus-hypothetical correction is retained for consistency, but NBER w35620 and its PDF could not be fetched in this pass; independent primary verification remains open. Likewise, precise legal outcomes and programme-failure causal claims require the underlying judgment/evaluation, not synthesis alone.

Mapped to your 6 pillars. Evidence-strength ranking is called out explicitly per pillar — this matters for knowing which claims to trust in a pitch.

### 6.1 Pillar 1 — Teacher data collection / formative assessment

- **i-Ready (Curriculum Associates)** — strongest evidence: 27-state, 400+ district, 964,000+ student study found **effect sizes 0.14-0.24 SD**; independently verified by HumRRO and Johns Hopkins CRRE; meets ESSA Tier 2/3; diagnostic-to-state-test correlation 0.78-0.85.
- **Renaissance Star Assessments** — used in 6,000+ UK/Ireland schools, validated by the National Center on Intensive Intervention.
- **Edulastic** — 80,000+ standards-aligned questions, real-time dashboards, early-warning visualizations.
- **Formative** — real-time live-answer monitoring; added "Luna AI" for item generation.
- **Kahoot! analytics** — case-study-level gains reported (66%→81%→93.6% across a term, single-teacher anecdote, not controlled).
- **Evidence-strength flag**: i-Ready and Star have the strongest independent, peer-reviewed evidence; Edulastic/Formative/Kahoot analytics claims are largely vendor case studies.

### 6.2 Pillar 2 — Conducting class/live activities

- **Kahoot!** — strongest evidence in this pillar: independent peer-reviewed meta-analysis found **0.72 SD** improvement (≈50th→72nd percentile, "a full letter grade"); a 2025 meta-analysis of 43 studies confirmed gains in achievement/retention/motivation/reduced anxiety (16 studies, 2,070 participants in the quantitative pool).
- **Nearpod** — 2025 studies report engagement gains, LearnPlatform ESSA **Tier III "Promising Evidence."**
- **Pear Deck** — positive engagement self-reports (75-80%), but literature itself notes an "absence of peer-reviewed research directly studying" it — mostly practitioner/action research.
- **ClassDojo** — **mixed evidence**: some studies show reduced disruption/improved self-awareness; a 2025 paper explicitly "problematises ClassDojo as a digital tool for behaviour management" and notes low treatment-integrity (teachers misimplement). Deserves the most skepticism of any tool researched.
- **Classcraft** — a 2021 meta-analysis (Zhang, *Education Research International*) confirmed significant achievement/motivation effects vs traditional instruction.

### 6.3 Pillar 3 — AI content generation (teacher-facing, whole-class or per-student)

All figures vendor-reported unless noted — treat adoption/time-saved numbers as directional, not causal:

- **MagicSchool AI** — most-deployed in US K-12: 5M+ educators, 160 countries, 13,000+ schools; commercial benchmark amounts omitted under D10. 80+ tools; teachers self-report 7-10 hrs/week saved. SOC2/FERPA/COPPA/GDPR/CCPA compliant, no student data used for model training (stated).
- **Curipod** — one-prompt full interactive lesson generation; notable design: anonymous-to-peers/visible-to-teacher participation to reduce shy-student pressure; adapts feedback mode by lesson phase.
- **Diffit** — text-to-reading-level conversion (2nd-11th+ grade) + auto vocab/comprehension questions. Nov 2024 survey of 2,517 teachers: 96% time-saved, 93% differentiation-helped.
- **Khanmigo for Teachers** (Khan Academy) — free for K-12 teachers, 25+ tools including IEP assistant, standards alignment.
- **SchoolAI** — teacher-built guardrailed "Spaces" + live mastery dashboard (not opaque chat log). 1M classrooms, 80+ countries, 400+ districts in two years; funding and subscription amounts omitted under D10. ESSA Level III certified; certification scope remains subject to the existing source checks.
- **Google Gemini for Education** — free with Workspace; 30+ Classroom tools; expanding to all Classroom languages Apr 2026.
- **Microsoft Copilot for Education ("Teach")** — launched Oct 2025, free for all M365 Education by 2026; native Canvas/Blackboard/Schoology integration from Spring 2026.
- **Evidence-strength flag**: this entire pillar is almost entirely vendor-reported — genuinely independent peer-reviewed efficacy research on AI content-generation specifically is scarce industry-wide as of 2026.

### 6.4 Pillar 4 — AI teaching-assistant / adaptive learning (customization, tracking, recommendations)

This is where the strongest **and** the most contested evidence sits:

- **Carnegie Learning / MATHia — the gold-standard study in the entire research set**: a US DoE-funded RCT, 18,000+ students, 147 schools, found blended instruction **nearly doubled** year-2 growth on standardized math tests. Separate Student Achievement Partners 2021 study: **16-percentile-point improvement** for median students on Algebra I, largest gains for underperforming students. Meets **ESSA Tier 1 "Strong"** (blended).
- **i-Ready / IXL** — see §6.1; IXL independently validated by SRI International, meets ESSA Tier 2, correlational study across 42,940 schools/12 states.
- **DreamBox Learning** (K-6 math) — Harvard CEPR study: **dose-response relationship** — 20 min/week → +2.5 NWEA MAP points; 60 min/week → +7.5 points. Caveat: intensive-need students "may not benefit" as much.
- **Squirrel AI** — RCTs show gains vs traditional instruction, largest for weaker-foundation students — but **largely company-sponsored/affiliated studies**, independent replication outside China limited.
- **Khanmigo (tutoring mode)** — the most rigorous *recent* study: an **NBER-circulated 2-year RCT** (w35620), 18 Tennessee middle schools. **Corrected after adversarial review:** the *measured* intent-to-treat effect is **≈1.3 percentile ranks/term, i.e. ≈0.06–0.08 SD/year**. The 0.14 SD figure sometimes quoted is a separate *hypothetical* — the implied effect if a student had engaged for a full year's worth of active use, which almost no student did. Do not pair the two as if they were the same measurement. The authors note the observed gain "resembles gains from Khan Academy practice *without* AI." **Critical finding: engagement was the binding constraint, not model capability** — students used it on only ~1/3 of active days, many sent off-topic messages or tried to extract answers directly rather than engage pedagogically. This is a crucial cautionary data point: **access ≠ actual beneficial use.**
- **Century Tech** — vendor-stated 30% topic-understanding improvement, 20% higher math-proficiency gains, ~6 hrs/week teacher-workload reduction — **independent verification not found**, figures are vendor materials.
- **Evidence-strength ranking**: Carnegie Learning (RCT, largest N, DoE-funded) > i-Ready/IXL (ESSA-validated) > DreamBox (dose-response, Harvard-affiliated) > Squirrel AI (company-affiliated) > Khanmigo (well-designed RCT but modest/contested effect + documented engagement problem) > Century Tech (vendor-stated only).

### 6.5 Pillar 5 — Adjacent efficiency features

- **Attendance automation (facial recognition)** — 2026 systems claim 98%+ accuracy even with masks/glasses (CNN/HOG-SVM, browser-based). **No studies found on whether this actually improves attendance rates or outcomes** — only recognition-accuracy engineering literature.
- **SEL/behavior tracking** — CASEL's 20-year research synthesis finds SEL programs have "meaningful, causal impacts" (academic performance, conduct, school climate) and is low-cost. **Important gap: tracking-tool measurement lags behind SEL-outcome research** — the pedagogy is well-evidenced, the tech tooling to track it reliably is not.
- **Parent communication automation** — vendor-reported time savings (7-10 hrs/week pre-automation, 45-55 min/day via digital attendance reconciliation), one case study citing 60% reduction in response delays, 15-30% reduction in chronic absenteeism from automated alerts — **all vendor case studies, not independent research.**
- **Auto-grading / AWE (essay grading)** — genuinely rich technical literature: hybrid/LLM models achieve QWK 0.75-0.86 vs human raters on K-12 essays (>0.8 = strong agreement); **fine-tuning matters enormously** (fine-tuned GPT-3.5 QWK 0.613-0.859 vs zero-shot only 0.023-0.327); reliability drops sharply for short-answer/zero-shot grading. **Documented bias: LLM graders produce more "medium" scores, fewer extremes than humans** — may under-reward excellent work and under-penalize weak work.
- **Handwriting AI grading** — ~72% of schools globally reportedly already use some AI grading (2026 survey); AI-to-human agreement ~95% cited for human-in-the-loop pipelines; Gradescope (acquired by Turnitin **3 Oct 2018**, [company announcement](https://www.turnitin.co.uk/press/turnitin-acquires-gradescope), checked 2026-09-06) used by 3,000+ institutions, 60-70% grading-time savings reported. **Mostly vendor/survey-reported, not independently validated.**
- **Early-warning/at-risk systems** — in use in at least half of US high schools; prediction accuracy well-studied (one model ~94% accurate predicting final grade by week 6) but **evidence that EWS actually reduces absenteeism/dropout via triggered intervention is thin** — prediction ≠ proven intervention efficacy. Weaker predictive power for some subgroups (e.g. newcomer English learners).

### 6.6 Pillar 6 — Parent/student portals

- **ClassDojo** — free tier shows Class/School Story, individual Portfolio, **last 2 weeks** of behavior points, direct messaging. Paid tier extends history to 365 days.
- **Seesaw** — parents see only **teacher-approved** work (deliberate curation gate, not all activities), tagged per child, feedback + messaging in 100+ languages, full historical journal access.
- **PowerSchool** — the most "raw data" model: real-time attendance, per-assignment grades + teacher comments, configurable alerts. Traditional SIS view, not curated/narrative.
- **Toddle** (IB-oriented) — learning "evidence" (photo/video/audio) as primary artifact rather than raw scores; narrative end-of-trimester reports; positioned narrative-first vs PowerSchool's numeric-first model.
- **Age-appropriateness research (directly relevant to your Std 1 vs Form 5 range)**:
  - A 2026 *Journal of School Health* study on secondary-school parent-monitoring portals found real communication/support benefits but flagged effects on **student autonomy, wellbeing, and parent-child dynamics as "understudied."**
  - A 2026 *Journal of Adolescence* study: **99.6% of parents track at least one domain** of their teen digitally; tracking is "widespread, often accepted, and linked to overprotection" — documented tension between adolescent autonomy needs and continuous visibility.
  - A documented middle-ground finding: **"limiting access to designated times can preserve student independence while keeping parents informed"** — i.e., time-boxed/digest visibility is a real compromise pattern, not a binary between full transparency and full opacity.
  - Younger-child data: Michigan Medicine C.S. Mott poll — for ages 7-9, 50% of parents report *educational-app-only* use (vs 32% social media) — parents of Std-1-age children already default toward curated/gated tools (consistent with Seesaw's model, not PowerSchool's).
  - **Genuine evidence gap: no study prescribes an age-based data-disclosure taxonomy for school apps specifically** — this would be a real design decision to make, not one to copy from existing research.

### 6.6.1 Teacher preparation time — EEF trial and transfer limits

**[P, checked 2026-09-06]** EEF’s ChatGPT teacher-choice trial involved **259 teachers in 68 English state-funded secondary schools**, preparing Year 7/8 science lessons. The ChatGPT-with-guidance group reported **56.2 versus 81.5 minutes weekly**, a **25.3-minute (31%)** reduction for that preparation task. A blinded panel detected no apparent difference in sampled resource quality. [EEF project and evaluation report](https://educationendowmentfoundation.org.uk/projects-and-evaluation/projects/choices-in-edtech-using-generative-ai-chatgpt-for-ks3-science-lesson-preparation-2024-teacher-choices-trial).

This is not evidence of whole-workload reduction, proven quality equivalence, pupil attainment, or the same result across Malaysian years/subjects/languages. The evaluation report is dated 2024; the project page’s later completion metadata must not be treated as the trial date. It supports measuring a teacher-assisted preparation workflow, not promising a national saving.

### 6.6.2 Korea adoption — chronology without a single-cause claim

**[N, 15 Oct 2025; checked 2026-09-06]** reported school adoption fell from **37% in the semester ending July 2025 to 19% in the semester starting September 2025**. The report describes shortened testing, technical/content problems, teacher/parent concerns and political change; it does not isolate “teacher overload” as the sole cause. [Rest of World](https://restofworld.org/2025/south-korea-ai-textbook/). Keep the January participation count, March launch and later legal/status changes chronologically separate. D6 remains neutral on compulsory/optional use, while D4’s staged exposure stays fixed.

### 6.7 Overall efficacy meta-analyses on AI-personalized/adaptive learning in K-12

- **RAND** — Cognitive Tutor Algebra 1 RCT: significant improvement, but **only in year 2 of implementation** — no significant year-1 effect. RAND's broader "Informing Progress" report states plainly: **"evidence of efficacy in rigorous studies for blended instructional models is mixed."**
- **EEF (UK)** — Digital Technology strand: moderate learning gains, but core guidance is technology should **supplement, not replace**, teacher-led interaction; explicitly not a guarantee for any given school.
- **ITS meta-analyses** — modest but significant effect, **g = 0.271** overall, similar across elementary/middle and for low-achieving students, but **weaker in studies including rural schools** (equity-relevant). Reading-comprehension ITS effect 0.60; math ITS historically much smaller (g = 0.01-0.09, 2013 meta-analysis). ITS vs. human tutoring: only a small ITS edge (0.20) — AI tutoring approaches but doesn't clearly beat human tutoring.
- **AI-personalized STEM (2025 meta-analysis, 99 effect sizes/32 RCTs)** — AR/VR showed largest effects; **personalization combined with classroom (teacher-mediated) use showed stronger effects than purely solo/at-home use** — directly relevant if product design assumes teacher-mediated rather than student-alone use.
- **Bottom-line synthesis**: the most rigorous, largest-N, government-funded evidence shows **real but modest effects (~0.14-0.25 SD)**, concentrated more in **math** than other subjects, requiring **sustained, correctly-dosed usage**, generally **stronger in year 2+ of implementation, not immediately**. Nothing in independent literature supports "transformative overnight gains" — honest framing is "meaningful incremental gains under disciplined, teacher-mediated implementation."

---

## 7. Go-to-market reality: B2G procurement vs. private/international schools

### 7.1 No standing vendor panel exists

- No public, named "approved vendor list" for classroom software was found at federal or state level. KPM procures large ICT programs (hardware, connectivity, maintenance) as **discrete open tenders** via moe.gov.my/perolehan — not a rolling panel a startup can apply to join.
- **DELIMa is the de facto software gateway today** (bundles Google/Microsoft/Apple + named third-party tools like Canva, Padlet, Tinkercad, Kahoot!), but **no documented vendor application/approval process for getting onto DELIMa was found anywhere** — inclusion appears to require either direct KPM negotiation (for large players) or is simply undocumented publicly.

### 7.2 School-level budget reality — the "land small, land often" opportunity

**Citation corrected after targeted follow-up (2026-09-06): SPK Bil. 8/2012 was superseded by Surat Pekeliling Kewangan Bil. 1 Tahun 2021** ("Pengurusan Kewangan bagi Peruntukan Bantuan Persekolahan Umum KPM"), effective 1 Oct 2021, which explicitly cancels SPK 8/2012 and its 2013 amendment; a later "SPK Bil. 1/2021 (Pindaan)" also exists (date and content not established). moe.gov.my's PCG page (updated 4 Sep 2026) confirms SPK 1/2021 as the governing circular. The earlier monetary thresholds came from secondary summaries, not a first-party PDF read. **Cite SPK 1/2021, not 8/2012; exact current ceilings and the later amendment remain unverified.** The Scribd “Pecahan PCG 2026” rate claims remain unverified/do-not-use; values omitted under D10.

- Software purchases are **explicitly permitted** under the "PCG Bukan Mata Pelajaran" (non-subject) allocation ("buku rujukan, ensiklopedia, **perisian**...").
- Capital-equipment ceilings differ by school level and allocation; **exact current limits remain primary-unverified** (SPK 1/2021).
- ICT-committee (JPICT) approval depends on applicable purchase classification and threshold; **current threshold remains primary-unverified**, not merely a headmaster choice.
- **Tablet computers are explicitly prohibited from PCG purchase** — relevant if any pitch assumes schools buy devices from PCG.
- **Practical read:** a modest software subscription may fit delegated school authority, but classification and thresholds need a first-party check before using this as an entry strategy. No approved spending limit is established here.

### 7.3 The 1BestariNet pattern — a cautionary template, not a precedent to repeat

- Malaysia's best-documented large federal edtech procurement (see §1.4) went to a **conglomerate with existing telco/infrastructure standing (YTL)**, bundled as one giant multi-year megadeal — not to a pure-play edtech vendor competing on product merit. It ended in a decade-long political/legal controversy.
- **This is a strong argument against chasing a federal megatender as go-to-market strategy.**

### 7.4 More realistic entry points found

- **State-level pilots with corporate sponsorship, not KPM budget**: Sabah Digital School Pilot (5 primary schools, 1,350 "Didik Tab" tablets, Year 1-5); Sekolah Rintis Bangsa Johor (iPads for Year 4-6, tied to Google Classroom/DELIMa, partnered with **Affin Digital Space**, a bank-linked initiative, not a pure edtech vendor). — Sourced from search snippets only (source pages blocked, 403); directionally useful, not fully verified.
- **Google's entry route**: MOE approached Google directly (not via competitive tender found); local **systems integrators (Matrix Connexion, Awantec Systems)** did on-the-ground deployment — a viable channel model: partner with an SI that already has a Google/Microsoft relationship with MOE, rather than approach MOE cold.
- **Microsoft's entry route**: CSR/showcase-school partnerships (STEM4ALL from 2019, EdVision with Lenovo from 2020, 5 named Showcase Schools) — not a commercial tender either.
- **Critical negative finding — narrowed after targeted verification (2026-09-06)**: **no official source located in this review establishes a Malaysian-founded EdTech startup holding the specific KPM software-procurement or authenticated DELIMa integration status being investigated.** Every documented KPM-level success required conglomerate scale (YTL), a systems-integrator partner (Google/Microsoft's route), or global-vendor CSR relationships (Microsoft's showcase schools). **Two qualifications the pitch must respect:** (1) **Pandai Education does have a documented government relationship** — it is named as a strategic partner in the official Ministry of Digital/MDEC press release (11-12 Feb 2026) for the Sarawak AI-Powered Classroom PoC, and appears on a Selangor state-assembly Q&A page and JPN-level community sites as a DELIMa "rakan strategik." These are pilot/partnership designations (in-kind, CSR-style, or informal — the contractual nature could not be established), not KPM procurement wins; Pandai's own material describes itself as "working alongside DELIMa," not integrated into it. (2) **Sasbadi** (listed) holds real KPM contracts — but via the **textbook-publishing route** (e.g. a textbook package for the 2027 curriculum, Apr 2026-Apr 2029), not edtech/software procurement. **So the defensible claim is: "this research found no verified small/mid Malaysian edtech example of the normal KPM software-procurement or DELIMa-vendor route" — not "no Malaysian edtech has any government relationship."** The inbound Kota Buku route remains unusually valuable precisely because it provides a direct conversation; it does not itself establish procurement access or approval.

### 7.5 Private/international schools — thinner evidence, but structurally different

- Not part of the government PCG/tender system at all — funded and procured autonomously, decided by principal/head-of-school and/or school board, not sebut harga/tender rules.
- Relevant association: **AIMS (Association of International Malaysian Schools)**, founded 1997, 40+ member schools by 2019 — no published procurement/vendor-engagement info found from AIMS itself (a genuine documentation gap, confirmed by direct site fetch, not just a search miss).
- **"MABE" could not be verified to exist as a named association** — closest real matches are AIMS (international schools), NAPEI (National Association of Private Educational Institutions, private K-12 broadly), or MAPCU (tertiary only, likely not relevant). **Flag: confirm the intended acronym before using it anywhere.**
- No Malaysia-specific documented sales-cycle length or case study found — this section would benefit from direct outreach to 2-3 AIMS member schools rather than more web research.

---

## 8. Teacher pain points in Malaysia

### 8.1 Workload — well-documented, high confidence

- **NUTP** (teachers' union) says workload affects **400,000+ teachers**; repeated 2025 calls for a formal KPM/JPA workload committee. [Kosmo, 7 Jul 2025](https://www.kosmo.com.my/2025/07/07/beban-tugas-guru-makin-teruk-nutp/)
- NUTP language stays generic: "weak digital infrastructure and malfunctioning education applications consume significant teacher time" — **NUTP has never named DELIMa or APDM specifically by name in any source found.** Don't attribute platform-specific criticism to NUTP without a firmer citation.
- **Government responses (verified official actions)**:
  - Nov 2025: SSDM (student-behavior logging system) reverted to misconduct-only recording after teachers were made to log thousands of "positive behaviour" entries — NUTP welcomed it.
  - Dec 2025: Minister Fadhlina Sidek announced **SPL KPM** (teacher training-management system, launched early 2024) would be **abolished in 2026** specifically to cut admin load.
  - RPM 2026-2035 commits to an **"80:20" policy** (80% teaching time, 20% non-teaching) — a forward target, not yet a measured outcome.
- A lower-tier open-access study (n=100 teachers) found strong workload-burnout correlation, admin/paperwork flagged as primary exhaustion source — indicative, not authoritative.
- **The widely-cited "64.1 hrs/week" figure (Focus Malaysia, 11 Sep 2025) — traced and DO NOT CITE.** Targeted follow-up (2026-09-06) found its origin: Abdull Sukor Shaari, Abd. Rahim Romle & Mohamad Yazi Kerya, *"Beban Tugas Guru Sekolah Rendah,"* a conference paper at Seminar Kebangsaan Kepimpinan dan Pengurusan Sekolah, **12-14 Feb 2006** — 274 primary-school teachers, 15 schools, **one district** (PKG Langgar, Kota Star, Kedah). The 39.5/24.6-hour split matches exactly. It is 20 years old, one-district, primary-only, and not peer-reviewed; Focus Malaysia reproduced it without attribution. A commonly repeated alternative (65.46 hrs primary / 67.01 hrs secondary, "16,699 teachers, MOE-linked") could not be traced to any named study — do not substitute it. **Alternative source to verify:** [OECD TALIS 2013](https://www.oecd.org/en/publications/talis-2013-results_9789264196261-en.html). The earlier ~71% figure concerns time within a typical lesson, not the whole working week; its complement includes maintaining order, not only administration. **Open:** retrieve the exact Malaysia table and denominator before quoting the ~17-hour, ~71% or 78.7% figures. Do not use them as proof of a weekly 80:20 split.
- 5,000+ early-retirement applications/year since 2022 (official, per Deputy Minister Wong Kah Woh); NUTP attributes this partly to non-teaching burden (advocacy interpretation).

### 8.2 APDM-specific friction — weakest evidence tier

- No NUTP statement, academic study, or news article specifically naming APDM was found — only practitioner/how-to blog content (anecdotal, not journalism): internet slowness from simultaneous nationwide login times, "Kelas Belum Ditetapkan" data errors at year-start, deletion locked to school-level "APDM Admin" role only.
- **No quantified "X hours/week on APDM" figure exists anywhere in the literature** — if the pitch needs this number, it will require primary interviews/a fresh survey, not existing research.

### 8.3 VLE Frog complaints — historical only, not current

- Nearly all substantive Frog VLE studies date **2015-2019**, pre-dating DELIMa. Findings: limited internet access, heavy syllabus/workload, low ICT skill/facility correlated with low usage. **Use as historical adoption-failure pattern evidence, not current-state evidence** — Frog is discontinued.

### 8.4 Differentiated instruction in mixed-ability classrooms

- A KPM-internal source is notable: **Institut Aminuddin Baki** (KPM's own leadership-training institute) produced a paper on differentiated-teaching practice/problems (~Mar 2023) — content unverified (fetch failed) but its **existence signals MOE-internal awareness of this exact problem**, a useful pitch data point regardless of the paper's specific findings.
- General finding (moderate-tier journal, HRMARS/IJARPED): teachers are aware of student diversity and try to plan by ability level, but implementation is limited by teacher knowledge, readiness, attitude, and lack of training exposure.
- **No study found quantifying class-size + workload + differentiation-difficulty together** — the weakest-evidenced pain point of the set; the pitch may need to lean on general MOE class-size statistics plus this qualitative finding rather than one strong quantitative citation.

---

## 9. Cross-cutting strategic observations

These are factual synthesis points connecting the research above — not product design decisions, which remain yours to make.

1. **The AI gap in the local market is real and open.** SMAP (the strongest local competitor) has zero AI features. No Malaysian-founded startup found (CikguAI, Cikguu, AI Classroom World) has significant confirmed scale, funding, or a documented government-school win. KooBits is the only regional player with a confirmed, currently-operating Malaysia school channel, and it's math-only, Singapore-MOE-curriculum-oriented, sold via a local reseller.

2. **But government is not standing still.** KPM's own national "AI-Powered Classroom" pilot (27→260 schools, targeting full national rollout by 2030) plus DELIMa 3.0's DETa assistant means any pitch to government schools is positioning **alongside or against an official state initiative**, not into a vacuum. AI Classroom World/SMKDAR-AI is the closest existing grassroots analog and a potential partner-or-competitor consideration.

3. **Federal-scale procurement has a bad track record and no small-vendor precedent through the normal software route.** 1BestariNet (megadeal → contract dispute → corruption investigation, eventually cleared) is the cautionary template. No small/mid Malaysian edtech company has documented success winning a KPM contract or DELIMa vendor status through a normal software-procurement process — every KPM-level success required conglomerate scale, an SI partnership, or CSR-style relationships. (Qualification from verification: Pandai does hold a documented *Ministry of Digital/MDEC* pilot partnership, and Sasbadi holds KPM *textbook-print* contracts — neither is the software-procurement route. See §7.4.)

4. **School-level and state-level entry points look more realistic than a federal push — with the caveats the body sections carry.** PCG rules may allow delegated school-level software approval, but classification and thresholds remain unconfirmed from a first-party read of SPK 1/2021 (§7.2). State-level pilots (Sabah, Johor) with corporate/bank sponsorship, or partnering with an existing Google/Microsoft systems integrator, are the closest "how vendors actually got in" patterns found — but the Sabah/Johor details rest on search snippets only (source pages blocked), so treat them as directional, not documented (§7.4). *(Hedges re-inserted here after adversarial review noted the synthesis had dropped caveats present in the body.)*

5. **Compliance is a real, non-trivial cost center, not a checkbox.** Mandatory DPO (near-certain at national scale), mandatory 72-hour breach notification, biometric data now "sensitive," no Malaysia-specific children's-data law (meaning Sifututor would likely need to design its own consent flow rather than adopt an existing template), and no formal KPM third-party route verified in this research (an access uncertainty, not proof that no process exists) all need to be designed for from day one, not bolted on later.

6. **The curriculum foundation is mid-transition.** KSSR/KSSM → KP2027 replacement runs 2026-2031, with multiple curriculum versions live simultaneously across different year/form cohorts for years. Any content architecture needs curriculum-version as a first-class, swappable concept. BM/History now being mandatory even in international schools (from the same Jan 2026 announcement) is a positive signal for including private/international schools in scope, since it creates new DSKP-aligned content demand there too.

7. **DSKP-alignment is table stakes, not a differentiator.** Pandai already proves the market expects chapter/topic/subtopic/TP-level curriculum mapping. Real differentiation has to come from teacher-workflow value — the pillars you specified (data collection, conducting class, content generation, personalization/tracking) — not from curriculum coverage alone.

8. **The evidence-backed honest pitch is "meaningful incremental gains," not "transformative."** Across every credible independent study found (Carnegie Learning, i-Ready, IXL, RAND, EEF, the ITS meta-analyses), effects are real but modest (~0.14-0.25 SD), concentrated in math more than other subjects, require sustained correct-dosage usage, and often don't show up until year 2 of implementation. Khanmigo's own RCT found the access-to-actual-engaged-use gap (students used it ~1/3 of days) was the real bottleneck, not the AI's capability — a genuinely important design consideration: adoption/engagement design may matter more than model sophistication.

9. **No one has solved the parent/student portal age-appropriateness question.** No study prescribes what data is appropriate to show a Std 1 (age 7) parent vs a Form 5 (age 17) parent/student. Existing products split between curated (Seesaw, teacher-approved-only) and raw (PowerSchool, full SIS data) models; research suggests time-boxed/digest visibility as a middle ground, and shows continuous tracking is linked to "overprotection" concerns for teens specifically. This is a genuine open design decision, not a solved problem to copy.

---

## 10. Master list of dead ends, unverified items, and follow-ups needed

**Confirmed non-existent / could not verify existence:**
- "iSTUDENT" as a named MOE system — likely conflation of SMM/APDM/IDME.
- "MindValu" as an edtech company — domain does not resolve.
- "MABE" as a Malaysian private-school association — likely conflation of AIMS/NAPEI/MAPCU.

**Needs primary-source verification before external/pitch use:**
- APDM workload duplication statistic (47.5%/32.6%) — ResearchGate blocked full citation metadata.
- ~~"64.1 hrs/week" teacher workload figure — source study not cited.~~ **Resolved (2026-09-06): traced to a 2006 one-district conference paper. Do not cite; use TALIS 2013 instead (§8.1).**
- KPM circular numbers for "Guru Data" appointment (SPI Bil. 7/2018) and pupil-photo/consent rules — sourced only from secondary summaries.
- ~~PCG budget ceilings — sourced from a 2012 circular; confirm still current.~~ **Partly resolved (2026-09-06):** the governing circular is SPK Bil. 1/2021 (not 8/2012); the ceilings appear unchanged per secondary summaries. Still open: a first-party read of SPK 1/2021 and its "(Pindaan)" amendment, and the current per-capita rate table.
- Government tender/quotation RM thresholds (sebut harga vs tender terbuka) — structure confirmed, exact figures not extracted from a primary document.
- bpk.moe.gov.my deep-link DSKP category URLs — exist per Google's index, but returned 403/404 on direct fetch this session (likely bot protection); verify manually in a browser before using as clickable citations.
- Sabah Digital School Pilot and Bangsa Johor pilot details — Malay Mail source pages blocked (403), relying on search snippets only.
- ~~Whether the MDEC Sarawak PoC and KPM's "260 schools" pilot are the same initiative.~~ **Resolved as far as public sources allow (2026-09-06): no official cross-reference exists in either direction — treat as two distinct, unreconciled initiatives and flag the possible overlap (§1.3). Also note the national programme's inconsistent school counts across reports.**
- Sasbadi's "Ace-it" platform (Samsung classroom partner) — identified but feature detail unverified.
- Whether Riiid has actually rebranded to "Socra AI" — domain redirect observed, not explicitly stated on the new site.
- Malaysia's proposed child-specific PDP Regulations amendments — **verified 2026-09-06 as still in consultation** (Public Consultation Paper No. 4/2025; Chambers, 10 Mar 2026). Re-check pdp.gov.my immediately before any pitch is finalized (§3.2).
- **New, from verification:** Pandai Education's exact contractual status with the Ministry of Digital/MDEC Sarawak pilot and with JPN Selangor's "rakan strategik" designation (MOU vs informal vs sponsorship) could not be established (§7.4).

**Genuine research gaps (not found anywhere, may need primary research/interviews instead of more web search):**
- Quantified time-cost of APDM specifically (no "X hours/week" figure exists in the literature).
- Class-size + workload + differentiated-instruction difficulty studied together with hard numbers.
- Private/international school procurement decision-makers and sales-cycle length in Malaysia specifically (only generic global blog content found) — would benefit from direct outreach to 2-3 AIMS member schools.
- Any peer-reviewed study prescribing age-appropriate data-disclosure thresholds for parent portals by child age.
- A documented, KPM-published EdTech vendor approval process, if one exists at all (absence of evidence found, not confirmed evidence of absence — worth a direct enquiry via Sifututor's existing agent-access-map lanes to KPM's Bahagian Teknologi Pendidikan or a JPN contact, rather than more public web search).

---

*Compiled by Claude Code from 9 parallel research agents, 2026-09-06. Source list is embedded inline throughout — no separate bibliography file. Next session on this concept should start by re-reading this file rather than re-researching any of the above.*

### SEPADU-specific evidence debt — 2026-09-06

**DO NOT QUOTE as established facts:** **85,500** Sabah/Sarawak teachers, **147,512** SEN pupils, and **37.4%** OKU-friendly school facilities. Their current primary publication, denominator/year and scope have not been established in this pass; keep [review §5](partner/SEPADU-review.md) flags intact. Do not turn population estimates into the device denominator or assume that a facilities statistic measures software accessibility. Use D8’s teacher-only programme scope, not an inferred pupil-device base. The early LKAN report-year/edition and e-RPH primary-copy checks above remain open too.
