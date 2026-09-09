# Sifututor.my &amp; Nakngaji.my — SEO, GEO/AEO, Performance &amp; Accessibility Audit

**Date:** 07/08/2026
**Method:** 4 parallel research agents — 2 trend-benchmark passes (WebSearch, "what actually works in 2026") + 2 live technical audits using real data (`curl` against robots.txt/sitemap/raw HTML/response headers, plus Google PageSpeed Insights API calls).
**Companion doc:** [sifututor-nakngaji-competitive-gap-analysis-2026-08.md](sifututor-nakngaji-competitive-gap-analysis-2026-08.md) covers UX/content/design gaps vs. competitors — this doc is the technical layer.
**Known gap in this data:** Google PageSpeed Insights API calls for both sites hit a hard daily quota (`RESOURCE_EXHAUSTED`, not transient) on both mobile and desktop requests — **no real Core Web Vitals or Lighthouse scores were obtainable this run.** Everything performance-related below is inferred from structural signals (caching headers, image formats, third-party scripts), not measured. Re-run the PSI calls on a fresh quota day, or run Lighthouse directly in Chrome DevTools, before treating any performance number as fact.

---

## 1. Benchmark: what actually works in 2026

### SEO
- JSON-LD is the only structured-data format worth using — Google no longer recommends Microdata/RDFa.
- `LocalBusiness`/`Service` schema (address, hours, phone, service area) powers Maps/local-pack eligibility and gives AI engines explicit entity facts.
- **FAQPage schema no longer produces rich results in Google Search as of May 2026** (deprecated) — still worth keeping for AI-citation extractability, just don't expect SERP snippets from it.
- **Self-hosted `Review`/`AggregateRating` schema does not work** — Google disallows an entity marking up reviews of itself (reaffirmed July 2026, explicit anti-fake-review language). Only third-party platforms (actual Google Business Profile reviews) count toward star display.
- Core Web Vitals carry real ranking weight (~28% of ranking weight in 2026 estimates) but act mainly as a tiebreaker among pages of similar content quality — a slow page with strong content still outranks a fast page with thin content.
- Mobile-first indexing applies to 100% of sites now — anything present only on desktop is functionally invisible to indexing.
- **Local SEO (Malaysia)**: Google Business Profile completeness is the single most important local-visibility asset — often outweighs on-site SEO for "tutor near me" style queries. NAP (Name/Address/Phone) must be byte-identical across site, GBP, and directories.

### GEO/AEO (AI search citation)
- **Established**: answer-first structure (first 40–75 words after a heading directly answers the implied question — this is the "extraction window" AI engines chunk and score); concrete stats/numbers over vague claims (Princeton GEO study found this improved AI-citation visibility by up to 41%, the single most effective tactic tested); question-formatted headings + comparison tables earn measurably more citations (~4.2x) across ChatGPT/Perplexity/Gemini/AI Overviews; traditional technical SEO is still the foundation GEO sits on top of, not a replacement for it.
- **Platform behavior differs**: Perplexity and Google AI Overviews retrieve live at query time (crawlability/freshness matters right now); ChatGPT/Claude/Gemini mostly draw on training-data cutoffs (being authoritative/indexed *before* training matters more than real-time freshness). Only 11% of domains get cited by both ChatGPT and Perplexity — one engine's citation doesn't predict another's.
- **Emerging / don't over-index**: `llms.txt` is **not confirmed useful** by any major AI search engine (ChatGPT search, Perplexity, Google AI Overviews/AI Mode, Gemini, Copilot) as of 2026 — Google's own May 2026 guidance explicitly says it's not needed. Adoption is concentrated in developer tools (Cursor, Windsurf), not consumer answer engines. Treat as optional/low-priority, not a real gap.

