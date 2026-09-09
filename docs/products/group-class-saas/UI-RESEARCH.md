# Kelas — UI/UX Reference Research
**Last updated:** 2026-06-25
**Status:** In review — decisions pending per section
**Purpose:** Document all open-source projects researched as UI/UX references for Kelas. Covers marketing landing page, admin dashboard, and domain-specific patterns.

---

## Research Method

Six parallel research agents were run on 2026-06-25 covering:
1. SaaS admin dashboards (shadcn/ui + Next.js focus)
2. Service-based business management platforms (gym, booking, membership)
3. Marketing landing page templates and live SaaS sites
4. Open-source SaaS boilerplates
5. Live SaaS products with notable landing pages (Dub, Midday, OpenStatus, Inbox Zero)
6. SE Asia design context and market-specific recommendations

Approach: tiru-vasi (copy and innovate) — find reputable open-source projects, study their UI patterns, adapt for Kelas. All code references are MIT or GPL unless noted as inspiration-only (AGPL).

---

## Category 1 — Marketing Landing Page

The public-facing site visitors see before signing up. Current state: boilerplate ixartz copy with Kelas content, no visual polish.

### Options Reviewed

#### Option A — `nobruf/shadcn-landing-page`
- **URL:** https://github.com/nobruf/shadcn-landing-page
- **Stars:** ~1,200
- **License:** MIT ✅ (most permissive — copy freely into any project)
- **Stack:** Next.js + shadcn/ui + TypeScript + Tailwind CSS
- **Demo:** https://shadcn-landing-page-livid.vercel.app
- **Sections:** navbar, mobile sidebar, hero, sponsors, benefits, testimonials, pricing, FAQ, footer
- **Pros:** MIT license, Next.js App Router (same stack as Kelas), composable with installed shadcn components, dark mode support
- **Cons:** Lower visual polish out of the box, fewer sections than leoMirandaa variant
- **Use case:** Drop-in code base to build on top of

#### Option B — `leoMirandaa/shadcn-landing-page`
- **URL:** https://github.com/leoMirandaa/shadcn-landing-page
- **Stars:** ~1,900
- **License:** MIT ✅
- **Stack:** Vite + React + TypeScript + shadcn/ui + Tailwind CSS ⚠️ (NOT Next.js)
- **Demo:** https://shadcn-landing-page.vercel.app
- **Sections:** 16 sections — hero, sponsors, about, stats, how-it-works, features, services, CTA, testimonials, team, pricing, newsletter, FAQ, footer
- **Pros:** MIT, most complete section coverage of any free template, dark mode, stats callout block
- **Cons:** Vite/React SPA — different stack to Kelas (Next.js App Router). Would require rewriting components
- **Use case:** Design reference only — study section structure, don't copy code

#### Option C — Cruip Simple Light
- **URL:** https://github.com/cruip/tailwind-landing-page-template
- **Stars:** ~4,500
- **License:** GPL ⚠️ (free for personal + commercial use; cannot resell/redistribute as a template)
- **Stack:** Next.js App Router + Tailwind CSS v4 + TypeScript + React Server Components
- **Demo:** https://simple.cruip.com
- **Figma:** Included ✅
- **Design:** Light/minimal — whites and light grays, subtle geometric decorative elements (planets, stripes, gradients). Centered hero with dual CTA. Clean sans-serif. Generous whitespace.
- **Sections:** hero, logo strip, 6-card feature grid, single testimonial, footer
- **Pros:** Best visual quality of free templates, Next.js App Router (same stack), Figma file included, looks professionally designed out of the box
- **Cons:** GPL license (more restrictive than MIT — fine for Kelas own product, cannot resell template), fewer sections than leoMirandaa
- **Use case:** Highest visual quality starting point

#### Option D — Cruip Open React Template
- **URL:** https://github.com/cruip/open-react-template
- **Stars:** ~4,700
- **License:** GPL ⚠️
- **Stack:** Next.js + Tailwind CSS v4 + TypeScript
- **Demo:** https://open.cruip.com
- **Figma:** Included ✅
- **Design:** Light base (despite "open/dark" name — the live demo is light). Blurred gradient accent shapes, soft illustrations, hero with video thumbnail embed, 3-col feature workflow, feature matrix, 9-card testimonials grid.
- **Pros:** More sections than Simple Light, Figma included, gradient blur treatment gives visual depth
- **Cons:** GPL, slightly denser layout than Simple Light
- **Use case:** If Kelas wants visual depth and more sections without going dark

