# Sifututor Ecosystem Executive Deck — Asset Review Register

Status: active visual-quality gate  
Purpose: prevent weak, misleading, sensitive, or presentation-unfriendly assets from entering the executive deck.

## Approval rule

An asset may appear in the presentation only when it passes all five checks:

1. **Relevant** — it proves a capability that matters to the ecosystem story.
2. **Visually strong** — it has a clear focal point, useful composition, and enough visual character to hold attention.
3. **Slide-legible** — its important content remains understandable inside a 16:9 presentation frame.
4. **Truthful** — its status is known and can be described accurately as live product, current product evidence, controlled test evidence, or prototype.
5. **Safe** — it contains no exposed personal data, credentials, confidential operational details, or misleading performance figures.

Decisions:

- **APPROVED** — safe to compose into a slide, followed by a final in-slide inspection.
- **CONDITIONAL** — requires cropping, masking, annotation, or a clear status label; the derivative must be inspected again.
- **REJECTED** — must not be used.
- **CURRENT CAPTURE NEEDED** — capability is important, but the available asset is not suitable evidence.

## Reviewed assets

| System | Source | Visual assessment | Truth / safety assessment | Decision | Required action or intended use |
| --- | --- | --- | --- | --- | --- |
| Ripple Suite | `ripple-suite/public/help/screenshots/help-homepage.png` | Strong module overview with clear product breadth. | No obvious personal data. The source's temporary process banner, beta labels, and incomplete lower module row were excluded. | APPROVED | Verified derivative: `assets/verified/ripple-capability-overview.png`. Candidate for the ecosystem control-layer montage. |
| Ripple Suite | `ripple-suite/public/help/screenshots/matching-request-detail.png` | Weak loading/skeleton state; does not communicate finished capability. | Safe, but visually unconvincing. | REJECTED | Do not use. |
| Ripple Suite | `ripple-suite/public/help/screenshots/reconciliation-dashboard.png` | Useful financial-operations structure. | Contains volatile operational figures and a temporary banner. | CONDITIONAL | Use only if all figures and the banner are removed or replaced with a safer current capture. Re-inspect afterward. |
| Ripple Suite | `ripple-suite/public/help/screenshots/matching-request-list.png` | Visually clear matching workflow and meaningful information density. | Exposes parent/student names, dates, locations, request IDs, and operational counts. | REJECTED | Do not use the original. A purpose-built anonymised capture is required if matching detail is needed. |
| Ripple Suite | `ripple-suite/public/help/screenshots/tutor-payments-overview.png` | Clean interface but dominated by an empty state; limited presentation value. | No personal data, but includes a stale-data warning and date-specific zero figures. | REJECTED | Do not use. Seek a stronger, safely anonymised payment-flow view. |
| Ripple Suite | `ripple-suite/public/help/screenshots/knowledge-luna-chat.png` | Strong, distinctive AI knowledge-workspace view; clear focal area and executive-level relevance. | No visible personal data or confidential metrics. The temporary process banner and unrelated product sidebar were excluded. | APPROVED | Verified derivative: `assets/verified/ripple-luna-workspace.png`. Candidate for the intelligence/knowledge layer. |
| Finch | `finch-inbox/docs/audits/2026-06-05-product-audit/screenshots/10-inbox-default.png` | Broken-state image showing invalid access and cookie UI. | Not credible product evidence. | REJECTED | Do not use. |
| Finch | `finch-inbox/docs/audits/2026-06-05-product-audit/screenshots/11-owner-dashboard.png` | Dark multi-brand view, but visually repetitive and dominated by zero/test states. | Contains E2E/test-brand identifiers, a cookie banner, staging reference, and operational state. | REJECTED | Do not use. Capture a clean, representative inbox or omnichannel workspace instead. |
| Finch | `finch-inbox/docs/audits/2026-06-05-product-audit/screenshots/52-settings-analytics.png` | Strong dark analytics aesthetic and clear table structure. | Exposes channel names, response-rate data, timing metrics, and a cookie banner. | REJECTED | Do not use in an executive deck. A clean anonymised current capture is needed. |
| Creative Hub | `creative-hub/docs/assets/width/dashboard-after.png` | Clean but visually sparse; weak as a hero product proof. | Contains a user initial, greeting, and date. | REJECTED | Prefer the Content Planner view. |
| Creative Hub | `creative-hub/docs/assets/width/planner-after.png` | Strong capability proof: content workflow, brand filtering, status, design, and publishing schedule in one view. | Uses clearly marked demo content. Identity chrome and unrelated navigation were excluded; the `demo` status remains visible. | APPROVED | Verified derivative: `assets/verified/creative-hub-content-planner.png`. Candidate for the growth/content operations montage. |
| Creative Hub | `creative-hub/docs/assets/width/departments-after.png` | Too sparse to hold attention in a presentation. | Safe except for user initial; limited narrative value. | REJECTED | Do not use. |
| Learnest | `lls/docs/mobile-app-prototype/screenshots/student-00-dashboard-after-login-vp.png` | Visually polished mobile-product proof with a strong device-format contrast to desktop systems. | Prototype evidence, not confirmed live-product evidence; synthetic identity appears safe. | APPROVED | Verified derivative: `assets/verified/learnest-student-dashboard-prototype.png`. It must always carry a visible `Prototype` label. |
| Kelasapp | `kelas/screenshots/feature-showcase.png` | Attractive multi-feature composition. | Exposes a real-looking customer name and invoice value. | REJECTED | Do not use the original. Create a privacy-safe crop/mask derivative or obtain a clean current capture. |
| Tutor App | `sifututor_tutor/docs/ui-audit-screenshots/home-01-top.png` | Polished mobile dashboard structure. | Exposes a real-looking tutor name, earnings, activity metrics, and an offline warning. | REJECTED | Do not use. Obtain a safe representative capture with synthetic data and a healthy connection state. |
| Parent App | Repository asset inventory | No suitable presentation screenshot was found in the initial inventory; app icons alone do not prove capability. | No evidence asset approved yet. | CURRENT CAPTURE NEEDED | Capture a clean representative parent journey with synthetic or approved data. |
| SIMS | Repository asset inventory | Brand assets exist, but no approved presentation-grade operational screenshot was found in the initial inventory. | No evidence asset approved yet. | CURRENT CAPTURE NEEDED | Capture one safe, information-rich operational view that demonstrates the SIMS core without personal or financial data. |
| Sifututor public brand imagery | `https://sifututor.my/wp-content/uploads/2025/03/register.jpg` | Strong human-learning moment with clear emotion and sufficient crop flexibility for an editorial hero. | Public first-party Sifututor imagery; no visible private data or unsupported product content. | APPROVED | Local derivative: `assets/verified/sifututor-human-learning-public-v1.jpg`. Use as the dominant human-service image, not as system evidence. |
| Generated supporting photography | Built-in image-generation workflow, parent coordination scene | Strong editorial composition with useful left-side negative space, realistic hands, natural lighting and no visible text. | Generated supporting imagery only; no interface, logo, metric or capability claim. | APPROVED | `assets/verified/generated-parent-coordination-v1.png`. Always identify as illustrative/generated in the prototype evidence note. |
| Generated supporting photography | Built-in image-generation workflow, operations coordinator scene | Strong editorial composition with useful right-side negative space, realistic subject and restrained styling. | Generated supporting imagery only; no interface, logo, metric or capability claim. | APPROVED | `assets/verified/generated-operations-coordinator-v1.png`. Always identify as illustrative/generated in the prototype evidence note. |
| Malaysia map | Wikimedia Commons `Blank malaysia map.svg` | Recognisable flat Malaysia geography suitable for the reference-style roadmap component. | Geographic base map only; recoloured for Sifututor. It does not indicate current foreign operations. | APPROVED | `assets/verified/malaysia-map-public-v1.svg`. Pair only with direction language and the explicit no-launch-commitment guardrail. |