### Web performance
- **LCP**: good ≤2.5s / needs improvement 2.5–4s / poor &gt;4s. **INP** (replaced FID in March 2024, still current): good ≤200ms / needs improvement 200–500ms / poor &gt;500ms. **CLS**: good ≤0.1 / needs improvement 0.1–0.25 / poor &gt;0.25.
- Google grades field data at the 75th percentile over a rolling 28 days (Chrome UX Report), not a single Lighthouse run — lab scores are diagnostic, not the ranking signal itself.
- Mobile is the harder bar in practice: average mobile load (~8.6s) runs ~3.4x slower than desktop (~2.5s) industry-wide.
- Common WordPress/marketing-site culprits: unoptimized images (no WebP/AVIF, no responsive sizing), render-blocking CSS/JS, unthrottled third-party scripts (tag managers, pixels, chat widgets), web fonts without `font-display: swap`, no page caching/CDN.
- **Business impact**: a 1-second delay can cut conversions up to 20%; conversion rate drops ~4.42% per extra second of load (0–5s range); bounce probability rises 32% going from 1s→3s load.

### Accessibility (WCAG)
- WCAG 2.2 Level AA is the current target standard, referenced by US DOJ (federal, effective Jan 2026), EU EAA, UK public-sector rules.
- **Malaysia has no hard legal mandate**: the PWD Act 2008 "encourages" accessible platforms but doesn't mandate WCAG compliance and has no enforcement mechanism; MCMC has no specific web-accessibility regulation. The case for fixing accessibility here is UX + SEO, not legal risk — say so plainly rather than implying compliance exposure.
- Accessibility and SEO overlap heavily: alt text feeds image search, heading hierarchy is what Google uses to parse page structure, clean semantic HTML is also easier for AI crawlers to parse correctly.
- **Baseline to calibrate against (WebAIM Million 2025, ~1M homepages scanned)**: 95.9% of homepages fail WCAG 2.2 A/AA. The 6 highest-impact failure categories (79% low-contrast text, 55% missing alt text, 48% unlabeled form inputs, 45% empty links, missing `lang` attribute, empty icon buttons) cause 96% of all detected errors industry-wide — finding several of these below is the norm, not a sign of an unusually bad build.

---

## 2. Sifututor.my — technical findings (07/08/2026, live `curl` audit)

| Check | Finding |
|---|---|
| `robots.txt` | Exists. Cloudflare "Content-Signal" convention: `search=yes, ai-train=no, use=reference`. **Explicitly `Disallow: /` for ClaudeBot, GPTBot, Google-Extended, Bytespider, CCBot, Amazonbot, Applebot-Extended, meta-externalagent, CloudflareBrowserRenderingCrawler** — a full crawl block, not just a training opt-out. References `sitemap_index.xml`. |
| Sitemap | `/sitemap.xml` returns empty/404-like. `/sitemap_index.xml` (Yoast) works — 2 sub-sitemaps, `page-sitemap.xml` lastmod = same day as audit (actively regenerating). |
| `llms.txt` | Not present (404 both root and `.well-known/`) — per the benchmark above, low priority given it's not confirmed useful anywhere yet. |
| Title / meta description | `"Trusted Home &amp; Online Tutors Across Malaysia - Sifututor.my"` / present, reasonable length. **Note**: title itself uses "Home & Online Tutors" — same venue-anchoring language flagged as a brand-rule conflict in the companion UX doc. |
| Canonical / viewport / lang | All present and correct (`lang="en-US"`). |
| Open Graph / Twitter Card | Complete, populated (not boilerplate) on both. |
| JSON-LD | 1 block, `@graph` with `WebPage, ImageObject, BreadcrumbList, WebSite, Organization+EducationalOrganization, PostalAddress, Service, SearchAction`, etc. **No `FAQPage`, no `LocalBusiness`, no `Review`/`AggregateRating`.** |
| Headings | Exactly 1 H1 (correct). 59 H2s, only 2 H3s — a very flat structure typical of an Elementor-built page, not a strict nested outline. |
| Images | 87 `&lt;img&gt;` tags. 28 have empty `alt=""`; the rest are populated with descriptive text. |
| Caching | `cf-cache-status: DYNAMIC` — homepage not served from Cloudflare edge cache, every hit round-trips to origin. |
| Security headers | HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy all present. Gzip compression confirmed. |
| PageSpeed Insights | **Unavailable — API quota exhausted (429) on both mobile and desktop.** |

---

## 3. Nakngaji.my — technical findings (07/08/2026, live `curl` audit)