#### Option E — Dub.co (inspiration only)
- **URL:** https://github.com/dubinc/dub
- **Stars:** ~23,700
- **License:** AGPL-3.0 ⛔ (cannot copy code into closed commercial SaaS)
- **Live site:** https://dub.co
- **Stack:** Next.js + Tailwind CSS + custom @dub/ui design system
- **Design:** Light mode primary. Bold short hero headline ("Turn clicks into revenue"). White/light backgrounds, dark text, blue accents, generous whitespace. Card-based feature sections per product pillar. Live counter animations showing platform scale. Customer logos (Twilio, Vercel, Framer, Perplexity). Interactive feature demos. Changelog section on homepage.
- **What to learn:** Hero structure (short headline + 1-sentence sub + dual CTA + trust micro-copy), feature card layout, customer logo strip treatment, metrics callout, two-track CTA ("Start for free" + "Get a demo")
- **Use case:** Visual benchmark — study the design decisions, do not copy code

#### Option F — Midday (inspiration only)
- **URL:** https://github.com/midday-ai/midday
- **Stars:** ~14,200
- **License:** AGPL-3.0 ⛔
- **Live site:** https://midday.ai
- **Design:** Dark-first. Deep dark navy/charcoal backgrounds, bright white typography, teal/blue accents. High contrast, low color saturation. Italic word emphasis in hero headline ("The business stack for *modern* founders"). ROI/time-savings callout ("4–6 hours saved"). "14-day free trial · Cancel anytime" trust line directly under CTA.
- **What to learn:** Italic headline emphasis technique, ROI callout blocks, feature card grids with per-function screenshots, trust micro-copy positioning under CTA
- **Use case:** Visual benchmark for premium dark aesthetic; also study the "14-day trial" micro-copy pattern

#### Option G — OpenStatus (inspiration only)
- **URL:** https://github.com/openstatusHQ/openstatus
- **Stars:** ~8,800
- **License:** AGPL-3.0 ⛔
- **Live site:** https://openstatus.dev
- **What to learn:** Pricing transparency in hero ("Free to start. Paid plans from $30/mo") — SE Asian SMB operators are price-sensitive and respond to upfront pricing
- **Use case:** Copy the pricing-in-hero pattern only

---

### Comparison Matrix — Marketing Landing Page

| | nobruf (A) | leoMirandaa (B) | Cruip Simple (C) | Cruip Open (D) | Dub (E) | Midday (F) |
|---|---|---|---|---|---|---|
| License | MIT ✅ | MIT ✅ | GPL ⚠️ | GPL ⚠️ | AGPL ⛔ | AGPL ⛔ |
| Can copy code | Yes | Yes | Yes (own product) | Yes (own product) | No | No |
| Stack match | ✅ Next.js | ❌ Vite | ✅ Next.js | ✅ Next.js | ✅ Next.js | ✅ Next.js |
| Visual polish | Medium | Medium | High ✅ | High ✅ | Very High | Very High |
| Figma included | No | No | Yes ✅ | Yes ✅ | No | No |
| Dark mode | Yes | Yes | No | Yes | No (default) | Yes |
| Section count | Medium | Most (16) | Fewer | More | Full site | Full site |
| Stars | 1.2k | 1.9k | 4.5k | 4.7k | 23.7k | 14.2k |

### Recommendation
- **Code base:** Cruip Simple Light (C) — best visual quality, Next.js, Figma included. GPL is fine for Kelas own product.
- **Visual benchmark:** Dub.co (E) — aim for this quality level when styling
- **Patterns to steal:** Midday's "14-day trial" micro-copy, OpenStatus's pricing-in-hero, leoMirandaa's 16-section structure

### Decision
- [ ] **PENDING** — Hafiz to review and decide

---

## Category 2 — Admin Dashboard (Web App Shell)

The authenticated application shell — sidebar, navigation, page layout — that all Kelas modules (Class Management, Attendance, Billing, etc.) sit inside.

