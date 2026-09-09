# Kelasapp — Design & UI Consistency Audit (2026-07-03)

> The third audit lens. MVP-READINESS covered code, UX-CX-AUDIT covered flows and feedback
> loops (all 16 findings closed). This one covers **the design itself**: does Kelasapp look
> like a distinctive, trustworthy Malaysian education product, and is the visual system
> internally consistent? Method: 3 parallel code scanners (typography/spacing rhythm,
> color-token/component-variant drift, brand-expression assessment) + a hands-on screenshot
> pass (desktop 1280px + phone 375px) + the existing UI-RESEARCH.md direction as the anchor.
> Before/after mockups were produced by injecting the proposed token set into the live app
> (no code changed); see the companion visual gallery artifact.

## Status

**IMPLEMENTED (2026-07-04).** Hafiz gave the go ("Built it") and the locked spec shipped
on `feat/finish-mvp-polish` in four commits:
- **W1 `b300923`** - identity token pass (teal primary+brand, slate-50 wash, white
  sidebar + teal active tint, emerald #157F62, clean red, card shadow token, Jakarta
  headings at original sizes, tnum app-wide, uppercase table headers + sidebar labels,
  py-2.5 cells, dark equivalents).
- **W2 `91a3820`** - dashboard hierarchy (KPI micro-labels, colored glyphs, hero
  Belum-dikutip in --warning amber, section zones Ringkasan/Perlu tindakan/Prestasi,
  tinted EmptyState).
- **P1 `e8dc921`** - consistency (warning token at 4 amber sites, billing/help button
  sizes, 12 card paddings unified, settings/profile widths, sub-heading standard).
- **P2 `135ff13`** - mechanical batch (hover-underline links, brand-foreground pill,
  check icon size, error title, pagination gap bug, **Geist Mono fully removed**).
Plus the earlier attendance overflow bugfix `031eb53`. Verified: light+dark, EN+BM spot,
375px (attendance + public invoice, zero overflow), 151 unit tests + lint + tsc + i18n
green on every commit. W3 (landing unification) remains post-beta.

---

## Verdict

**The scaffolding is competent; the identity layer was specified and never wired in.**
Kelasapp today is ~90% default shadcn/slate with a teal garnish. The decisive facts:

1. `--primary` is still shadcn's near-black slate (`global.css:62`), so **every filled
   button in the app is black** — while the landing page's CTA is a teal gradient. The
   single most important UI element reads as two different products.
2. Teal exists but was demoted to `--brand` ("secondary accent"): on the operator
   dashboard it reaches exactly three surfaces (sidebar badge, checklist progress, chart
   bars) plus link text. Everything else is slate.
3. Plus Jakarta Sans (the display face) is loaded app-wide but used **only in marketing** —
   zero dashboard usages. All app headings are default-weight Inter.
4. The neutral palette is the cool "satnaing slate" — the exact "generic AI shadcn"
   fingerprint the team's own UI-RESEARCH called out (Category 4A), together with the
   default radius and borders it recommended keeping (those are fine).

**Standing rule from Hafiz (2026-07-03): NO side highlight bars / left accent borders,
anywhere - active states and severity read through background tint + colored text/icon only.**

## FINAL LOCKED SPEC (2026-07-04) - single source of truth

Shaped through v1-v5 mockups + three rounds of Hafiz's feedback (cool kept, hierarchy
kept, no tiles, original title sizes, no mono, no side bars, wash "close to original").