| Check | Finding |
|---|---|
| `robots.txt` | Same pattern as Sifututor — Content-Signal `ai-train=no`, and a full `Disallow: /` block for the same list of major AI crawlers. References `sitemap.xml` + `sitemap.html`. |
| Sitemap | `sitemap.xml` is itself the index (Google XML Sitemaps plugin). 3 sub-sitemaps, ≈19 total URLs. **`post-sitemap.xml` has only 1 URL, lastmod 2021-12-07 — the blog is effectively abandoned.** |
| `llms.txt` | Not present — low priority per benchmark above. |
| Title / meta description | `"nakngaji.my – Belajar Mengaji Al-Quran Online atau Di Rumah"` / present, includes trust signal ("1,900+ pelajar," "4.9★ di Google"), slightly long (~187 chars) for guaranteed full SERP display. |
| Canonical / viewport | Present and correct. |
| **`lang` attribute — real bug** | `&lt;html lang="en-US"&gt;`, but the page content is Malay and the JSON-LD itself declares `inLanguage: "ms-MY"`. This is a genuine, fixable i18n/SEO/accessibility mismatch. |
| Open Graph | **Incomplete — only `og:description` is present.** No `og:title`, `og:image`, or `og:url`. Social share previews (Facebook, LinkedIn, WhatsApp link previews) will render broken or blank. |
| Twitter Card | **None present at all.** |
| JSON-LD | 1 block, `@graph` with `Organization+EducationalOrganization` (legal name, address, phone, socials), `WebSite`, `Service`, **and `FAQPage`** (multiple real Q&amp;A pairs — good for GEO extractability even without a rich-result payoff). No `LocalBusiness`, no `Review`/`AggregateRating` — so the "4.9★ di Google" claim in the meta description isn't backed by machine-readable rating data (though per the benchmark, self-hosted AggregateRating wouldn't earn stars in search anyway — the actual fix is a `LocalBusiness` type with a GBP link, not a self-serving rating schema). |
| **Headings — real bug** | **Zero `&lt;h1&gt;` tags found anywhere on the homepage.** 12 H2s, 6 H3s exist, but the page has no top-level heading landmark at all. |
| Images | All 9 sampled images have descriptive, non-empty `alt` text; lazy-loading and responsive `srcset` in use — genuinely good practice, ahead of Sifututor here. |
| Image format | PNG/SVG only — no WebP/AVIF. One CSS class is literally named `sp-no-webp`, suggesting WebP conversion is explicitly disabled by a plugin. |
| Caching | `cf-cache-status: DYNAMIC` — same as Sifututor, not edge-cached. |
| Security headers | HSTS, X-Frame-Options, nosniff, referrer-policy all present; HTTP/3 supported (`alt-svc: h3`). |
| PageSpeed Insights | **Unavailable — API quota exhausted (429) on both mobile and desktop.** |

---

## 4. Cross-cutting pattern: both sites block AI *training* crawlers only — RESOLVED, no action needed (07/08/2026)

**Update after deeper verification**: the original framing of this finding (below, struck through in spirit, kept for record) overstated the impact. Re-reading the raw `robots.txt` on both sites shows the block is Cloudflare-managed (`# BEGIN Cloudflare Managed content`, not a hand-edit) and only targets **pure-training crawlers**: ClaudeBot, GPTBot, Google-Extended, Bytespider, CCBot, Amazonbot, Applebot-Extended, meta-externalagent. It does **not** block OAI-SearchBot, ChatGPT-User, PerplexityBot, Claude-SearchBot, or Claude-User — those fall under the general `User-agent: * → Allow: /` and are open on both sites.

Why that distinction matters:
- OpenAI and Anthropic each run separate crawlers for training (GPTBot/ClaudeBot) vs. live search/citation (OAI-SearchBot, Claude-SearchBot) vs. user-triggered browsing (ChatGPT-User, Claude-User). Blocking the training crawler does not stop a site from being cited in live ChatGPT Search or Claude answers — the crawlers that actually drive those citations are already unblocked here.
- Google's own documentation confirms `Google-Extended` controls only Gemini/Vertex AI training data and "does not impact a site's inclusion in Google Search nor is it used as a ranking signal in Google Search" — it has zero effect on AI Overviews eligibility.
- Bytespider/CCBot/Amazonbot/Applebot-Extended/meta-externalagent are bulk-training scrapers with no citation or referral-traffic value to a site like this in the first place.