### Options Reviewed

#### Option A — `satnaing/shadcn-admin`
- **URL:** https://github.com/satnaing/shadcn-admin
- **Stars:** ~12,400 (most starred in entire shadcn dashboard space)
- **License:** MIT ✅
- **Stack:** Vite + TanStack Router + shadcn/ui + Tailwind CSS + TypeScript ⚠️ (NOT Next.js)
- **Demo:** https://shadcn-admin.netlify.app
- **Features:** Collapsible sidebar with icon-only mode, Cmd+K global command palette, 10+ pages, light/dark mode, RTL support, custom components beyond standard shadcn
- **Pros:** Most visually refined free shadcn dashboard available, best sidebar polish, highest community validation
- **Cons:** Vite SPA not Next.js — routing is different. Cannot copy pages directly, must adapt components
- **Use case:** Primary visual reference for sidebar design and command palette

#### Option B — `Kiranism/next-shadcn-dashboard-starter`
- **URL:** https://github.com/Kiranism/next-shadcn-dashboard-starter
- **Stars:** ~6,600
- **License:** MIT ✅
- **Stack:** Next.js 16 + App Router + React 19 + shadcn/ui + Tailwind v4 + TanStack Table + TanStack Form + Zod + Clerk + Recharts + Zustand + nuqs
- **Demo:** https://dub.sh/shadcn-dashboard
- **Features:** Clerk Organizations multi-tenancy built in, server-prefetched TanStack Tables with URL state (nuqs) for search/filter/pagination, analytics overview, user/product management, kanban, billing/subscription, plan-gated content, six theme variants
- **Pros:** Same stack as Kelas (Next.js + Clerk + shadcn), Clerk multi-tenancy already wired, TanStack Table pattern is gold standard for student/class list pages
- **Cons:** Less visually polished sidebar than satnaing
- **Use case:** Best code-level reference — same tech stack, multi-tenancy already done

#### Option C — `arhamkhnz/next-shadcn-admin-dashboard`
- **URL:** https://github.com/arhamkhnz/next-shadcn-admin-dashboard
- **Stars:** ~2,600
- **License:** MIT ✅
- **Stack:** Next.js 16 + App Router + TypeScript + Tailwind CSS v4 + shadcn/ui + React Hook Form + Zustand + TanStack Table + Zod + Biome
- **Demo:** https://next-shadcn-admin-dashboard.vercel.app
- **Features:** Multiple dashboard personas including **Academy dashboard** — directly domain-aligned. Also includes Email, Chat, Calendar, Kanban, Tasks, Invoice, Users, Roles pages. Multiple theme presets. Collapsible sidebar.
- **Pros:** Has an **Academy dashboard** out of the box, Roles/Users/Invoice pages map to Kelas modules, Next.js App Router (same stack)
- **Cons:** Lower stars than satnaing/Kiranism — less community validation
- **Use case:** Closest domain match — Academy dashboard is essentially Kelas admin

#### Option D — `Qualiora/shadboard`
- **URL:** https://github.com/Qualiora/shadboard
- **Stars:** ~679
- **License:** MIT ✅
- **Stack:** Next.js 15 + App Router + React 19 + TypeScript + Tailwind v4 + shadcn/ui + NextAuth.js + React Hook Form + Zod + TanStack Table + Recharts + **FullCalendar** + i18n
- **Demo:** https://shadboard.vercel.app
- **Features:** FullCalendar fully integrated — interactive calendar for weekly timetables and scheduling. Also Email, Chat, Kanban, settings with billing/plan pages, theme customizer.
- **Pros:** Only template with FullCalendar built in — directly relevant for class weekly schedule view, Next.js App Router
- **Cons:** Lowest stars (679), uses NextAuth instead of Clerk
- **Use case:** Reference specifically for the class schedule calendar screen