## Logo candidates requiring canonical check

| Candidate | Inspection result | Decision |
| --- | --- | --- |
| `sifu-tutor/public/images/logo.png` | Correct full-colour Sifututor wordmark, 539×112 with transparency. Strong on a light surface. | APPROVED on light backgrounds only. |
| `sifu-tutor/public/images/logo-dark.png` | Renders the unrelated word `CROVEX`; it is not a Sifututor logo. | REJECTED. |
| `ripple-suite/public/logo-3.png` | Appears identical to the Sifututor wordmark rather than a distinct Ripple Suite identity. | REJECTED as a Ripple logo pending canonical confirmation. |
| `finch-inbox/frontend/public/finch-logo.png` | Clean transparent bird mark at 256×256; remains distinctive at small presentation size. | APPROVED. |
| `lls-frontend/public/assets/images/Learnest-logo.png` | Compact transparent Learnest wordmark at 132×26; legible when treated at sufficient width and contrast. | APPROVED with contrast treatment. |

## Generated-image gate

Owner correction, 1 September 2026: the ecosystem executive deck must avoid isometric and 3D imagery at all cost. Generated-image records below are retained only to preserve the review history. No generated image is active in the approved flat editorial direction.

AI-generated imagery is supporting visual language, never product evidence. A generated asset is approved only when:

- it contains no invented interface, logo, product name, metric, or business claim;
- it has a clear focal point and useful negative space for slide composition;
- it visually supports the actual ecosystem narrative rather than generic “technology” decoration;
- hands, faces, devices, perspective, connections, and repeated objects are free of obvious generation defects;
- it is inspected at full resolution and again inside the final slide;
- its role is visually distinct from real screenshots and official logos.

For each concept, generate multiple candidates and select only the strongest. A technically successful generation is not automatically an approved asset.

## Generated-image review record

| Asset | Visual assessment | Defect / truth assessment | Decision | Presentation role |
| --- | --- | --- | --- | --- |
| `assets/rejected/ecosystem-hero-a.png` | Strong cinematic composition and useful negative space. | Contains invented interface graphics on multiple devices. | REJECTED | None. Preserved only as review evidence. |
| `assets/rejected/ecosystem-hero-b.png` | Strong right-weighted ecosystem and clean title space. | Isometric/3D visual treatment conflicts with the owner-approved editorial direction. | OWNER-REJECTED | None. Must not return to the active deck. |
| `assets/rejected/command-centre-a.png` | Clean, balanced command-centre architecture. | 3D environment conflicts with the owner-approved editorial direction. | OWNER-REJECTED | None. Must not return to the active deck. |
| `assets/rejected/service-journey-a.png` | Strong loop and readable stage separation. | Contains multiple garbled generated labels despite the no-text instruction. | REJECTED | None. Preserved only as review evidence. |
| `assets/rejected/service-journey-b.png` | Strong unlabeled loop with four visually coherent service scenes. | Produced four islands instead of five and uses the prohibited 3D/isometric treatment. | OWNER-REJECTED | None. Must not return to the active deck. |
| `assets/rejected/service-journey-c.png` | Clean loop and polished rendering. | Again produced four islands; also introduced small device-like surfaces. Less useful than journey B. | REJECTED | None. Preserved only as review evidence. |

## Final in-slide verification

After composition, every slide must be rendered at 1920×1080 and inspected for:

- focal hierarchy within three seconds;
- readable headline and supporting sentence;
- screenshot readability without zooming;
- no accidental exposure created by cropping;
- consistent logo sizing and adequate contrast;
- no misleading implication that generated art is a real interface;
- balanced density, strong visual interest, and no wall-of-text effect.

Only the rendered slide—not the source asset alone—is the final approval unit.
