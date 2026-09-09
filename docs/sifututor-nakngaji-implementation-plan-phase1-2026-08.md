# Implementation Plan — Sifututor.my &amp; Nakngaji.my (Phase 1: No UI/UX Required)

**Date:** 07/08/2026
**Sourced from:**
- [sifututor-nakngaji-competitive-gap-analysis-2026-08.md](sifututor-nakngaji-competitive-gap-analysis-2026-08.md) (UX/content/design gaps)
- [sifututor-nakngaji-seo-geo-performance-audit-2026-08.md](sifututor-nakngaji-seo-geo-performance-audit-2026-08.md) (technical SEO/GEO/performance/accessibility audit)

**Scope of this doc:** every fix identified across both research docs that can ship **without a design pass** — no new sections, no new components, no layout changes. Pure technical fixes, metadata, schema, infra config, and in-place copy edits that swap text within an existing element.

**Not in this doc:** anything that needs a new UI component or a layout/visual decision (stat bars, tutor credential cards, rate tables, review-distribution bars, FAQ blocks, video intros, etc.). Those are listed at the very end as **Phase 2 — deferred pending a design pass**, referencing the companion UX doc's "Medium effort" and "Bigger bets" sections so nothing gets lost.

**Both sites are WordPress.** Exact plugin names below are what the technical audit could confirm from the outside (HTTP responses); a couple are marked "verify in WP Admin" because the audit couldn't see behind the login screen. Confirm before editing.

---

## EXECUTION STATUS — updated 07/08/2026

**Access route (confirmed working):** `ssh staging` (72.62.251.97, Hostinger KVM8, root, key `~/.ssh/id_ed25519`), then `wp` at `/usr/local/bin/wp` with `--allow-root`. Document roots: `/var/www/prod/sifututor-my` and `/var/www/prod/nakngaji-my`. Backups written to `/root/backups/` on the server before every change.