| Token / element | Final value | Notes |
|---|---|---|
| `--primary` (+ sidebar-primary) | teal `#0E6E63`, white foreground | every filled action; logo tile |
| `--brand` | unified to `#0E6E63` | links/buttons share one teal; ring + chart-1 follow |
| `--background` | `#F8FAFC` (slate-50) | one gentle cool step off white; cards lift |
| `--border` / `--input` | `#E2E8F0` (slate-200) | cool ramp with the wash |
| `--sidebar` | white | sits above the wash; active item tint `#E3F1EE`, text `#0B5A51`, semibold; NO side bars |
| `--success` | `#157F62` (deep emerald, 4.9:1) | TEXT-SAFE; lighter `#1F9D74` only for fills/graphics if ever needed |
| `--destructive` | `#D7263D` | clean red, distinct from marketing coral |
| Warning ink (P1 token) | `#B45309` | replaces 4 raw-amber sites; hero KPI value |
| Card elevation | `--shadow-card: 0 1px 2px rgb(16 24 40/.05), 0 1px 3px rgb(16 24 40/.06)` | replaces bare shadow-sm |
| Headings | Plus Jakarta Sans at ORIGINAL sizes, tracking -0.015em | page titles, card titles |
| Page subtitle | `text-sm` | fixes P2 #10 |
| Numerals | `tnum` app-wide (body) | money app; NO mono - Geist Mono deleted (P2) |
| Table headers | 11px uppercase, tracking .07em, semibold | incl. sort-button headers |
| Table cells | `py-2.5` | slightly taller rows |
| Sidebar group labels | 10.5px uppercase, tracking .09em | UTAMA / KEWANGAN etc. |
| KPI cards (dashboard) | 11.5px uppercase micro-labels; colored icon GLYPHS (no boxes): teal/teal/amber/emerald; values Jakarta 700 | hero "Belum dikutip": 2rem, weight 800, amber ink |
| Dashboard zoning | eyebrows 11px uppercase `#64748B`: RINGKASAN / PERLU TINDAKAN / PRESTASI | i18n keys needed |
| EmptyState icon | tinted `bg-brand/10 text-brand` circle | no grey-on-grey |
| Dark mode | primary `#2BA898` + ink `#06231F` fg; sidebar accent `#17332F`/`#8FD1C7`; background/borders keep existing dark values | full dark sweep required |
| Standing rules | NO side bars/left accent borders anywhere; deliverables for Hafiz in English | permanent |

Contrast verified: teal on white 6.4:1, amber `#B45309` 4.6:1, deep emerald 4.9:1,
red 4.9:1, eyebrow slate 4.7:1 (11px bold). StatusBadge tone pairs untouched.

What is already GOOD and must be protected: radius 0.625rem tokens, border-first cards
with a single consistent `shadow-sm` (zero rogue elevation found), `tabular-nums` on
tables, themed scrollbars, uniform table-row link styling across all 7 tables, a coherent
`--brand`/`--primary` separation rule, and the semantic StatusBadge/statusTones system.

---

## Part 1 — The identity gap (original analysis; token values SUPERSEDED by the locked spec)

The direction was researched and recommended in UI-RESEARCH.md (2026-06-28) and left
unconfirmed. The warm neutrals below were REJECTED by Hafiz (cool kept); see the FINAL
LOCKED SPEC above for the real values.

**Original proposed token set (historical):**

| Token | Current | Proposed | Why |
|---|---|---|---|
| `--primary` (filled buttons) | near-black slate | deep teal `#0E6E63` | The brand carries the money actions; matches landing CTA |
| `--background` | cool white | warm off-white `#FBFBF9` | Removes the cool-template feel |
| `--foreground` | cool navy-black | warm near-black `#17191C` | Warm ink that doesn't fight teal |
| neutrals (border/muted/secondary) | slate | warm greys (`#E7E5E0`, `#F4F3EF`…) | The single biggest "mature vs generic" tell |
| `--success` | green-700 | emerald `#1F9D74` | "Paid" gets the research emerald |
| `--destructive` | shadcn red | clean red `#D7263D` | Distinct from coral |
| sidebar tokens | white + black logo tile | warm paper + teal logo tile + teal-tinted active item | Highest-frequency brand touchpoint |
| Headings | default Inter | Plus Jakarta Sans (`--font-display`), tight tracking | Already loaded; marketing already uses it |
| Numerals | default | `tnum` app-wide | Money app; amounts align everywhere |
| Coral `#E8603C` | unused in app | stays marketing-accent only | Research: teal CTAs test more trustworthy for money |

**Rejected direction (for the record):** the generic design-system tool recommended
"Claymorphism + excitement purple + Fira Code" for education — rejected: Kelasapp is a
money-trust product for adult operators, not a children's app; UI-RESEARCH's teal
direction stands.

### W1 — Identity token pass (the before/after mockup)
Change the tokens above in `global.css` (+ dark-mode equivalents), add `font-display` to
TitleBar + dashboard CardTitles, `tnum` on body. **This is what the gallery shows.**
- Files: `src/styles/global.css`, `src/features/dashboard/TitleBar.tsx`, small CardTitle touches.
- Effort: ~2-3h including a full light+dark sweep of every page (token changes hit everything).
- Risk: medium (broad blast radius, but token-only; the CX-audit sweep pattern covers it).

### W2 — Brand-surface upgrades (dashboard reads as Kelasapp)
1. **KPI stat row**: icon in tinted tile (teal; amber for Belum dikutip; emerald for
   attendance), value in display face at 800 weight. (`(operator)/page.tsx` StatCard)
2. **Sidebar**: teal logo tile, active item = teal tint + weight (NO side accent bar -
   Hafiz rule: never use side highlight bars/left border accents anywhere). (`Sidebar.tsx`,
   token-level `--sidebar-*` covers most of it)
