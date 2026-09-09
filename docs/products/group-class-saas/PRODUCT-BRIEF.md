# Group Class Management SaaS — Product Brief
**Status:** Discovery / Pre-build
**Last updated:** 2026-06-25
**Author:** Hafiz (CTO) + Claude Code
**Discovery source:** 2026-06-22 meeting with Sopan (Ustaz Azim) + Nak Ngaji team

---

## 1. The Problem

Operators who run group-based learning — madrasah, tuition centers, online academies, physical learning centers — manage their operations with a fragmented stack:

- **Class records** in Excel or a basic system (Mudeer, SMAP)
- **Attendance** marked manually by teachers, reported inconsistently
- **Billing** via bank transfer + WhatsApp — payment links are hard to share, follow-up is manual
- **Student placement** done by gut feel or spreadsheet
- **Teacher management** with no grading, no scheduling consistency
- **No visibility** into class health (which classes are dying, which are thriving)
- **No AI** — every insight requires a human to compile a report

These operators can't see their own business clearly. They know students exist; they don't know if the business is healthy.

**First discovery partner:** Sopan (Ustaz Azim, Sengkembangan) — Islamic group class operator, ~400 students, 50+ teachers, currently on Mudeer + CloseZero + Google Meet. Pain points surfaced in 2026-06-22 meeting.

---

## 2. What We're Building

A **multi-tenant SaaS platform** for any operator that runs structured group learning.

