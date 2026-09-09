# KESUMA Ecosystem Research Dossier

**Compiled:** 31/07/2026
**Method:** 9 parallel research agents, primary-source weighted (gazetted Acts from AGC and eAkta, Treasury circulars as PDFs from ppp.treasury.gov.my, agency financial reports, MyProcurement API, Budget 2026 speech and expenditure estimates, agency tender portals). Web search budget was exhausted partway; later work used direct WebFetch, PDF extraction, DNS and HTTP inspection.
**Companion artifacts:**
- Background reference: https://claude.ai/code/artifact/539e4d3f-5020-4853-b456-2c62af156f5b
- Strategy brief: https://claude.ai/code/artifact/66753a1f-2f70-44ab-8437-a9d49f969b80

**Purpose:** preserve the source-level detail so this does not need re-researching. Condensed recall versions live in Claude memory as `reference_kesuma_ministry_ecosystem.md` and `project_kesuma_business_opportunity.md`.

**Confidence convention used throughout:** CONFIRMED (primary source read directly) / REPORTED (secondary source, plausible, unverified) / NOT FOUND (searched, absent) / CONTESTED (official sources disagree).

---

## Part 1: What KESUMA is and what sits under it

### 1.1 The ministry

KESUMA is Kementerian Sumber Manusia, Malaysia's Ministry of Human Resources, previously referred to as MOHR or KSM. Cabinet approved the acronym 01/03/2026; official use from 04/03/2026. KE.SU.MA from the Malay name; also an old Malay word for "flower".