3. **Action-needed queues**: tinted icon tile in the card header ("Receipts to verify"
   amber, "Absence alerts" red, "Unpaid invoices" brand) so the eye lands on work first -
   tint fills only, no border stripes.
4. **EmptyState tint**: accent-tinted icon circle instead of grey-on-grey.
- Effort: ~2h. Risk: low (additive styling).

### W3 — Landing ↔ app unification (bigger, later)
Marketing templates hard-code their own hex palette (teal-500/gray-*/#242424) instead of
tokens. Move marketing onto the shared tokens; carry one CTA treatment across both.
- Effort: ~3-4h. Risk: low-medium (marketing only). Can wait until after beta.

---

## Part 2 — Consistency drift (scanner findings, all file:line-verified)

### P1 (visible cross-page) — fix with W1/W2 pass
1. **Billing is a button-size island**: its list header uses `size:'sm'` while every other
   page header (and even billing's own detail page) uses default. Also help page + two
   back-links. → normalise to default. (`billing/page.tsx:82,87`, `billing/settings:39`,
   `billing/pending:46`, `help:27`)
2. **Missing `--warning` token** forces raw amber in 4 app sites (dashboard outstanding,
   billing detail, BillingTable balance, ClassForm RM0 warning) + StatusBadge's amber tone.
   → add `--warning`/`--warning-foreground`, refactor the 4 sites + badge tone.
3. **Headerless-card form padding**: 9 create/edit pages use `pt-6` (asymmetric, doubled
   with Card's own `py-6`) vs 3 settings pages using `py-6`. → one recipe.
4. **Settings-form width drift**: Payment `max-w-2xl` vs Business/Invoicing `max-w-md`
   (identical shells, 2× width jump); profile cards `max-w-2xl` vs `max-w-lg`. → one token.
5. **Sub-section heading soup**: `text-sm font-semibold` vs `text-sm font-medium` vs
   `text-base font-semibold` for the same role (attendance page, ImportWizard,
   PayoutAdjustments, PublicPaymentForm). → one standard (`text-sm font-semibold`).

### P2 (small, mechanical)
6. Always-underlined links (5 sites: ClassForm ×3, EnrollPanel, attendance page) vs the
   31-site `hover:underline` convention.
7. `IdNumberField.tsx:57` uses `text-white` on brand fill instead of `text-brand-foreground`
   (breaks dark-mode contract).
8. ImportWizard's completed-step Check is `size-5` at :108 but `size-4` at :186.
9. `dashboard/error.tsx:29` page title `text-xl` vs TitleBar's `text-2xl` standard.
10. TitleBar subtitle is 16px muted while every CardDescription is 14px → subtitle to `text-sm`.
11. `InvoicingSettingsForm` lone `space-y-5` (all other forms `space-y-6`).
12. Geist Mono loaded globally, used in exactly one facet badge → decide: mono for numeric
    columns or drop the font.
13. (found during design iteration) DataTable pagination: "Baris per halaman" and
    "Halaman X daripada Y" render with no gap between them at laptop widths -
    `data-table/pagination.tsx` needs a gap between the two groups.

### Explicitly fine (no action)
Card elevation, StatusBadge/statusTones colors, AttendanceSheet marking colors, table-link
uniformity, `size-4` icon baseline, brand/primary separation rule, auth `max-w-sm` cards,
field-hint `text-xs` convention, marketing's separate palette (until W3).

---

## Iteration record (2026-07-03, at Hafiz's request)

Three self-critique rounds on the mockups (dashboard + billing as flagships):
- **v1** - straight application of the UI-RESEARCH tokens. Critique: KPI labels limp
  (body-size text against big numbers), table headers same visual weight as table content,
  card-vs-canvas separation too timid, sidebar section labels don't read as labels.
- **v2** - KPI labels become 11.5px uppercase letter-spaced micro-labels; table headers
  11px uppercase (#6B685F); canvas deepened to warm #F7F6F2 (borders/muted follow);
  sidebar group labels 10.5px uppercase. Verdict: the grid finally reads as structure.
- **v3 (FINAL)** - page titles 1.8rem/800 with 14px subtitles (also fixes P2 #10); the
  "Belum dikutip" KPI value takes amber ink #B45309 so outstanding money reads as a
  signal; everything else from v2 kept. Converged - further rounds would be taste.

**The v3 deltas are now part of the W1/W2 spec:** deeper warm canvas #F7F6F2, uppercase
table headers, KPI micro-label treatment, sidebar group-label treatment, title scale
1.8rem + text-sm subtitle, amber ink on the outstanding-money KPI value.

## Hafiz's design review (2026-07-03, v4 = final direction)

Four feedback points on v3, all applied in v4:
1. **Page titles keep the ORIGINAL size** (text-2xl) - the 1.8rem bump rejected. Display
   font (Plus Jakarta Sans) stays, at the original scale.
2. **No icon tile boxes on the KPI cards** - replaced with colored glyphs only
   (teal / teal / amber / emerald), no background shapes.
3. **COOL neutrals confirmed** - the warm-canvas experiment (v2/v3) rejected outright.
   Background, borders, muted colors stay exactly as they are. "I like the overall
   theme to feel cool." The hierarchy work is kept: "your version better in terms of
   visual hierarchy."
4. **Attendance save-button overflow** - a REAL bug he spotted in the before shots: at
   375px the header row didn't wrap and "Simpan kehadiran" burst 11px past the card
   border. Fixed in code and committed (`031eb53`).

**W1/W2 spec is therefore now:** teal primary + teal sidebar identity (tint only, no
bars), display-font headings at original sizes, tabular numerals, uppercase table
headers + sidebar section labels, KPI micro-labels + colored glyphs, amber ink on the
outstanding-money value, emerald success, clean red destructive. NO neutral/background
changes.

## Hierarchy audit (2026-07-03, at Hafiz's request: "cool background makes everything flat")

Diagnosis - five mechanical causes of flatness on the cool ground:
1. One surface plane: canvas and cards are the same brightness; hairline border +
   shadow-sm is the only separator.
2. Everything is an identical card (dashboard = ~8 equal boxes; nothing leads).
3. No page zoning (summary / to-do / analytics mixed without section markers).
4. Compressed type range between levels (24 > 16 > 14 > 12 with uniform weights).
5. No importance ranking inside the KPI row (the business-critical number renders
   identical to the routine ones).

v5 "layered cool" proposal (mocked, in the gallery):
- L1 Layered cool canvas #F8FAFC (slate-50 - FINAL after two rounds: #F4F6F8 too neutral,
  #F1F5F9 too far from the original; Hafiz wants "closer to the original shade", so one
  gentle cool step off white - 2026-07-04), borders #E2E8F0 (slate-200), sidebar white.
- L2 Section eyebrows: 11px uppercase zone labels (RINGKASAN / PERLU TINDAKAN /
  PRESTASI) chapter the dashboard.
- L3 Hero stat: "Belum dikutip" value at 2rem vs 1.5rem neighbours (importance = size).
- L4 Geist Mono for all RM amounts + numeric IDs (decided today: mono stays and gets
  this job). Ledger-like columns in tables, distinct money texture.
- L5 Two-layer soft card shadow (0 1px 2px + 0 1px 3px, ~5-6% ink) so the border is
  not the only separation.
Levers considered but NOT mocked (available if wanted): de-carding the KPI row
(numbers directly on canvas), zebra rows, intensified row hover, tinted section bands.

## Proposed execution order (pending approval)

| Wave | Contents | Effort | Risk |
|---|---|---|---|
| **W1** | Identity token pass + display headings + tnum (the gallery mockup) | ~2-3h + full sweep | medium |
| **W2** | KPI tiles, sidebar accents, queue accents, EmptyState warmth | ~2h | low |
| **P1 batch** | warning token, billing sizes, form padding/width, heading standard | ~2h | low |
| **P2 batch** | items 6-12, mechanical | ~1h | very low |
| **W3** | landing/app unification | ~3-4h | low-medium (post-beta candidate) |

Verification plan per wave: full-page screenshot sweep light + dark, EN + BM, desktop +
375px on the core screens (dashboard, tables, forms, invoice detail, public invoice,
attendance), plus the standard gates (tests, tsc, lint, i18n parity).

---

## Decision needed from Hafiz

1. **Confirm the identity** (W1 palette as mocked) — or adjust (e.g. different teal, keep
   cool neutrals, different heading face). The gallery exists precisely for this call.
2. Approve wave order (W1 → W2 → P1 → P2 now; W3 post-beta) — or reorder/trim.
3. Geist Mono: FINAL 2026-07-03 - REMOVE ENTIRELY. Hafiz first said keep, then rejected
   the mono-money mock on sight ("doesnt look good"). Amounts use Inter + tabular
   numerals (tnum) instead; the font and its one badge usage are deleted (P2).

**v5 approved 2026-07-03 minus the mono lever** - implementation green-lit:
W1 (identity + layered cool) -> W2 (dashboard hierarchy) -> P1 -> P2. W3 post-beta.