**Not** a replacement for a specific system.
**Not** restricted to Islamic education.
**Not** 1-to-1 tutoring (that's Nakngaji/sifu-tutor).

The product manages the full operational lifecycle of a group class business:
- Create and manage classes (group, mixed, online, physical)
- Enroll students and place them by level
- Track attendance per session
- Bill students automatically, follow up on non-payers
- Pay teachers based on sessions
- Monitor class health
- Use AI to surface insights, draft communications, recommend actions

**One-line positioning:** *Run your classes, not spreadsheets.*

---

## 3. Target Market

### Primary (Malaysia, Phase 1)
| Operator Type | Example | Size |
|---|---|---|
| Islamic learning centers (kelab mengaji) | Sopan, ex-Al-Baghdadi network | 50–500 students |
| Madrasah operators | State-linked and private madrasah | 100–2,000 students |
| Tuition centers (any subject) | Maths, Science, BM tuition centers | 50–300 students |
| Online academies | Google Meet / Zoom based classes | 50–1,000 students |

### Secondary (Phase 2+)
| Operator Type | Notes |
|---|---|
| Physical schools (private/international) | Larger scale, more complex |
| Corporate training groups | Different billing model |
| Pondok/madrasah networks | Multi-branch, requires org hierarchy |
| Southeast Asia expansion | Similar pain points across SG, ID, BN |

### Who is NOT the target (for now)
- 1-to-1 tutoring platforms (that's sifu-tutor / Nakngaji)
- University / LMS platforms (Moodle, Canvas territory)
- Large public schools (government procurement cycle too slow)

---

## 4. Competitive Landscape

*Research completed 2026-06-25. Sources: mudeer.my, smap.my, simtrainsystem.com, skooldash.com, yuran.my, ezflow.my, ieducentre.com, classflow.my, Capterra, Zekolah survey.*

### Market Size
79.8% of Malaysian students attend tuition (Zekolah 2024, n=263, up from 60% in 2020). Average family spend: RM464/month. 67,000+ registered tuition centres (EzFlow estimate — unverified vs MOE). Islamic education (kelas mengaji, tahfiz, madrasah) represents a parallel untracked grassroots network of tens of thousands of micro-operators.

### Competitor Breakdown

| Player | Price Entry | Target | LHDN | Hafazan | Parent App | WhatsApp-Native | Scale |
|---|---|---|---|---|---|---|---|
| **Mudeer** | RM60/mo min (RM3/student) | Islamic education | ❌ | ❌ | ❌ | ❌ (Telegram) | ~100 clients est. |
| **SMAP** | Quote only | Tadika, Islamic school | ❌ | ❌ | ✅ | ✅ | Unknown |
| **SimTrain** | Free / RM80/mo | Tuition centres, multi-branch | ✅ | ❌ | ✅ | Partial | 200+ centres, 500k students |
| **ClassFlow** | RM89/mo | Tadika, tuition | Unknown | ❌ | ✅ | Unknown | Unknown |
| **Skooldash** | ~RM208/mo equiv | Madrasah, tahfiz | ❌ | ✅ | ✅ | ❌ | 500+ inst (self-reported) |
| **Yuran.my** | Free tier | Broad (fee-first) | ❌ | ❌ | Unknown | ✅ | Unknown |
| **EzFlow** | RM89/mo | Service biz (tuition as edge case) | Business only | ❌ | ❌ | ✅ | Unknown |
| **iEduCentre** | Quote only | SG-origin, tuition/music | ❌ | ❌ | ✅ | Unknown | 400k users (claimed) |

### Key Findings Per Competitor

**Mudeer** — The closest Islamic education specialist. Does teacher allowance automation well (testimonial: reduced calculation from 6–9 days to near-instant). But admin-only — zero curriculum/Hafazan tracking, no direct-view attendance dashboard, no class health monitoring, no AI. Pricing RM60/month minimum + RM300 registration fee. Clients include Sopan (SoPaN listed as named client).

**SMAP** — Broader feature set (HR, payroll, donations module, WhatsApp invoice delivery). Targets tadika/taska more than mengaji. No published pricing — creates buyer friction. Site blocks were encountered in research.

**SimTrain** — Most scaled and complete Malaysian player. LHDN e-invoice compliance (significant regulatory advantage). RFID/QR attendance. Multi-branch consolidation. Free tier up to 100 students. BUT: zero Islamic education features, entirely secular tuition focus, no Hafazan tracking, no madrasah positioning.

**Skooldash** — The only player with Hafazan tracking module. But appears India/Bangladesh-origin, annual billing only, hostel/transport modules aimed at large formal madrasah, not agile for small kelas operators. No LHDN compliance.

**Yuran.my** — WhatsApp-native payment links is a genuine local differentiator. But generic platform (also serves sports clubs), no Islamic-specific features, no published pricing.

### The 5 Whitespace Gaps We Exploit

**Gap 1 — Group class as first-class entity (nobody does this)**
All competitors model "student" or "centre" as the core entity. Nobody models "group class" natively. For kelas mengaji operators, the group class IS the operational unit — one teacher, one cohort, one recurring session, rotating syllabus. Architect around the class group, not the student row.

**Gap 2 — Hafazan/Quran progress + admin management in one product**
No Malaysian-origin product covers both. Mudeer = admin only. Skooldash = Hafazan tracking but not Malaysian. The gap: "Student X is on Surah Al-Baqarah ayat 45, paid this month, attended 3/4 sessions, teacher Ustaz Y is paid." Nobody can show this today.

**Gap 3 — LHDN e-invoice compliance for Islamic operators**
SimTrain has it for tuition centres. None of the Islamic education players (Mudeer, SMAP, Skooldash) have it. Mandatory as LHDN rolls out e-invoice requirements.

**Gap 4 — AI features (nobody has real AI)**
ClassFlow mentions "AI tools" vaguely. No competitor has streaming AI insights, smart follow-up drafting, or placement recommendations. This is our clearest product differentiation.

**Gap 5 — Teacher/Ustaz mobile experience**
No product has a strong teacher-facing mobile app for one-tap group attendance marking, live Quran progress update, and pay slip view. Teachers are underserved users.

### Our Competitive Position
We are not building "Mudeer with AI". We are building the first group-class-native, AI-powered management platform for any operator running structured group learning — starting with the Islamic education segment (clearest whitespace) and expanding to secular tuition, schools, and beyond.

---

## 5. Product Name Options

The name must work for:
- Malaysian operators (Islamic + secular)
- Group class context (not 1-to-1)
- SaaS product feel
- Potential international expansion

### Option A — **Kelas**
- Malay word for "class" — immediately understood
- Clean, single word, memorable
- Positions around the core entity (the class)
- Domain: `kelas.my` / `kelasapp.com` / `usekelas.com`
- Tagline: *"Run your classes, not spreadsheets"*
- Risk: Generic, may be hard to trademark

### Option B — **Hadir**
- Malay word for "present" / "attendance"
- Speaks directly to the #1 pain point (attendance visibility)
- Unique, short, memorable
- Domain: `hadir.my` / `hadirapp.com`
- Tagline: *"Every class. Every student. Every payment."*
- Risk: Might imply only attendance tracking, not full management

### Option C — **Klasio**
- Kelas + modern SaaS suffix (-io)
- International feel while rooted in Malay
- Domain: `klasio.com` / `klasio.my`
- Tagline: *"The operating system for group learning"*
- Risk: Slightly awkward pronunciation for English speakers

### Option D — **ClassHQ**
- English, immediately communicates "headquarters for classes"
- Works internationally without translation
- Domain: `classhq.com` / `classhq.my`
- Tagline: *"Your class operations, centralized"*
- Risk: Generic English, less differentiated in Malaysian market

### Decision: **Kelas / kelasapp.com** ✅ Locked 2026-06-25

`kelasapp.com` confirmed available. `kelas.my` and `kelasio.com` are taken.
Tagline: *"Run your classes, not spreadsheets."*

---

## 6. Core Modules (MVP)

Based on Sopan discovery session — these are the minimum to migrate any operator off Mudeer/SMAP.

### Module 1 — Class Management
- Create classes: type (kumpulan kecil, kumpulan besar, individu, family, online, physical)
- Set capacity limits per class
- Assign teacher(s) per class
- Set class schedule (recurring sessions)
- Syllabus management (linear or cyclical/rotating)
- Class health status: green (healthy capacity), yellow (warning), red (critical)

### Module 2 — Student Management
- Student profiles (name, contact, guardian, level)
- Level assessment at intake
- Placement into class by level + availability
- Mid-cycle join support (track where student enters the syllabus)
- Enrollment status (active, paused, dropped)

### Module 3 — Attendance
- Teacher "tik-tik" — marks attendance per session via mobile-friendly interface
- Admin direct-view dashboard — all classes, all sessions, one screen (no clicking into each class)
- Absence tracking + automatic follow-up trigger
- Google Meet integration (future) — identity matching via pre-registration

### Module 4 — Billing & Invoicing
- Monthly subscription billing per student
- Invoice generated automatically (e.g., on 25th of month for next month)
- "Burn" policy enforcement — absent students still billed
- Payment via FPX/bank transfer (FIUU/CIP gateway)
- Payment link sharing — easy copy/share from dashboard
- Manual payment recording (bank transfer confirmation)
- Non-payment follow-up queue

### Module 5 — Teacher Management
- Teacher profiles
- Class assignments
- Session logging (teacher updates sessions completed — drives pay calculation)
- Teacher grading system (A/B/C) for quality tracking
- Pay calculation based on sessions × rate per class type

### Module 6 — Operator Dashboard
- Class health overview (all classes, green/yellow/red at a glance)
- Revenue summary (collected vs outstanding)
- Attendance rate across all classes
- Student count trend (growing / shrinking / stable)

### Module 7 — AI Layer (differentiator)
- **Class health narrative:** "Kelas Asas B has been red 3 weeks. 4 students haven't paid since April."
- **Follow-up message drafting:** Click → AI reads student history → writes WhatsApp/email in operator's tone
- **Student placement recommendation:** Based on level assessment, AI suggests best class
- **Syllabus gap analysis:** Mid-join student — AI identifies what they missed
- **Teacher insights:** AI flags underperforming teachers based on class health trends

---

## 7. Tech Stack

### Decision: Next.js 15 + TypeScript (AI-first SaaS stack)

| Layer | Choice | Reason |
|---|---|---|
| Framework | Next.js 15 (App Router) | Full-stack TypeScript, streaming, Server Actions |
| Language | TypeScript | Type-safe end-to-end, best AI tooling support |
| Database | PostgreSQL (KVM8) | Consistent with ripple-suite, pgvector for AI |
| ORM | Drizzle ORM | Type-safe, fast, Neon/PG compatible |
| Auth + Tenancy | Clerk (Organizations) | Multi-tenant built-in, org switching, roles |
| Platform billing | Stripe / Billplz | Operators pay platform subscription |
| Class billing | FIUU / CIP / FPX | Students pay operators (Malaysian gateway) |
| AI | Vercel AI SDK + Anthropic Claude | Streaming, tool use, RAG — first-class |
| Email | Resend | Transactional + operator comms |
| WhatsApp | WhatsApp Business API | Operators connect their own WA Business number |
| Styling | Tailwind CSS + shadcn/ui | Accessible, fast, consistent |
| Deployment | KVM8 (PM2 + Nginx) | Consistent with ripple-suite |

### Why not Laravel
- AI ecosystem (Vercel AI SDK, Anthropic SDK) is TypeScript-native
- Multi-tenancy with Clerk is architecturally safer than row-level filtering
- Stripe + TypeScript SDK is best-in-class
- Claude Code assists more effectively in TypeScript
- This is a SaaS product, not a rebuild of an existing system

---

## 8. Go-to-Market Strategy

### Phase 1 — Sopan (Validate)
- Onboard Sopan as first paying operator
- Build MVP modules 1–6 with Sopan's workflows as the reference
- Goal: Sopan migrates off Mudeer completely
- Timeline: TBD

### Phase 2 — Warm Network (Grow)
- Nak Ngaji introduces to ex-Al-Baghdadi network (7–8 operators)
- Madrasah/pondok expansion in Pahang via Sopan's network
- Goal: 10 paying operators

### Phase 3 — Self-Serve (Scale)
- Public landing page + self-serve operator signup
- Operator onboards their own teachers and students
- Goal: 50+ operators

### Phase 4 — Expand
- Southeast Asia (Singapore, Indonesia, Brunei)
- Secular tuition centers, corporate training
- Mobile apps for teachers + students

---

## 9. Pricing Model (TBD)

Three options to evaluate:

| Model | Structure | Pros | Cons |
|---|---|---|---|
| Per-student | RM1–3/active student/month | Scales with operator growth | Hard to predict for operator |
| Flat tier | RM99/149/299/month by student count | Predictable for operator | May undertax large operators |
| Revenue share | % of class fees collected | Aligns incentives | Complex to track, operator resistance |

**Recommendation when ready:** Flat tier with student count bands (Starter: up to 100 students, Growth: up to 500, Scale: unlimited). Simple to understand, predictable for both sides.

> To be finalized after Sopan pilot. Don't let pricing block the build.

---

## 10. Open Decisions

| Decision | Status | Notes |
|---|---|---|
| Product name | **LOCKED: Kelas / kelasapp.com** | 2026-06-25 |
| Pricing model | Pending | Finalize after Sopan pilot |
| PostgreSQL host | Pending | KVM8 existing instance or new dedicated DB? |
| WhatsApp integration depth | Pending | Operators bring their own WA Business number? |
| Mobile app | Phase 2 | Teachers need mobile-friendly attendance marking |
| Google Meet integration | Phase 2 | Identity matching via email pre-registration |

---

## 11. GitHub Reference Repos

*Research completed 2026-06-25 across 5 search angles (14 sub-agents, 200+ sources).*

### Recommendation: Start from `ixartz/SaaS-Boilerplate`

No single repo covers all six Kelas modules. The strategy is:
1. **Fork `ixartz/SaaS-Boilerplate`** as the foundation
2. **Reference domain-specific repos** for data model and module design

---

### Foundation (fork this)

| Repo | Stars | License | Why |
|---|---|---|---|
| [ixartz/SaaS-Boilerplate](https://github.com/ixartz/SaaS-Boilerplate) | ~7k | MIT | Next.js 15/16 + TypeScript + Clerk Organizations + Drizzle ORM + PostgreSQL + Stripe + shadcn/ui. Exactly our stack, multi-tenancy pre-wired. |

Alternative if you want Prisma instead of Drizzle: `The-SaaS-Factory/next-14-saas-boilerplate` (Clerk + Prisma, MIT).

---

### Class + Billing Domain (reference)

| Repo | Stars | License | What to borrow |
|---|---|---|---|
| [ivan-my-wong/flowclass](https://github.com/ivan-my-wong/flowclass) | 37 | MIT+AGPL | **Highest relevance** — built for education businesses, not schools. NestJS + Next.js + PostgreSQL. Class scheduling, enrollment approval workflow, Stripe per-class invoicing, student CRM. Missing: attendance, multi-tenancy. |

---

### Attendance Module (reference)

| Repo | Stars | License | What to borrow |
|---|---|---|---|
| [TanvirCou/grade-sync](https://github.com/TanvirCou/grade-sync) | low | Unknown | Prisma + Neon + Clerk — exact stack match. Per-lesson attendance, BigCalendar scheduling, AI attendance pattern analysis. |
| [SchoolyardSMS/SchoolyardSMS](https://github.com/SchoolyardSMS/SchoolyardSMS) | 2 | MIT | Next.js 16 + Bun + Prisma + Shadcn. Multi-status attendance tracking, PWA, broadcast messaging. No billing. |
| [Yogndrr/MERN-School-Management-System](https://github.com/Yogndrr/MERN-School-Management-System) | 1k+ | MIT | Best reference for teacher-facing attendance workflow and report generation logic. MERN stack — study the patterns, not the code. |

---

### Data Model Reference (study, don't fork)

| Repo | Stars | License | What to borrow |
|---|---|---|---|
| [frappe/education](https://github.com/frappe/education) | ~541 | GPL-3.0 | Best education domain model: Program → Batch → Student Group → Course. Maps to Kelas: Enrollment → Cohort → Class → Subject. Multi-site multi-tenancy. Python — reference only. |
| [emirshn/course-management-system](https://github.com/emirshn/course-management-system) | 9 | Unknown | Students + teachers + parents + classes + timetables + attendance — all in one TypeScript repo. Unmaintained since Oct 2023 but data model is solid. |

---

### Billing / Invoicing (reference)

| Repo | Stars | License | What to borrow |
|---|---|---|---|
| [invoiceninja/invoiceninja](https://github.com/invoiceninja/invoiceninja) | ~9.8k | Elastic | **Best recurring billing state machine available.** `RecurringInvoice` model with FREQUENCY_* constants, `next_send_date`, partial payments, overdue logic. PHP — study the state machine, map to TypeScript. |
| [flowglad/flowglad](https://github.com/flowglad/flowglad) | ~1.7k | Unknown | TypeScript + Next.js + Drizzle + Supabase. Subscription primitives that match our stack. Study Drizzle schema + Trigger.dev job scheduling for billing cycle automation. |
| [al1abb/invoify](https://github.com/al1abb/invoify) | ~6.3k | MIT | Next.js + TypeScript + Shadcn + Puppeteer. Best reference for PDF invoice UI and generation pipeline. No backend. |
| [pdovhomilja/nextcrm-app](https://github.com/pdovhomilja/nextcrm-app) | ~519 | MIT | Next.js + Prisma + PostgreSQL. Best-in-class invoice lifecycle data model (create/issue/pay/cancel, PDF, credit notes). Extend with `recurring_schedule` + `billing_cycle_id` + `student_id`. |

---

### License Warnings

| Repo | License | Risk |
|---|---|---|
| LearnHouse, CourseLit | AGPL-3.0 | Cannot incorporate into a closed SaaS product without buying commercial license. Reference only. |
| Invoice Ninja | Elastic | Can read, cannot redistribute commercially. Reference only. |
| Edu-Sekai | Proprietary | All rights reserved — reference architecture only, no code. |

---

### Confirmed Gap = Market Opportunity

No single open-source TypeScript/Next.js project combines: group class scheduling + attendance + recurring billing + multi-tenancy for the education SME (tuition centre / madrasah) vertical. Every existing project handles 2–3 of these. **That gap is Kelas.**

---

## 12. What's Next

1. ✅ Competitor research completed (Section 4)
2. ✅ Product name locked: Kelas / kelasapp.com
3. ✅ GitHub repo landscape researched (Section 11)
4. ✅ Foundation: scaffolded from `ixartz/SaaS-Boilerplate` → `/kelas` repo (local only, 2026-06-25)
5. ✅ PRD written — `PRD.md` (7 modules, 42 user stories)
6. ✅ Data model designed — `DATA-MODEL.md` (15 tables, Drizzle schema, multi-tenant)
7. ✅ Dev environment running — PGlite + Next.js 16 at localhost:3000, migrations applied
8. ✅ Landing page branded — Kelas copy, pricing, FAQ, no boilerplate remnants
9. ✅ UI/UX reference research completed — `UI-RESEARCH.md` (6 agent search, 3 categories)
10. Hafiz reviews and decides UI references per category (landing page, dashboard, domain)
11. Design system defined (brand colour, typography, component tokens)
12. Admin dashboard shell built (sidebar, navigation, org switcher)
13. Module 1 — Class Management screens built
14. Module 3 — Attendance screens built

---

## 13. Document Index

| Document | Purpose |
|---|---|
| `PRODUCT-BRIEF.md` | This file — product overview, strategy, decisions |
| `PRD.md` | Full product requirements — user stories, acceptance criteria |
| `DATA-MODEL.md` | PostgreSQL schema (15 tables, Drizzle notation) |
| `OVERVIEW.md` | Public-facing product overview for partners/clients |
| `EXECUTIVE-SUMMARY.md` | 2-page compressed version for cold outreach |
| `UI-RESEARCH.md` | UI/UX reference research — all options, comparisons, decisions |

---

*This document will be updated as decisions are made. It is the source of truth for the product before a codebase exists.*