- Mission: the "3K", Kebajikan (welfare), Kemahiran (skills), Keberhasilan (outcomes)
- Vision: "National leader in human resources development and management"
- Minister (2026): YB Dato' Sri Ramanan Ramakrishnan, since 17/12/2025, replacing Steven Sim Chee Keong (12/12/2023 to 17/12/2025)
- Deputy Minister: YB Datuk Khairul Firdaus bin Akbar Khan, same date
- HQ: Menara PERKESO Putrajaya, Levels 6 to 12, Presint 2 (occupies floors of its own statutory body's tower)
- Budget 2026 ministry vote: RM1.828 billion (scope unclear whether inclusive of agency allocations)

### 1.2 The legal split that governs everything

This is the single most useful structural fact in the dossier. The agencies are **not peers**.

**Act 640 (PTPK)** contains Bahagian III *PERBADANAN*, s.6 *Penubuhan Perbadanan* ("Suatu pertubuhan perbadanan dengan nama Perbadanan Tabung Pembangunan Kemahiran ... ditubuhkan"), s.7 *Meterai Perbadanan*, Bahagian IV *LEMBAGA* (s.16 Lembaga Pengarah), s.25 *Ketua Eksekutif*, and critically **s.90 invoking the Statutory Bodies (Accounts and Annual Reports) Act 1980**.

**Act 652 (JPK)** contains Bahagian II establishing a *Majlis* (Council), Bahagian III *PELANTIKAN PEGAWAI*, and s.68 *Pekhidmat awam*. It has **no** *Penubuhan Perbadanan*, **no** *Meterai Perbadanan*, **no** *Lembaga Pengarah*, and no reference to Act 1980.

Act 652 renamed and re-empowered an existing department. Act 640 incorporated a body with its own board, seal and balance sheet. Procurement behaviour follows directly.

### 1.3 Departments (civil service, part of KESUMA directly)

| Agency | Function | Serves |
|---|---|---|
| **JTKSM** (Labour Dept, Peninsular) | Enforces Employment Act 1955 and 11 other statutes including Gig Workers Act 2025. Wage disputes, retrenchment, foreign worker clearance, licenses private employment agencies under Act 246. Runs the Labour Court function under s.69 EA1955 (a power exercised by officers, not a separate tribunal). | Employers, employees, foreign workers, recruiters |
| **JTK Sabah / JTK Sarawak** | State equivalents under the Sabah/Sarawak Labour Ordinances | Same, per state |
| **JTM** (Manpower Dept) | Operates training institutes: 24 ILP, 8 ADTEC, 1 JMTI. Est. 1967. Distinct from DSD/JPK which sets standards rather than running institutes. | School leavers, trainees |
| **DSD / JPK** (Skills Development) | Sets NOSS, issues SKM L1-3, DKM L4, DLKM L5. Accredits training providers. Runs NDTS/ADI apprenticeships and RPL/PPT. Lineage: LLPPKK (1971) → MLVK (02/05/1989) → JPK (01/09/2006). | Trainees, training centres, employers |
| **DOSH / JKKP** (OSH) | Enforces OSHA 1994 (Act 514) and Factories and Machinery Act 1967. Inspection and enforcement only. Now also administers regulations under Act 872. | All workplaces |
| **JPPM** (Industrial Relations) | Mediates disputes under IRA 1967; unresolved cases referred by Minister to Industrial Court | Employers, employees, unions |
| **Mahkamah Perusahaan** (Industrial Court) | Adjudicates dismissal and trade disputes, issues binding awards. Distinct from Labour Court (wage claims only). | Employers, employees, unions |
| **JHEKS** | Trade union registry under Trade Unions Act 1959. Running since July 1946. | Trade unions |
| **MITRA** | Malaysian Indian community programmes. Transferred from PMO ~27/01/2026. Recent, has moved ministries before. | B40/M40 Indian community |

### 1.4 Statutory bodies (own boards, own balance sheets)

| Agency | Function |
|---|---|
| **PERKESO / SOCSO** | Employment Injury and Invalidity schemes (employer 1.75% + employee 0.5%), Employment Insurance System (EIS, from 01/01/2018), Self-Employment scheme (Act 789, rebranded **LINDUNG KENDIRI** 22/08/2025), foreign worker scheme, and MYFutureJobs (run directly, not outsourced) |
| **HRD Corp** (formerly PSMB/HRDF, rebranded June 2021) | Collects 1% payroll levy from employers with 10+ Malaysian staff (0.5% voluntary for 5-9), disburses as training grants |
| **NIOSH** | OSH training/consultancy/research. Sole authorised examiner for the Safety and Health Officer qualification. Company limited by guarantee, est. 1992. |
| **PTPK** | Loan fund (~3% declining balance) for SKM/DKM/DLKM training. Est. 01/06/2006 under Act 640. |
| **TalentCorp** | Returning Expert Programme, Critical Occupations List (MyCOL), MyMahir AI. Placement under KESUMA is current per its own branding but no machinery-of-government order was found confirming the move from PMO/Economy. |

### 1.5 Common mix-ups, verified

- **EPF/KWSP is under the Ministry of Finance, NOT KESUMA.** Both are payroll deductions; different ministries.
- **Foreign worker levy collection is with Immigration (Ministry of Home Affairs).** JTKSM only does front-end labour-market clearance.
- **CIDB Green Card is under the Ministry of Works**, not DOSH/NIOSH.
- **Private employment agency licensing is done by JTKSM directly** under Act 246, not by a separate body. Requires 51%+ Malaysian ownership, "Agensi Pekerjaan" in the company name. Unlicensed operation: fine to RM200,000 and/or 3 years.

---

## Part 2: Gig Workers Act 2025 (Act 872), the core finding

### 2.1 Status and dates (CONFIRMED)

| Event | Date |
|---|---|
| Royal Assent | 16/12/2025 |
| Gazetted | 31/12/2025 |
| **In force** | **31/03/2026** |
| Subsidiary regulations made | 28/03/2026, in force 31/03/2026 |
| MPGiG members appointed (26) | effective 01/04/2026 |
| MPGiG first meeting | 03/04/2026 |

**No phased rollout, no transition period.** s.1(2) permitted different commencement dates for different provisions; the Minister did not use it. s.4 saved existing service agreements but immediately subjected them to the Act; s.5 voids any less-favourable term.

Four regulations, all P.U.(A) 2026, signed by Minister Ramanan: 143 (Social Security), 144 (Tribunal), 145 (Compounding), 146 (Conciliation).

**The moratorium:** PERKESO/the Minister gave platforms an informal **3 to 6 month window** to complete technical integration, measured from 31/03/2026. So it lapsed somewhere between 30/06/2026 and 30/09/2026. It is **administrative, not statutory**, it appears nowhere in the Act and creates no legal defence.

Primary sources:
- Act 872 text: https://www.mohr.gov.my/aktapekerjagig2025/assets/documents/Act%20872.pdf
- Official 127-question FAQ: https://www.mohr.gov.my/aktapekerjagig2025/assets/documents/faq.pdf
- KESUMA commencement release: https://www.mohr.gov.my/pdf/2026/KSM.%20100-2-1-1%20JLD%205_72_31032026.pdf
- P.U.(A) 143/2026: https://www.mohr.gov.my/aktapekerjagig2025/assets/documents/PUA143_2026%20-%20PERATURAN%20PEKERJA%20GIG%20(KESELAMATAN%20SOSIAL).pdf

### 2.2 Coverage, is a tutoring marketplace captured?

The definition chain in s.2:

> **"platform provider"** means any digital intermediary system provider who connects the service by a gig worker to a service user

> **"gig worker"** means an individual who (a) is a citizen or PR of Malaysia; (b) enters into a service agreement with a contracting entity for the performance of **(i) any service with any contracting entity who is a platform provider**; or (ii) any service as specified in the Schedule with any contracting entity who is not a platform provider; and (c) receives earnings

The Schedule's nine services (acting, film, music, aesthetics, translation, journalism, pre/post-natal care, palliative/elderly care, photography/videography) **only limit non-platform contracting entities**. Limb (b)(i) says *any service*. Tutoring does not need to be listed.

FAQ Q7 confirms: covers "semua pekerja gig yang memberi perkhidmatan melalui sistem pengantara digital yang disediakan oleh penyedia platform".

**No size, revenue or headcount threshold.** Only escape is s.111 discretionary ministerial exemption, none published.

**Qualifications:**
- Citizenship gate: only Malaysian citizens and PRs are gig workers (FAQ Q9). Foreign tutors are outside.
- Gig workers are **not employees**, Federal Court, *Loh Guet Ching v Menteri Sumber Manusia* (2024), cited FAQ Q13. So no EPF, Employment Act or EIS obligations follow.

**THE OPEN QUESTION:** "contracting entity" means a platform provider who *engages and enters into a service agreement* with the gig worker. If tutors contract only with parents and the platform is a pure introducer taking a listing fee, there is an argument it falls outside. But "service agreement" includes oral and **implied** agreements, and the platform processes tutor payments. **Needs a written legal opinion.**

**Strongest evidence for capture:** **Kiddocare**, a childcare/caregiving marketplace structurally near-identical to a tutoring marketplace, is on PERKESO's list of platforms that submitted worker data.

### 2.3 Platform obligations, section by section (CONFIRMED from Act text)

| Section | Obligation |
|---|---|
| **s.3** | Written service agreement specifying parties, period, services, obligations of both parties, rate and details of earnings, payment method, benefits/tips. Oral and implied count, but prescribed terms must be present. s.8(3) voids any waiver of worker rights. |
| **s.8(2)** | Disclose automated monitoring systems and their consequences; disclose automated decision-making used for assignment and working conditions; **provide a non-automated review mechanism**. Closest thing Malaysia has to EU platform-work algorithm rules. |
| **s.11** | Payment as agreed; where the agreement is silent, **within 7 days** of service completion. |
| **s.12** | Deductions capped at **50% of earnings** in any earnings period. **The DG determination expressly lists "fi pengurusan"** (fees for providing the app/booking system, connecting customers, operations management) as a permitted deduction, so platform commission is inside the cap. Exceeding 50% needs prior written DG approval via a **paper form filed at a district labour office**. |
| **s.13** | Earnings slips on request **within 3 days**, in DG-prescribed form (JTK GIG S13-1/2026), 8 mandatory field groups including bank/payment instrument details, itemised deductions, every advance, payment method, earnings period and dates. |
| **s.14** | Deactivation: suspend max 14 days to hold inquiry; **written notice**; **right to be heard** before terminating or extending; if no grounds found, reactivate **and pay 50% of average daily earnings** for the suspension period computed from actual service days in the preceding 30 days (worked example FAQ Q42); if grounds found, may terminate or extend by max 7 further days then must reactivate; **written explanation** either way. |
| **s.17** | Internal grievance mechanism in the service agreement; disputes resolved **within 30 days**. Deactivation disputes excluded, they escalate to the Conciliator (Industrial Relations Dept) then the Tribunal. |
| **s.82(b)** | **Workers must be able to see their deductions inside the platform's own app.** UI and ledger requirement. |
| **s.83(a)-(d)** | Submit worker information to PERKESO; ensure each worker registered under Act 789; **deduct 1.25% of earnings per transaction** (P.U.(A) 143/2026 reg.2); remit. |
| **s.83(e)-(f)** | Notify worker to top up if monthly total falls below plan minimum; notify worker to select a plan if it exceeds minimum, **within 3 days** of PERKESO notification (reg.3). |
| **s.83(g)** | **"provide a mechanism in his digital intermediary system that can connect with the Organization's system"**, a literal statutory API integration mandate. No exemption, no small-operator carve-out. |
| **s.103 (Part IX)** | OSH: risk assessments, safe equipment, information/instruction/training/supervision, emergency procedures, **accident and occupational-disease reporting to DOSH**. |

**Reporting to SEGiM: none.** ISEAS flags this as a deliberate gap, the Act "does not mandate requirements on contracting entities to stringently maintain its database and report to a designated public authority".

### 2.4 Penalties (CONFIRMED from Act text)

| Provision | Offence | Penalty |
|---|---|---|
| **s.108** (general) | Any contravention with no express penalty. **Catch-all covering s.3 service agreements, s.11 late payment, s.12 unlawful deductions, s.13 earnings slips, all s.14(10) deactivation breaches, all s.103(2) OSH breaches** | **RM50,000 and/or 2 years** |
| s.45(1) | Failure to comply with Tribunal award | RM50,000 / 2 years |
| s.45(2) | Continuing offence after conviction | + up to **RM500 per day** |
| **s.86** | Failure to pay contributions/deductions; deducting a contribution not determined by PERKESO; failing to submit statements/records; false records; obstructing an Inspector; any Part VIII contravention | **RM10,000 / 2 years** |
| s.85 | False statement to cause a contribution or benefit payment | RM10,000 / 2 years |
| s.104(2) | Gig worker fails to follow OSH measures | RM2,000 / 3 months |
| s.87 | On conviction under s.86(a)/(b), court **shall** order payment of all arrears **plus interest** | Restitution on top |
| **s.109** | **Directors, managers, secretaries, officers, partners, sole proprietors personally liable** for body-corporate offences unless they prove due diligence | Personal exposure |
| ss.75, 90, 102 | Compounding by JTK / PERKESO / DOSH with written PP consent | Max 50% of maximum fine |
| s.107 | No prosecution without written consent of the Public Prosecutor | Procedural gate |

Each missed s.14 notice, reinstatement, right-to-be-heard and written explanation is a **separately chargeable RM50,000 offence**.

### 2.5 Contribution mechanics (CONFIRMED, FAQ Q119-127)

**Rate: 1.25% of each transaction, deducted from the gig worker's earnings only.**

FAQ Q127 is explicit that platforms bear no contribution cost:
> "Tiada apa-apa tambahan kos yang dikenakan kepada penyedia platform memandangkan potongan caruman perlindungan keselamatan sosial dibuat daripada pendapatan pekerja gig sahaja. Malah kos integrasi juga ditanggung oleh PERKESO **tertakluk kepada kesediaan teknikal sistem penyedia platform dan kewujudan fungsi teras yang diperlukan untuk menyokong integrasi di dalam sistem penyedia platform**."

**That caveat is the commercial opening.** Government funds its side of integration only if the platform is already technically ready and already has "the core functions required to support integration". Platforms lacking per-transaction deduction logic, a contribution ledger, a worker registry, earnings-slip generation or a compliant deactivation workflow must build it themselves at their own cost.

**Act 789 plans:**

| Plan | Insured monthly earnings (RM) | Monthly contribution (RM) | Annual (RM) |
|---|---|---|---|
| 1 | 1,050 | 13.10 | 157.20 |
| 2 | 1,550 | 19.40 | 232.80 |
| 3 | 2,950 | 36.90 | 442.80 |
| 4 | 3,950 | 49.40 | 592.80 |

Multi-platform workers get deducted by **every** platform on actual earnings (FAQ Q124), so platforms must handle cross-platform reconciliation they cannot see. If the monthly total falls short of the plan minimum, **the worker pays the shortfall themselves**.

Note: SOCSO membership was already compulsory for **e-hailing from Nov 2018** and **p-hailing from Oct 2021**. The Act's novelty is the automatic collection mechanism, not the mandate.

**Platform co-contribution of RM1-3 per active day is a PROPOSAL, not law**, from Esther Chua (Angsana Health), Jose Rizal (GEM) and Dr Khor Swee Kheng in The Edge. No legal force.

### 2.6 SEGiM does not legally exist under Act 872 (CONFIRMED)

The word "Commission"/"Suruhanjaya" **does not appear as a body anywhere in Act 872**. The Act's institutional architecture is **Part V Gig Workers Tribunal** and **Part VI Consultative Council (ss.46-68)**.

ISEAS Perspective 2026/48 (07/07/2026) is blunt: *"the current rhetoric ... misleadingly describes the GWA as having instituted a 'gig economy commission' (SEGIM). Malaysia's government has to abide by the law, which has established a leaner consultative council."* The MoHR-UM report had recommended a federal commission at a proposed initial budget of RM100 million; not adopted, ISEAS suggests, "due to the heavy fiscal outlays and potential political co-optation."

- Dec 2023: shelved by then-minister Sivakumar as duplicative
- 05-06/03/2026: Cabinet approved **in principle**, announced by DPM Zahid Hamidi
- 31/03/2026: KESUMA's own commencement release still uses future tense ("penubuhan SEGiM ... **akan** memastikan")
- Still not operational as of May 2026
- **DNS: segim.gov.my, www.segim.gov.my, segim.mohr.gov.my all NXDOMAIN**
- **Zero occurrences** of "SEGiM" or "Suruhanjaya Ekonomi Gig" in the Budget 2026 speech or Federal Expenditure Estimates 2026

**Enforcement actually splits three ways:** JTK/Labour Dept (Part VII, ss.69-77), PERKESO (Part VIII, ss.78-94), JKKP/DOSH (Part IX, ss.95-106).

### 2.7 MPGiG, the live regulatory risk

The Consultative Council is the body that actually exists. 26 members (7 government, 6 platform providers, 6 worker representatives, 5 academics), chaired by KESUMA, first met 01/04/2026.

**Its "Fair Compensation Structure for Gig Workers" study was due September 2026.** Recommendations become a **gazetted Ministerial order**; non-compliance carries **up to 2 years' imprisonment and/or RM50,000**. Minimum earnings rates are its first agenda item.

For a marketplace already constrained by the s.12 50% deduction cap, a mandated earnings floor hits unit economics directly.

Source: https://www.nst.com.my/news/nation/2026/07/1483772/study-gig-workers-income-rates-expected-september

### 2.8 The one government system actually built

**eADUAN GIG** (https://eaduan-gig.mohr.gov.my/), live since 01/04/2026, is a **re-badge**: page title "eAduan - Sistem Pengurusan Aduan JTKSM", cookies scoped to `www.eppax.gov.my`, running **Apache 2.4.6 on CentOS with Tomcat**. Complainant self-registration only, no operator module. Target 21 working days.

**KESUMA satisfied the Act's complaint-channel requirement by extending a legacy system rather than procuring a new one.** This is the best available predictor of how the ministry handles future digital requirements.

### 2.9 Compliance status and market size

| Date | Figure | Source |
|---|---|---|
| 05/08/2025 | 821,456 self-employed contributors under Act 789 across 20 sectors (p-hailing 133,481, e-hailing 189,450) | MOHR FAQ Q1(b) |
| 05/02/2026 | "Nearly 870,000" self-employed covered | NST |
| Mar-Apr 2026 | **<1% of gig platforms pre-registered; only 2 fully API-compliant** | My Mobility Vision letter, NST 25/04/2026 |
| 24-25/04/2026 | **~2% of ~1.2m gig workers onboarded**, despite PERKESO's infrastructure being "fully ready" | NST, Sinar Harian |
| 11-12/05/2026 | **14 platforms engaged, 7 submitted data, 1 (FastGig) fully integrated** | NST, quoting PERKESO CEO Datuk Seri Dr Mohammed Azman Aziz Mohamed |
| 04/07/2026 | PERKESO "actively collaborating", **no updated numbers released** | FMT |

The seven that submitted: **AirAsia Ride, Kiddocare, Eternal Meteor (GoGet), ShopeeFood Malaysia, Troopers Innovation, Fastgig, Delivery Hero Malaysia (foodpanda)**.

**Grab, the largest operator, was NOT among them.** Grab has since committed RM10m+ via its Gig Hub, building in-house.

**No prosecution, compound or enforcement action under Act 872 had been reported as of 31/07/2026.**

### 2.10 Industry reaction

**Pushing FOR harder enforcement:** Malaysian E-hailing Coalition / Gabungan eHailing Malaysia (GEM), chief activist **Masrizal Mahidin**: *"There is no excuse for platform providers to delay ... Any excuses related to technical constraints can no longer be used as a justification to delay."* Cites s.82 and s.83, demands "stricter and more punitive enforcement."

**Asking for phased rollout:** My Mobility Vision (MMV), founder **Wan Agyl Wan Hassan**. Their NST letter (25/04/2026) is the best pain document: PERKESO API documentation v2.1 not available, platforms told to wait; only 2 platforms fully API-compliant; no SOP for data exchange across API/Postman/Excel formats; duplicate-deduction risk for workers with concurrent full-time employment. MMV notes the 3-6 month window is *"administrative rather than statutory"*.

**Academic criticism:** Ong Tze Chin (UM Law), FMT 06/07/2026, the 1.25% is *"stripped from a gig worker's earnings"* with no employer matching, characterising it as legalising a wage deduction.

**Platform silence:** Grab Malaysia and AirAsia Ride both **declined to comment** for The Star's 11/07/2026 feature. No public statement found from foodpanda, Lalamove, Maxim, InDrive, ShopeeFood, Ninja Van, J&T, Flash Express, Pos Laju, Teleport, MyCar, EzCab, Riding Pink, Bungkusit, DeliverEat, Borzo or ServisHero on compliance cost or engineering.

The Edge quantifies it: smaller platforms like **GoGet need 3-6 months** to integrate, and an industry source says *"Larger platform players have the resources but the smaller ones will not be able to do it and could die out."*

### 2.11 The compliance vendor market: near-total white space

**Software vendors: nobody.** Kakitangan, Swingvy, Talenox, PayrollPanda, BrioHR, Employment Hero, Darwinbox, Info-Tech, HR2eazy, Times Software all have **zero Act 872 product**. Kakitangan's own 2026 Malaysia Payroll & HR Compliance Guide does not mention gig workers, Act 872 or platform providers at all. Global EOR players (Deel, Remote, Multiplier, Papaya, Rippling) have generic Malaysia guides only. What exists is content marketing without product (Omni HR, Byte HR, AJobThing).

**PERKESO publishes no public API or developer documentation.** Probes of gig.perkeso.gov.my, api.perkeso.gov.my and developer.perkeso.gov.my: **none resolve**. Integration is bilateral and bespoke, which structurally favours an intermediary.

**Law firms: ~10 publishing, advisory only.** Skrine leads with four alerts. Also LHAG, Shearn Delamore, Rahmat Lim, Donovan & Ho, Chooi & Company, LAW Partnership, DFDL, HSF Kramer.

**Big 4: completely absent.** No PwC, Deloitte, EY or KPMG Malaysia publication in either language. Sole exception: Vialto Partners (ex-PwC global mobility), advisory only, explicitly not systems.

**Paid training exists:** MEF Academy RM1,300/person, Malaysian Export Academy RM972/person, both HRD Corp claimable, **neither covering technical integration**.

### 2.12 The e-Invoice precedent (the right analogue)

LHDN's MyInvois mandate produced ~247 companies applying within ~15 months, and 58 MDEC-accredited Peppol service providers by May 2026.

Critically, **LHDN required no vendor licensing** (FAQ Q118: "There is no registration requirement at this juncture"); accreditation was optional and became purely a marketing asset.

Adoption: 7,400 taxpayers / 58m invoices (Oct 2024) → **204,928 taxpayers / >1 billion invoices** (March 2026).

Pricing settled at **RM50 to RM200/month for SMEs**, RM700 to RM2,500 for enterprise. About 24 of 32 solutions were existing accounting products with a bolt-on module. A services layer of **157+ accounting firms** formed faster than the software layer.

**And it slipped repeatedly on cost.** Anwar, January 2026: "the government has agreed to extend the penalty-free transition period for e-invoicing for another year, **as many have said the cost is too high**."

**Key difference favouring a standalone gig product:** e-Invoice vendors bolted modules onto existing ERPs. Gig platforms are bespoke apps with no incumbent system to bolt onto.

**Cleaner services analogue:** the PDPA 2024 DPO mandate (mandatory from 01/06/2025, outsourced DPOs expressly permitted) produced a pure-play vendor, dpomalaysia.my, selling outsourced-DPO retainers.

---

## Part 3: HRD Corp

### 3.1 Levy economics (CONFIRMED, Financial Report 2025 Note 14 and Note 21)

| Metric | 2025 | 2024 |
|---|---|---|
| **Levy collected** | **RM2,534,924,723** | RM2,327,459,807 |
| **Training grant disbursed** | **RM2,443,579,510** | RM1,986,710,269 |
| Fund balance at 1 January | RM3,849,612,017 | RM3,564,678,878 |
| Fee income from training providers | RM12,674,210 | RM17,873,021 |
| Unutilised levy written back | RM16,154,161 | RM42,975,688 |

Levy trend: RM474.86m (2020) → RM847.97m (2021, after March 2021 base widening) → RM1.81bn (2022) → RM2.13bn (2023) → RM2.30bn (2024) → RM2.53bn (2025).

**90,000+ registered employers** covering 4.59m employees (2023: 89,912). **Only 47% of registered employers made at least one training claim in 2025.**

HRD Corp's liquid assets (cash + investment portfolio) exceed RM4.3bn, drawing Auditor-General and press scrutiny for behaving more like an investment institution than a disbursement body.

### 3.2 Becoming a provider (CONFIRMED)

- **Registration: RM1,000 HQ + RM500 per branch, one-year validity.** Renewal RM1,000/year (apply 3 months before, or within 6 months after, expiry). Address change RM1,000; name change RM1,000.
  - Note: the widely-cited "RM200 renewal every 3 years, RM50 per course" figure is **wrong**.
- **Requirements:** at least 1 full-time trainer and 1 support staff, permanent office address, SSM/ROS registration, **business nature must specify "training services or consulting"** (most common rejection cause), signed Integrity Pledge, and a **Master Service Agreement digitally stamped at LHDN** (https://stamps.hasil.gov.my), a cross-portal step.
- **Course registration: no fee.** 3-year validity.
- **Trainer requirement:** TTT (Train the Trainer) or TTT Exemption certificate. From **01/01/2025**, all HRD Corp certified active trainers must hold **Accreditation status** under HRD-TDF (Employer's Circular 6/2024, 13/12/2024). Two routes: by Assessment (certified after 01/01/2021) or by Activity (before). TTT cost REPORTED at RM2,500-4,500/trainer; official pages 404.
  - Circular 6/2024 records that the grace period was extended to 31/12/2024 "based on request from training community", official acknowledgement of friction spanning four years.
- **Star rating: DISCONTINUED in 2019** (PSMB Star Rating introduced 2016, reviewed 2018, formally discontinued by Training Provider Circular 1/2019). Nothing replaced it.
- **No public provider directory.** Customer acquisition is direct sales only.
- **7,530 active providers (2024).** That is the real competitor count. Entry is cheap, which is exactly why.
- **Two TTT-certified trainers are the hard floor to register a single course.** TTT is 5 days at **RM2,684/person incl. 8% SST** (confirmed independently by MIM and GEM Consultancy, matching HRD Corp's own figure). TTT exemption application RM300; assessment fee RM150; **accreditation RM60, renewal RM60 every 3 years**. Three to four trainers is the practical business minimum, so budget **RM8,000-11,000** to stand up a credible bench.
- **Certified is not enough.** As at end-2024 there were **13,123 registered certified trainers but only 9,492 accredited**. The ladder is TTT Certified, then Accredited, and only the second lets you bill.
- Pre-approval **may include a site visit to your premises**. Trainer records live at trainers.hrdcorp.gov.my, a system separate from e-TRiS.
- **Attendance floor: trainees must complete at least 75% of total training hours** or the claim is prorated.
- **Training material you develop yourself is NOT separately claimable.** Only licensed material from a principal is, with pre-approval, valid 2 years. Your own IP must be priced into the course fee.
- **IEC review is 10 working days**, with 30 days to respond to queries. **If the committee never acknowledges it, the course silently proceeds as a General Course** and you lose the uncapped pricing without being told.

Published SLA (https://hrdcorp.gov.my/wp-content/uploads/2026/07/Training-Provider_Basic-flow.pdf):
- Training Provider approval: 2 working days
- Programme registration and approval: 3 working days
- Claims processing: 3-5 working days

### 3.3 The Allowable Cost Matrix, the pricing lever

Five segments: General Courses, Focus Area, Industry Specific, Professional Certification, Internal Trainer Allowance.

**General Courses, CAPPED:**
- In-house: **max RM10,500/day/group** (full day = min 7 training hours); RM6,000/half day (max 4 hours). Min 2 trainees face-to-face, 1 for Remote Online Training. Prorated below 5 trainees.
- Local public: **max RM1,750/pax/day**; RM1,000/pax/half day
- E-learning: **max RM875/day/pax (RM125/hour/pax)**. Remote Online Training is now treated the same as face-to-face, not as e-learning.
- Overseas public: as charged, assistance capped at 50%

**Focus Area / Industry Specific / Professional Certification, NO CEILING.** All three are "**as per charged**", per pax, prorated by attendance completion.

**The nine Focus Areas:** Industry 4.0; Green technology and renewable energy; Fintech; Smart construction; Smart farming; Aerospace; Blockchain; **Micro-credential**; **Future technology**.

Focus Area programmes are "designed around nine strategic pillars, **excluding introductory courses, foundation programmes, seminars and conferences**. The integration of technology is a core component."

**Approval route:** Training Provider submits a Course Verification Form → Processing Officer screens → **Industry Expert Committee (IEC)** → recommends approval/rejection/enhancement → Acknowledgement Letter attached at course registration.

**For MicroCredential Focus Area, the Training Provider must obtain MQA endorsement.** Unlike JPK, MQA is not blocked by the absence of an AI NOSS. MQA's *Guidelines to Good Practices: Micro-credentials* (Aug 2020) offers voluntary quality assessment to "other providers", not just HEPs.

**AI is not its own Focus Area**, it must be positioned under Industry 4.0 or Future Technology. **This classification is INFERRED (from MDEC pricing above the General ceiling), not confirmed in writing. Verify before pricing above RM1,750/pax/day.**

Other allowances: trainee allowance max RM250/pax/day (<100km) or RM500/pax/day (>=100km incl. accommodation); meal allowance max RM100/pax/day; internal trainer allowance max RM1,400/day/group; overseas trainer daily allowance max RM500/pax/day; consumables RM100/group without quotation. SST claimable within the cap.

### 3.4 Where demand actually is

**AI/digital is a much smaller slice than the national conversation suggests.** Two independent official sources: Digitalisation + Industry 4.0 was **3.2% of 2024 training places**; digital economy/ICT was **103,000 of 2.8m places in 2025 (3.7%)**. **Management, leadership and safety take 40%.** ESG has no category. e-Invoice has none.

**Training places by skill area, 2024** (Annual Report 2024 Table 3, total 2,549,188 approved places; abridged from 24 categories):

| Skill area | Places | Share |
|---|---|---|
| Management and leadership | 630,523 | 24.73% |
| Safety | 404,046 | 15.85% |
| Operation management | 263,861 | 10.35% |
| Productivity | 223,807 | 8.78% |
| Finance and accounting | 186,104 | 7.30% |
| Quality | 183,001 | 7.18% |
| Sales, marketing, customer service, retail | 172,555 | 6.77% |
| **Digitalisation** | **68,249** | **2.68%** |
| Legal and law | 61,711 | 2.42% |
| Engineering | 61,234 | 2.40% |
| Scientific, technical, statistics | 27,274 | 1.07% |
| Sustainability (the ESG proxy) | 24,251 | 0.96% |
| Security | 21,714 | 0.85% |
| **Industry 4.0** | **14,409** | **0.56%** |

**Delivery mode:** in-house was **1,842,561 of 2,549,188 places (72%)**; public courses 364,312 (14%); remote online and e-learning made up most of the rest. **The money is in bespoke in-house delivery**, which is also the mode with worse per-day economics unless you clear Focus Area classification.

**Delivery constraints:** max 50 trainees/group for soft skills, **25 for technical (AI is technical)**. Min 2 in-house, 1 remote. Below 5 trainees the fee is prorated (a 3-person session pays 3/5 of the cap). **Public courses are funded for a maximum of 9 trainees per employer.** Sessions must run at least 4 hours to claim at all.

**Employer utilisation, 2024 (the wedge):**

| Employer size | Employers | Levy paid | Assistance approved | Utilisation |
|---|---|---|---|---|
| Large | 8,032 | RM1,155.39m | RM1,325.80m | **114%** |
| Medium | 16,162 | RM452.96m | RM405.92m | 90% |
| **Small** | **73,890** | RM719.11m | RM543.43m | **76%** |
| Total | 98,084 | RM2,327.46m | RM2,275.15m | |

**Small employers are the underserved segment and the least likely to have an internal L&D function.** Utilisation above 100% reflects drawdown of levy accumulated in prior years.

**Reconciliation note on the 4% fee:** audited 2025 accounts show RM69.33m of service fee income against RM2.44bn disbursed, which looks like 2.8%. The gap is the reimbursement schemes, where employers are paid directly and no provider service fee applies.

### 3.5 The claim process and its friction

**Deadline: 6 months** after training completion (effective 01/08/2019, per the official Process Flow PDF). Public guidance is contradictory, third-party guides variously say 30 days, 60 days and 6 months. **6 months is correct.**

**Claim documents:** Form JD14 (claim declaration, must be completed by the training provider, submitted to employer for declaration, **approvable only at MANAGER level or above**, declaration date must be on or after training completion, carries criminal warning under the PSMB Act 2001 of RM20,000 fine / 2 years); Form T3 (attendance, daily wet signatures for physical training, waived for remote but full details still required, NRIC and citizenship mandatory); Invoice (must be addressed to HRD Corp/PSMB, state employer name, programme title and dates, carry the provider's SST number); Generated Attendance Report for ROT (retrieved from the platform, showing name, date, log-in/log-out or duration, **signed by BOTH provider and employer with name, designation, company stamp and date**).

**Note: "Form JD3" could not be confirmed to exist.** Possible conflation with a separate "Form 3 Schedule of Arrears" relating to levy arrears.

**The structural trap (from HRD Corp's own process diagram):**
> "Training Providers must ensure that the trainee attendance is accurate, as **employers cannot amend it once**."
> "Claims must be submitted by Training Providers **before** the employers' submission of claims"

The provider enters attendance; it locks; the employer is downstream and powerless to correct it; and the employer cannot start their claim until the provider files theirs. A single provider-side NRIC typo becomes an unfixable defect for the employer.

**4% service fee** deducted from every provider claim (effective 01/02/2021, exclusive of SST). Worked example: claim RM12,000 → fee RM480 → net RM11,520.

**Levy forfeiture:** unutilised levy forfeited after **2 years** (revised from 5 years, effective 01/01/2020), with a **RM10,000 floor**. Formula: Levy Balance 2 years ago − Claims within 2 years − Forfeiture + Levy Contributed within 2 years. Worked example: RM100,000 balance, zero claims, RM20,000 contributed → **RM90,000 forfeited**. Same balance with a **single RM5,000 claim** → **RM0 forfeited**.

**15% MADANI deduction** (Employer's Circular 5/2024, 25/11/2024): employers with unused levy of RM50,000+ AND utilisation below 50% face a **15% deduction**, effective 01/01/2025, commencing 01/03/2025. No opt-out, no objection mechanism.

**April 2026 mass course deactivation:** courses not registered in 2025/2026, without a 2025/2026 grant approval, and not Professional Certification were reclassified **inactive**. No stated transition period.

**REPORTED (could not verify on hrdcorp.gov.my, the PDF 404s): Employer's Circular 2/2026**, issued 07/05/2026, effective 15/06/2026: 14-day mandatory wait after approval before training may commence; 90-day outer window (replacing 6 months); one query only with 5 calendar days to respond; **no amendments after approval**; **no appeals**; confirmed dates mandatory; physical verification of face-to-face and ROT sessions. Four independent consultancies agree on issue date, effective date and fine detail, but the official circular index shows no 2/2026 and the referenced PDF returns 404.

Note the 2026 relaxation: public training may commence 3 calendar days after approval **effective 15/06/2026 to 31/12/2026 only**, reverting to 14 days from 01/01/2027.

### 3.6 e-TRiS: no API, and a failed replacement

**There is NO public e-TRiS API. CONFIRMED by multiple probes:**
- `developer` / `api` / `apigateway` / `docs` / `openapi` `.hrdcorp.gov.my` → all NXDOMAIN
- `devportal.hrdcorp.gov.my` resolves to 137.59.110.22 but **times out** on 80/443, internal only
- hrdcorp.gov.my sitemap (117 pages): zero API/developer/integration pages
- Support Centre KB: 12 categories, none developer-facing
- **The string "API" does not appear once in the entire HRD Corp Annual Report 2024** (text-extracted and grepped)

An **internal** API gateway exists: the attendance portal links to `https://apigatewayprod.hrdcorp.gov.my/login/azure`, which DNS-resolves to an **Alibaba Cloud API Gateway** (`...ap-southeast-3.alicloudapi.com`), returns HTTP/2 404 with `server: Kaede/3.5.3.804`, and 404s on /docs, /swagger, /api-docs, /openapi.json. It serves HRD Corp's own apps via Azure SSO. Not an integration surface.

**Architecture:** e-TRiS at https://etris.hrdcorp.gov.my/DigiGov/index.jsp returns `server: Apache-Coyote/1.1`, `JSESSIONID` on path `/DigiGov`, `charset=ISO-8859-1`, an old Tomcat COTS e-government product ("DigiGov"), fronted by an AWS ALB. The `/DIGIGOV/digigov.htm?actionFlag=...` URL signature appears identically on **Gujarat eNagar, Gujarat Investor Facilitation Portal and the Tamil Nadu Single Window Portal**. Live on the legacy `etris.hrdf.com.my` by 06/04/2019 at latest.

**Vendor: could not confirm.** A search summary associated eNagar with TCS, and TCS markets a DigiGOV product family, but the attribution could not be independently retrieved and grepping live e-TRiS HTML found zero occurrences of "TCS" or "Tata". **Do not state TCS built e-TRiS.**

**Bulk operations are Excel only.** Bulk trainee upload exists in RPL grant flows ("Template to Upload Trainee Details" → Microsoft Excel → "Upload Trainee Details Excel"). Bulk attendance update exists (download-modify-upload round trip). **No bulk levy submission**, the words upload, excel, template, batch, bulk, csv appear **zero times** in the official Levy User Guide. **No CSV, no XML, no JSON anywhere.**

**The attendance evidence chain terminates in a human-signed, company-stamped PDF.** An API would make the wet signature meaningless. This is the hard architectural stop on any "auto-submit attendance" product.

**The RM14m New Core System failure.** HRD Corp's own press statement (06/02/2026) states the NCS was *"a procurement amounting to RM14 million and has been delayed for more than four (4) years following three (3) unsuccessful User Acceptance Tests (UATs)."* Three top management suspended, three more on 21/02/2026 (six total). CEO Shamir Aziz called the suspensions "procedural steps to guarantee the independence of an ongoing internal probe". Corroborated by NST, BusinessToday, The Sun, FMT.

**Notable tension:** the 2024 Annual Report reported the NCS at **93% complete, exceeding its Ministry KPI at 116% achievement**.

**Vendor: not named in any source.**

**UX friction, from primary sources:**
- **Fractional-day e-learning input** (Circular 3/2024, p.4): to claim e-learning, the user keys a decimal "day" value into e-TRiS: 1hr=0.1, 2hr=0.2, 3hr=0.3, **4hr=0.5, 5hr=0.7, 6hr=0.8**, 7hr=1.0. Non-linear, non-obvious, requires a PDF lookup table to fill a form field.
- Grant application is ~16 discrete steps through "folders" and "sub-folders", a file-system metaphor.
- No published file size limit, format whitelist, session timeout, browser compatibility matrix, mobile support, outage log or status page. The Support Centre has a category literally named "Technical Support E-Tris" **containing no troubleshooting articles**.
- e-Disbursement bank registration is a separate first-claim-only setup step; "Missing e-Disbursement details" is a named delay cause.
- Charter promises **7 working days** for claim reimbursement; three independent providers report **14-30 days**. Charter promises 24 hours for grant applications; providers report 3-10 working days. Every SLA clock only starts "upon receiving the complete application form", which makes the charter unfalsifiable from outside.

**A dedicated Facebook group, "eTRiS HRD Corp Users (Malaysia)"**, exists to "Discuss common issues, errors, and system updates" (login-walled, contents unread).

### 3.7 HRD Corp technology procurement

**HRD Corp does NOT use ePerolehan.** It runs its own portal at https://hrdcorp.gov.my/procurement/, register via HRD Corp Supplier Portal → purchase RFP document online (non-refundable) → attend briefing → submit via the Accounting and Procurement System (APS). Reference format `PSMB (RFP) N/YYYY`.

MyProcurement records procurement "bagi Agensi Kerajaan yang menggunakan peruntukan Kerajaan Persekutuan". PSMB is levy-funded, so it sits outside.

| Ref | Title | Doc price | Indicative value | Dates |
|---|---|---|---|---|
| **PSMB (RFP) 2/2026** | **HRD Corp Claimable Courses System (HCCS)**, development, configuration, installation, testing, commissioning, training, maintenance | RM100 | not published | Purchase 27/07-03/08/2026; briefing 04/08/2026 11:00; **closes 24/08/2026 12:00** |
| PSMB (RFP) 3/2025 | Document Management System incl. migration | RM1,500 | **RM4,500,000** | Closed 18/08/2025 |
| PSMB (RFP) 2/2025 | Integrated Security Management System | RM1,500 | **RM5,000,000** | Closed 13/08/2025 |
| PSMB (RFP) 8/2024 | Competency Mapping and Analytics Platforms | RM500 | not published | Closed 14/01/2025 |
| PSMB (RFP) 7/2024 | Data Management and Advanced Analytics | RM300 | not published | Closed 03/12/2024 |
| PSMB (RFP) 2/2024 | Network Monitoring System (retender) | RM100 | not published | Closed 04/07/2024 |

**Award results / winning vendors: not published.** The portal publishes invitations only.

**HYPOTHESIS (no source states this):** PSMB (RFP) 2/2026 for HCCS could be a re-procurement arising from the troubled New Core System programme.

**ICT on the balance sheet:**

| Year | ICT System additions | Gross cost at year-end | Depreciation | Carrying amount |
|---|---|---|---|---|
| 2023 | RM11,088,973 | RM93,193,517 | RM10,185,675 |, |
| 2024 | RM1,214,241 | RM94,407,758 | RM11,524,932 | RM41,009,549 |
| 2025 | RM11,665,827 | **RM106,073,585** | RM11,789,134 | RM40,886,242 |

ICT System is ~55% of HRD Corp's RM192.6m PP&E gross cost at end-2025.

**Do not misread:** AR2024's "Digitalisation, RM76,954,771" is **levy-funded training grant disbursement** to employers for digitalisation courses, not HRD Corp's own IT spend.

**Confirmed vendor relationships:** SAP (won the SAP Customer Excellence Award for Southeast Asia) and Alibaba Cloud (Pioneer Award for Big Data in Digital Government; corroborated by the `acw_tc` cookie on e-LATiH). CTO: Ts. Ragunathan Gopalakrishnan.

### 3.8 e-LATiH is a rebranded commercial script (CONFIRMED)

https://elatih.hrdcorp.gov.my/ is **Infix LMS**, a commercial Envato/CodeCanyon Laravel script. Smoking gun in the localisation file:

```
"Engineer at InfixLMS":"Engineer at eLatihLMS"
"Infix CRM":"Infix CRM"   (6 occurrences)
"Keep me up to date on Infix":"Keep me up to date on Infix"
```

Plus the CodeCanyon licence-verification module ("Module Verification", "Envato Email Address", "Envato Purchase Code").

Stack: Laravel (`XSRF-TOKEN`, `e_latih_malaysias_premier_learning_hub_session`), rebranded theme at `/public/frontend/elatihlmstheme/` served from `elatihcp.hrdcorp.gov.my`, Alibaba Cloud, **iPay88** payments, **BigBlueButton** live classes, Vimeo/YouTube, Site24x7 RUM, hCaptcha/reCAPTCHA.

**Definitively NOT** Moodle, Totara, Docebo, EdApp or Cornerstone.

**Pukunui Malaysia: RULED OUT as builder**, their page positions e-LATiH as *inspiration*, not their work. **OpenLearning: could not confirm**, and the Infix/Laravel fingerprint rules them out as platform provider; most likely a content partner.

e-LATiH's own meta description claims it was "developed by Human Resource Development Corporation (HRD Corp)". 2,000+ free and 70,000+ premium courses, 160,000+ resources, 31 categories, priced free to RM580. Content partners include Accenture, AirAsia Academy, Harvard Business School Publishing; 13 partner MoUs signed 27/02/2024.

There is a formal **Content Provider (CP) programme** with a CP Portal, FAQ and briefing sessions. **Revenue-share terms not disclosed.**

### 3.9 Governance context

**Auditor-General's Report 2/2024 (covering 2019-2023):**
- **RM51.69 million** in Gerak Insan Gemilang grants flagged as suspicious; **3,726 individuals** received multiple training payments; **234 participants** flagged with identical names and identification numbers
- **RM205.42 million** outstanding levies as at 31/12/2023, from 21,058 employers (up from RM72.47m in 2020)
- **62 levy applications approved AFTER training completion dates**, the exact failure the 2026 14-day advance rule addresses
- RM49.38 million unrealised losses from 29 investment transactions
- RM120 million deposit irregularities on the Menara Ikhlas property purchase

**MEF was notably supportive**, President Syed Hussain Syed Husman attributed arrears to pandemic cash flow and said "I think HRD Corp has been sensitive" to SME needs. **No MEF, FMM or SME Association criticism of the claim process itself was found.**

**Aftermath:** 6 executives suspended Feb 2026, MACC investigation, independent audit, anti-corruption groups calling for a forensic probe. RM270.7m recovered per thesun.my 01/07/2026.

**Counter-narrative:** HRD Corp approved RM2.62 billion in financial assistance in 2025, up 32%, across 2.8m+ training places.

### 3.10 The 2025 policy shift

**MADANI Graduate Scheme (SGM)**, Employer's Circular 1/2025, allows employers to use levy funds for **graduate salaries** rather than exclusively training. Alwyn Lau ("Corporate training sector in crisis?", 25/08/2025) asks *"what's going to happen to the training sector for whom the HRD funds have been a critical source of revenue?"*

**Circular 1/2026 exempts registered employers in the education industries from levy payment for all of 2026.** Relevant to Sifu Edu Learning Sdn Bhd's own classification.

---

## Part 4: Other agencies' systems and procurement

### 4.1 JTKSM

**Systems:** **ePPAx** (https://www.eppax.gov.my/) is the primary system, s.60K prior approval, employer transfers, foreign domestic workers, and since Dec 2024 the mandatory online reporting that replaced paper forms PA 1/13 and PA 2/13. Modules: SiPermit, APS (private employment agency licensing with i-payment). Also **FWCMS** (module FWeApproval), **XPats Gateway**, **i-Stat**, **MyLabourHub** (DOSM-hosted), **SISPAA** complaints, and a MyGOV Android complaints app.

**FWCMS is owned and operated by Bestinet Sdn Bhd (894387H)**, CONFIRMED from the fwcms.com.my footer. A privately owned system JTKSM consumes, not a JTKSM-procured system. Not Bursa-listed.

**UNCLAIMED LEAD:** JTKSM's staff SSO resolves to **`https://intranet.jtksm.primuscore.com/saml/login`**, a commercial third-party domain hosting a government department's SAML identity provider. **Owner could not be identified.** An SSM or WHOIS lookup would name an incumbent KESUMA IT supplier.

**Who built ePPAx: NOT PUBLICLY AVAILABLE.** JTKSM/KSM copyright only.

**Could not verify existence of:** "Working for Workers"/WFW portal (candidate domains do not resolve, absent from the full nav tree), "e-Buruh".

**Live ICT procurement (July 2026), all via ePerolehan `QT26...`, no prices published:**

| Ref | Title | Closes |
|---|---|---|
| QT260000000013653 | Maintenance of Sistem Perekodan Digital (SPD) for 12 Labour Courts, 36 months | 27/07/2026 |
| QT260000000021079 | ICT hardware, mobile SPD for Mobile Labour Court, JTK Sarawak | 30/07/2026 |
| **QT260000000022169** | **ICT hardware, SPD + video conferencing, Kota Kinabalu, explicitly supporting AKTA PEKERJA GIG 2025** | 28/07/2026 |
| QT260000000022305 | Mobile Labour Court, JTK Sabah | 31/07/2026 |

### 4.2 DOSH

**DOSH publishes no tender or quotation section at all**, verified by enumerating the full nav tree in both languages, the sitemap, and the site's own search for "sebut harga" and "perolehan". Procurement runs entirely through ePerolehan.

**Systems:** **MyKKP / MySKUD** (workplace registration, renewal, accident notification), **APIS** (Ageing Plant Information System), **CIMS** (chemical management), SISPAA, staff directory, intranet.

**MyKKP technical fingerprint:** Angular + Ionic SPA, **Site24x7 RUM** (ManageEngine/Zoho, appKey 4d6f76b8fab9d8e6c77b12ca751d415f), **FingerprintJS** bot defence with `x-bni-fpc`/`x-bni-rncf` cookies, leftover base-href values `/ion_dash/` and `/ion_main/` indicating a shared multi-app Ionic codebase. **No vendor named.**

**REPORTED (could not verify, tenderpanel 403s, tenderdb 500s):** tender QT240000000034441, "Perkhidmatan Penyelenggaraan Sistem MyKKP selama 40 bulan", closing 14/01/2025, ICT codes 210102/210103/210104/210106/210107. A 40-month maintenance term implies an incumbent. **Retrieving this award record would name DOSH's systems maintainer.**

**Could not verify:** "eMall JKKP" (domain does not resolve).

### 4.3 JPK / DSD

**Procurement:** two maintained pages (Tender Offer, Quotation Offer). Live entry: *SEBUT HARGA ... PERALATAN PEJABAT (SMARTBOARD)*, No. JPK(S).400-5/6/131, codes 020201 & 020302, 22-29/04/2026, directing bidders to **www.treasury.gov.my** with physical submission to Aras 7, Blok SP4, Kompleks Setia Perkasa, Putrajaya. **No 2024-2026 JPK ICT tender found.**

**Systems: two generations of MySPIKE run in parallel.**
- **MySPIKE v1** (https://www.myspike.my/): **Yii PHP framework** on the **AdminLTE** admin template, jQuery/Bootstrap/DataTables. NOSS subscribable online since 01/07/2020.
- **MySPIKE v2** (https://myspike.tvet.gov.my/), note the migration **off dsd.gov.my onto tvet.gov.my**. Nine modules: Pengguna, NOSS, Personel (SPKM), Agensi, PPT, NDT, Statistik, Admin Pengguna, Persijilan. Related: AppSPIKE (SLaPB/SLDN), ppt.tvet.gov.my, upcoming UP_TVET Flexi. Front end built on the commercial "edufile" Bootstrap template.

MySPIKE expands as **"Sistem Pengurusan Integrasi Kemahiran Malaysia"** (per JPK's own outage notice), not "Informasi".

**Who built either version: NOT PUBLICLY AVAILABLE.**

**Could not verify:** "e-Binaan" and a standalone NOSS registry host (`noss.dsd.gov.my`), neither resolves. NOSS is a module inside MySPIKE.

**Note:** dsd.gov.my serves a broken TLS intermediate chain; automated fetchers reject it.

### 4.4 PTPK, the most transparent procurement in the ecosystem

**Runs its own e-tender system: https://smart.ptpk.gov.my/WebApp/TenderMS.aspx**

It is the **only** one of the four that publishes bid prices and winning suppliers by name.

**Open (as at 31/07/2026):** PTPK/PR/SH/07/2026, Security Posture Assessment 2026, 2 years, closes 28/07/2026 12:00.

**Awarded, with named winners:**

| Date | Ref | Title | Winner | Value |
|---|---|---|---|---|
| 09/03/2026 | PTPK/PR/SH/12/2025 | CCTV supply and installation, HQ | **EYESOFT TECHNOLOGY SDN BHD (108648-H)** | **RM248,846.00** (of 3 bids: 255,000 / 198,837.28 / 248,846) |
| 04/03/2026 | PTPK/PR/SH/01/2026 | BYD Atto 3 Ultra, Jubli Perak lucky draw | **SISMA AUTO (KL) SDN. BHD.** | **RM123,800.00** |
| 24/04/2026 | PTPK/PR/SH/16/2025 | Baju batik | **NOOR ARFA SERVICES SDN BHD** | **RM85,540.00** |

**ICT tender openings with full bid spreads:**

> **PTPK/PR/TEN/01/2025, PEROLEHAN PERISIAN PENGURUSAN KUTIPAN HUTANG PEMINJAM (DEBT COLLECTOR SOFTWARE)**, closed **05/11/2025**. **Eight bidders**, 180-day validity: RM7,988,049.88 (non-Bumi) / **RM4,119,695.44 (Bumi, lowest)** / RM4,267,030.00 (Bumi) / RM4,425,00.00 *(sic)* (non-Bumi) / RM6,269,400.00 (non-Bumi) / RM4,538,751.84 (non-Bumi) / RM4,301,141.26 (Bumi) / RM4,410,000.00 (Bumi). **Award not yet published.**

> **PTPK/PR/TEN/04/2025, PENYEWAAN PERALATAN ICT TAHUN 2025**, closed 30/10/2025. Seven bidders, 2-year term: RM1,685,256 / RM1,391,961 / RM1,685,256 / RM1,403,131 / **RM1,381,014 (lowest)** / RM1,597,776 / RM1,671,400

**PTPK also publishes indicative prices on MyProcurement** (unlike the departments):

| Ref | Title | Indicative price |
|---|---|---|
| PTPK/PR/SH/07/2026 | Security Posture Assessment, 2 years | **RM200,000** |
| PTPK/PR/SH/08/2026 | Oracle database forensic review, 6 months | **RM200,000** |
| PTPK/PR/SH/09/2026 | ICT equipment supply and rental, 3 months | **RM135,000** |
| PTPK/PR/SH/06/2026 | Network and WiFi maintenance, 3 years | **RM330,000** |

**Systems:** **e-SMART@PTPK** (https://smart.ptpk.gov.my/, ASP.NET/IIS), **Sistem Permohonan Pinjaman Kolej Online** (http://online.ptpk.gov.my:7777/ptpk/online/, **port 7777 is the Oracle Application Server default**), **MyPerkasa TVET** (footer "© 2021 BPM | PTPK", self-attributed), e-Form, e-Tender, e-Feedback, Penyata Online (PHP).

**Strong inference: PTPK's back end is Oracle**, from two independent signals (port 7777 and the Oracle forensic-review tender). The debt collector tender indicates PTPK is actively replacing its loan-recovery stack.

Loan products: conventional PLK and Islamic PLK-i, with an appointed external collection-agent panel grounded in Act 640 s.58 and s.65.

**Note:** ptpk.gov.my serves a broken TLS chain and refused direct connections; read via the Wayback Machine.

### 4.5 Audit and Parliament coverage

**LKAN** (https://lkan.audit.gov.my/) carries a distinct **"Badan Berkanun"** report category separate from Persekutuan/Negeri/Khas, the audit architecture mirrors the legal split.

**NOT FOUND:** any LKAN report specific to JTKSM, DOSH/JKKP, JPK or PTPK IT systems or procurement, in the listings reachable. The portal's keyword search returned only filter scaffolding to automated fetches. Not exhaustive.

**Parliament: NOT VERIFIED.** parlimen.gov.my serves a broken TLS chain. No parliamentary answer naming MySPIKE, MyKKP, ePPAx or PTPK system costs was retrieved. **This is the largest genuine coverage gap.**

**Bursa Malaysia:** announcement search returns HTTP 403 to automated retrieval. **No contract announcement was confirmed for any of Heitech Padu, Datasonic, Awantec/Prestariang, Silverlake, MyEG, Theta Edge, Microlink, DNeX, Censof, Iris Corp, Agmo, Revenue Group, Ramssol or Sedania with any of these four bodies.** This is **absence of retrievable evidence, not evidence of absence**, do not read it as clearing any company.

---

## Part 5: Malaysian government procurement rules

### 5.1 The rules that matter most for a product company

**PK 7.6 permits direct negotiation for software licences up to RM1,000,000** on agency board approval, where the software comes from its owner or a sole agent holding an appointment letter. **Owning the IP is the qualifying condition.** A licensed product can be bought without an open tender; a service cannot.

**PK 2.1 para 2.10(iv) makes source code and IPR arising from government development contracts the property of the Government**, with mandatory technology transfer.

**Combined:** license what you own; do not sell bespoke development.

**PK 2.1 para 2.10(iii) instructs agencies to prioritise MSC/MD-status companies for ICT procurement.** Real but soft, a directive with no scored margin, unlike the Bumiputera preference table.

### 5.2 The statutory body exemption

**Circular WP 7.5, in force 15/01/2026, grants federal statutory bodies an explicit exemption from ePerolehan.** PERKESO (speed2u.my), HRD Corp (eTRiS) and PTPK (own e-tender) each run their own portal and supplier registry.

**Register with MOF and watch ePerolehan and you will never see their tenders.** The three agencies most relevant to this dossier are exactly the three that will not appear.

### 5.3 Mechanics

- **MOF vendor registration: RM450 for 3 years, ~7 working days for ICT codes.** Runs on Arahan Perbendaharaan 166 and 184, **there is no PK circular governing MOF registration**.
- **Correct codes: 210104 = software development, 210103 = software supply. 210101 is HARDWARE.**
- MOF fee breakdown: **RM50 processing (non-refundable, paid before assessment) + RM400 registration (paid on approval) = RM450 for 3 years.** Up to 30 kod bidang held at once, free. Bumiputera status application free. Digital certificate ~RM120 (first user free for 3 years). **Minimum paid-up capital RM2,500** for ordinary kod bidang including all ICT codes.
- **Premises rules:** a residential home, SOHO, shared partition or co-working space is **permitted**. A company secretary's office, tax agent's office, virtual office, P.O. Box or mailing-box address is **not**. MOF and PKK conduct unannounced verification visits.
- **Cost stack on RM500,000:** 0.8% eP fee, 1% PROTÉGÉ, 2.5% performance bond held for the contract term plus 12 months.

**The threshold ladder (supplies and services, per PK 2.1 as amended 01/10/2024, confirmed unchanged for 2026 by PK 2.21 dated 24/02/2026, the 2026 relaxations apply to works only):**

| Band | Method | Notes |
|---|---|---|
| up to RM20,000 | Pembelian Terus | **Supplier need NOT be MOF-registered.** Agency should obtain three price offers. **The easiest possible first government invoice.** |
| RM20,000 to RM50,000 | Pembelian Terus | Supplier **must** be MOF-registered under the relevant kod bidang |
| **RM50,000 to RM100,000** | Sebut Harga | **Reserved entirely for Bumiputera-status companies. Closed to non-Bumiputera firms.** Min 5 invitees, notice ≥7 consecutive days |
| **RM100,000 to RM500,000** | Sebut Harga | **The realistic beachhead.** Open to any MOF-registered supplier under the relevant code. No CIDB, no open-tender machinery, no Bumiputera requirement. Not subject to FTA obligations. Must run fully online through eP. |
| above RM500,000 | Tender Terbuka | Open tender, publicly advertised |
| above RM50,000 | Rundingan Terus | Direct negotiation. No value ceiling but **MOF approval required in every case, at any value.** |

**Bumiputera price preference (PK 1.5 s.6.2, latest amendment in force 01/01/2025):** RM50k-100k reserved entirely; >RM100k-500k **10%**; >RM500k-1.5m 7%; >RM1.5m-5m 5%; >RM5m-10m 3%; >RM10m-15m 2.5%; >RM15m none.

Correct term is **Sijil Taraf Bumiputera (STB)**, granted by MOF after a PKK premises visit ("Sijil Akuan Bumiputera"/"SAB" are not primary-document terms). 51% tier requires 51%+ Bumiputera equity, board, key posts, employees, and financial management, **and the financial controller or finance director must be Bumiputera**, a genuine tightening new in the 2025 amendment. Status is a revocable privilege, not a right. **No ICT kod bidang is Bumiputera-reserved** (only printing, travel agency and insurance brokerage are).

**Kod bidang detail, and a real constraint:**

| Code | Scope | Staff qualification required |
|---|---|---|
| 210101 | Hardware, low end (PCs, notebooks, printers, peripherals) | Engineering **or** computing degree **or** diploma |
| 210102 | Hardware, high end (servers, mainframe, SAN/NAS) | Both degrees |
| **210103** | **Software supply** (OS, database, off-the-shelf packages incl. maintenance) | Engineering **or** computing degree **or** diploma |
| **210104** | **Software and system development, customisation, maintenance** | **Engineering degree AND computing degree** |
| 210105 | Telecommunications and networking | Both |
| 210106 | Data management (database, hosting, DR, storage) | Both |
| 210107 | ICT security (firewall, encryption, PKI, anti-virus) | Both |
| 210108 | Multimedia (video conferencing, graphic design, animation) | Any one |
| 210111 | Independent Verification and Validation | ISO/IEC 17025 or TMMi L3+, plus certified testers |
| **221110** | **Training services, instructors, moderators** | No licence required |

**210104 reportedly requires BOTH an electrical/electronics engineering degree AND a computing degree** among declared owners, directors or staff, while 210103 accepts any one route including a diploma. If the team is all computer-science graduates, 210103 is straightforward and 210104 may need a hire or director appointment. *(Reported from the official eP registration guide via secondary transcription, confirm with the MOF Unit Pendaftaran Syarikat before planning around it.)*

**There is no AI or LLM sub-code.** The list dates from 10/01/2023. Register AI work under 210104, or 210106 if data-centric.

**ICT consultancy (340602 and siblings) is a much harder separate track:** RM50,000 paid-up capital, three permanent staff, five years post-graduation experience for every equity holder. **Bumiputera status does not apply to consultant registration at all.**

**What is NOT required:** CIDB registration does not apply to pure software (s.25(1) Act 520 bites only on statutorily defined "construction works"; PK 2.9 requires CIDB+SPKK only for *perolehan kerja*). ISO 27001, ISO 9001 and CMMI are **not mandated by any circular**, treat as per-tender scored criteria. The one horizon item: the National Anti-Corruption Strategy 2024-2028 commits MOF to proposing **MS ISO 37001** for contracts ≥RM10,000,000.

**What IS required:** security vetting (*tapisan keselamatan*) under PK 2.1 para 2.11 for vendors accessing government data or premises, plus staff declarations under the **Official Secrets Act 1972 (Act 88)**. PDPA still binds you as a private contractor even though it does not bind the Government, mandatory DPO above 20,000 data subjects (10,000 for sensitive data), breach notification 72 hours to the Commissioner and 7 days to data subjects, penalty to RM250,000 and 2 years. Cyber Security Act 2024 licensing applies only to managed SOC monitoring and penetration testing, not ordinary development.

**The invisible ICT gate: JPICT, JTISA and JDN.** MAMPU was rebranded **Jabatan Digital Negara (JDN)** on 12/12/2023, any circular predating that saying "MAMPU" now means JDN. PK 2.1 para 2.10(i) requires every ICT procurement to obtain technical approval through the agency's own JPICT steering committee, the ministry-level JPICT, and **JTISA** (the public sector ICT technical committee) under JDN, governed by SPA Bil. 7/2024 via the PROFIT system at profit.jdn.gov.my. **You have no role and no visibility.** This is why RFPs stall, go quiet for months, or reappear re-scoped. Do not read silence as disinterest.

**PK 2.1 para 2.10(ii) directs agencies to prioritise in-house public sector expertise** to reduce dependence on external suppliers. You are competing against the agency's own team, by policy.

**Free pipeline intelligence:** PK 2.1 section 3 requires every agency to key its **Perancangan Perolehan Tahunan** (annual procurement plan) into ePerolehan **by 15 January each year**, with the tender-method portion published on MyProcurement. A stated objective is *"maklumat awal mengenai perolehan yang akan dipelawa supaya pembekal dan kontraktor bersedia untuk menyertainya"*, advance notice so suppliers can prepare. **Read every target agency's PPT in January.**

**Why the exemption exists:** PERKESO and HRD Corp are **self-funded** from contributions and levies, so they fall outside the federal allocation system entirely. **PTPK spends federal money, so it publishes** to MyProcurement as well as running its own portal. **TalentCorp publishes nothing at all.** Statutory bodies are exempt from the *system*, not the *rules*, WP 7.5 still requires them to follow PK 2 and PK 3 methods, forbids limited tender outright, and requires each body to write its own procurement SOP copied to MACC.

**Horizon:** the Government Procurement Act 2025 will make MOF registration a statutory precondition to bidding.

**UNRESOLVED, highest priority:** the Tax Compliance Certificate requirement. The governing circulars are image-only scans and it may gate both bidding and payment.

### 5.4 Corrections to commonly-held premises

- **MyEG is now Zetrix AI and lost its Immigration concession in 2025.** Its foreign-worker permit business moved to Bestinet via FWCMS.
- **MAMPU is now Jabatan Digital Negara.**
- Steven Sim was replaced as Minister by Dato' Sri Ramanan Ramakrishnan in December 2025.

### 5.5 The MYEG / Bestinet concession (context on the largest model in this ecosystem)

**MYEG Services** held Malaysia's e-government concession from 2000, reportedly earning ~**RM57 million/year** from foreign-worker permit renewal alone (circa 2014-15); government concession services were >25% of total revenue as of FY2021. It also upsold foreign-worker insurance and dormitory services beyond contracted scope.

**Bestinet** took over via FWCMS, mandatory for new ePLKS applications since **Feb 2025**, under a **6-year contract to January 2031**. FWCMS spans 11 modules (eQuota, eEmbassy, eRecruitment, Bio-Medical System, Online Insurance, eVDR, eEnforcement and others). Revenue comes from transaction fees, health-screening fees, insurance commissions, record-maintenance fees and permit/visa renewal fees.

The per-permit fee rose from **RM100 to RM215** in 2024 after Bestinet threatened a **RM1.63 billion** legal claim over inability to charge fees 2018-2024. The Public Accounts Committee estimates a **minimum RM3.22 billion over six years** (ceiling 2.5m foreign workers); the government had paid **RM381 million** by mid-2025.

Contentious: PAC found the system operated for years without a formal signed contract, with control weaknesses including unauthorised users approving applications. A newer proposed platform ("TURAP") faces fresh monopoly pushback in 2026. The ILO has disputed the "UN-recognised" framing (the cited World Summit Award is not a UN endorsement).

**This is the structurally largest model in the ecosystem: owning the mandatory system of record for a government process.** It requires winning a concession, not meeting an accreditation bar.

---

## Part 6: Training market competitive landscape

### 6.1 Price anchors (the consolidated card)

| Anchor | Price | Source |
|---|---|---|
| Public 2-day AI, low end | RM1,200-2,500/pax | CorporateTrainingMY |
| 1-day AI awareness (vendor-branded) | RM1,099-1,600/pax | Trainocate AI-900, AWS-GA |
| Entry AI awareness (catalogue) | RM1,100-1,400/pax | Iverson AI-3017, DP-900 |
| 2-day AI for managers, MIM brand | RM2,000-2,300/pax (+8% SST) | MIM |
| Microsoft associate/expert AI (5 day) | RM3,000-3,500/pax | Iverson, Trainocate AI-102 |
| **3-day AWS ML Engineering** | **RM5,400/pax, identical at both majors** | Iverson + Trainocate |
| Government-set 2-day AI course | **RM5,500/pax** | **MDEC** |
| AI certification (exam-based) | RM5,500-6,000 | MIM |
| Technical AI certificate, 2 months | RM7,400 | Forward College |
| Premium vendor AI tracks | RM7,000-13,600/pax | ISACA, Red Hat AI500, Cloudera |
| In-house group engagement | RM8,000-20,000/group | Observed market |
| Iverson catalogue median (473 courses) | RM4,600 exc. 8% tax | Iverson Store API |

**Implied market day rate: ~RM700-1,800 per pax per day.**

**Pricing opacity is the norm**, of ~27 organisations examined, only about eight publish any RM figure. Publishing a transparent price card would be an unusual market position.

### 6.2 The two majors

**Trainocate (M) Sdn Bhd**, KL Eco City, 51-200 employees, 24 countries, "30 years". **38 vendor Principals** including AWS, Alibaba Cloud, Cisco, CompTIA, **Databricks**, Dell-EMC, EC-Council, Fortinet, **Google Cloud**, IBM, ISACA, ISC2, Microsoft, NetApp, Nutanix, Oracle, Palo Alto, PMI, Red Hat, SAFe, Splunk, Tableau, Linux Foundation, Trend Micro, UiPath, VMware. **NVIDIA/DLI absent.** Claims *"All courses listed on our website are HRD Corp Claimable."* Also a Yayasan Peneraju ALTI.

**Iverson Associates Sdn Bhd (199401017652)**, founded 1994, "350,000+ students trained". Authorisations: AWS, Citrix, Cloud Credential Council, **Cloudera**, CompTIA, DASA, Dell EMC, DevOps Institute, EC-Council, EPI, EXIN, IBM, ISACA, ISC2, ITIL, Microsoft, OffSec, PMI, PRINCE2, Red Hat, SAP, Salesforce, ServiceNow, Veritas, VMware. **No NVIDIA, no Google Cloud.** Runs WooCommerce with an open Store API exposing 473 priced courses. Catalogue distribution: min RM420 / p25 RM2,000 / **median RM4,600** / p75 RM7,000 / p95 RM13,600 / max RM27,500.

**Correction: Trainocate was NOT formerly Iverson.** Distinct entities, no rebrand relationship, no supporting string in either site's HTML.

### 6.3 Vendor training partnerships

| Vendor | Open to a small MY company? | Notes |
|---|---|---|
| **Microsoft** | **YES, the only genuinely open door** | Training Services Partner Onboarding Form, **1-2 weeks**. Needs official courseware, delivery by MCTs, achievement codes, Metrics that Matter surveys. No business plan, no stated base fee. MCT requires the MCT Program Agreement, a qualifying credential (profile must include AB-730 or AB-731), a **3-day MCT Onboarding Experience**, and a program fee (**amount not published anywhere**). MCT renewal for 2026 requires **6 training deliveries** recorded in MTM. The optional Solutions Partner designation needs 1,000 courseware points + 200 exam units via the Pearson Partner Store + 4.25/5 average MTM. |
| **Google Cloud** | Invitation only | Member tier: 2 authorised trainers, 200 learners/year, CSAT 4.3 min, 70% response rate. Technically achievable but entry is relationship-gated. |
| **AWS** | **NO, closed** | *"The AWS Training Partner program is not currently accepting new applications."* Only ATPs may offer, deliver or resell official AWS Training. Alternative: resell/wrap AWS Skill Builder (US$29/month individual, US$449/year). |
| **NVIDIA DLI** | Only via partner or academic route | Certified Instructor Program accepts only Authorized Learning Partners / Education Services Partners, NVIDIA employees, or **academic faculty**. **No Malaysia-based DLI partner exists**, confirmed absent from both Trainocate's and Iverson's lists. The **University Ambassador Program is free**, gives free instructor certification and training "valued at $500 per student", and explicitly permits ambassadors to *"purchase workshops at a discount and resell/instruct them to industry and professional continuing-education customers."* Requires academic employment, NVIDIA nomination, 2 workshops/year to 40+ students. |

**Two market gaps:** NVIDIA DLI is absent from every Malaysian provider checked; Databricks is held only by Trainocate.

International vendors are HRDF-claimable only through HRD Corp-registered local partners, which is precisely why the authorised-partner layer exists.

### 6.4 Other players (verified status)

- **MDEC sells AI training at RM5,500/pax**, 100% HRD Corp claimable under SBL, approved 03/06/2025, two-day sessions at MDEC HQ Cyberjaya. **Your regulator is also your competitor.**
- **MIM** (est. 1966): Certified AI Practitioner RM5,500 member / RM6,000 non-member; AI-Enhanced Essential Skills for Managers 2 days RM2,000/RM2,300. Syllabus is conceptual (governance, ethics, decision-making) with no hands-on build content, an attack surface. HRD Corp claimable status not explicitly stated.
- **Peoplelogy Berhad**, ACE Market, listed 20/05/2025, ticker PEOPLE. Revenue TTM **RM30.30m**, market cap RM86.46m, ~100 employees, 6,700+ talent upskilled. **A useful ceiling reference for what a Malaysian corporate-training business scales to.** Note: the "LEAD" brand could not be found across five surfaces, the premise appears incorrect. Stock code 0356 is medium confidence only.
- **Info Trek Sdn Bhd (199601014730)**, founded 1996, PJ. Microsoft Learning **Silver**, weaker vendor tier. Advertises "5 Star Rated Training Provider by HRDF" but hedges that only *some* AI programmes are claimable. **No pricing published** (their WooCommerce API returns one product: "Booking", RM1.00).
- **iTrain (M) Sdn Bhd (694591-P)**, ~2005, KL Trillion. Deliberately **vendor-neutral** with own certifications (AIBE, MLBI, CCPS, CCDP, CCSS, CDE). Sharpest commercial framing found: *"100% HRD Corp Claimable"* with *"NO UPFRONT PAYMENT REQUIRED"*. No pricing published.
- **Forward College** (Penang, est. 2020): Professional Certificate in Applied Deep Learning **RM7,400**, 2 months online live, HRDF claimable. **Stack is Java/Deeplearning4j/ND4J/DataVec**, dated against a Python/PyTorch market standard, an attack surface.
- **CADS**, rebranded to cads.ai, **HQ relocated to Singapore**. No pricing. **The Khazanah link could not be verified, do not assert it.** MDEC and MoHE partner references are supportable.
- **Flood of 2024-25 vintage micro-providers**: AITraining2U, Oxydata, Pertama Partners, CorporateTrainingMY, Radiant Institute, Dah Reply, AIGC Malaysia, NobleProg. Most HRD Corp registered, most publishing no pricing.
- **Dropped from the competitor set:** NetAssist (an MSSP, not a training company, and no AI/data/cloud training), Supahands/SUPA (AI data infrastructure, potential supplier not rival), ASK Training (Singapore only), Sunway TES (accountancy exam prep only), Le Wagon (no Malaysia presence, confirmed).

**Domain corrections:** infotrek.com.my → **info-trek.com** · netassist.my → **mynetassist.com** · thecads.com → **cads.ai** · trainocate.com/my → **trainocate.com.my** · forwardschool.my → **forward.edu.my** · supahands.com → **supa.so** · peoplelogy.com.my → **peoplelogy.com**

### 6.5 Malaysia Digital status

**MDEC explicitly lists "Training and consultancy" among activities that CANNOT be sponsored under MD Status** (https://www.mdec.my/expats/pre-application-process-for-md-company). An AI development/solutions arm can qualify; a training arm cannot.

MD Status qualifying activities (~19-20) include **Artificial Intelligence**, big data analytics, fintech, IoT, cybersecurity, data centre and cloud, blockchain, creative media technology, sharing economy platform, UI/UX, IC design, 3D printing, robotics, autonomous technologies, systems/network architecture, GBS/KPO, VR/AR/XR, drone, advanced telecommunications. **"Training", "education" and "IT consultancy" do not appear.**

Maintenance requirements within 12 months: paid-up capital **RM1,000** minimum, **2 full-time knowledge workers** at RM5,000+ average monthly basic salary, **RM50,000** annual opex. For the tax incentive, paid-up capital jumps to **RM50,000** (New Investment) or **RM250,000** (Expansion).

Tax incentive: RTR 10% (or 5% with 3+ sustainability conditions) on non-IP income for 10 years; 0% on IP income (OECD modified nexus, MyIPO-registered); or ITA 60%/100% of qualifying capex for 5 years. Application fee **RM1,080 incl. SST** (New Investment) / RM2,160 (Expansion). Evaluation 21 working days, then NCI, then MIDA decision letter. **Applications must be received by 31/12/2027.**

**UNRESOLVED, high priority:** new applications under the Promotion of Investments Act 1986 stopped after **28/02/2026**; MITI's **New Incentive Framework** took effect 01/03/2026 for manufacturing with **services following in Q2 2026**. Whether the MD Tax Incentive is absorbed into, exempt from, or parallel to NIF for services is not addressed by MDEC, MITI or MIDA. **Confirm with MDEC (clic@mdec.com.my) or a tax adviser.**

### 6.6 JPK accreditation: not worth it for B2B AI training

**There is no AI or machine learning NOSS, and none is planned.** Three independent checks: registry search returns zero for "Artificial", "Machine" and "Kecerdasan"; the Industry 4.0-flagged NOSS list contains no AI/ML standard (it is robotics, industrial automation, drones, CNC); the official 2026 NOSS development plan contains only two new NOSS (Malaysian Sign Language Instructor/Assessor; Palliative Care) plus reviews of IT-020 and IT-053. **There is also no cloud-computing NOSS.**

Actual ICT NOSS in force (J620): Front-End Software Development (L4), Full Stack Software Development (L5), Web & Mobile App Visual Design (L3), Digital Forensics First Response (L3), Cybersecurity Defence Operations (L4, 2025), Cybersecurity Services / Penetration Testing (L5, 2025). Legacy IT-020, IT-030, IT-121, IT-082 codes still listed.

**Barrier to becoming a Pusat Bertauliah:** Sdn Bhd with **minimum paid-up capital RM50,000**; premises owned or leased with 1+ year remaining, holding local council **and Bomba** operating approval; centre name must not read as a business entity; full curriculum package (NOSS matrix, Course of Study, written instruction manuals per module, assessment documents, schedules); facilities meeting NOSS equipment ratios; a Technical Advisory Committee. Personnel: PPB (manager), PPD (internal verification), **PP (assessor-instructor, requires SKM in Vocational Training Officer I-031-3)**, TP (instructor). VTO part-time is **360 hours classroom + 720 hours internship**, RM2,500-3,600 at private centres. Induction (KIPPKM) 2 days, capped RM350/person.

Statutory fees: new accreditation first ≤3 programmes **RM1,500**; each additional programme RM200; renewal RM200 each; premises change RM200/programme; name change RM50. Per-candidate: SKM RM100 citizen / RM200 non-citizen; DKM/DLKM RM200/RM350; Penyata Pencapaian RM100/RM200.

Published SLA: ≥90% of new programme accreditations within 2 months of a *complete* application. Realistic end-to-end estimate **6-12 months** (flagged as estimate).

**The high-leverage exception: ADI Pekerjaan route (b).** SLDN and ADI merged into **Akademi Dalam Industri (ADI)** per letter [JPK 700-2/2/26 (13)] dated 23/12/2024. ADI Pekerjaan route (b) is experience-evidence-based (80% workplace / 20% theory) and states verbatim: *"Bagi kategori ini, syarikat atau pusat latihan **tidak perlu mendapatkan pentauliahan JPK**."* Incentive **RM4,000 per programme**. Personnel require only the ADI induction, **none need VTO**. Constraints: candidates 18-40, new hires at minimum wage or staff with <2 years' experience, certification maps to an existing NOSS.

**No HRD Corp scheme examined requires JPK accreditation** to register as a provider or make a course claimable.

**MBOT** registers individuals, not courses, 69,732 registrants as at July 2026. Professional Technologist: RM600 assessment + RM350 registration, "Ts." and "P.Tech", RM200/year renewal with 30 CPD hours. Marginal for short courses; worth having a "Ts." on the trainer bench.

---

## Part 7: Our own capability inventory (audited 31/07/2026)

### 7.1 What is real and shipped

| Product | Maturity | Paying external customers | Real users |
|---|---|---|---|
| **SIMS** (sifu-tutor) | Production, years of data | n/a (internal backbone) | Staff daily + tutors + parents |
| **Ripple Suite** (10 modules + Collection + PV) | Production, all live | n/a (internal) | Internal ops staff |
| **Luna AI** | Production, beta module | n/a (internal) | Internal staff |
| **Tutor + Parent apps** | Shipped to both app stores; active rebuild | n/a | Real tutors + parents |
| **Learnest LMS** | Production, 139 API endpoints, ~80% health | "Live, early access", volume unevidenced | Students/tutors/parents/admin |
| **Creative Hub** | Production since 09/07/2026 | n/a (internal) | **7 named users** |
| **Kelasapp** | Live private beta, 548 E2E green | **Zero.** Pilot (Sopan) not migrated | Demo tenant only |
| **Finch** | Production internal; SaaS pivot incomplete | **Zero.** Blocked on Curlec live keys | ~4 internal inbox staff |
| **KICU** | Claimed live on both stores | Unknown | **Not verifiable from this workspace** |

**Hard scale evidence (measured, from the Hostinger migration assessment against the live box):** SIMS is 129 tables / 7.6M rows / 3.1 GB logical MySQL, 12 GB on disk, **62 GB of user uploads** growing 1-2 GB/week. `pulse_entries` 3.0M rows, `user_logs` 1.4M rows, `notifications` 892k rows. 29,090 queued jobs / 787 failed. Production hosting ~$148/month, 83% disk full.

**Company profile claims (self-authored PDF, 24/07/2026, not independently corroborated):** operating since 2018, founders Syamil Yusoff and Hafiz Razali, **22,000+ students served, 50,000+ registered tutors, 9 products, 3 mobile apps**. Registered entity appears as **Sifu Edu Learning Sdn Bhd**. Two GitHub orgs: `Sifututor/*` and `Learnest-Lab/*`.

### 7.2 Business lines actually running

1. **1-to-1 tutoring marketplace (Sifututor)**, the 2018 original, the cash-generating operation
2. **1-to-1 Quran/Islamic tutoring marketplace (Nakngaji)**, launched 2022, same model, claimed 1,000+ Quranic tutors, runs on the *same* SIMS/Ripple infrastructure (Ripple's Collection module has explicit `st` and `nn` brand worklists)
3. **Product studio / SaaS vendor (Learnest Lab)**, the 2026 pivot: Kelasapp, Finch, Learnest LMS, KICU
4. **EdTech D2C (Learnest LMS)**, freemium SPM courses with premium subscriptions

**There is no software-dev agency and no AI-consultancy business line operating today.** The company profile positions for it; that is intent, not a running line.

### 7.3 The gig-worker engineering that matters

**Ripple Suite `tutor-payments`** is the flagship and the most directly transferable asset:
- 7-status slip lifecycle (`eligible → approved → processing → paid`, plus `needs_fix`, `discarded`, `settled`), slip UIDs `TPS-YYMM-XXXX`, DB unique index enforcing one eligible slip per tutor per cutoff
- Commission calculation with per-class breakdown (duration, hourly rate, online flag, SIMS commission vs resolved amount) and **automatic discrepancy detection** against SIMS audit rates and cumulative hours
- Payment adjustments via structured notes (addition/deduction/info) with their own approval workflow
- **Approval gates:** cannot approve without bank details on file, zero discrepancies, zero pending notes
- Bank account management stored in Ripple's own Postgres (never written back to SIMS), bulk Excel import
- **Batch disbursement:** Maybank M2U bulk-payment XLSX auto-split at 100 rows, transfer-proof upload, confirm-transfer with bank reference, then **background write-back to SIMS** with per-slip sync-status polling and retry
- Payment slip PDFs; granular permissions

**SIMS-side:** `monthly-bonus` (tiered at 70/85/100 hours, **online classes weighted 0.5x**), `refunds-commitment-fees`, `payment-transfers` (LHDN-safe re-allocation), `level-changes`, `ExecutiveSummaryService` (payouts and margin), `UnpaidEarningsController`, `DemandHeatmapController`. Separate staff commission engine (threshold-tiered, default 2% above RM11,000 of prior-month first-invoices, else 1%).

**Kelasapp `payouts`:** a clean second-generation implementation, RunPayrollPanel, PayrollTable, PayoutAdjustments, BulkMarkPaid, PayslipPdf, with `teacherPayouts`/`teacherPayoutLines`/`teacherPayoutVoidSnapshots`, KL-timezone month bounds, **integer-cents money math**, unit tests against PGlite.

### 7.4 Existing Malaysian compliance work

**Statutory payroll (SIMS `staff-payments`):** `StaffService::createStaffPayment()` persists a `has_services` JSON flag set of `EPF`, `SOCSO`, `EIS`, `HRDF`, `IncomeTax`; staff profile columns `epf_number`, `socso_number`, `eis_number`, `income_tax_number`. Payslip PDF, React admin screens, permission gates.

**Scoping honestly:** this is **flag-and-record**, not a calculation engine. There are **no EPF/SOCSO/EIS rate tables, no age-banded logic, no PCB/MTD schedule computation, and no Borang A / Borang 8A / CP39 / EA generation**. **No HRDF levy calculation**, just a boolean. Rate math appears to be entered, not computed.

**LHDN e-Invoice:** `LhdnComplianceService` (113 lines) is a real, tested guard with a three-state decision engine on invoice auto-void, BLOCK if `lhdn_submitted_at` is set ("Finance must issue a Credit Note first"), WARN if the first attended/verified class is ≥24h old, ALLOW otherwise. `markSubmittedToMyInvois()` records timestamp and optional UUID, gated on invoice status `paid`. Migration adds `lhdn_submitted_at` and `lhdn_uuid`.

**No direct MyInvois API integration**, submission is a manual Finance action, with QuickBooks in the loop. What exists is the credit-note-not-void invariant, which is the genuinely hard business-rule part.

**THE GAP: no self-billed e-Invoice anywhere.** Grepped `self-billed` / `self-bill` across sifu-tutor, ripple-suite, kelas and lls: **zero hits**. Under Malaysia's e-Invoice regime, payments to individual gig workers generally require the payer to issue a self-billed e-Invoice. Tutor commission payouts run monthly in production. **Live compliance exposure and the most obvious adjacent product gap.**

**Other Malaysian-specific work:** FIUU gateway (SIMS parent invoices), Curlec/Razorpay MY (LLS, Finch), DuitNow QR (Kelasapp), Maybank M2U bulk XLSX with auto-split (Ripple). RM currency, Asia/Kuala_Lumpur, DD/MM/YYYY, `60xxxxxxxxx` phone format enforced as code rules. EN/BM bilingual throughout. PDPA-oriented consent records with append-only writes and `withdrawn_at` stamping.

### 7.5 Team and capacity

| Person | Role |
|---|---|
| **Hafiz Razali** | Co-founder, CTO / Lead Dev. Sole owner of production approval, deploys, secrets, DNS, payment writes, risk acceptance. Effectively the only person who touches production. |
| **Syamil Yusoff** | Co-founder. No engineering footprint in the workspace. |
| **Helmi (Harazali)** | Solo dev on finch-inbox. Owns Finch's prod VPS. Reports via mandatory daily non-technical reports. |
| **Noman Ali** | `webadmin@sifututor.my`, maintains the LLS README. |
| **Jivan** | Developer, **scoped to Kelasapp only, explicitly no production/deploy/secrets**. |
| **Ops/support staff** | ~4 on the EDU inbox; 7 named Creative Hub production users; SIMS has 200 granular staff permissions. |

**One-senior-engineer organisation** plus 2-3 scoped contributors, running 9 products on heavy Claude Code / Codex agent leverage governed by a homegrown "Agent OS" (94 playbook files, ~200 skills, hooks, quality gates, a Koda memory MCP server). **That agent infrastructure is itself a real, non-trivial internal asset and arguably the least-recognised sellable thing in the portfolio.**

**Engineering maturity signal:** Creative Hub `STATUS.md` (27/07/2026) documents a `/api/admin/demo-reset` endpoint live in production with no environment guard that **destroyed 83 production rows and the entire audit trail**, one crash away from deleting all 7 users including the superadmin. A follow-on audit of 124 SQL-using files found 25 confirmed schema-drift findings. Delivery velocity is currently ahead of operational maturity.

### 7.6 No existing B2B or government customers

**No evidence of any paying B2B or government client anywhere in the workspace.** No capability statement, tender document, procurement response, MDEC/HRDF provider registration, or client list. The only named prospective B2B customer is Sopan (Ustaz Azim's madrasah), a not-yet-migrated pilot.

**Do not misread the 615 Labs list.** `finch-inbox/BUSINESS_DISCOVERY.md` records that Sifututor rents inbox capacity inside **615 Labs Sdn Bhd**'s multi-tenant platform alongside 17 client businesses (Elevete Patisserie, Kawan Food, HIPSALON, Yamalube and others). **Those are 615 Labs' clients. Sifututor is a fellow tenant, not their vendor.**

---

## Part 8: Contested numbers and could-not-verify register

### 8.1 Numbers where official sources disagree

**Gig worker headcount:**

| Figure | Source | Date | Note |
|---|---|---|---|
| **1.64 million** | **MDEC via KESUMA FAQ Q1** | 2024 data | **Methodology NEVER published.** Covers p-hailing, e-hailing, freelancers, online services, others, broader than platform workers. ISEAS notes it only "likely corresponds" with the law's coverage, suggesting it was constructed to match the Act's scope. |
| **~1.2 million** | **MOF, *Economic Outlook 2026*** | Oct 2025 | Official Budget document |
| **650,000** (370,000 active p-hailing) | **DOSM survey Apr-Jul 2022** via ILMIA | 2022 | **The only actually measured survey** |
| 1.12 million | MDEC programme data | 2022 | |
| "more than 3 million" | Utusan / Malay Mail | 2024-2026 | Unverified |
| 3.22 million | MyGiG president | 2026 | Industry claim |

**The Malaysian government uses 1.2 million and 1.64 million simultaneously in official documents. DOSM publishes no gig series at all**, only "own-account worker". DOSM LFS Q1 2025: 16.7m employed, 3.45m (20.7%) in informal employment.

**Platform count:**

| Count | Source | Basis |
|---|---|---|
| **246** | KESUMA FAQ (MDEC 2024) | "berdaftar dengan pelbagai Kementerian dan Agensi" |
| 146 (127 local, 19 foreign) | ISEAS (MDEC 2023) | platforms since 2014 |
| 140+ | MDEC CEO, Dec 2023 | verified by MDEC and KKD |
| 123 | MyDIGITAL/Ipsos whitepaper | registered with MDEC, 2021 |

**No published register or licence list exists. Act 872 has no licensing regime. Size on the low end.**

**Market value, the RM650m figure is a misattribution.** ISEAS states "The gig economy was valued at RM650 million in 2025 (MDEC 2023)" with no footnote. The original MDEC statement (Bernama 25/09/2022) says growth *"especially from the development aspect of local platforms"* from RM371.4m (2021) to at least RM650m (2025), a sub-component. **In the same statement MDEC gave the headline: "the overall market size for this industry in Malaysia estimated to be worth at least RM1.61 billion."**

Best available sizing: MDEC gig market RM1.63bn (FY2022), RM1.33bn (Q3 2023). e-Conomy SEA 2025: transport + food delivery GMV **US$4bn (~RM17bn) 2025 → ~US$6bn by 2030**. Grab alone contributed RM9.9bn = 0.5% of GDP in 2023.

**"Gig = 17% of GDP" does not hold up**, almost certainly a misreading of MOF's *Economic Outlook 2026*, which says **mixed income** (all self-employed and unincorporated enterprises) is 17.2% of GDP. "RM130 billion gig economy" is internally inconsistent (RM130bn ÷ RM2.03tn ≈ 6.4%, not 17%).

**No official gig-economy GDP contribution figure exists** from DOSM, BNM, Ministry of Economy or EPU.

### 8.2 Budget 2026, what is actually there

**The "RM100 million PTPK gig allocation" is misattributed.** It is real and PTPK-administered and for gig worker training, but it came from **Anwar's Amanat Tahun Baharu 2026 (~04-05/01/2026)**, not Budget 2026. Announced by Minister Ramanan 05/01/2026, mechanism "sedang diperhalusi". **Still not operational as of 31/07/2026**, no eligibility criteria, no application route, no disbursement data. On 02/07/2026 Ramanan asked Cabinet to **convert it from loans into grants** because TVET trainees must give up work to train. Still a proposal.

**What Budget 2026 actually contains for gig workers (CONFIRMED from the speech PDF):**

| Item | Amount | Para |
|---|---|---|
| **PERKESO SKSPS subsidy**, govt bears **70%** of contribution for first-time registrants in non-mandated sectors, **50%** year 2; capped at 736,678 contributors | **RM100 juta** ← *the real Budget 2026 RM100m* | ¶166 |
| i-Saraan + i-Saraan Plus + i-Suri, >600,000 contributors | RM250 juta | ¶165 |
| **MARA**, TVET explicitly for "**pekerja gig**", B40, vulnerable | **RM30 juta** ← *the only Budget 2026 training line naming gig workers* | App. p.172 |
| BSN "Pembiayaan Mikro MADANI GIG", 4%, to RM20,000, 5 years | RM20 juta | p.190 |
| PTPK general TVET, >25,000 trainees in AI/EV/semiconductors (**not gig-specific**) | RM650 juta | ¶65 |
| HRD Corp, 3 million training places | RM3 bilion | ¶65 |
| HRD Corp for licensed **taxi** drivers | RM10 juta | ¶76 |
| SJKP housing guarantee raised RM10bn → RM20bn, explicitly naming gig workers; up to 120% of financing, limit RM360,000 | RM20 bilion guarantee | ¶216 |
| BUDI95 fuel quota, extra for >52,000 active e-hailing drivers |, | p.26 |

**PACE package, 01/05/2026, >RM710 million:** EIS benefits RM580m (PERKESO), HRD Yakin MADANI RM100m (HRD Corp), **skills training for gig workers RM20m (PTPK)**, Industry Training Matching Grant RM10m (TalentCorp).

**i-Saraan Plus (new 2026):** 20% match, **RM600/year, RM6,000 lifetime**, but **restricted to full-time e-hailing and p-hailing**. Other informal/self-employed get standard i-Saraan (RM500/year, RM5,000 lifetime). Drivers auto-registered as EPF *members* via platform partners, but **contributions remain voluntary**. 480,000+ participated in i-Saraan in H1 2025.

**Act 872 does NOT mandate EPF or EIS.** ISEAS Table 2 lists it as an omission, noting inclusion "would face some hurdles; the EPF rests under the ministry's jurisdiction (Finance)." MOF *Economic Outlook 2026* says compulsory self-employed contribution "will be explored".

**MyMahir NAICI:** Budget 2026 Appendix 24 gives MSMEs an **extra 50% tax deduction on AI training recognised by MyMahir NAICI**, uniquely available even to levy-paying firms normally excluded. Applications to TalentCorp until **31/12/2027**. **NAICI launched May 2025 and publishes NO course recognition process at all.** AI MyMahir itself is RM110m with TalentCorp and EY across 60 constituencies, ~22,000 beneficiaries. Note a discrepancy: Ramanan framed it as gig-focused; TalentCorp's own release does not name gig workers.

**Kenduri Padanan 70:** government subsidised up to 70% of worker contributions in 2026 under Lindung Kendiri, capped ~RM232.80/person/year. ~298,827 gig workers actively contributing by November 2025.

**PERKESO injury trend (media release 01/04/2026):** accidents under Lindung Kendiri **4,021 (2023) → 4,839 (2024) → 5,496 (2025)**; benefit recipients 6,294 → 6,725 → 7,893.

**Pre-Act coverage was poor:** SESSS participation was only **26% of gig workers** as at May 2025. Among p-hailing riders (DOSM 2022), 72% had SOCSO but **46% paid for it themselves**, only 27% platform-paid. EPF participation 22%.

**Earnings context:** Utusan investigation (Aug 2023) found e-hailing drivers averaged **RM1,350/month net**. Share of p-hailing riders earning below the RM1,500 minimum wage fell from 43.1% to 30.7% after joining p-hailing. 74% report gig work as main income; 77% under 40; 76% Malay.

### 8.3 Consolidated could-not-verify register

**Act 872 / gig:**
- Whether Sifututor is a "contracting entity" under s.2, **the highest-value open question**
- MDEC's methodology behind 1.64 million
- Any DOSM gig-worker statistic (none exists)
- Official gig-economy GDP contribution (none exists)
- Any published register or count of licensed platform operators (no licensing regime)
- Eligibility criteria / application route / disbursement data for the RM100m or RM20m PTPK gig money
- Any SEGiM budget allocation (absent from both primary Budget documents)
- i-Saraan Plus operational/registration status
- 2026 SESSS/SKSPS gig registration totals post-Act
- PERKESO API documentation v2.1 contents, **no public developer portal exists**
- Published compliance cost per platform, **nobody has priced this market publicly at all**

**HRD Corp:**
- Whether AI is officially classified as a Focus Area, **inferred, verify before pricing above the General ceiling**
- TTT course cost and duration (official pages 404)
- Employer's Circular 2/2026 (four consultancies agree on its content; the official index shows no 2/2026 and the PDF 404s)
- e-LATiH Content Provider revenue share and submission terms
- Counts of registered employers / training providers (not in the financial report)
- Who built e-TRiS (DigiGov platform lineage is well-evidenced; TCS involvement is **not** confirmed, do not state it)
- The vendor on the RM14m New Core System
- Published claim rejection rate (none exists)
- Current JomPAY biller code, three conflicting values: **500181** (HRD Corp Support Centre, most authoritative), 4044 (2022 official slip artwork, likely superseded), 74038 (BrioHR, unverified, same article cites the dead hrdf.com.my domain). **Never hardcode**, JomPAY requires a fresh per-payment Ref-1 from a generated e-Slip.
- Contents of the e-Invoice circular 4/2024 (image-only PDF, no text layer), the most likely place for a future integration requirement

**Procurement / other agencies:**
- **Tax Compliance Certificate requirement**, circulars are image-only scans, may gate bidding AND payment. **Highest-priority unresolved procurement item.**
- Whether the MD Tax Incentive survives the NIF transition for services from Q2 2026
- MD Status application fee on an official MDEC page, and any end-to-end approval SLA
- Owner of `primuscore.com` (JTKSM's SAML IdP host)
- Who built ePPAx, MyKKP, MySPIKE v1/v2, or PTPK's loan system
- Winner of PTPK/PR/TEN/01/2025 (debt collector software) and PTPK/PR/TEN/04/2025
- MyKKP 40-month maintenance tender QT240000000034441 (would name DOSH's incumbent)
- Any LKAN report on these four bodies' IT systems or procurement
- Any parliamentary written answer naming MySPIKE, MyKKP, ePPAx or PTPK system costs, **the largest coverage gap**
- Any Bursa announcement linking the 15 named Malaysian IT companies to these bodies, **absence of retrievable evidence, not evidence of absence** (Bursa 403s automated retrieval)
- MCT Program Fee amount (not published on any official Microsoft page)
- MQA voluntary micro-credential assessment fee and turnaround
- Standard JPK PB accreditation validity term
- Current head of AI Malaysia after the 26/06/2026 leadership transition
- Whether MD2030 (MyDIGITAL branding) and AI Nation 2030 are formally the same plan

**Premises that did NOT survive verification:**
- SEGiM as the regulator of Act 872 (it is not, and does not operationally exist)
- Platforms co-contributing to the 1.25% (they do not)
- A platform registration/licensing requirement (none exists)
- "Form JD3" (no evidence it exists)
- HRD Corp QR attendance (it is geolocation check-in, not QR)
- Trainocate formerly being Iverson (distinct entities)
- Peoplelogy's "LEAD" brand (not found across five surfaces)
- The CADS-Khazanah link (unverified, do not assert)
- "Working for Workers"/WFW portal, eMall JKKP, e-Binaan, e-Buruh, MD Talent (domains do not resolve / absent from navigation)
- The RM100m PTPK gig allocation being in Budget 2026 (it was a January 2026 speech)

---

## Part 9: Dated items as at 31/07/2026

| Date | Item |
|---|---|
| 03/08/2026 | **HRD Corp PSMB (RFP) 2/2026** document purchase closes. RM100. Supplier portal registration is a prerequisite. |
| 04/08/2026 | HCCS mandatory briefing, 11:00, Wisma HRD Corp |
| 07/08/2026 | MDEC National AI Compute Exchange Call for Partnership closes |
| 24/08/2026 | HCCS submission closes, 12:00 |
| 31/08/2026 | 100,000 youths aged 18-30 completing Rakyat Digital courses receive 3 months free AI software access. **Vendor was not finalised as at 28/07/2026.** |
| ~September 2026 | **MPGiG "Fair Compensation Structure" study due.** Becomes a gazetted Ministerial order; non-compliance up to 2 years / RM50,000. Minimum earnings rates are the first agenda item. |
| ~30/09/2026 | Act 872 administrative moratorium fully lapses on the 6-month reading (already lapsed 30/06/2026 on the 3-month reading) |
| 01/01/2027 | HRD Corp public training reverts to a 14-day post-approval wait (the 3-day relaxation runs 15/06/2026 to 31/12/2026 only) |
| 31/12/2027 | MyMahir NAICI AI training tax deduction applications to TalentCorp close |
| January 2031 | Bestinet FWCMS contract ends |

**Open now:** PERKESO RFP **T/PKS 02/2026** (job portal) via speed2u.my. PTPK/PR/SH/07/2026 (Security Posture Assessment).

---

## Appendix: key primary source URLs

**Act 872 and gig:**
- Act text: https://www.mohr.gov.my/aktapekerjagig2025/assets/documents/Act%20872.pdf
- Official FAQ (127 questions): https://www.mohr.gov.my/aktapekerjagig2025/assets/documents/faq.pdf
- P.U.(A) 143/2026 Social Security: https://www.mohr.gov.my/aktapekerjagig2025/assets/documents/PUA143_2026%20-%20PERATURAN%20PEKERJA%20GIG%20(KESELAMATAN%20SOSIAL).pdf
- P.U.(A) 143/2026 Conciliation: https://lom.agc.gov.my/ilims/upload/portal/akta/outputp/3434451/PUA143_2026.pdf
- KESUMA commencement release: https://www.mohr.gov.my/pdf/2026/KSM.%20100-2-1-1%20JLD%205_72_31032026.pdf
- PERKESO release 01/04/2026: https://www.perkeso.gov.my/images/kenyataan_media/2026/010426%20SIARAN%20MEDIA%20SAMBUT%20AKTA%20PEKERJA%20GIG%20AKTA%20872%20-%20latest.pdf
- ISEAS Perspective 2026/48: https://www.iseas.edu.sg/wp-content/uploads/2026/07/ISEAS-Perspective_2026_48.pdf
- eADUAN GIG: https://eaduan-gig.mohr.gov.my/

**HRD Corp:**
- Financial Report 2025: https://hrdcorp.gov.my/wp-content/uploads/2026/07/HRD-Corp-Financial-Report-2025-Digital-Version.pdf
- Annual Report 2024: https://hrdcorp.gov.my/wp-content/uploads/2025/06/HRD-Corp-Annual-Report-2024-Digital-Version.pdf
- Training providers: https://hrdcorp.gov.my/training-providers/
- Procurement portal: https://hrdcorp.gov.my/procurement/
- ACM Nov 2025: https://hrdcorp.gov.my/wp-content/uploads/2025/11/Attachment-ACM-Table-November-2025-Edition.pdf
- ACM Guidebook Jan 2026: https://hrdcorp.gov.my/wp-content/uploads/2025/12/Jan-2026-Version_Allowable-Cost-Matrix-2025.pdf
- Claimable Course Workshop 2026: https://hrdcorp.gov.my/wp-content/uploads/2026/05/HRD-CORP-CLAIMABLE-COURSE-WORKSHOP-2026-1.pdf
- Provider basic flow: https://hrdcorp.gov.my/wp-content/uploads/2026/07/Training-Provider_Basic-flow.pdf
- Suspension statement 06/02/2026: https://hrdcorp.gov.my/hrd-corp-suspends-3-top-management
- Circular 5/2024 (15% MADANI): https://hrdcorp.gov.my/wp-content/uploads/2024/11/Employer_Circular_No.05_2024-ENG-PLM-2.0-1.pdf
- Circular 6/2024 (trainer accreditation): https://hrdcorp.gov.my/wp-content/uploads/2024/12/6-Employer-Circular-No6-2024.pdf
- Client charter: https://hrdcorp.gov.my/client-charter/

**Other agencies:**
- Act 640 (PTPK): https://eakta.mohr.gov.my/assets/pdf/akta_kemahiran/Akta%20Tabung%20Pembangunan%20Kemahiran%202004%20(Akta%20640).pdf
- Act 652 (JPK): https://eakta.mohr.gov.my/assets/pdf/akta_kemahiran/Akta%20pembangunan%20kemahiran%20kebangsaan%20Akta652.pdf
- PTPK e-tender: https://smart.ptpk.gov.my/WebApp/TenderMS.aspx
- JTKSM: https://jtksm.mohr.gov.my/en/home
- DOSH: https://dosh.gov.my/en/
- DSD/JPK: https://www.dsd.gov.my/en/ (broken TLS chain)
- MySPIKE v2: https://myspike.tvet.gov.my/
- MyProcurement API: https://myprocurement.treasury.gov.my/procurements/fetch

**Budget and policy:**
- Budget 2026 speech: https://belanjawan.mof.gov.my/pdf/belanjawan2026/ucapan/ub26.pdf
- Federal Expenditure Estimates 2026: https://belanjawan.mof.gov.my/pdf/belanjawan2026/perbelanjaan/Anggaran_Perbelanjaan_Persekutuan_2026.pdf
- Economic Outlook 2026: https://belanjawan.mof.gov.my/pdf/belanjawan2026/economy/economic-2026.pdf
- National AI Action Plan 2026-2030: https://strapi.naio.okie.my/uploads/AI_Nation_2030_National_AI_Action_Plan_2026_2030_Eng_V_290726_49cb382621.pdf
- MD Tax Incentive guidelines: https://moore.com.my/taxflash/Guidelines-on-MD-Tax-Incentive-(New-Investment-Incentive)-dated-26.4.24.pdf
- MDEC non-qualifying activities: https://www.mdec.my/expats/pre-application-process-for-md-company

---

# ADDENDUM: Proposal opportunity research (31/07/2026)

Separate research pass on "what business can we create for KESUMA". Full analysis in three artifacts:
1. https://claude.ai/code/artifact/73e244d2-abbc-4470-9f20-3a3f39dc5cff (hooks)
2. https://claude.ai/code/artifact/0244a503-3d37-47f5-956c-f78d2429133c (concepts)
3. https://claude.ai/code/artifact/526db389-c41b-4a87-9f2c-665d9e84d475 (teardown + Codex pack)

Condensed recall version in Claude memory as `project_kesuma_proposal_opportunity.md`.

## Corrections to the main dossier above
1. **MACC issued No Further Action on HRD Corp in Dec 2024** (no offence under the MACC Act). The "MACC investigation" framing above overstates it. 3 executives suspended Feb 2026, rising to 6 under disciplinary proceedings by July 2026.
2. **AI is CONFIRMED NOT an HRD Corp Focus Area.** Full text extraction of the Jan 2026 ACM guidebook returns zero hits for "AI", "artificial intelligence" and "machine learning". The dossier above flagged this as inferred; it is now a verified negative. Do not model uncapped AI pricing.
3. **MOF field codes for training work** are 221110 (Khidmat Latihan/Tenaga Pengajar), 222504 (Pusat Latihan), and for consultancy 241100 / 241200 / 241300. The ICT codes above (210103/210104) apply to software, not training.
4. **PROTEGE-RTW sits under KUSKOP**, and its RM2,000/month allowance is paid by the host company as a procurement obligation, not by government.
5. **TVET institution counts**: 669 public / 24 state / 652 private = 1,345 total (ISEAS 2025).
6. **EY's RM110m MyMahir role is CSR (EY Ripples), not a procurement award.**
7. Minister is **Ramanan Ramakrishnan since 17/12/2025**, not Steven Sim.

## Key new facts
- **PTPK TKPI scheme already pays providers on outcomes**: 90% on agreement completion, final 10% only 3 months after completion AND outcome achieved, certified by MPC. Outcomes = job placement/retention, promotion, or income increase. Place-and-Train mandated. Mainstream PLK-i has no such gate. (A second possible scheme, "TVET Berimpak Tinggi" 19/05/2025 RM200m with MARii/NASCA/CREST/MOSTI+KPT verifiers, has the same 90/10 architecture, could not confirm whether one scheme or two.)
- **HRD Corp AR2024 "Gig Economy" category: 207 training places of 2,549,188 = 0.01%.** Act 872 has no training provision; gig workers have no levy pot; PLM excludes them; Grab routes via PTPK.
- **RM100m PTPK gig tranche**: PM announced ~01/01/2026; Minister proposed loan-to-grant conversion 2-3 July 2026; **Cabinet not approved as of 03/07/2026**.
- PTPK loan book: 115,780 accounts in default, RM933.9m arrears (Oct 2024), ~97k of ~380k paying to schedule. Loan range RM2,700 to RM142,400 per programme (median ~RM20,100), NOT the widely-quoted RM5,000-24,000. Living allowance RM800/month (raised from RM600). 3% admin fee on reducing balance.
- **Live e-TRiS registry**: 3,657 AI programmes from 1,060 providers; 48% of providers have one. "AI for productivity" is 23% of AI titles.
- **e-LATiH**: free AI course 2,538 enrolments vs paid RM50 course = 3.
- **The real problem is underemployment and wages, not unemployment.** Graduate unemployment 3.2%, employability 92.5% (record). Underemployment 32.2% = 1.6m. 30.6% of first-degree graduates earn <=RM2,000. Nobody owns wage progression.
- **Sabah gets 2.17% of national training vs ~10% of population.** Sarawak is occupied (CENTEXS, SDEC).
- **PK 2.4 clause 2.4**: consultancy "Kajian" up to RM500,000 by direct appointment, no tender.
- **Ops Daya** (MACC + PERKESO, from 09/06/2026): fraud in Daya Kerjaya 2.0. 143 companies, 98 detained, 1,638 more suspected ~RM45m. **The fraud passed every front-door check; caught by AI pattern-detection plus whistleblowers, after payment.**

## Open questions that decide the strategy
1. Has PTPK's 10% outcome gate ever actually been withheld?
2. Are TKPI and "TVET Berimpak Tinggi" one scheme or two?
3. Did Cabinet approve the RM100m loan-to-grant conversion?
4. Is PERKESO contribution data legally accessible for outcome verification in any form (PDPA, OSA 1972, Act 4/789)?
5. Is the outcome-measurement market genuinely empty, or did HRD Corp's failed RM14m New Core System already cover it?

---

# ADDENDUM C — Session close, 31/07/2026 (afternoon)

## Deliverables published
- **Five-proposal client pack**: https://claude.ai/code/artifact/2f7b35b9-3ec4-4278-9c34-65974a84d008
- **JPK/ADI full proposal (internal draft)**: https://claude.ai/code/artifact/c33302c6-1013-470d-a8e9-b19e7b979afa

## Codex challenges 1, 4, 5 (verdicts)
Challenges 1/4/5 initially hung on stdin and never ran; re-run with `< /dev/null`. Outputs in session scratchpad `codex/c{1,4,5}-out.md`.

- **C1 (thesis)**: "KESUMA cannot measure outcomes" is a **category error**. AG finding was narrowly about PSMB corporate KPI governance. HRD-TEE live since 2019; TEE portal now live (tee.hrdcorp.gov.my, 2026 guideline); NTI + eTRiS exist; World Bank did aggregate productivity analysis. Defensible gap is only: incomplete coverage, self-report, no wage linkage, no counterfactual, poor provider comparability. Key insight: *measurement creates losers only if tied to consequences; if it only populates a dashboard it is politically harmless and commercially low-value.* KESUMA **declined** PAC's forensic effectiveness audit = negative buyer signal.
- **C4 (capacity)**: ceiling **RM50–100k, max 3 months**, no production dependency, no 24/7 support. **Performance bond above RM200,000** (AP 176.2: 2.5% ≤RM500k, 5% above). Federal tender threshold RM500k (PK 5.1). Payment planning 45–90 days; stress case 180 days. Verdict: **"bid for the study, not the system."**
- **C5 (political risk)**: never lead with audit/failure framing. Six HRD Corp execs suspended Feb 2026, still suspended July. HRD Corp sent legal demands to media over PAC coverage (minister ordered withdrawal). "Reset done" April 2026. Sequence **TalentCorp → PTPK → PERKESO → HRD Corp**. Recommended employer-first commercial model (declined by Hafiz, who wants government buyers only). Rule adopted: **never both deliver and independently assess the same training.**
- NCS cautionary tale: RM14m, reported 93% complete in the 2024 annual report, actually 4+ years delayed after three failed UATs.

## Verified facts that changed the plan
- **PTPK window CLOSED.** Performance-based allocation already issued as **Executive Circular No. 2 of 2026**, provider clinics June 2026, RM650m in Budget 2026. Only a post-implementation gaming review remains (RM50–90k).
- **SEGiM Cabinet-approved in principle, NOT operational.** No leadership or budget line found; Act 872 currently administered via JTKSM. Not a contractable counterparty yet. MPGiG (tripartite council) advises on minimum income rates and sector standards.
- **JPK/ADI is actively scaling, not passively failing.** Target **10,000 registrations/year for 3–5 years**, mainstreaming ambition. 2025: ~9,000 apprentices + 2,000 existing workers, **~1,500 companies**. Incentive stack = RM1,000/month + HRD levy reclaim + Income Tax Act 1967 deduction. **AI is a named ADI priority sector** (with semiconductors, EV automotive, aerospace, green tech).

## Learnest Lab operating scale (for all future bids)
Stated by Hafiz: operating **since 2018**, combined cumulative revenue **approaching RM60m**, Nakngaji ≈ 2/3 of Sifututor.
SIMS production reads 31/07/2026 (read-only lane, `deleted_at IS NULL`): 26,961 tutor registrations / 4,481 active / 2,204 have taught / 1,333 active in 90 days / 281,282 hours / 190,909 classes / 12,173 students / RM11.51m parent revenue / RM5.19m paid to tutors / 99 active staff.
**SIMS holds only ~16 months of an 8-year business**, so raw SIMS counts are floors, roughly one fifth of true cumulative scale. Client-facing figures used: 20,000+ tutors, ~2,000 monthly, 1,000,000+ hours, 50,000+ students.

## Open items
1. **No named recipient at JPK.** This is the binding blocker; the gap is a relationship, not an argument.
2. Survey-house quote needed to firm proposal 01 pricing.
3. BM version: declined by Hafiz.
4. This dossier remains **git-ignored**; needs `git add -f` to persist.