#### Option E — `shadcnstore/shadcn-dashboard-landing-template`
- **URL:** https://github.com/shadcnstore/shadcn-dashboard-landing-template
- **Stars:** ~816
- **License:** MIT ✅
- **Stack:** Next.js 15 + App Router + React 19 + TypeScript + Tailwind v4 + shadcn/ui + TanStack Table + Recharts + Zustand
- **Demo:** https://shadcnstore.com/templates/dashboard/shadcn-dashboard-landing-template/dashboard
- **Features:** Ships BOTH marketing landing page AND admin dashboard in one Next.js repo — 30+ pages including 2 dashboard variants, Mail, Tasks, Chat, Calendar, Users, billing, 3 login variants, and a landing page with hero/features/pricing/FAQ
- **Pros:** Single repo for both marketing site and app — no separate project, MIT, 30+ pages
- **Cons:** Lower stars (816), less polished than satnaing/Kiranism
- **Use case:** If Kelas wants one Next.js repo for both marketing site + app

#### Option F — `marmelab/shadcn-admin-kit`
- **URL:** https://github.com/marmelab/shadcn-admin-kit
- **Stars:** ~982
- **License:** MIT ✅
- **Stack:** shadcn/ui + Tailwind + React Router + TanStack Query + React Hook Form + React Admin ⚠️ (not Next.js)
- **Demo:** https://marmelab.com/shadcn-admin-kit/demo
- **Features:** Built on React Admin — battle-tested for data-heavy admin panels. Pre-built CRUD List/Show/Edit/Create pages with sorting, filtering, bulk actions, export, column visibility, pagination. Compatible with 50+ data providers.
- **Pros:** Best reference for heavy CRUD UI — managing hundreds of students, attendance records, payment histories. Bulk actions are done.
- **Cons:** Not Next.js, different routing
- **Use case:** Reference for CRUD-heavy page patterns (student list, invoice list, attendance table)

---

### Comparison Matrix — Admin Dashboard

| | satnaing (A) | Kiranism (B) | arhamkhnz (C) | shadboard (D) | shadcnstore (E) | marmelab (F) |
|---|---|---|---|---|---|---|
| License | MIT ✅ | MIT ✅ | MIT ✅ | MIT ✅ | MIT ✅ | MIT ✅ |
| Stack match | ❌ Vite | ✅ Next.js | ✅ Next.js | ✅ Next.js | ✅ Next.js | ❌ React Router |
| Clerk built in | No | Yes ✅ | No | No | No | No |
| Visual polish | Very High ✅ | High | Medium-High | Medium | Medium | Medium |
| Stars | 12.4k ✅ | 6.6k | 2.6k | 679 | 816 | 982 |
| Domain match | Generic | Generic | Academy ✅ | Generic | Generic | Generic |
| Calendar | No | No | No | FullCalendar ✅ | No | No |
| TanStack Table | No | Yes ✅ | Yes | Yes | Yes | No |
| Includes landing | No | No | No | No | Yes ✅ | No |

### Recommendation
- **Sidebar/shell visual reference:** satnaing/shadcn-admin (A) — highest polish, most community-validated sidebar design
- **Code base for tables/list pages:** Kiranism (B) — same stack, Clerk multi-tenancy, TanStack Table
- **Domain reference:** arhamkhnz (C) — has Academy dashboard, see how they structured it
- **Calendar screen:** Qualiora/shadboard (D) — only one with FullCalendar

### Decision
- [ ] **PENDING** — Hafiz to review and decide

---

## Category 3 — Domain-Specific References (Similar Use Case to Kelas)

Projects that solve a similar problem — managing people, sessions, scheduling, and billing — even if not in education.

### Options Reviewed

#### Cal.com / Cal.diy
- **URL:** https://github.com/calcom/cal.diy (MIT core) | https://github.com/calcom/cal.com (AGPL full)
- **Stars:** ~45,800 (cal.diy MIT) / ~41,000+ (cal.com AGPL)
- **License:** MIT (cal.diy) / AGPLv3 (cal.com)
- **Stack:** Next.js 15 + React + TypeScript + Tailwind CSS + tRPC + Prisma + PostgreSQL
- **Domain match:** Scheduling platform — booking flows, recurring events, event types, timezone handling, team availability
- **Relevant patterns:**
  - Weekly schedule grid — cleanest open-source scheduling calendar available
  - Event type list — maps to class catalogue
  - Multi-step booking wizard — maps to class enrolment flow
  - Team scheduling — maps to multi-teacher session management
  - Availability editor — maps to teacher availability