**Standard practice, with real numbers (2026 data)**: 61% of enterprise sites run exactly this hybrid pattern — block pure-training bots, leave search/retrieval bots open. 25% of the top 1,000 websites block GPTBot outright; ClaudeBot sits at ~35% block rate among prominent sites measured. This is mainstream practice, not an aggressive outlier.

**Decision: no change needed.** Both sites already run the standard hybrid configuration — just applied automatically by Cloudflare rather than deliberately chosen. There is no real GEO/AI-citation cost currently being paid. Closed as resolved 07/08/2026; revisit only if Cloudflare's managed rule set changes or a specific AI-citation channel is later found to actually need OAI-SearchBot/Claude-SearchBot-class access that isn't already granted.

---

## 5. Prioritized action list

### Quick wins (low effort, do first)
- **Nakngaji**: add a single `&lt;h1&gt;` to the homepage — currently has none, a real and easily-fixed gap.
- **Nakngaji**: fix `&lt;html lang="en-US"&gt;` → `lang="ms-MY"` (or the correct BCP-47 tag) to match actual page content and the site's own JSON-LD.
- **Nakngaji**: add `og:title`, `og:image`, `og:url` — current share cards on Facebook/WhatsApp/LinkedIn are broken or blank.
- **Nakngaji**: add Twitter Card meta tags (currently none).
- **Sifututor**: fix or redirect `/sitemap.xml` to `/sitemap_index.xml` so tools/scripts hitting the plain path don't get an empty response.
- **Sifututor**: fill in the 28 images with empty `alt=""` — accessibility and image-SEO gap.
- **Both**: decide and act deliberately on the AI-crawler block (see section 4) rather than leaving it as an unexamined default.
- **Both**: re-run Google PageSpeed Insights (quota was exhausted this session) to get real Core Web Vitals numbers before prioritizing any performance work further.

### Medium effort
- **Sifututor**: rebuild the flat H2-heavy heading structure (59 H2s, 2 H3s) into a properly nested outline — helps both SEO parsing and GEO passage-extraction.
- **Both**: add `LocalBusiness` schema (address, hours, phone, service area) linked to the real Google Business Profile — this is the correct way to surface the star rating both sites already claim in copy, not a self-hosted `AggregateRating`.
- **Nakngaji**: revive or formally retire the blog — `post-sitemap.xml` has one URL from 2021; an abandoned blog subdirectory is a stale-content signal either way.
- **Both**: convert images to WebP/AVIF with responsive `srcset` — Nakngaji's `sp-no-webp` class suggests this is currently actively disabled by a plugin, worth checking why.
- **Both**: enable edge caching (`cf-cache-status` currently `DYNAMIC` on both homepages) — likely the single biggest lever on TTFB/LCP given everything else measured is already reasonably clean.

### Bigger bets / needs real data first
- **Both**: once PageSpeed quota resets, run full mobile + desktop Lighthouse passes and prioritize LCP/INP/CLS fixes based on actual numbers, not inference.
- **Both**: apply the GEO answer-first/stat-specific/question-heading content patterns from the benchmark section to key landing pages (booking page, tutor pay page, FAQ pages) — highest-leverage GEO move once the crawler-block decision above is resolved.
- **Both**: run a real WCAG 2.2 AA pass (contrast ratios, form labels, keyboard navigation, empty-icon-button labels) — none of that was checkable via `curl`/raw HTML alone and needs an actual rendered/interactive audit.
- **Sifututor**: consider adding `FAQPage` schema (Nakngaji already has it) — no rich-result payoff per current Google guidance, but still useful for GEO extractability.

---

## Reuse notes for future sessions
- This doc is a point-in-time technical snapshot (07/08/2026). Re-verify before acting if read more than ~60 days later — both SEO/GEO best practices and the sites' own technical state will drift.
- **The PageSpeed Insights gap is the most important thing to close on a re-run** — every performance conclusion above is inferred from secondary signals (caching headers, image formats, script load), not measured Core Web Vitals. Don't treat "likely slow" as "confirmed slow" until the API call succeeds.
- Companion UX/content doc: [sifututor-nakngaji-competitive-gap-analysis-2026-08.md](sifututor-nakngaji-competitive-gap-analysis-2026-08.md).