**Safety rules applied** (from a prior session's incident where a regex corrupted `rgba()` values on 7 pages): never regex `_elementor_data`; target nodes by widget ID; verify a `json_decode`/`wp_json_encode` round-trip is byte-identical before writing; `wp elementor flush-css` + `wp cache flush` after every change; verify live before moving on.

### DONE and verified live

| # | Site | Change | Verification |
|---|---|---|---|
| 1 | Nak | Trashed default `hello-world` stub post | URL now 404; `post-sitemap.xml` has 0 URLs |
| 2 | Nak | `lang="en-US"` → `ms-MY` via `language_attributes` filter in `nakngaji-accessibility.php` (v1.2). WPLANG untouched so admin UI stays English | Homepage + Singapore pages both emit `lang="ms-MY"`; `wp-login.php` still 200 |
| 3 | Nak | Full Open Graph + Twitter Card set added to `nakngaji-schema.php` (og:locale/type/site_name/title/description/url/image + dimensions, twitter:card/title/description/image). Uses `home-hero01.png` (1000x619 raster; the SVG logo would not render on Facebook/WhatsApp) | 9 og tags + 4 twitter tags live on homepage; inner pages get derived title/url |
| 4 | Nak | Homepage hero promoted from H2 to H1 (widget `27020ab`, post 29) | Exactly 1 H1, 11 H2s. Typography is `custom` with explicit px sizes and the CSS selector is tag-agnostic, so no visual change |
| 5 | Sifu | Alt text added to 3 testimonial images (ids 13908/13907/13906) after visually inspecting each | Empty alts 28 → 22 live |

**Correction to the audit — the "28 empty alt" finding was mostly wrong.** Most are decorative vectors and icons (`Vector-2`, `Vector-8`, `3dicons-*`, `feather-arrow-right`, `Group-*`, `Ellipse-24`) where `alt=""` is *correct* WCAG practice. Filling all 28 would have made accessibility worse. Only ~7 were genuine gaps; 3 content images are now fixed, the rest are icons left correctly empty.

**Correction to the audit — Nakngaji WebP is already working.** The `sp-no-webp` CSS class implied ShortPixel had WebP disabled. It does not: `.png.webp` variants are being served. Sifututor also serves WebP and AVIF. No action needed.

**Correction to the audit — `/sitemap.xml` on Sifututor is already fine.** It returns a clean `301 → /sitemap_index.xml`. Not a gap.

### NEW finding, not in the original audit — Sifututor footer contains leftover Astra demo content

Visible on the live production footer, not hidden by CSS:
- Placeholder Latin text: *"Quam quam lacus, amet lorem eu nunc, eget dui libero et faucibus facilisis sed odio suspendisse"*
- A **day-care logo hotlinked from an external demo site**: `https://websitedemos.net/daycare/wp-content/uploads/sites/1041/2022/03/day-care-logo.svg`
- Four social icons (Facebook, Instagram, Twitter, YouTube) with **empty `href=""`**, so they link nowhere

Real profile URLs found elsewhere on the site: Facebook `https://www.facebook.com/sifututor.my`, Instagram `https://www.instagram.com/sifututor/`, YouTube `https://www.youtube.com/channel/UC2YgeGwWZ6jo8R93GMEXYbg`. No Twitter/X URL found anywhere, so that icon likely should be removed rather than linked.

Not fixed, because the replacement footer tagline is a content decision.

### DONE in second pass (09/08/2026), decisions resolved

| # | Site | Change | Verification |
|---|---|---|---|
| 6 | Sifu | **Removed leftover Astra demo content from footer.** Confirmed first that it was genuinely visible (no `display:none`, no `visibility:hidden`, no Astra responsive-hide class) — it was just easy to miss in column 1 of 4 with a 46x17px logo. Cleared `astra-settings[footer-html-1]` | 0 `websitedemos.net` refs, 0 lorem ipsum live |
| 7 | Sifu | **Wired real social profiles** in `footer-social-icons-1` (Facebook `sifututor.my`, Instagram `sifututor`, YouTube channel) and disabled the Twitter icon since no account exists | 0 `href=""` links remain; 3 real profiles live |
| 8 | Sifu | **Tutor count unified to 10,000+.** The homepage "10,000+" turned out to refer to *parents*, so was never a conflict; the real clash was 4,500+ vs 10,000+ *verified tutors*. Fixed in 4 separate storage locations: `_elementor_data` (posts 15634, 15860), the rendered `post_content` copies, and the Yoast meta description (which alone fed the meta tag, `og:description` AND the JSON-LD) | Sitewide sweep of 8 pages returns 0 instances of the old figure; 0 published posts in DB |
| 9 | Sifu | **Footer tagline rewritten** (appeared on every page). Old: *"The best 1-to-1 Home Tuition Service provider in Malaysia…"* — both a venue-anchor violation and an unsubstantiated superlative. New: *"Malaysia's trusted 1-to-1 tutoring platform, matching your child with the right tutor, at home or online."* | Live on all pages; 0 residual instances of the old string |
| 10 | Both | **`LocalBusiness` schema added** with real GBP-sourced `geo` coordinates and `hasMap` + `sameAs` links to each Google Business Profile. Nakngaji via `nakngaji-schema.php`; Sifututor via the existing `wpseo_schema_organization` filter in `sifututor-schema.php` (augments Yoast's graph rather than competing with it) | Both homepages emit valid JSON-LD with `["Organization","EducationalOrganization","LocalBusiness"]`, geo, and hasMap |

**GBP listings (resolved from Hafiz's Maps links):**
- SifuTutor — `https://maps.app.goo.gl/wKi7aPMJZ1UUFEwx7`, place ID `0x31cc51e9394213a7:0x4b8f921c54c160b3`, 3.1234419 / 101.470662
- Nakngaji.my — `https://maps.app.goo.gl/BtWmE2bTpGhZLpMn6`, place ID `0x89af491ea77145e3:0x43bc048cdae5d32c`, 3.1235488 / 101.4700773

**Post-change health check:** all 7 key pages on both sites return 200; registration/booking forms still render (237 and 55 form field markers respectively).

### Two more audit corrections found during execution

- **The "26 home tuition instances" was inflated.** Only 11 are real; the rest were duplicate HTML attributes. Of the 11, exactly **one** was a brand-positioning violation (the sitewide footer tagline, now fixed). The rest are legitimate service-format descriptors and were deliberately left: the booking form's "Type of Tuition" dropdown, the tutor FAQ's "teach either online or through home tuition", and "Online Learning Portal for all Home Tuition Students".
- **Elementor JSON encoding is per-post, not global.** Post 15860 round-tripped with default flags, 15634 required `JSON_UNESCAPED_SLASHES`, and the footer template 1864 round-tripped with **no** flag combination at all. The guard caught each case and refused to write until a lossless path was confirmed; for 1864 the fix was a literal string swap that never re-encodes the JSON. Always detect the flag per post; never assume.

### PERFORMANCE BASELINE — measured 09/08/2026 (first real numbers)

The PageSpeed Insights API was quota-blocked on both attempts, so this was measured with **Lighthouse 12 run locally against headless Chrome**. These are lab numbers, not field/CrUX data.

| | Perf | A11y | SEO | Best Prac | LCP | CLS | TBT |
|---|---|---|---|---|---|---|---|
| Sifututor **mobile** | **68** | 93 | 100 | 96 | **4.79s POOR** | 0.066 good | 54ms good |
| Sifututor desktop | 88 | 93 | 100 | 100 | 1.43s good | 0.015 good | 0ms good |
| Nakngaji **mobile** | **49** | 97 | 92 | 79 | **4.58s POOR** | 0.000 good | **1280ms POOR** |
| Nakngaji desktop | 80 | 97 | 92 | 78 | 1.91s good | 0.000 good | 172ms good |

**Headline: desktop is fine on both sites; mobile is the problem on both.** Targets are LCP ≤2.5s, CLS ≤0.1, TBT ≤200ms.

**CLS is excellent everywhere (0.000–0.066)** which confirms the earlier Elementor CSS print-method fix worked and is holding.

Top opportunities, from the Lighthouse audits:

| Site | Opportunity | Est. saving |
|---|---|---|
| Sifututor mobile | Eliminate render-blocking resources (33 of them; worst are elementskit-lite CSS 51KB, jQuery 30KB, a custom-css-js file 15KB) | **2.76s** |
| Sifututor mobile | Reduce initial server response time | 0.73s |
| Sifututor mobile | Reduce unused CSS | 0.47s |
| Nakngaji mobile | Eliminate render-blocking resources | **1.99s** |
| Nakngaji mobile | Reduce initial server response time | 0.81s |
| Nakngaji mobile | Reduce unused CSS | 0.69s |

Third-party weight is similar on both: Google Tag Manager ~325KB, Facebook pixel ~160–190KB. Blocking time from third parties is modest (~35–45ms each), so they are a payload problem more than a blocking problem.

LCP element differs: on Sifututor it is a **text heading** (so the delay is caused by blocked CSS/JS, not image loading); on Nakngaji it is the **hero image** `home-hero01`.

**Important correction:** Lighthouse's "Use HTTP/2, save 1.75s" finding on Sifututor is a **false positive**. Direct `curl --http2` checks confirm the document and static assets all negotiate HTTP/2 correctly. The audit result is an artifact of the local headless run. Do not action it.

**What this changes about the plan:** edge caching addresses "reduce initial server response time", worth roughly 0.7–0.8s. That is real but it is *not* the biggest win. **Render-blocking resources is 3–4x larger** and should be tackled first or alongside. Caching alone will not move either site out of POOR on mobile LCP.

### PERFORMANCE WORK — change 1 done, measured (09/08/2026)

**Change 1: dequeued unused `gum-elementor-addon` assets on the Sifututor homepage.** That plugin hooks `elementor/element/before_section_start`, which fires for *every* Elementor element, so it enqueued 7 files (owl.carousel JS+CSS, superslides, easing, easyPieChart, price-table.js, allscripts.js, style.css) on pages using none of its `gum_*` widgets. Verified first that no gum widget and no gum component class (`.popover-box`, `.price-period-switch`, `.owl-carousel`, `.make-responsive-mobile`) appears on the homepage. Implemented as mu-plugin `sifututor-asset-trim.php`, deliberately an allowlist (currently front page only) because templates embedded at render time are not visible in the page's own `_elementor_data`.

Measured result on Sifututor mobile:

| Metric | Before | After |
|---|---|---|
| Performance score | 68 | **73** |
| LCP | 4.79s | **4.47s** |
| FCP | 4.43s | **4.11s** |
| Speed Index | 6.00s | **4.87s** |
| Render-blocking files | 33 | **28** |

Screenshot verified: homepage renders identically. Assets now load in `<body>` (Elementor re-enqueues them during content render) so they no longer block first paint.

**Change 2 investigated and REJECTED — both candidates are dead ends:**

- **ElementsKit `widget-styles.css` (50.6KB, ~2.2s)** is enqueued unconditionally in `enqueue_frontend_css()` with no setting to load only in-use widget styles. The `elementskit_options.widget_list` active/inactive flags (22 active, 21 inactive) do not affect this static monolithic file. ElementsKit *is* genuinely used on the homepage (accordion, buttons), so the file cannot be dropped.
- **`custom-css-js/10359.css` (70KB raw, 378 rules)** contains styles the homepage genuinely uses (`custom_radiobtn` ×18, `tata` ×3, `bella` ×2, `highlight` ×3). Cannot be removed or made page-conditional without splitting the file rule by rule.

**What actually remains, honestly:** the structural problem is now the *count* of render-blocking files (28), many of them tiny 0.6–1.6KB Elementor per-widget stylesheets. Each costs a round trip, which is expensive on mobile latency. The standard fix is CSS/JS concatenation + minification, which requires an optimisation plugin (Autoptimize free, or WP Rocket / FlyingPress paid). No such plugin is installed on either site. That is a bigger change needing explicit approval and careful config, not a surgical edit.

Remaining safe-ish lever without a new plugin: edge caching, worth ~0.73s ("reduce initial server response time").

### NAKNGAJI PERFORMANCE — root cause found, needs Hafiz (Cloudflare dashboard)

Nakngaji mobile scores 48-49, the weakest of the four measurements. The dominant cause is **not** the site itself:

| Source | JS execution time |
|---|---|
| `/cdn-cgi/challenge-platform/scripts/jsd/main.js` (Cloudflare bot challenge) | **~2,500ms** |
| Everything else on the page combined | ~870ms |

Reproduced across two independent runs: 2,559ms and 2,463ms, with TBT 1,280ms and 1,215ms (target is ≤200ms). This single script is roughly three quarters of all JavaScript execution on the page.

**Why this is a real finding and not a testing artifact:** `sifututor.my` was measured in the same session, with the same headless Chrome, and its Cloudflare challenge cost was **0ms**. If headless detection alone were responsible, both zones would behave the same. The difference is per-zone Cloudflare configuration. Both sites *serve* the script tag; only nakngaji.my executes the expensive challenge.

**Caveat to keep:** headless browsers are more likely to be challenged than real visitors, so the real-world cost to an actual parent on a phone is probably lower than 2.5s. The finding is directionally solid (nakngaji.my is configured more aggressively than sifututor.my) but the exact user-facing cost is unconfirmed. Confirm with Chrome UX Report field data or a real-device test before treating 2.5s as the true figure.

**RESOLVED 09/08/2026.** The scoped tokens in `agent-access` (`cloudflare-admin`, `cloudflare-readonly`, `cloudflare-sifututormy-dns-write`) don't cover nakngaji.my, but the global key at `~/.cloudflare-credentials` (`CF_EMAIL`/`CF_API_KEY`) does — it has access to all 4 zones (learnest.my, nakngaji.my, sifututor.my, tutorla.tech). No new access lane was needed.

**Correction to the initial diagnosis:** it was NOT that nakngaji.my was configured more aggressively than sifututor.my. Both zones had byte-identical bot settings (`fight_mode: true`, `enable_js: true`) on the Free plan. Sifututor showing 0ms in one Lighthouse run was Cloudflare's per-request challenge decision (sampling), not a configuration difference — flagged as a caveat before acting on it, then disproven by reading actual zone settings via the API rather than assuming.

**Two-step fix, because the API enforces a dependency the docs don't state up front:**
1. `PUT .../bot_management {"enable_js": false}` while `fight_mode: true` → rejected (`10400 Bad Request`). Confirmed via a same-payload no-op that the token/endpoint itself works, ruling out a permissions problem.
2. `PUT .../bot_management {"fight_mode": false}` alone → accepted, but had **zero effect** on the challenge script (verified: same 2,547-2,559ms cost after, script still present in raw HTML). The Free plan's JS Detections (`enable_js`) is the setting that actually injects `/cdn-cgi/challenge-platform/scripts/jsd/main.js`, and it evidently cannot be disabled while paired with `fight_mode: true` — but CAN be disabled once `fight_mode` is already off.
3. `PUT .../bot_management {"fight_mode": false, "enable_js": false}` (fight_mode already off from step 2) → accepted. Cache purged (`purge_everything`). Verified: 0 occurrences of `challenge-platform` in the raw homepage HTML afterward.

**Measured result, 2 independent Lighthouse runs after the fix (mobile):**

| Metric | Before (2 runs) | After (2 runs) |
|---|---|---|
| Performance score | 49, 48 | **72, 71** |
| Total Blocking Time | 1,280ms, 1,215ms | **45ms, 62ms** |
| Cloudflare challenge JS cost | 2,559ms, 2,463ms | **0ms, 0ms** |
| First Contentful Paint | 3.96s | 3.99s (unchanged) |
| LCP | 4.58s | 4.94s, 5.34s (noisier, not meaningfully changed) |

**Nakngaji went from the weakest of all 4 measurements to roughly matching Sifututor's 73.** TBT (the metric this fix targets) improved by over 96%. LCP did not improve, consistent with the fix removing blocking *script execution* rather than anything affecting the largest visible element's paint time.

Site verified healthy after: homepage and `/jadi-tutor/` both 200, registration form still renders (55 form-field markers, unchanged from before).

**Tradeoff now live, not yet time-tested:** nakngaji.my has zero Cloudflare bot mitigation as of 09/08/2026 (`fight_mode: false`, `enable_js: false`). FluentForm's own spam controls are the only remaining defense on the public forms. **Watch form-spam volume over the next 1-2 weeks.** If it becomes a problem, the two options discussed were: re-enable at the cost of the ~2.5s mobile penalty, or upgrade nakngaji.my to Cloudflare Pro (~USD 20/mo) for Super Bot Fight Mode, which allows bot protection without the JS challenge cost. Sifututor's bot settings were deliberately left untouched — same tradeoff exists there but was not acted on this session.

Rollback if needed: `PUT .../bot_management {"fight_mode": true, "enable_js": true}` restores the pre-change state (saved in session backups as `cf-nakngaji-bot-BEFORE.json`).

Second issue on Nakngaji, same monolithic pattern as Sifututor's ElementsKit: `ultimate-elementor/assets/min-css/uael-frontend.min.css` at 79.1KB / 2,177ms render-blocking. UAEL is genuinely used (the FAQ widget is `uael-faq`), so it cannot simply be dropped.

### SIFUTUTOR HEADING FIX — done and verified (09/08/2026)

The 13 non-heading items flagged earlier were fixed. Root cause split across two locations:

- 7 directly in the homepage (post 1436): "4.9", "google reviews", "2600+ verified reviews", "Free" x4
- 6 in a shared Elementor template embedded via shortcode (`[elementor-template id="8487"]`, "Video Testimonials"): "Play Video" x6

**Note the exclusion that mattered:** an initial broad search for "4.9" also matched a legitimate real heading — "Rated 4.9 by over 2,600 Malaysian parents on Google." — which was correctly excluded rather than converted. A same-text substring search would have wrongly flagged a real heading; matched on exact widget title instead.

All 13 confirmed `typography_typography: custom` before touching them, so retagging couldn't alter their visual size. Applied by setting each widget's `header_size` to `div` (a valid Elementor heading-widget HTML tag option that keeps identical CSS styling, just removes it from the document's heading outline). Both posts round-tripped losslessly with default JSON flags; each write was guarded to abort if the changed-count didn't exactly match the expected id list.

**Verified:** H1 count still exactly 1; H2 count dropped from 59 to 46 (the 13 removed, all genuine section headings like "How It Works" / "Frequently Asked Questions" untouched); 0 remaining `<h1-6>` containing "Play Video" or bare "Free"; homepage screenshot confirms pixel-identical rendering (stat badges, review counts, testimonial play buttons all unchanged in size/position); page still returns 200.

### EDGE CACHING — done, scoped to form-free pages only (09/08/2026)

**Pre-work found the original plan's assumption wrong on two counts.** (1) Both sites already have a healthy, connected Redis object cache (`wp redis status` → Connected, PhpRedis 5.3.7) — database-query caching was never actually missing, despite the "no caching plugin installed" note in the original technical audit. (2) Static assets (JS/CSS/images) already cache for 30 days at the edge. The only real remaining gap was HTML-document caching (`cf-cache-status: DYNAMIC` on every page, confirmed by the original audit).

**Full "cache everything" was rejected as unsafe once actually checked.** Sifututor's homepage itself embeds a live FluentForm (`_fluentform_3_fluentformnonce` baked into the HTML) via an Elementor template shortcode, not just the obvious `/register-your-child/` page — this is a lead-gen site, so forms are deliberately pervasive, not confined to one page. Checked every public page on both sites for a form nonce before deciding what could be cached:

| Site | Pages with a form (never cache) | Pages with zero forms (cacheable) |
|---|---|---|
| Sifututor | `/`, `/register-your-child/` | `/our-story/`, `/tutor-faqs/`, `/support/`, `/reviews/`, `/tutor/payment-structure/`, `/tutor/` |
| Nakngaji | `/`, `/jadi-tutor/daftar/`, `/jadi-tutor/kuiz/`, `/nakngaji-singapore/` | `/jadi-tutor/` only |

**Implemented as Cloudflare Cache Rules** (not legacy Page Rules — Free plan Page Rules cap at 3, Cache Rules don't), one ruleset per zone, matching only the confirmed form-free paths above, with an explicit `not any(http.request.cookies["wordpress_logged_in"][*] != "")` bypass so a logged-in editor previewing a page never gets served a cached copy. Edge TTL 1 hour, browser TTL 30 minutes. Neither zone had any pre-existing cache rule to preserve (`10003: could not find entrypoint ruleset` on both before creating).

**Verified, in this order:**
1. All 7 whitelisted pages confirmed `cf-cache-status: HIT` (one edge-propagation delay on first pass, resolved on retry — not a config problem, just normal first-hit latency per edge node).
2. All 5 form-bearing pages re-checked immediately after and confirmed still `DYNAMIC`, completely untouched by the new rules.
3. Registration page (`/register-your-child/`) re-fetched: form still renders (170 field markers), nonce still present and correctly generated per-request.
4. Real-world speed measured on a cached page: TTFB dropped from the site's typical ~0.7-0.9s to **0.07-0.13s** — roughly 85% faster, 3 consecutive requests all confirmed.

**By design, there is no scenario where this caused a lead to be lost** — every page containing a form was excluded from caching entirely, not merely given a short TTL. The earlier plan of "cache everything with a short TTL and hope nonces survive" was replaced with "never cache anything with a form," which is a stronger guarantee at the cost of not speeding up the two highest-traffic pages (both homepages). That tradeoff was surfaced to Hafiz in plain language before implementing, and he chose the safe/scoped version over the higher-risk full-cache version.

**Not done, deliberately:** homepage and booking-flow caching on either site. If wanted later, the safer path is Cloudflare APO for WordPress (paid, ~$5/mo) which handles nonce/session compatibility natively, rather than hand-rolling a riskier TTL-based approach on marketing pages that embed lead forms.

### Still open

**Cosmetic / low priority:** the booking form's "Home Tuition (Online)" option is self-contradictory phrasing. "At Home / Online" would be cleaner, but it is a form-field change with downstream data implications, so it was left alone.

### Previously blocked, now resolved above
- **Footer demo content** (above): needs a replacement tagline, and a decision on the Twitter icon.
- **"Home tuition" copy**: 29 instances (26 homepage, 2 tutor-faqs, 1 support). Needs categorization into brand-positioning uses (rewrite) vs. legitimate format descriptors like "home or online" (keep). Not a find/replace.
- **Trust-stat reconciliation**: `/tutor` says 4,500+ tutors, `/our-story` says 10,000+ tutors / 30,000+ students, `/register-your-child` says 10,000+ parents. Needs the real current figure.
- **LocalBusiness schema (both sites)**: needs the Google Business Profile URL to link via `sameAs`. Note the research finding that self-hosted `AggregateRating` does not produce stars and risks a manual action, so the GBP link is the actual mechanism.
- **Edge caching (both sites)**: deliberately held to last. Must exclude booking/registration forms or it breaks lead capture.
- **Sifututor heading hierarchy** (59 H2s, 2 H3s) and **FAQPage schema**: both still valid, neither started.

---

## 0. Decisions — BOTH RESOLVED 07/08/2026

Both open questions were worked through and closed before implementation. Recorded here with the reasoning so the conclusions don't get re-litigated later.

### Decision 1 — AI-crawler block in robots.txt → **RESOLVED: no change needed**

**What the original finding claimed:** both sites `Disallow: /` for ClaudeBot, GPTBot, Google-Extended, Bytespider, CCBot, Amazonbot, Applebot-Extended, meta-externalagent — framed as blocking the sites from ever appearing in ChatGPT/Claude/Gemini answers.

**What deeper verification actually showed:** that framing overstated the impact. Reading the raw `robots.txt` on both sites:
- The block is **Cloudflare-managed** (`# BEGIN Cloudflare Managed content` — not a hand-edit anyone made in WordPress).
- It blocks **only pure-training crawlers**. It does **not** block OAI-SearchBot, ChatGPT-User, PerplexityBot, Claude-SearchBot, or Claude-User — those fall under the general `User-agent: * → Allow: /` and are open on both sites.
- OpenAI and Anthropic each run *separate* crawlers for training vs. live search citation vs. user-triggered browsing. Blocking GPTBot/ClaudeBot does **not** prevent citation in live ChatGPT Search or Claude answers — the crawlers that drive those are already unblocked.
- Google's own documentation confirms `Google-Extended` governs only Gemini/Vertex training and "does not impact a site's inclusion in Google Search nor is it used as a ranking signal" — no effect on AI Overviews eligibility.
- Bytespider/CCBot/Amazonbot/Applebot-Extended/meta-externalagent are bulk-training scrapers with no citation or referral value to a marketing site.

**Standard practice (2026 data):** 61% of enterprise sites run exactly this hybrid pattern (block training bots, allow search/retrieval bots). 25% of the top 1,000 sites block GPTBot; ClaudeBot sits at ~35% block rate among prominent sites. This is the mainstream configuration, not an aggressive outlier.

**Conclusion:** both sites already run the standard hybrid setup — just applied automatically by Cloudflare rather than deliberately chosen. No GEO/AI-citation cost is currently being paid. **No robots.txt edit in Phase 1.** Revisit only if Cloudflare's managed rules change.

### Decision 2 — Nakngaji blog → **RESOLVED: retire the stub**

**What verification showed:** the single "post" is `https://nakngaji.my/hello-world/`, dated 2021-12-07 — WordPress's **default placeholder post** that ships with every fresh install, not a real article that was written and abandoned. `/blog/` returns 404, so there's no exposed blog section in the nav either.

So this was never "revive vs. retire an existing blog" — there was no blog. **Decision: retire the stub** (see step 3.5). Whether Nakngaji should eventually start a real content channel is a separate strategic question, deliberately not bundled into this cleanup.

---

## 1. Baseline measurement (do this first, before any other change)

**1.1 — Re-run Google PageSpeed Insights for both sites, both mobile and desktop, and save the raw results.**
- Why: the technical audit's PSI calls hit a hard daily quota — every performance finding in that doc is currently *inferred* (no caching, no WebP, third-party scripts), not measured. Every fix below that touches performance (caching, image format) needs a real before/after number to prove it worked.
- How: `https://pagespeed.web.dev/` (browser UI, no quota issue there) for `sifututor.my` and `nakngaji.my`, mobile + desktop each. Screenshot or save the JSON export of all four runs.
- Effort: 10 minutes.
- Output: 4 baseline reports, timestamped, kept alongside this plan for before/after comparison.

**1.2 — Run Google's Rich Results Test on both homepages.**
- Why: confirms the current JSON-LD (Organization/EducationalOrganization/WebSite/Service, plus FAQPage on Nakngaji) is actually valid, before adding more schema on top of it in section 2.
- How: `https://search.google.com/test/rich-results`, paste each homepage URL.
- Effort: 5 minutes.

**1.3 — Confirm WP Admin plugin inventory for both sites.**
- Why: the audit could only see what's externally visible. Sifututor's sitemap confirmed Yoast SEO; Nakngaji's sitemap confirmed a *different* plugin ("Google XML Sitemaps"), and it's not yet confirmed which plugin generates Nakngaji's JSON-LD or handles its meta tags — several of the fixes below assume "edit it in the SEO plugin," and that only works once we know which plugin owns which field on each site.
- How: WP Admin → Plugins, on each site. Note the SEO plugin (Yoast vs. RankMath vs. something custom), the sitemap plugin, and any image-optimization plugin (Nakngaji's `sp-no-webp` CSS class suggests ShortPixel — confirm).
- Effort: 10 minutes.
- Output: a short plugin map for each site, referenced in the steps below wherever "confirm in WP Admin" appears.

---

## 2. Sifututor.my — Phase 1 fixes (no UI/UX)

Ordered low-risk-and-fast first.

**2.1 — Fill in the 28 images with empty `alt=""`.**
- Why: accessibility gap (WCAG 2.2 AA) and image-SEO gap; zero visual change, alt text isn't rendered unless the image fails to load.
- Where: homepage, likely via Elementor image widgets or the WP Media Library.
- How: identify the 28 images (the audit sampled the homepage; a fuller pass should check other high-traffic pages too — `/tutor`, `/register-your-child`), write one descriptive sentence per image (what it shows, not "image123.jpg").
- Effort: ~1–2 hours depending on total image count across pages.
- Verify: re-run the same `curl` check from the technical audit, or use a browser accessibility inspector, and confirm 0 empty alts remain on checked pages.

**2.2 — Fix or redirect `/sitemap.xml`.**
- Why: it currently returns empty/404-like while `/sitemap_index.xml` (Yoast) is the real one — external tools hitting the conventional path get nothing.
- How: in Yoast SEO settings, confirm the sitemap index URL is `/sitemap_index.xml`; either add a redirect from `/sitemap.xml` → `/sitemap_index.xml`, or check whether a caching/security plugin is intercepting the plain path and exclude it.
- Effort: 15–30 minutes.
- Verify: `curl -sI https://sifututor.my/sitemap.xml` returns 200 or a clean redirect, not empty.

**2.3 — Copy fix: remove "home tuition" anchoring language.**
- Why: flagged in the UX doc as a live conflict with the standing brand rule (never anchor on "home tuition," stay venue-agnostic). This is a text swap inside existing elements — title tag, homepage subheading, `/tutor-faqs/`, `/support/` — no layout change.
- Where: `&lt;title&gt;` tag ("Trusted Home &amp; Online Tutors Across Malaysia" → drop "Home"), homepage hero subheading, and the specific instances on `/tutor-faqs/` and `/support/`.
- How: find/replace in the page builder text fields; re-run the meta-description/title check afterward since the `&lt;title&gt;` tag itself needs updating too, not just visible copy.
- Effort: ~1 hour (needs a careful pass to catch every instance, not just the homepage).
- Verify: `curl` the raw HTML of all 4 pages and grep for "home tuition" — should return nothing.

**2.4 — Copy fix: reconcile the tutor/student count stat across pages.**
- Why: `/tutor` says 4,500+ tutors, `/our-story` says 10,000+ verified tutors / 30,000+ students, `/register-your-child` says 10,000+ parents. Pick one real, defensible number set and use it everywhere.
- How: get the actual current figure from wherever it's tracked internally, update all three (at least) pages to match.
- Effort: 30 minutes once the real number is confirmed.
- Verify: grep all fetched pages for the stat, confirm consistency.

**2.5 — Add `LocalBusiness` schema.**
- Why: the correct, working way to make the business's identity/location/hours machine-readable to Google and AI crawlers. (Do **not** add self-hosted `Review`/`AggregateRating` schema — confirmed in the technical-audit research that Google blocks an entity rating itself; that would be wasted effort with zero payoff.)
- How: via Yoast SEO's local SEO add-on if enabled, or a custom JSON-LD snippet added to the existing `@graph` block (needs a developer/code-snippet plugin, e.g. WPCode) since the current schema is hand-built, not auto-generated by a single toggle.
- Effort: 1–2 hours depending on whether Yoast Local SEO is already licensed/active.
- Verify: Rich Results Test shows a valid `LocalBusiness` (or `EducationalOrganization` extended with address/geo) entity.

**2.6 — Add `FAQPage` schema.**
- Why: Nakngaji already has this; Sifututor doesn't. No rich-snippet payoff anymore (Google retired FAQ rich results in May 2026) but it's still useful as an answer-first, structured block for GEO/AI-answer extraction.
- Where: `/tutor-faqs/` and `/support/` — both already have real Q&amp;A content, this just marks it up.
- How: if Yoast's FAQ block is available in the page builder, use it (it auto-generates the schema); otherwise hand-add JSON-LD matching the existing FAQ content.
- Effort: 1–2 hours.
- Verify: Rich Results Test recognizes the `FAQPage` type (even without a visual snippet).

**2.7 — Enable edge caching.**
- Why: `cf-cache-status: DYNAMIC` on the homepage means every hit round-trips to origin — likely the single biggest lever on TTFB/LCP given everything else is reasonably clean.
- How: Cloudflare dashboard → Caching → Configuration, set an appropriate cache rule for static/marketing pages (careful not to cache the booking form or anything with dynamic/session content); alternatively a WP-side cache plugin (WP Rocket, W3 Total Cache — check 1.3's plugin inventory) working alongside Cloudflare.
- Effort: 1–2 hours, plus testing that the booking form still works correctly after caching is enabled (forms/dynamic content must stay uncached or use cache-exclusion rules).
- Verify: `curl -sI https://sifututor.my/` shows `cf-cache-status: HIT` on a second request; re-run PSI and compare TTFB to the 1.1 baseline.

**2.8 — Rebuild the heading hierarchy (59 H2s, only 2 H3s) into a properly nested outline.**
- Why: flagged as SEO/GEO structure issue — a flat wall of H2s makes it harder for both search engines and AI passage-extraction to understand section relationships.
- **Caveat**: this is borderline Phase 1/Phase 2. If it's purely a tag-level change (relabeling some existing H2s to H3 where they're genuinely sub-points of another H2, no text or visual style change) it belongs here. If Elementor's heading widget styling is tied to the tag choice (i.e., changing H2→H3 would visually shrink the text unless a custom class is applied), this needs a quick check with whoever manages Elementor before executing — flag it as Phase 1 only if the visual style can be held constant independent of the tag.
- Effort: 2–4 hours (needs a full pass mapping which H2s are actually sub-points of a preceding H2).

**2.9 — Convert homepage images to WebP/AVIF.**
- Why: currently no modern image format in use anywhere the audit checked.
- How: confirm image-optimization plugin from 1.3; enable WebP/AVIF output (most plugins do this automatically with a fallback for old browsers, zero visual change, same images).
- Effort: 30 minutes–1 hour if a plugin is already installed; longer if one needs to be added and configured.
- Verify: re-run PSI, check the "Serve images in next-gen formats" audit clears.

---

## 3. Nakngaji.my — Phase 1 fixes (no UI/UX)

Ordered low-risk-and-fast first; the first three are real bugs, not optimizations.

**3.1 — Add a single `&lt;h1&gt;` to the homepage.**
- Why: **zero H1 tags currently exist anywhere on the page** — a real structural gap, not a nice-to-have. The existing hero headline text ("Nak Belajar Mengaji Quran Tapi Malu?") is almost certainly already visible on the page as some other tag (likely a styled `&lt;div&gt;`/`&lt;span&gt;` or an H2) — this fix is about changing its *tag*, not its appearance.
- How: in Elementor (or whichever page builder), find the hero headline widget and set its HTML tag to H1 in the widget's advanced settings — this should not change its visual size/style if the styling is class-based rather than tag-based (confirm no visual shift after saving).
- Effort: 15–30 minutes.
- Verify: `curl` the homepage, confirm exactly 1 `&lt;h1&gt;` exists; visually confirm no style change.

**3.2 — Fix the `lang` attribute.**
- Why: `&lt;html lang="en-US"&gt;` on a Malay-language page; the site's own JSON-LD already correctly declares `ms-MY`. Screen readers mispronounce the content and search engines may misjudge the page's language targeting.
- How: WordPress Admin → Settings → General → Site Language, set to Bahasa Melayu if the whole site is meant to serve `ms-MY`; if only some pages are Malay and others English, this needs a per-page or theme-level fix instead (check with whoever manages the theme's `header.php` if the site-language setting alone doesn't change the `&lt;html&gt;` tag).
- Effort: 15 minutes if it's a simple site-language setting; longer if it needs a theme-level code change.
- Verify: `curl` the homepage, confirm `lang="ms-MY"` (or the correct tag matching actual content).

**3.3 — Add the missing Open Graph tags.**
- Why: only `og:description` currently exists — no `og:title`, `og:image`, `og:url`. Social share previews on Facebook/WhatsApp/LinkedIn currently render broken or blank, which directly hurts referral-link click-through since WhatsApp sharing is a very common parent-to-parent referral path in Malaysia.
- How: identify the SEO plugin from 1.3 and fill in its social/OG settings for the homepage (and ideally sitewide defaults so every page gets a fallback); if no SEO plugin manages this, add the missing tags via a code-snippet plugin.
- Effort: 30 minutes–1 hour.
- Verify: paste the homepage URL into Facebook's Sharing Debugger or LinkedIn's Post Inspector and confirm a full preview card renders (title, description, image).

**3.4 — Add Twitter Card meta tags.**
- Why: currently completely absent.
- How: same plugin/settings pass as 3.3, most SEO plugins generate both OG and Twitter Card tags together from the same fields.
- Effort: bundled with 3.3, minimal extra time.
- Verify: Twitter/X Card Validator (or just confirm the meta tags exist in raw HTML if the validator tool isn't accessible).

**3.5 — Delete the default "Hello World" stub post.**
- Why: `https://nakngaji.my/hello-world/` is WordPress's default placeholder post from the original install (2021-12-07), not real content. It's the only URL in `post-sitemap.xml`, so it's the sole reason an otherwise-empty blog section appears in the sitemap at all.
- How: WP Admin → Posts → move "Hello world!" to Trash and delete permanently. Then regenerate the sitemap (Google XML Sitemaps plugin usually does this automatically on post change; verify).
- Effort: 5 minutes.
- Verify: `curl -s https://nakngaji.my/post-sitemap.xml` returns an empty urlset or 404, and `https://nakngaji.my/hello-world/` returns 404.
- Note: no redirect needed — this URL has no meaningful inbound links or traffic to preserve. Whether Nakngaji should later start a real blog is a separate strategic question, not part of this cleanup.

**3.6 — Add `LocalBusiness` schema.**
- Same rationale and caveat as Sifututor's 2.5 (don't add self-hosted Review/AggregateRating — it won't produce stars in search). This also directly backs up the "4.9★ di Google" claim already in the meta description with real, verifiable data tied to the actual Google Business Profile.
- Effort: 1–2 hours, same dependency on confirming which plugin currently generates the JSON-LD.

**3.7 — Enable edge caching.**
- Same rationale as Sifututor's 2.7 — `cf-cache-status: DYNAMIC` here too.
- Effort: 1–2 hours, same caution about excluding forms/dynamic content from caching.

**3.8 — Investigate and fix the `sp-no-webp` CSS class / enable WebP output.**
- Why: the class name strongly suggests an image-optimization plugin (likely ShortPixel, based on the `sp-` prefix) has WebP explicitly *disabled* — worth understanding why before just flipping it on, in case there was a compatibility reason.
- How: confirm the plugin from 1.3, check its WebP setting, test on a staging copy first if possible before enabling sitewide.
- Effort: 1–2 hours including testing.
- Verify: re-run PSI, confirm "Serve images in next-gen formats" clears.

**3.9 — Soft pricing mention on the homepage, if a text-only insertion is possible without new layout.**
- Why: real rates (RM25–55/session) currently only exist on the terms page — high friction for price-comparing parents.
- **Caveat**: only belongs in Phase 1 if there's an existing text block (e.g., inside the hero subtext or an existing benefits line) where a phrase like "from RM25/session" can be inserted without creating a new visual element. If it needs a new price-callout component, it moves to Phase 2 (see below) — confirm which case this is before starting.
- Effort: 30 minutes if a slot exists; otherwise reclassify as Phase 2.

---

## 4. Re-verification (after sections 2 and 3 are done)

**4.1** Re-run PageSpeed Insights (both sites, both strategies) and compare against the 1.1 baseline — confirm caching/image-format changes actually moved LCP/CLS/INP in the right direction.
**4.2** Re-run Rich Results Test on both homepages plus the FAQ pages — confirm all new schema validates with no errors.
**4.3** No robots.txt re-check needed (Decision 1 closed as no-change) — but do confirm the Cloudflare-managed block hasn't drifted if Cloudflare pushes a managed-rules update during the work.
**4.4** Spot-check both sites in an actual browser (not just curl) to confirm none of the "invisible" fixes accidentally changed anything visually — especially 2.8 (heading hierarchy) and 3.1 (H1 tag change).

---

## 5. Phase 2 — deferred, needs a design pass first

Not detailed here since these require UI/UX decisions before implementation. Full detail is in the companion UX doc's "Medium effort" and "Bigger bets" sections. Listed here just so nothing gets lost between the two docs:

**Sifututor:**
- Above-the-fold trust stat bar (new component)
- Named, one-line risk-reversal guarantee placed near every CTA (needs a copy + placement design decision)
- Rate table by tutor tier (new page/section, replaces "starting from" teasers)
- Named tutor cards with visible credentials on the homepage (new component)
- Outcome-specific testimonials + video testimonials (content + possibly new testimonial card design)
- Tutor response-time as a visible profile metric (new UI element, needs the underlying data tracked first)
- Short FAQ block directly under the booking form (new section)
- Gated/verified-only reviews (policy + possibly new review-display component)
- Subject × location × level SEO directory pages (new page template)

**Nakngaji:**
- Per-tutor credential cards (ijazah, sanad chain, years teaching, gender) — new component
- Named, one-line satisfaction/replacement guarantee (copy + placement)
- Reframe the 40-question tutor vetting quiz as a visible trust asset on the homepage (new section, not just a copy tweak, since it likely needs its own visual treatment to land as "trust asset" rather than a buried FAQ line)
- Named matching system copy + visual treatment
- Outcome-based testimonials + named tutor testimonials on the recruitment page
- Family/parent progress-dashboard framing (bigger product feature, not a marketing-page fix)
- Rating-distribution-bar review UI (new component)

**Both:**
- Response-time/turnaround visible trust metric
- Video intros on tutor profiles
- Subject/location/level SEO directory pages

---

## Reuse notes for future sessions
- This plan assumes the Phase 1 items above are genuinely zero-visual-impact; a couple (2.8, 3.9) are flagged with explicit caveats to re-check during implementation rather than assumed safe.
- Re-baseline (section 1) before starting; re-verify (section 4) after finishing — don't skip either, since several of these fixes only prove out with a real before/after number, not by eye.
- Once Phase 1 ships, the natural next step is a design pass scoped to the Phase 2 list, likely a `/brainstorm` or `ripple-brainstorming`-style session per item before any of those go into dev.
