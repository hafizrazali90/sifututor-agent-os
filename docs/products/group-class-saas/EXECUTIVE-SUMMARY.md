# Kelasapp — Executive Summary

**Group Class Management Platform for Southeast Asia**
kelasapp.learnestlab.com · Private Beta (live) 2026

---

## The Opportunity

Malaysia has over 67,000 registered tuition centres and a parallel network of tens of thousands of Islamic learning operations — madrasah, kelas mengaji, tahfiz, and pondok. 79.8% of Malaysian students attend tuition; average household spend is RM464/month on education (Zekolah, 2024).

Every one of these operators shares the same problem: they run a real business on WhatsApp, Excel, and hope. Attendance is marked in group chats. Fees are chased individually. Teacher pay is calculated by hand at month-end. Nobody has real visibility into whether the business is growing or shrinking.

The platforms serving this market — Mudeer, SimTrain, ClassFlow — have not meaningfully innovated in years. None have AI. None are built around the group class as the core business entity. None serve both Islamic and secular operators.

---

## What We're Building

**Kelasapp** is a multi-tenant SaaS platform that manages the full operational lifecycle of any group class business: class scheduling, student enrolment, attendance tracking, fee collection, teacher pay, and AI-powered business insights — in a single platform.

**One-line pitch:** Run your classes, not spreadsheets.

Kelasapp is not a tutoring marketplace. It is not a school ERP. It is purpose-built for the operator running recurring group sessions — Islamic or secular, online or physical, 50 students or 2,000.

---

## Product

Seven integrated modules:

| Module | What It Does |
|---|---|
| **Class Management** | Create classes with type, capacity, schedule, and assigned teacher. Live health signal (green/yellow/red) for every class. |
| **Student Management** | Profiles, enrolment, level tracking, mid-cycle join support. |
| **Attendance** | One-tap mobile marking for teachers. Admin cross-class dashboard — all sessions, one screen. Automatic absence alerts. |
| **Billing & Invoicing** | Auto-generated monthly invoices. FPX payment links for WhatsApp sharing. Non-payment queue. LHDN e-invoice fields. |
| **Teacher Management** | Pay calculated automatically from session count × rate. Pay slips accessible to teachers. |
| **Operator Dashboard** | Business snapshot on login — class health, revenue, attendance, action queue. |
| **AI Layer** | Plain-English class health narratives. One-click follow-up message drafting. At-risk student detection. Placement recommendations. |

---

## Differentiation

Five gaps no competitor fills:

1. **Group class as the core entity** — competitors model the student or centre. We model the class.
2. **Admin + curriculum in one product** — no Malaysian platform shows attendance + payment + learning progress together.
3. **LHDN e-invoice compliance for Islamic operators** — SimTrain has it for secular. Nobody has it for Islamic education.
4. **Real AI** — not a buzzword. Streaming insights, message drafting, risk detection.
5. **Teacher mobile experience** — the most underserved user in this market.

---

## Market & Competition

| Competitor | Price | LHDN | AI | Islamic Features | Key Gap |
|---|---|---|---|---|---|
| Mudeer | RM60/mo | ❌ | ❌ | ✅ | No visibility, admin-only |
| SimTrain | Free–RM80 | ✅ | ❌ | ❌ | Zero Islamic support |
| Skooldash | ~RM208/mo | ❌ | ❌ | Partial | Not Malaysian, no LHDN |
| **Kelasapp** | RM99–299/mo | ✅ | ✅ | ✅ | — |

---

## Business Model

SaaS subscription per operator. Flat tier by student count — predictable for both sides.

| Tier | Monthly | Students |
|---|---|---|
| Starter | RM99 | Up to 100 |
| Growth | RM199 | Up to 500 |
| Scale | RM299 | Unlimited |

No per-student fees. No transaction fees on class payments beyond FIUU's gateway rate.

---

## Go-to-Market

**Phase 1 (Now)** — Onboard Sopan (Sengkembangan, ~400 students) as the founding operator. Validate product-market fit and refine workflows. Sopan migrates off Mudeer.

**Phase 2 (Q4 2026)** — Warm network expansion via Nak Ngaji's ex-Al-Baghdadi operator network and Sopan's introductions into Pahang madrasah. Target: **10 paying operators**.

**Phase 3 (2027)** — Self-serve public onboarding. Teacher and student mobile apps. Target: **50+ operators**.

**Phase 4** — Southeast Asia expansion (Singapore, Indonesia, Brunei). Secular tuition and corporate training.

---

## Traction

- **Sopan** confirmed as founding partner following a 2026-06-22 discovery session with Ustaz Azim.
- Product built and deployed live in private Beta (2026-07-05). Product brief, full PRD, and data model complete.
- Built by **Learnest Lab Malaysia (LLM)** — creators of Nakngaji, Malaysia's leading 1-to-1 Islamic tutoring platform. Deep domain knowledge, existing operator network, and established technical infrastructure.

---

## Technology

- Modern cloud-native stack: Next.js, TypeScript, PostgreSQL
- Multi-tenant by design — operator data is fully isolated
- FPX payments via FIUU (licensed Malaysian payment gateway)
- AI via Anthropic Claude API with Vercel AI SDK
- Compliant with PDPA and LHDN e-invoice requirements

---

## Contact

**Learnest Lab Malaysia (LLM)**
kelasapp.learnestlab.com (live, private Beta)

---

*Kelasapp is a product by Learnest Lab Malaysia (LLM).*