- **Cal.diy MIT core** may be partially reusable (not just inspirational)
- **Note:** Cal.com went closed-source in early 2026; cal.diy is the MIT community fork

#### Solidtime
- **URL:** https://github.com/solidtime-io/solidtime
- **Stars:** ~8,700
- **License:** AGPL-3.0
- **Stack:** Laravel (PHP) + Vue.js + TypeScript + Tailwind CSS + Inertia.js
- **Domain match:** Time tracking SaaS — client list, project/session list, billable rate per session, invoice generation, multi-org with roles
- **Relevant patterns:**
  - Session/project list layout — maps to class list
  - Client list — maps to student list
  - Billable rate config per client/project — maps to per-class or per-student fee
  - Invoice generation and billing reports — maps to monthly billing
  - Multi-org with role-based access — maps to admin vs teacher vs parent roles
- **Design quality:** Highest design quality in Laravel + Vue/Inertia space. Feels like commercial SaaS.
- **Note:** Stack overlap with sifu-tutor (Laravel + Inertia). UI patterns translate to React even though frontend is Vue.

#### ClassroomIO
- **URL:** https://github.com/classroomio/classroomio
- **Stars:** ~1,580
- **License:** AGPL-3.0
- **Stack:** SvelteKit + Supabase + TailwindCSS
- **Domain match:** Multi-tenant course/class management platform
- **Relevant patterns:**
  - Multi-tenant org-switcher — maps to Kelas operator switching
  - Sidebar dashboard layout
  - Course cards — maps to class cards
  - Role-based views (teacher vs student)
  - Clean empty states
  - Multi-teacher-per-organisation model
- **Gap:** Light on physical attendance tracking and recurring fee invoicing

#### MemberMatters
- **URL:** https://github.com/membermatters/MemberMatters
- **Stars:** ~87
- **License:** MIT ✅
- **Stack:** Django + Python backend, Vue.js + TypeScript frontend
- **Domain match:** Membership management for clubs/makerspaces
- **Relevant patterns:**
  - **Member profile page** — status + payment history + access/attendance log in one scrollable view. Best reference for Kelas student profile page.
  - Recurring Stripe billing with self-service cancel/update
  - Membership status dashboard
  - Dark mode support
- **Note:** Low stars but MIT and highly relevant profile page pattern

#### Gymie
- **URL:** https://github.com/lubusIN/laravel-gymie
- **Stars:** ~471
- **License:** MIT ✅
- **Stack:** Laravel 12 + Filament Admin Panel 5.x + Livewire 3 + PHP 8.2
- **Domain match:** Gym management — member roster, attendance, membership billing, PDF invoices
- **Relevant patterns:**
  - Filament-powered member CRUD with sortable/filterable tables
  - Attendance tracking (time-based)
  - PDF invoice generation
  - Membership/subscription management
- **Note:** Most relevant for sifu-tutor (Laravel + Filament) rather than Kelas (Next.js)

#### Costasiella (archived)
- **URL:** https://github.com/costasiella/costasiella
- **Stars:** ~36
- **License:** GPL-2.0
- **Stack:** Django + GraphQL + React + Apollo Client
- **Status:** Archived January 2026 — read-only, fully complete
- **Domain match:** Multi-discipline studio management (Yoga, Dance, Karate, Fitness) — closest feature parity to Kelas of any open-source project
- **Relevant patterns:**
  - Class schedule → session enrolment → attendance sheet → monthly invoice pipeline
  - Customer subscription and class pass tracking
  - Capacity management per class
  - Instructor payment calculation — maps to teacher payout
  - Mollie recurring billing integration
- **Note:** Archived so no active development. Use as domain model blueprint only, not visual reference.

---

### Comparison Matrix — Domain-Specific

| | Cal.diy | Solidtime | ClassroomIO | MemberMatters | Gymie | Costasiella |
|---|---|---|---|---|---|---|
| License | MIT ✅ | AGPL | AGPL | MIT ✅ | MIT ✅ | GPL |
| Stack | Next.js | Laravel+Vue | SvelteKit | Django+Vue | Laravel | Django+React |
| Design quality | Very High | Very High | Good | Good | Good (Filament) | Basic |
| Scheduling UI | Best-in-class ✅ | Session list | Course cards | No | No | Class schedule |
| Student/member roster | No | Client list | Student list | Member list ✅ | Member list | Student list ✅ |
| Attendance | No | No | Partial | Access log | Yes ✅ | Yes ✅ |
| Billing/invoicing | No | Yes ✅ | No | Stripe billing | PDF invoices | Monthly invoices ✅ |
| Multi-tenant | Yes ✅ | Yes ✅ | Yes ✅ | No | No | No |
| Feature parity to Kelas | Scheduling only | High (minus attendance) | Medium | Medium | High | Very High ✅ |

### Recommendation
- **Scheduling/calendar UI:** Cal.diy — gold standard, MIT, study the weekly grid and booking flow
- **Session + billing patterns:** Solidtime — best design quality, maps client→project→session→invoice to student→class→session→invoice
- **Student profile page layout:** MemberMatters — member profile with status + billing + attendance in one view (MIT)
- **Domain blueprint:** Costasiella — the only project with the full Kelas pipeline end-to-end, use as feature/screen reference

### Decision
- [ ] **PENDING** — Hafiz to review and decide

---

## SE Asia Design Context

Researched specific design considerations for the Malaysian/SEA market:

### Color Palette Recommendation
| Role | Color | Hex | Reasoning |
|---|---|---|---|
| Brand primary | Deep teal | `#0D7C6E` | Between trust-blue and growth-green — modern, educational without being generic |
| Brand accent | Mint | `#2BA898` | Lighter teal for hover states, badges |
| CTA | Warm coral | `#E8603C` | Strong contrast, energy, stands out against teal |
| Background | Off-white | `#F8F9FA` | Avoids harsh pure-white |
| Alt section | Pale mint | `#F0FAF8` | Section alternation |
| Text primary | Near-black | `#1A1A2E` | Better than pure black |
| Text secondary | Mid-grey | `#6B7280` | Supporting text |
| Borders | Light grey | `#E5E7EB` | Dividers |

> Note: Colors are a research recommendation — final decision by Hafiz

### Typography
- **Recommended:** Inter or Plus Jakarta Sans
- Both have excellent Malay/Latin coverage
- Render well on Chrome Android (dominant browser in Malaysia/Indonesia)
- Available on Google Fonts (low latency in SE Asia)
- Minimum body size: 16px (never below 15px — mid-range Android rendering)

### Mobile-First Requirements
- Target under 2 seconds LCP on 4G
- Minimum 48px tap targets
- Sticky bottom CTA bar on mobile (highest-converting pattern for SMB SaaS)
- Test on Samsung Galaxy A-series (dominant device in Malaysia/Indonesia)
- Signup form: email only upfront — ask centre name, phone during onboarding

### SE Asia-Specific Patterns
- **WhatsApp CTA converts better than contact forms** for Malaysian/Indonesian SMB operators
- **Show pricing upfront** — price-sensitive SMB buyers leave pages that hide pricing
- **Local social proof converts better** — "Used by 500+ learning centres in Malaysia" > Fortune 500 logos
- **Bahasa Malaysia toggle consideration** — even if operators read English, BM signals "built for us"

### Recommended Landing Page Section Order
1. Nav — Logo + Features/Pricing links + sticky "Start free" CTA
2. Hero — headline + sub + dual CTA + product screenshot + logo strip
3. Problem strip — 3 pain points ("Chasing payments via WhatsApp", "Lost in spreadsheets", "No student progress visibility")
4. How it works — 3 steps: "Add your classes → Enrol students → Get paid automatically"
5. Features grid — 3-4 cards: Class Scheduling / Billing & Invoicing / Student Progress / Reporting
6. Testimonials — 2-3 quotes from Malaysian/regional operators with name + centre + photo
7. Pricing — 2-3 tiers, monthly/annual toggle, "Most Popular" highlighted
8. FAQ — 6-8 questions (free trial, multiple branches, payment gateways, Bahasa)
9. Final CTA — repeat hero CTA
10. Footer — logo, nav, social, WhatsApp contact, privacy/terms

---

## Category 4 — Visual identity & component polish (mature, not generic/AI)

**Researched:** 2026-06-28 (3 parallel research agents). **Goal (Hafiz):** every screen should look professional, consistent, mature, not AI-generated or generic.

### Why it looks generic right now
The "AI / generic shadcn" look is a fingerprint of accepted **defaults**, not a shadcn limitation. The tells: slate/zinc neutrals, `0.5rem` radius on everything, default Inter at default sizes, the stock card border + soft shadow, no brand colour (or a generic violet), and cramped uniform `gap-4` spacing. Kelasapp runs on those defaults today. The fix is to edit **design tokens once** (colour, radius, font, shadow, spacing); every component updates everywhere. You do NOT rewrite components.

### A. Theme/identity pass (highest leverage, do first)
Prioritised; Tier 1 is roughly one hour and transforms the look:
1. Replace slate/zinc neutrals with a warm tinted neutral.
2. One saturated brand accent, rationed to a single primary action per screen (no second accent).
3. Move radius off the default `0.5rem` to a deliberate value (e.g. `0.625rem`).
4. Commit the font intentionally (see C) and add a display face for headings.
5. Border-first elevation: hairline 1px borders + one signature soft shadow; remove the default heavy shadow.
6. Strict 8px spacing scale, then double section gaps (generous whitespace).
Tool: **tweakcn.com** (edits the shadcn OKLCH tokens visually). Capture the tokens in a `design.md` the AI must follow.

### B. Component & interaction references (anchor)
- **Anchor: shadcn/ui official + satnaing/shadcn-admin** (both MIT, Radix-native, TW v4, already adopted).
- **Build a shared `ConfirmDialog`** modelled on satnaing's `confirm-dialog.tsx` (AlertDialog + `destructive` prop + `isLoading` + verb labels). Highest-leverage consistency move; replaces hand-rolled dialogs (VoidDialog, the QR error modal follows this too).
- **Toasts: standardise on `sonner`** (shadcn default); ban one-off success/alert messages.
- **Build a shared `EmptyState`** (variants: first-use / no-results / error).
- **Harvest** polished alert/empty/banner variants from **Origin UI** (free, Radix) but vendor the code in (it is "pre-acquisition / limited maintenance"; do not depend on it).
- Canonical confirm dialog: title is a question naming the object ("Void invoice #1042?"), description states the consequence, verb buttons, destructive = red, Cancel holds focus. Icon-in-tinted-circle only for high-severity/irreversible actions or standalone errors (exactly our QR error modal).

### C. Typography & colour identity (recommended; Hafiz to confirm)
- **Font: Inter** (self-hosted, `latin` subset, WOFF2, variable), with **tabular numerals + slashed zero** on globally; its tabular figures win the invoice/amount tables. Optional **Plus Jakarta Sans** Bold for marketing/headings only (or Inter 800 to ship one font). Avoid Geist (weak at small sizes on mid-range Android).
- **Colour (refined from the SE-Asia draft):** deep **teal `#0E6E63`** primary/CTA; **emerald `#1F9D74`** success / "Paid"; **warm near-black `#15171A`** text (the earlier `#1A1A2E` is navy and fights the teal); warm off-white `#FBFBF9` canvas; **coral `#E8603C` demoted** to a secondary/marketing accent (green/teal CTAs test more trustworthy for money actions); **clean red `#D7263D`** for destructive (distinct from coral). Teal only for >=16px text/controls (AA). OKLCH token map captured by the research; tune in tweakcn.
- Avoid the over-used "startup blue" and the violet "AI-startup" cliché; teal is the deliberate, mature anchor.

### D. Products to emulate (and what to copy)
- **Wise** — Inter workhorse + display face, one confident colour used sparingly (closest model: a money tool).
- **Mercury** — calm, monochromatic, sharp typesetting; UI and marketing feel like one system.
- **Ramp** — taming a saturated accent with whitespace (permission + guardrail for the coral).
- **Linear / Stripe / Vercel** — monochrome base + one rationed accent + border-first depth + doubled whitespace + intentional type.

### Recommendation / build order
1. **Theme pass** in tweakcn (teal primary, warm neutral, radius `0.625`, border-first, remove default shadow) + self-host Inter with tabular nums. The single biggest "mature vs generic" win.
2. **Component standards:** shared `ConfirmDialog` (model satnaing), `sonner` toasts, `EmptyState`; document in UI-CONVENTIONS.
3. Apply across screens (per-page spacing/typography pass) as we build M6.

### Decision
- [ ] **Identity (font + palette) — Hafiz to confirm** (recommended: Inter + optional Plus Jakarta Sans; deep teal `#0E6E63` + emerald + warm-neutral ink + demoted coral + clean red)
- [ ] **Theme pass + component standards — approve to implement**

---

## Overall Summary for Decision Making

### Marketing Landing Page — pick one code base, one visual benchmark

| Role | Pick | Why |
|---|---|---|
| Code base | Cruip Simple Light OR nobruf/shadcn-landing-page | Best quality (Cruip) vs best license (nobruf MIT) |
| Visual benchmark | Dub.co | Best-in-class modern SaaS landing |
| Section structure | leoMirandaa's 16-section order | Most complete blueprint |

### Admin Dashboard — pick by purpose

| Purpose | Pick | Why |
|---|---|---|
| Sidebar visual reference | satnaing/shadcn-admin | Most polished, highest stars |
| Code base (tables, multi-tenancy) | Kiranism/next-shadcn-dashboard-starter | Same stack, Clerk built in, TanStack Table |
| Domain reference | arhamkhnz/next-shadcn-admin-dashboard | Academy dashboard already exists |
| Class schedule calendar | Qualiora/shadboard | Only one with FullCalendar |

### Domain-Specific — use as blueprints, not code

| Purpose | Pick | Why |
|---|---|---|
| Full domain blueprint | Costasiella (archived) | Only project with full Kelas pipeline end-to-end |
| Scheduling/calendar UX | Cal.diy | Gold standard, MIT |
| Session + billing list patterns | Solidtime | Best design quality in this category |
| Student/member profile page | MemberMatters | MIT, perfect single-page profile pattern |

---

## Decisions Log

| Category | Decision | Date | Notes |
|---|---|---|---|
| Marketing landing page | PENDING | — | Hafiz reviewing options |
| Admin dashboard — main project | **Kiranism/next-shadcn-dashboard-starter** | 2026-06-25 | Next.js + Clerk + TanStack Table. All other dashboard projects used as page-level reference only |
| Admin dashboard — sidebar visual | satnaing/shadcn-admin | 2026-06-25 | Best sidebar polish — adapt visually into Kiranism's Next.js structure |
| Admin dashboard — domain reference | arhamkhnz/next-shadcn-admin-dashboard | 2026-06-25 | Academy dashboard tells us what screens/cards to build |
| Admin dashboard — calendar screen | Qualiora/shadboard | 2026-06-25 | FullCalendar integration for class schedule view |
| Admin dashboard — student profile | MemberMatters | 2026-06-25 | Status + billing + attendance in one scrollable page |
| Admin dashboard — CRUD/bulk actions | marmelab/shadcn-admin-kit | 2026-06-25 | Bulk enrol, bulk invoice generation patterns |
| Domain references | PENDING | — | Hafiz reviewing options |
| Brand colour | RECOMMENDED (confirm) | 2026-06-28 | Deep teal `#0E6E63` primary + emerald `#1F9D74` success + warm near-black `#15171A` ink + coral `#E8603C` demoted to accent + clean red `#D7263D` destructive; tune in tweakcn (Category 4C) |
| Typography | RECOMMENDED (confirm) | 2026-06-28 | Inter self-hosted (latin subset, tabular nums + slashed zero) + optional Plus Jakarta Sans display; avoid Geist (Category 4C) |
| Components & patterns (dialogs/toasts/empty) | shadcn official + satnaing/shadcn-admin | 2026-06-28 | Build shared ConfirmDialog (model satnaing), sonner toasts, EmptyState; harvest Origin UI vendored-in (Category 4B) |
| Theme/identity pass | RECOMMENDED (approve to implement) | 2026-06-28 | tweakcn token pass (teal, warm neutral, radius, border-first, kill default shadow) + self-host Inter; biggest mature-vs-generic win (Category 4A) |

---

*This document is the source of truth for all UI/UX reference decisions for Kelas. Update the Decisions Log as choices are confirmed.*
