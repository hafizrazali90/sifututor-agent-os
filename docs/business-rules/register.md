# Business rule register

Compiled on 3 October 2026. Start with [the authority and loading guide](README.md).
This register is a sourced compilation, not blanket approval of 104 policies.
Existing approved domain documents own their product decisions. Current user
corrections govern their exact scope. Historical memories, drafts and staff
requests remain visibly qualified. Code/database observations prove behaviour,
not intent. Rationale not recorded by a source remains unknown.

## BR-001

**BR-001 — One shared session for a multi-student Request. USER CONFIRMED.** When a Tutor Request selects students A, B and C for the same session, they participate together in one class session. Do not create one session per student merely because the Request contains three students. Separate Requests or genuinely separate scheduled sessions are different arrangements. Source: Hafiz’s current correction, Koda mem_1591e221e0e1. Rationale beyond this intended shared-session meaning was not supplied. Acceptance example: scheduling one session for A/B/C produces one session with three participants; student-specific evaluations can remain separate. Corroboration: [recovered corrective pack](https://chatgpt.com/space/page_da5a11a90d0c8191a95bdc2ae50ec786), section 3.4, explicitly says all selected students share the same tutor, subject, mode and lesson; each extra student adds price, never duration.

## BR-002

**BR-002 — Ownership and participation are different relationships. MEMORY EVIDENCE.** Student ownership belongs to the SIMS Parent; a Request selects its exact participating subset. A CRM enquiry or preparation record is not automatically the authoritative Student record. Source: mem_287d14be98b7; older imported Lead student memory mem_f6a2ef2fa655 needs interpretation in that preparation/import scope. Why: family ownership does not imply every child attends every Request. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-003

**BR-003 — Student limits depend on channel and object. LATER ISSUE DECISION.** Parent self-service selects at most five students per Request; staff/admin Requests have no maximum in the cited corrective decision. The family profile does not have a five-child cap. Source: [SIMS issue 2987](https://github.com/Sifututor/sifu-tutor/issues/2987). Why: a reported sixth-child failure came from putting a Request selection guard on the family profile. Older Nakngaji wording saying “maximum five” without channel context must not be applied globally. A closed issue does not establish that the production fix was verified.

## BR-004

**BR-004 — Extra participants do not add teaching time. SOURCE DECISION.** Extra-student pricing is separate from session duration. Additional students do not automatically multiply duration or produce extra sessions. Source: Nakngaji decision register. Acceptance: three students in one 30-minute online session remain one 30-minute session.

## BR-005

**BR-005 — Request identity includes delivery arrangement. MEMORY EVIDENCE.** The same student and subject may legitimately have separate Online and Physical Requests. Exact same Parent/student set/subject/mode requires duplicate review or an authorized separate-arrangement reason. Source: mem_b8644f135a63. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-006

**BR-006 — Scheduling plans; attendance consumes. LATER ADDENDUM.** An invoice purchases credits. Scheduled/Ongoing classes are planning records, not authoritative consumed invoice allocations. Consume one credit at the first Attended commit. Verified confirms that class and must not consume another credit. Source: sifu-tutor/docs/features/billing-cycle-revamp/ADDENDUM-B-class-invoice-separation.md and [issue 1785](https://github.com/Sifututor/sifu-tutor/issues/1785).

## BR-007

**BR-007 — Allocate in attendance-recording order. LATER ADDENDUM.** Use the oldest available invoice credit when attendance is committed, with serialized consumption. Do not reorder already consumed allocations by calendar class date. A backdated class recorded later cannot relocate an earlier consumption. Why: scheduling edits and backdating must not rewrite consumed financial history. Earlier calendar-based rebucketing and scheduled-class allocation instructions are superseded for this scope.

## BR-008

**BR-008 — Reversal restores the original credit. LATER ADDENDUM.** An authorized erroneous-attendance reversal before Verified/tutor payment restores exactly one credit to the same invoice. Other classes do not move. Verified or tutor-paid records require investigated adjustment/refund handling. Refunds reduce purchased credits and do not create replacement credits. Preserve legacy Attended/Verified allocations; no mass historical relinking or rebuilding.

## BR-009

**BR-009 — Payment and verification gates have an explicit first-class exception. LATER ADDENDUM.** The first parent class may be verified while its first invoice is unpaid. Later normal verification follows the paid gate; investigated admin handling remains distinct. Normal tutor payment requires a real Verified class. Source: same addendum. Do not turn an exception into blanket unpaid verification.

## BR-010

**BR-010 — Dormant automation stays dormant. SOURCE SAFETY DECISION.** The historical seven-day auto-verification command is unscheduled and must not be enabled simply because it exists. Source: addendum. A command’s existence is not business authorization.

## BR-011

**BR-011 — Unpaid escalation is a dated policy, not a universal formula. HISTORICAL SOURCE.** Older June billing material describes a watch at one unpaid invoice, a hard stop at two, overdue follow-up after seven days and a 72-hour escalation grace. Preserve that source/version and compare later changes before implementation. Invoice Paid/Unpaid status and Ripple partial receipts describe different layers; they are not inherently contradictory.

## BR-012

**BR-012 — Unpaid tutor commitment fee does not itself block SifuTutor assignment. LATER ISSUE DECISION.** Shortlisting can occur before TX approval. Final assignment requires TX Approved or the accepted existing globally verified/legacy-active route. An unpaid tutor commitment fee does not block assignment or first scheduling and does not require an exception solely for that fee. Awaiting/correction states still block; suspended, rejected, resigned and terminated states remain hard blocks. Source: [SIMS issue 2424](https://github.com/Sifututor/sifu-tutor/issues/2424). This does not waive Nakngaji’s separate brand-qualification requirement; see BR-075. Collection follow-up remains separate.

## BR-013

**BR-013 — Discovery fit, contactability, profile access and assignment readiness are distinct. MEMORY EVIDENCE.** Preserve Strong / Other Suitable / Wider fit groups; scoring cannot lift a weaker group above a stronger one. Inferred evidence must not be labelled exact subject fit. General reusable availability was deferred in the cited matching decision. Source: mem_e143e4c38bc2 and related matching correction memories; full IDs/original source should accompany implementation work. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-014

**BR-014 — An application is tied to the offered Request version. MEMORY CORRECTION.** Preserve the exact Request revision/fulfilment cycle and safe schedule/location snapshot. Legacy unbound interest is not equivalent evidence. Full household addresses do not belong in public application previews. Source: mem_83decd0f7ee7 family of correction records; locate the full record before changing the contract. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-015

**BR-015 — Web application uses the same application engine. SOURCE-DECLARED CONFIRMED DECISIONS.** Phone OTP resolves the same tutor identity. Tutors can apply before completing preferences, resume partial onboarding, and retain the application if they abandon later preferences. Open to other times is valid. Encourage the app without forcing installation. Opaque public links and safe previews are required. Source: public tutor acquisition clarification, 49-decision snapshot above.

## BR-016

**BR-016 — Earlier CX ownership is historical; use the September division. SUPERSEDED IN SCOPE.** July memories distinguish TX tutor verification/fee work from CX Request approval and parent communication. They must not reinstate one undivided CX Support owner after the approved September Matching/Customer Facing split. Use BR-080–083 for those responsibilities and the Verified first-class completion milestone. Sources: mem_53099b1ff1c6, created 26 July; mem_c5804337d1d4, updated 31 July; dual-cx-build-ready-pack-2026-09-14.md. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-017

**BR-017 — Exactly one operational Lead per Request; Family is optional. LATER MEMORY CORRECTION.** Each Request belongs to one operational Lead across channels. App Requests resolve the exact SIMS Parent’s canonical Lead, or create it with verified contact and source. Repeated submissions reuse it. A Family optionally groups two or more distinct Leads; duplicate same-contact Leads should be consolidated/archive-reviewed rather than turned into a Family. Source: mem_b5ed8a4f0ad7, August 26. This supersedes older Family-mandatory July diagrams within that corrected topology. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-018

**BR-018 — Shared contact data is not sufficient identity proof. MEMORY CORRECTION.** Different Parents may share phone/email. The exact SIMS Parent key identifies its canonical Lead; contact identity changes require governance. Do not automatically merge all equal phone numbers. Source: mem_2ae97d727bfd. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-019

**BR-019 — Enquiry and confirmed Request requirements are different. MEMORY EVIDENCE.** Preserve original acquisition context on the Lead. Exact confirmed matching requirements belong to each Request. New later requirements create additional Requests rather than overwriting earlier ones. Source: mem_0af2b45f564d family. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-020

**BR-020 — Historical imports do not trigger new operations. MEMORY CORRECTION.** Imported provenance does not disqualify legitimate new Request creation, but importing old history must not automatically create tasks, invoices or matching work. Preserve history and resolve the current PIC from current SIMS evidence rather than treating a spreadsheet as authority. Sources: mem_d23645d60c04, mem_d81095448ceb, mem_736ad21acf8e and mem_d1a2a7c9b7be families. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-021

**BR-021 — Tasks represent owed work, not a status label. SOURCE/MEMORY EVIDENCE.** A healthy InService customer does not need a fake matching task. An SLA expiry is not proof the customer no longer wants service. Older “auto lost after seven days with no tutor” was replaced by a seven-business-day evidence review and a manual outcome. Pre-service Cancelled/Lost differs from post-service Ended; genuine service history remains. Sources: CRM status/automation map and later correction memories. The exact latest owner source must accompany code changes.

## BR-022

**BR-022 — Capacity, operating calendars and consent need explicit settings. DATED SOURCE.** Older CRM policy records team capacity 30 with personal/today overrides, Mon–Fri 09:00–18:00 MYT, and versioned configuration without resetting SLA merely on handoff. Unavailability does not silently reassign existing work. DoNotContact requires an explicit consent lift and does not auto-expire. Later Lead/Family topology corrections mean consent scope must be reconciled rather than copied from old Family diagrams.

## BR-023

**BR-023 — One logical parent commitment fee per Request. MEMORY CORRECTION.** Duplicate fee rows on the same Request are a data conflict, not a fee-precedence rule. A valid paid, non-refunded fee elsewhere can support an explicit reasoned staff waiver where permitted; never auto-waive from its existence. Sources: mem_aeff90ddd80a family. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-024

**BR-024 — A refunded parent fee changes new-start eligibility, not history. MEMORY CORRECTION.** Finance review is needed for a new first class after refund; an already started service is not automatically cancelled. A refunded fee cannot qualify for a cross-Request waiver. Source: mem_8362efece955 family. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-025

**BR-025 — One month resignation notice. CURRENT USER CONFIRMED, 3 OCTOBER 2026.** Hafiz reconfirmed that the resignation notice condition for tutor commitment-fee refund operational eligibility is one month. This supersedes older two-month wording and resolves the historical-memory uncertainty. Finance validates the actual completed fee payment and refundable amount separately; this confirmation does not authorize a payment or code change. Source: Hafiz’s direct answer in this session, “One month”; updated mem_229322a1cdde. Recorded rationale in the prior source: time to find replacements for assigned Requests.


## BR-026

**BR-026 — Forty weighted verified hours award one RM200 bonus under the cohort rules. ISSUE DECISION.** Qualifying crossings on/after 1 July 2026 for active/verified tutors award one unpaid RM200 record. The July-reset cohort counts from July 1; restoration of earlier cases is individually reviewed. Bootstrap/migration activity is excluded. Existing, legacy or soft-deleted bonus records prevent duplicates. Attach to the nearest eligible class-backed payout; no bonus-only payout. Event processing is primary, nightly recovery secondary. Source: [issue 2277](https://github.com/Sifututor/sifu-tutor/issues/2277).

## BR-027

**BR-027 — Progress is not entitlement. MEMORY CORRECTION.** Attended-inclusive bonus progress and verified-hours payable qualification are distinct. A 100% progress display is not evidence that a bonus entitlement row exists. Hours are not class count. Sources: mem_b24d65b6052f and mem_acccbcd866cc families. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-028

**BR-028 — Evaluation and progress reports serve different purposes. SOURCE DECISION.** First-class evaluation establishes a baseline. The Nakngaji register calls for a progress report after twelve Verified classes; quick lesson notes are separate. Overdue reports must not cause an invented 10% deduction or payment delay. Older quarterly wording is not automatically the current cadence.

## BR-029

**BR-029 — Notification policy, delivery mechanism and observed sends are separate evidence. SOURCE REVIEW PLUS IMPLEMENTATION MEMORY.** The 9 June notification policy review explicitly lists request pause/reactivation as push + in-app, with a once-per-request/day cap; it reserves cross-channel WhatsApp/SMS escalation for payment risk. Therefore older WhatsApp wording cannot be generalized to all lifecycle actions. The 2 October code-check memory reports pause/resume/reopen push-only, cancellation push+email and ConfirmFirstClass email+push. That memory does not prove recipient delivery, and the June matrix does not establish a complete current email policy. Source: sifu-tutor/docs/features/notification-architecture/parent-tutor-notification-policy-review.md and mem_7cfd40299b1f. Before a sending action, inspect its exact current jobs, recipients and delivery evidence. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-030

**BR-030 — Staff commission calculation. SOURCE-DECLARED CONFIRMED RULES.** First invoices only. Commissionable amount = amount_due + approved commitment_fee_offset; do not add every discount back. Month = payment_date; missing payment_date means skip and flag, not guess. Eligible assigned staff must be active with a linked SIMS user; no CX department restriction. Monthly totals are per staff across Requests. Configurable defaults: below RM11,000 is 1%; RM11,000 and above is 2%. Source: staff commission snapshot and mem_1620.

## BR-031

**BR-031 — Commission history is auditable. SOURCE DECISION.** Keep rule snapshots, unique invoice+rule rows and skip zero amounts. Recalculate unpaid rows after crossing a monthly threshold; paid rows are immutable with adjustments. SIMS paid marking records external payroll rather than performing payroll. Unmark requires permissions and audit. Additions/deductions belong on payment records, not rewritten ledger entries.

## BR-032

**BR-032 — Tutor pay authority is SIMS class earnings. SOURCE DECISION.** Actual class.total_amount is primary; Ripple recalculation is a comparison, not a second authority. Eligible historical verified unpaid classes remain payable. The actual class tutor matters even if the Request was later reassigned. Separate additions, bonuses and deductions. Actual bank transfer proof precedes SIMS synchronization and paid marking; a provider callback is not automatically that proof. Source: tutor payments clarification. Export format and provider details must use the latest source rather than old CSV-only assumptions.

## BR-033

**BR-033 — Pending Verification is not Pending Payout. SOURCE DECISION.** The Tutor Ledger separates Attended/unverified backlog from Verified/unpaid payable. Default all-time unpaid visibility prevents past debts being hidden by a current-month filter. Phase 1 is read-only because SIMS already has the AP workflow; separate accounts.tutor_view permission from parent Accounts access. Source: ripple-suite/docs/features/tutor-ledger/clarification.md.

## BR-034

**BR-034 — Payment corrections and invoice credit/debit notes have separate controls. CLARIFIED DOCUMENT SCOPE.** The February 20 Accounts PRD allows audited payment-record edits and soft deletion (F28–F29). Credit/debit notes instead require different creator and approver, use Draft → Approved/Rejected and reasoned Approved → Voided, and retain history; only Approved notes affect balances (F35–F38). Every CN/DN references one invoice. These rules coexist in the same source and do not grant blanket editing/deletion of finalized financial records. SIMS remains invoice/full-payment authority; Ripple composes its governed receipts and adjustments without double-counting fee offsets. Sources: accounts/clarification.md Q15 and Q21–Q23; accounts/prd.md F28–F38. This is the source’s clarified design, not a new authorization for financial writes.

## BR-035

**BR-035 — Fee offset is a payment split, not duplicate revenue reduction. MEMORY CORRECTION.** Parent commitment-fee offsets must not be counted twice. Tutor refundable deposits are not automatically revenue. Use approved invoice adjustments once. Historical metric values are dated observations, not permanent financial rules. Sources: revenue clarification and mem_0590 family.

## BR-036

**BR-036 — Shared platform, separate brand qualification. SOURCE DECISION.** SIMS owns core operations, Ripple is the operational interface, identity is reusable across brands, and brand membership/qualification is separate. Nakngaji begins with its governed Quran catalogue; other subjects require scoped admin governance.

## BR-037

**BR-037 — Standard monthly requests and promotional packages are distinct choices. LATER USER CORRECTION.** Normal Nakngaji requests follow SifuTutor: choose classes per week and duration; derive monthly class count as weekly frequency × 4. Do not ask for an arbitrary ordinary total or force minimum totals of five online/four physical. Promotional bundles are additional commercial choices with their own immutable session quantities, not replacements for the normal flow. Online minimum duration is 30 minutes and physical 45 minutes. Extra time follows BR-074. Preserve old purchased credits and terms through later changes. Sources: mem_6bab6f2e4224, mem_37028012a8f2, mem_9af9e61ee750. This corrects the earlier unit-pricing summary in this compilation. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-038

**BR-038 — Discount and extra-student earnings have separate bases. SOURCE DECISION WITH CONFIGURATION QUALIFICATION.** Package discounts affect base tuition only; extra time and additional-student charges remain full price. Tutor extra-student payment is a fixed configured add-on, independent of the 30%/70% base-tuition split. At activation copy the current active SifuTutor surcharge/add-on values into independently configurable Nakngaji brand/mode settings; do not hardcode historical example rates as permanent policy. Each purchase snapshots its rates. Sources: mem_cafcca86d2c8, mem_090a5448d557, mem_b4700046489f. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-039

**BR-039 — Tutor earning sequence is distinct from customer consumption. SOURCE DECISION.** For the actual tutor and Request, verified earning sequence 1–7 uses 30%, then 8+ uses 70%; it continues across package cycles and resets on replacement tutor. Do not reset every invoice or confuse customer credit number with tutor earning sequence. One monthly payout can have brand sections.

## BR-040

**BR-040 — Qualification uses governed assessments. SOURCE DECISION.** Recorded Sifu threshold 16/20; Nakngaji SOP 16/19 and Tajwid 16/20 both required. Three attempts per version; additional attempts need staff reason. No answer disclosure. Audio submission is 2–3 minutes via upload in this decision. Assessment failure does not reject a person’s whole identity. Question bank requires qualified authoring/review; no AI-generated live examination. New Requests follow the chosen cutoff; legacy ongoing Requests preserve their old terms and migration is a separate phase.

## BR-041

**BR-041 — Recommend the 15-online and 12-physical packages. RECONCILED SOURCE DECISION; CURRENT CODE CORROBORATES.** The 20 August corrective pack recommends these presets for each price band while keeping all eligible presets selectable. Full Koda recall establishes that the neutral-presentation memory mem_08996bcb985a was created 18 August 2026 at 07:55 UTC and is explicitly marked outdated. It is older, not a later override; the previous compilation’s claim was incorrect. Current remote SIMS main at 82eab470cb8a9c85fbbbba60a42ffbb23bbdd25d sets the same recommendation defaults in NakngajiLaunchCatalogueService.php:283–284. UI labels follow the stored recommended flag, so source code does not prove the live database values or visible production page. Sources: [recovered pack](https://chatgpt.com/space/page_da5a11a90d0c8191a95bdc2ae50ec786), section 3.5; full Koda recall on 3 October; [pinned code](https://github.com/Sifututor/sifu-tutor/blob/82eab470cb8a9c85fbbbba60a42ffbb23bbdd25d/app/Services/Nakngaji/NakngajiLaunchCatalogueService.php#L283). No fresh business decision is needed.

## BR-042

**BR-042 — Request-based eligible cohort. SOURCE BUILD-PACK DECISION.** Recorded default cohort: Requests created on/after 1 September MYT, Open/legacy-active, without assigned/approved tutor. A staff owner is not a prerequisite. Bundles contain 1–3 eligible Requests and may cross owners. No invented 15-minute batching wait. Older same-owner bundle rules are superseded by this pack.

## BR-043

**BR-043 — Delivery starts the response clock. SOURCE DECISION.** Target three active applicants, batch maximum twenty, four-hour review starts at first confirmed delivery, not enqueue. Zero deliveries is a delivery problem, not lack of tutor interest.

## BR-044

**BR-044 — Contact caps survive operational changes. SOURCE DECISION.** Automatic opportunity window is 09:00 inclusive to 21:00 exclusive MYT. One automatic opportunity per tutor/day; recorded manual outreach counts, replies do not. Permanent tutor–Request no-repeat survives day/revision/owner/cycle changes without override. Queued/uncertain sends reserve capacity. Manual+automatic shared cap is sixty distinct Requests, with reasoned supervisor extension of 1–20. An unset daily RM budget requires cost review. Values are governed settings rather than scattered constants.

## BR-045

**BR-045 — Safe delivery recovery and routing. SOURCE DECISION.** Finch owns delivery retries: two definitive no-send retries after five then fifteen minutes. Unknown outcome is held and reconciled against the same operation, not resent under a new ID. Replies remain KeepUnassigned until an authorized claim; the Ripple Request owner is not automatically Finch inbox routing.

## BR-046

**BR-046 — Compare outreach costs against the same cohort. SOURCE DECISION.** Include manual and automatic spend and unresolved/no-approval outcomes. Allocate bundle costs across actual included Requests. Zero approvals means an unavailable cost-per-approval ratio, not zero cost. Fit precedes urgency, then scarce suitable supply, then age/ID tie-break. Historical group-post coverage is unknown rather than silently enforced.

## BR-047

**BR-047 — Kelasapp has its own group-class business model. DATED BUILD DECISIONS.** Guardian identity is separate from Student; family invoices combine child lines, adult students may pay themselves. Monthly class fees and teacher rates belong to the class and freeze for billing; they are not inherited blindly from a level. Recurrence lazily materializes sessions on action. Actual session teacher determines pay. Late counts as attended, Excused is excluded, Unmarked is not Absent; edit-window decisions use MYT. MVP billing is manually started and idempotent, with flat billing rather than invented proration. Payment proof remains pending until verified; a static DuitNow QR does not embed an invoice amount or prove payment. EN/BM support and the later BetterAuth decision supersede older source assumptions in their dated scope. Source: Kelasapp build-log snapshot.

## BR-048

**BR-048 — Finch pricing separates platform and messaging costs. CANONICAL DATED SOURCE.** July source lists RM199/RM449/RM899 monthly, RM1,908/RM4,308/RM8,628 annual and 3/8/20 seats, seven-day no-card trial, with v1 grandfathering. BYOWABA Meta charges go to the customer; ManagedWABA uses prepaid wallet reserve/capture and failed-send release/refund handling with balance limits. Treat these as dated commercial terms, not live-price verification. Only the approved Embedded Signup path is a customer onboarding flow; internal credentials are not a fallback. Source: Finch pricing snapshot.

## BR-049

**BR-049 — Learnest linking requires proof of ownership, not a guessed UID. DESIGN DECISIONS.** Student UID identifies a record, not ownership. SIMS verifies its registered Parent by SMS OTP; Learnest consumes a one-time grant atomically. SIMS verified name is read-only, existing UID/password login remains independent during an outage, transfer is minimal and environments have separate clients. Retiring public lookup requires audit. Recommendations/defaults in this design remain pending where their source says pending. Source: Learnest identity snapshot.

## BR-050

**BR-050 — Full parent ledger composition belongs to Ripple behind SIMS. LATER RECORDED CONTRACT.** The parent app calls one parent-authenticated SIMS endpoint. SIMS delegates composition to Ripple, which owns partial receipts, allocations, advances/overpayment credits, applications and adjustments. Apply source-owned FIUU paydate before filtering, sorting and pagination. SIMS validates/allowlists the response; the app renders supplied debit, credit, balance and summary values without combining money independently. Source: mem_c4578d3e4bf7. The older linked decisions file is a proposal predecessor; its fifteen-minute freshness recommendation is not thereby approved. The memory reports a completed backend release, which this compilation has not independently live-checked. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-051

**BR-051 — Creative Hub scope is locked by its own phase. SOURCE CANDIDATE.** Studio’s governed Flow A creation/analysis work is Phase 1; legacy management is frozen. Lens is per user rather than automatically tenant-wide, with one foundation. Source: creative-hub/docs/prds/PRD-studio.md and PRD index; verify source approval before implementation.

## BR-052

**BR-052 — Owner analytics and staff access are separate products. USER CORRECTION IN MEMORY.** Authorized owner access includes individual tutor earnings/payment and staff payroll/commission business records through the approved read-only service. This does not grant ordinary staff the same access or include authentication material/proofs/security secrets. Source: mem_f2d248ebf1a6 and owner-analytics risk decisions. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-053

**BR-053 — Partnership and classroom proposals are not signed operating rules. PROPOSAL / RESEARCH.** TEKUN material proposes TEKUN platform/data ownership and Sifututor operating responsibilities; continuity value must not depend on holding data hostage. Classroom device distribution is teachers-only while student/Parent web access remains. Sifututor fronts the product with Learnest Lab visible; legal entity/IP terms still require confirmation. Commercial numbers belong to the partner pack, not invented from concept text. Source: governed TEKUN sourcebooks and classroom sourcebook. No legal conclusion, contract approval or outreach is implied by this compilation.

## BR-054

**BR-054 — Reconciliation has two different matches. DATED SOURCE DECISION.** Gateway transaction → invoice differs from bank deposit → settlement total. For Fiuu, transaction ID and invoice number can provide exact paths; other gateways need invoice evidence or suspense/manual resolution. A bank settlement matches the sum of net gateway transactions, not every individual tuition payment separately. Direct-transfer amount/date candidates are medium confidence, not ownership proof. Why: gateways settle lump sums and references can be incomplete. Source: ripple-suite/docs/features/reconciliation/clarification.md.

## BR-055

**BR-055 — Reconciliation actions have different approval requirements. DATED SOURCE DECISION.** Write-offs require another authorized approver; ordinary unlink/rematch corrections are audited staff actions in this source. Individual and settlement tolerances are separate settings (recorded defaults RM0.50 and RM1.00), and tolerated variance is still logged. Later Question 18 selects configurable hybrid processing at 500 rows, superseding earlier blanket async statements in the same clarification. Why: accountability for loss is different from correcting a match; daily imports are smaller than monthly volume. Bank-deposit-only v1 scope conflicts with later staff requests to include money-out/balance reporting; those staff requests are not approval.

## BR-056

**BR-056 — Tutor conduct is separate from fit confidence. DATED SOURCE DECISION.** Display conduct and match confidence separately; conduct can act as a within-fit tie-break, never redefine exact subject fit. Historical conduct records do not automatically decay. No-record tutors may show system-derived evidence with a clear distinction. Category taxonomy and precise additive weights were explicitly pending in this source. Why: avoid implying match quality and behaviour are the same score. Source: rating/clarification.md, reconciled with BR-013. Early “any logged-in staff can write” is v1 history, not an override of later permissions.

## BR-057

**BR-057 — Published profiles change through drafts. DATED SOURCE DECISION.** At most one Ready and one Draft per tutor. Editing/regenerating creates a Draft while the Ready version remains available until confirmation. Public URLs are opaque; Ready content is concise, factual and parent-friendly, with BM/EN support. Manual edits need an overwrite warning. Generation requires governed SIMS fields plus supplementary notes/files. Why: preserve the already-shared Parent version while staff prepare changes. Source: profiles/clarification.md. Model/vendor choices and upload limits are dated configuration decisions, not invented permanent business requirements.

## BR-058

**BR-058 — Retention thresholds belong to a draft and require reconciliation. DRAFT SOURCE, UNRESOLVED INTERNAL CONFLICT.** March retention PRD proposes new-customer feedback, repeated-cycle support and missed-first-class follow-up, with idempotent generation and read-only completed records. Narrative says first class recorded/no class after three days, while functional rows use Verified status. Recorded defaults include third paid invoice and three-day follow-up, configurable. Later approved Dual CX service-start milestone is specifically the exact current-cycle Verified first class (BR-083); that resolves the CRM milestone but does not silently approve every draft retention trigger. Why: catch post-conversion issues early. Source: customer-retention/prd.md and September Dual CX pack.

## BR-059

**BR-059 — Audit uses the actual affected entity. SOURCE-DECLARED CLARIFICATION.** Bulk Lead changes have one record per affected Lead with batch context. Settings changes use settings audit rather than an invented Lead. Import execution is audited; preparatory preview is not the same operational event. Payment overview shows batch actions, slip details retain slip actions. Audit visibility has its own permission. Why: staff need useful chronology without duplicate or misleading events. Source: audit-trail-v2/audit-trail-v2-prd-clarification-session.md.

## BR-060

**BR-060 — Role design must use the revised requirements. DATED SOURCE, SECURITY-SENSITIVE.** The later roles PRD specifies one protected system superadmin, configurable other roles, default Staff assignment, server-side checks and role-change audit. It explicitly requires a linked staff record and rejects auto-superadmin promotion, superseding an earlier clarification’s no-staff-record shortcut. Development bypass is not a production authorization rule. Source: roles/prd.md and roles/clarification.md. No auth changes are authorized by this research.

## BR-061

**BR-061 — Staff knowledge answers distinguish evidence and uncertainty. DATED DESIGN DECISION.** Phase 1 feedback is collected for admin review rather than automatically tuning truth. Failed grounding validation adds a visible warning. Conversations are per-user; the cited admin design exposes metadata, not conversation bodies. Budget thresholds warn at 80%/100% rather than silently blocking staff. Documents can become searchable after processing without a truth-approval gate, so searchable does not mean business-approved. Why: speed, privacy and practical knowledge administration. Source: knowledge-assistant/clarification.md. These dated design choices must not be represented as live behaviour or current model pricing.

## BR-062

**BR-062 — Help publication requires review. SOURCE-DECLARED CLARIFICATION.** Seeded launch articles start as unpublished drafts; Hafiz reviews and approves each before publication. Why: staff help should not present unchecked process instructions as live policy. Source: help/help-prd-clarification-session.md.

## BR-063

**BR-063 — Settle the whole shared-class payout together. CURRENT USER CONFIRMED, 3 OCTOBER 2026.** Hafiz explicitly rejected deferring one student's eligible payout component while paying the others: settle the whole class amount together. Per-student earnings can be calculated within a class and summed, but do not authorize separate settlement or separate sessions. This supersedes the historical staff request to defer an individual student's extra-class amount. Sources: Hafiz's direct clarification in this session; historical calculation context in ripple-suite/docs/features/tutor-payments/clarification.md Q13/Q22. This records business intent; no payment operation or application change is authorized or performed.

## BR-064

**BR-064 — Promotion tagging is not earned promotion benefit. STAFF REQUIREMENT, NOT CONFIRMED POLICY.** The later promotion tab distinguishes valid tagging dates, Pending Assessment, Eligible/Completed and Disqualified. Existing tags should survive campaign end for assessment. FINAL50 examples require an existing active Student, genuinely new subject, first invoice between 26 August and 10 November 2026 and six hours in that first cycle, per eligible subject with RM50 rebate. Tutor/schedule/mode changes or cancel-and-recreate should not fabricate a new subject. Tutor/Sifututor-caused shortfall may need manual review. These are campaign-specific intake rules to reconcile with approved Marketing/Finance terms; do not generalize to all discounts.

## BR-065

**BR-065 — Staff requests can conflict with a later build pack. INTAKE SUPERSESSION CHECK.** September 18 outreach notes propose triggering on assigned tasks, routing conversations to relevant staff and different physical/online blast sizes. The later outreach pack above uses Request-based eligibility without owner prerequisite, cross-owner bundles, governed caps and KeepUnassigned replies. Preserve original staff need—less repetitive matching—but use the later approved scope where confirmation exists, rather than mixing both algorithms.

## BR-066

**BR-066 — An uploaded receipt or a logged payment is not automatically a reconciled paid invoice. STAFF-REPORTED REQUIREMENT.** Staff reports request many receipts/bank transactions per invoice, correct payer/date/reference evidence, unallocated advances, and paid synchronization only after the appropriate reconciliation step. Incorrect amount-only auto-matches were reported. Why: financial records must represent actual receipts and bank evidence without false paid status. Original reports describe symptoms and requested handling, not independently proven current bugs or a new authorized write policy.

## BR-067

**BR-067 — Reassignment must preserve who actually taught. HISTORICAL REQUIREMENT.** January technical guide and February 10 release note say tutor reassignment is blocked while associated classes are Ongoing or Attended, with a required reason and tutor-change audit. Verified/cancelled history remains; actual class tutor determines earnings, not the Request's later tutor. The report's loss/time-saved estimates are unverified document claims, not measurements from this compilation. Why recorded: avoid paying the replacement tutor for another tutor's completed work and avoid duplicating Requests solely to replace tutors. Sources: [Tutor Request Edit v2 guide](https://drive.google.com/file/d/1pgEsj70HYg2b67NNdOYt6okqtU3ozK6z/view) and [10 February SIMS changelog](https://drive.google.com/file/d/17wNvoXLU-akzAtLacbQrIDxY_SZ6bjFT/view). Compare current SIMS before applying these historical restrictions.

## BR-068

**BR-068 — February verification and billing copy is superseded in specific scopes. HISTORICAL SOURCE.** The February note describes payment-before-parent-verification, admin escalation, automatic recurring invoices and billing-date changes after scheduling changes. July Addendum B explicitly adds the first-invoice verification exception, attendance-based credit consumption and immutable consumed allocations. Preserve the earlier rationale—collect payment before normal tutor payout—but do not treat old release copy as proof that all future schedule changes may rewrite financial documents. This is an explicit source-age comparison, not a production finding.

## BR-069

**BR-069 — Account deletion wording and implementation are different. HISTORICAL SOURCE CONFLICT.** February mobile release copy calls the action permanent deletion, but its described mechanism sets tutor status to resigned and clears local data. That does not prove server-side erasure. Resolve the actual retention/deletion contract before promising users permanent deletion. No destructive action or legal conclusion is authorized.

## BR-070

**BR-070 — Staff assignment can directly approve; unsuccessful interest can be reconsidered. SOURCE-DECLARED CONFIRMED.** Lifecycle clarification for SIMS issue 1432 says Assign Tutor means Assign & Approve Tutor; staff can reconsider unsuccessful applications, while active duplicates remain blocked. The slice preserves legacy lifecycle compatibility and does not authorize destructive history repair or a full unrelated module migration. Why: allow governed staff decisions without permanent rejection from old unsuccessful interest. Source: sifu-tutor/docs/features/tutor-request-lifecycle-reconsideration/prd-clarification-session.md. This action still obeys current qualification/assignment gates in BR-012.

## BR-071

**BR-071 — Stable session IDs and separate movement history are a proposal. DRAFT, NOT IMPLEMENTATION APPROVAL.** June Option C-lite proposes one stable class ID, separate reschedule/postpone events, one current row per real session and no event rows in quota or tutor payout. It explicitly says draft before Hafiz approval. Legacy movement rows require classification and dependency evidence, never blind deletion. Why: old movement/history rows can look like real billable sessions. Source: sifu-tutor/docs/features/class-lifecycle-option-c/prd.md. Its older allocator references need July Addendum B reconciliation.

## BR-072

**BR-072 — The mobile roadmap records product choices, not automatic backend completion. DATED USER-DECISION LOG.** April 12 roadmap keeps lightweight quick notes separate from baseline evaluation and twelve-session progress reports. Recurring scheduling previews actual dates and stays within remaining quota. Unpaid earnings are estimates from verified classes and actual payout review can differ. Internal matching funnels and document-expiry features were cut; full in-app messaging was deferred after WhatsApp links, and resources/AI summaries depend on content/notes adoption. Stages 1–2 auto-clock-out nudges differ from a future server command; dormant UI does not prove a backend endpoint exists. Source: sifututor_tutor/docs/PLATFORM-ROADMAP-DECISIONS.md. Statutory claims in the source were not independently verified here.

## BR-073

**BR-073 — Ordinary frequency and prepaid quantity must not be conflated. USER CORRECTION.** Classes/week × 4 supplies ordinary monthly quantity. Promotional packages retain their specified session quantity. For example, two classes/week means eight ordinary monthly classes; it does not mean a mandatory fifteen-session promotion. Why: preserve the established Request flow while offering optional commercial promotions. Sources: mem_6bab6f2e4224, mem_37028012a8f2. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-074

**BR-074 — Extra-time method is governed by brand and mode. USER CORRECTION.** The shared engine supports proportional-hourly and fixed-interval methods. SifuTutor retains proportional-hourly by default. Nakngaji retains fixed fifteen-minute blocks at RM10 online/RM12 physical. Authorized admins configure it; Parents and ordinary request staff do not select a pricing formula per Request. Snapshot method, interval, quantity, rates and effective terms. Why: preserve confirmed brand pricing and prevent later settings from rewriting a purchase. Sources: mem_bfcd419ffaf3 and mem_5c8b9a9ad020. Older register row 043’s proportional language must not override this correction. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-075

**BR-075 — Applying and brand-qualified assignment are different stages. USER CORRECTION.** One tutor account and one combined app support both brands. Tutors may view/apply across brands before qualification; applications remain valid when qualification is completed later. Staff acceptance/assignment requires verification for the Request’s brand. Subject/level are not permission gates. Do not offer an exception that bypasses Nakngaji verification. Why: allow acquisition while protecting delivery qualification. Sources: mem_1d41e0ba23ba, mem_ad0a68c12567, mem_b48ad2125b1d. Legacy global Active/Verified compatibility alone does not prove Nakngaji qualification. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-076

**BR-076 — Nakngaji qualification workflow is a launch prerequisite. USER DECISION.** Shared phone identity, objective assessments, audio submission, fluency/Tajwid/makhraj review, resubmission recovery and staff qualification must exist and be verified before public launch. Ordinary manual qualification is not the launch workaround. Legacy-approved tutor import is separately controlled after the workflow exists. Reuse SIMS phone identity rather than inventing assessment-specific normalization. Sources: mem_35a2574a0414, mem_a61270b4c38a. The approved customer descriptor is “Quran & Islamic Learning Platform”; current launch copy is English, with the future Malay programme separate (mem_de86703c8515). **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-077

**BR-077 — Late cancellation does not create invented consumption. USER CORRECTION.** Nakngaji’s written two-day/last-minute cancellation condition was not operationally enforced. Cancelled/postponed sessions do not consume package quota, including late cancellation; attended sessions consume under BR-006. Why: website wording must not create a new financial charge that operations never applied. Source: mem_8bf898698f01. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-078

**BR-078 — Mid-package changes apply prospectively. USER DECISIONS.** Added extra-time charges cover only eligible remaining sessions from the approved effective session; package session quantity stays unchanged. Removing prepaid blocks produces an auditable unused-value account credit for next invoice/package, not an automatic cash refund. Additional-student changes likewise use the amendment flow and never recalculate purchased/billed/attended history. Preset selection is routine authorized CX work; custom discount/manual override requires elevated Finance/supervisor approval. Sources: mem_061ea3c0a6c4, mem_fa9cb70eadc9, mem_b4700046489f, mem_20cfd9528f7b. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-079

**BR-079 — One continuing arrangement keeps its Request identity. CONFIRMED PRODUCT DESIGN.** Every accepted information change creates a full immutable Request Revision with reason, actor and effective boundary. No real change, abandoned draft or failed action creates no Revision. Separate subjects, independently fulfilled lessons or genuinely new demand after terminal closure create linked/new Requests. Preserve prior financial and operational history. Old Duplicate remains restricted until replacement coverage and recovery are proven. Why: duplication previously fragmented a continuing need and moved history. Source: ripple-suite/docs/features/crm/request-change-and-legacy-duplicate-build-ready-addendum-2026-07-29.md. Its product approval does not authorize a migration.

## BR-080

**BR-080 — Matching and Customer Facing have distinct responsibilities. SEPTEMBER APPROVED DESIGN.** Matching finds suitable interested tutors. Customer Facing handles Parent options and follows through the first Verified class. TX owns verification; CX Onboarding owns parent-fee follow-up. Supervisor assigns missing Customer Facing from the queue; direct handover uses an eligible PIC, not round robin. Source: dual-cx-build-ready-pack-2026-09-14.md, D1–D16. Earlier “one CX Support owner” material needs this refinement rather than erasing either responsibility.

## BR-081

**BR-081 — Handover needs real candidate evidence, not a finished profile. APPROVED DESIGN.** At least one suitable interested tutor needs recorded contact outcome, availability and matching notes. Profile/verification completion is not the handover prerequisite. Candidate decline can continue with remaining suitable options; returning for more matching requires category and detail. Return to the current Matching PIC, or visible pending assignment if none is eligible; Customer Facing retains parent communication. Handover alone does not stop controlled sourcing. Why: transfer actionable work without forcing unnecessary completion or losing an owner. Source: Dual CX D2–D6/D14–D16.

## BR-082

**BR-082 — Early TX referral and fee follow-up are independent. APPROVED DESIGN.** Customer Facing may refer a suitable interested shortlist candidate before Parent selection, reusing the tutor’s existing TX case. Routine progress stays history; create actionable tasks only when relevant. A current committed Parent selection can start exact-Request collection only when SIMS says payment_required, even before assignment. Paid/waived settles collection; receipt upload alone proves neither. Sources: Dual CX D7–D12.

## BR-083

**BR-083 — Scheduling success is not service-start completion. APPROVED DESIGN.** Show Setup complete — awaiting first class after assignment/scheduling. Only authoritative verification of the exact current-cycle first class establishes Service started. Attended alone, a different class/tutor, an old cycle or unavailable evidence cannot complete it. Why: avoid reporting delivered service from setup activity. Source: Dual CX D13.

## BR-084

**BR-084 — Fresh Lead no-response calls use a snapshotted same-day target. USER CORRECTION.** Initial default is three genuine attempts at different times on the same day; Operations can configure the bounded count. A journey already started retains its target. No automatic calls are implied. This does not independently set later Lead Recovery or WhatsApp frequency. Source: mem_7e86c6ce09db. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-085

**BR-085 — Refund type follows the actual business event. USER DECISION.** A valid parent commitment fee is refundable only when its Request has no Attended/Verified class. Duplicate/excess/wrongly matched payments are payment corrections. Post-attendance goodwill/service compensation is a general customer refund. Why: unused fees, errors and compensation have different eligibility and audit meaning. Source: mem_6e220a0cade4. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-086

**BR-086 — Commitment-fee refunds use the approved bank-transfer route. USER DECISIONS.** Parent refunds use standalone bank payouts. Tutor fee refund attaches a locked linked line to an eligible unpaid editable final payment; otherwise use a standalone tutor refund payout. Never reopen approved/paid tutor payments; mark fee refunded after confirmed settlement, and retain failed payout recovery in the same case. FIUU refund capability is not an approved operational route. This differs deliberately from early-ending tutor compensation, which uses a normal class-backed payment and never a compensation-only payout. Sources: mem_03efe3151a5d, mem_0910293f5c1a, mem_e6cfdaac8153. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-087

**BR-087 — Tutor approval, payment availability and activation are distinct. USER DECISION / DATED CONTRACT.** Submitting verification details alone does not unlock fee payment. Authorized staff approval does; first assignment is not required. Ripple owns the staff review/link/proof workspace and SIMS owns eligibility, audited payment transitions and activation. New canonical Verified requires approval plus verified gateway settlement/Finance-confirmed offline payment; legacy Active is operational compatibility, not the same audit proof. Fees are configurable and parent/tutor fee settings are separate. Sources: mem_e916d822832f, mem_2fb9c78a7306, mem_c4162f932ad9, mem_b169ddf4f8ce. Assignment while an approved tutor fee remains unpaid is governed separately by BR-012. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-088

**BR-088 — Automatic payment alignment needs exact provenance. USER CORRECTION.** Automatically reconcile verified SIMS-paid and Ripple-verified records when the same payment is proven; no routine confirmation button merely to repeat matching evidence. Paid plus equal amount is insufficient: require immutable receipt identifying the command that changed status and exact receipt/credit source IDs and amounts. Recalculate coverage → revalidate alignment, even if total is unchanged. Fully covered Ripple credit while SIMS is still unpaid follows the normal Finance payment-update workflow unless it fails. Sources: mem_3f3a02ad8f70, mem_7c207a712773, mem_f95752c222b6.

## BR-089

**BR-089 — Pending FIUU recovery has a later explicit risk decision. USER CORRECTION.** A newer decision permits another Parent attempt when a newly observed transaction is Pending rather than successful, within the accepted duplicate-payment-risk policy. Preserve every transaction/receipt; verified success and paid invoices block another checkout. This supersedes the earlier exact-Pending-transaction-only continuation restriction. Source: mem_640d5dee995d superseding mem_58c7c57a9259. This compilation authorizes no payment operation.

## BR-090

**BR-090 — Awarded unpaid welcome bonus survives month changes. USER RULE.** Official unpaid entitlement must remain available and required in the next normal same-tutor class-backed payout. Reject duplicate bonus IDs and moving settled entitlement to a different payment. Pre-July missing-award candidates remain separately held for Finance review. Source: mem_672ff22ebacb and mem_2f1d570c5dea. One combined cross-brand bonus uses weighted eligible verified activity, not a bonus per brand (mem_5554fe19f900). **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-091

**BR-091 — Paid collection and service recovery have separate completion states. CURRENT USER CONFIRMED, 3 OCTOBER 2026.** When the invoice is fully paid but classes remain on hold, mark collection Done while a separate service follow-up stays open. Settlement does not establish service resumption. The approved collection queue still includes Needs Action, Upcoming and collapsed Done; contact history remains available. Sources: Hafiz’s direct answer in this session, “Yes—collection Done; service follow-up remains open”, and collection/workbench-redesign-prd.md. Exact follow-up ownership, closing evidence and implementation require their governing workflow; none is invented here. Extra collection phone numbers remain a separate draft.


## BR-092

**BR-092 — WhatsApp activity is factual evidence, not tutor intent. APPROVED STARTER DESIGN.** Finch provides delivery/reply evidence; Ripple/SIMS own identity, eligibility and workflow. Quiet tutors remain selectable in the indicator-only release; activity does not change match grouping/rank. Recorded defaults are ninety-day tutor activity, seventy-two-hour reply attribution and an advisory six-delivery/zero-reply warning. Exact Request history remains regardless of age. Show delayed/unavailable evidence and retain source retention/tombstones; do not copy conversation content into Ripple. Sources: finch-tutor-whatsapp-activity-build-ready-pack-2026-09-16.md and mem_bf53432ef456. Later automated outreach caps/explicit opt-out enforcement are different policies; neither may be inferred from silence. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-093

**BR-093 — Campaign attribution follows the actual intake source. USER DECISIONS.** Ripple receives Facebook Lead Form exports and owns original campaign/form attribution and spend joins. Marketing selects one controlled campaign per batch and splits mixed files; preserve immutable batch/Lead snapshots and do not guess historical attribution. Finch owns WhatsApp referrals and outbound delivery tags only. Sources: mem_e4ee98328c67, mem_5b96e87b5a16. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-094

**BR-094 — Call capture records actual attempts and preserves their owner. CONFIRMED CLARIFICATION WITH LAUNCH GATES.** Attempt/outcome metadata syncs immediately when online; audio upload alone is Wi-Fi-only. Call-time owner remains fixed after reassignment. Supervisor review is explicit, not inferred from playback. Small pilot uses a checked-and-logged manual DNC clearance for the business day; unavailable/ambiguous evidence means do not call. Technical DNC is required beyond the pilot; legal/privacy review remains Hafiz’s pre-launch responsibility. Active retention default is keep_all with no invented deadline, while controlled deletion/holds remain supported. Source: cx-call-capture-prd-clarification-session.md. No recording or outreach is authorized here.

## BR-095

**BR-095 — Legacy learning evidence is preserved before normalization. USER CORRECTIONS.** Exact aliases can map only to a valid current Subject+Level pair. “All subjects”, “Both”, person names, pricing questions and campaign slogans are not invented canonical Subjects or confirmed availability. Missing levels remain visible as needing confirmation. Imported provenance never disqualifies a current valid Request, but historical observations do not trigger operations. Sources: mem_12b43d7ce364, mem_4806cd83c163, mem_2c21889b745c, mem_b359980e4494, mem_8831088958a5, mem_6e539e960ba6 and the detailed memory appendix. Preserve the exact approved language/3M/Accounting/KAFA mappings there; do not generalize them to unsupported catalogue entries. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-096

**BR-096 — Each tutor has an independent Parent profile artifact. CONFIRMED DESIGN.** Grouping candidates streamlines one action/follow-up only. Each tutor retains a separate Link, Image or PDF. One delivery occurrence uses one format and channel; Phone Call is not digital profile delivery. Other Digital needs a service label. Generating/copying/downloading does not prove delivered; staff confirms actual delivered rows. Why: preserve exactly which tutor/profile the Parent received. Source: mem_513a4c463bb3 and tutor-matching-candidate-build-ready-pack-2026-08-14.md.

## BR-097

**BR-097 — Learning-support capability is Request-specific; a tutor's own application counts as Confirmed. USER CORRECTED 08/10/2026.** When support needs apply, a tutor who applied to the Request in the tutor app counts as able to support them, because the tutor app shows the Special Need row before Apply; staff record no separate support confirmation for applicants. A tutor added only by staff (no live application) still starts unconfirmed for that tutor/Request/Revision/cycle/participating-student fact set, and only Confirmed permits profile delivery. A staff-recorded Cannot support still blocks that tutor for this Request and is neutral globally. Material changes stale a staff confirmation. Share teaching-relevant support facts without child contact identity or exact home address. Source: Hafiz's current correction 08/10/2026 ("if tutor apply meaning they can"), Koda mem_748a5abc4b47, implemented in ripple-suite #1608 (PR #1609); supersedes the applicant part of the August 14 matching pack, section 6.4. Acceptance example: TREQ-895057 (special need "Others"): both applicants count as supported and the handover to Customer Facing is allowed; a tutor marked Cannot support stays blocked. This is different from brand qualification or general subject fit.

## BR-098

**BR-098 — Matching engine ownership changed in the design history. LATER DESIGN EVIDENCE.** The August 14 pack assigns the reusable matching/opportunity engine to Ripple while SIMS retains authoritative tutor eligibility, assignment and business transactions. Older “one canonical SIMS matching engine” recommendations are superseded in that design scope. Source: mem_8cacfd2048a8 and August 14 matching pack. Do not interpret “SIMS owns business truth” as meaning every ranking calculation must be implemented in SIMS. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-099

**BR-099 — Date labels must retain their actual financial meaning. DURABLE CORRECTION.** Creation Date uses created_at, Invoice Date uses invoice_date, Payment Date uses payment_date. Filters, sorting, exports and payloads must agree. updated_at means Last Updated only. Why: a backfill must not make an old invoice appear newly created or newly paid. Source: mem_7dc83b1b5924. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-100

**BR-100 — Source documents need explicit precedence, not one universal newest-file rule. USER DECISION AND COMPILATION CONTROL.** The Nakngaji register is intended to become its canonical current release contract and receive approved corrections first. Older PRDs/packs remain historical evidence and need superseded/current pointers. The fetched default-branch register still contains rows contradicted by later corrections, so this compilation cites those corrections explicitly; neither a stale “Confirmed” row nor current code resolves that drift alone. Source: mem_ace988d54918 and default-branch register comparison, 3 October 2026. **Memory metadata:** cited outdated records require independent source corroboration; their flag does not prove the whole rule was reversed. [Dates and authority audit](memory-audit.md).

## BR-101

**BR-101 — Parent acceptance belongs to the parent. SOURCE-DECLARED CONFIRMED DESIGN.** One shared, versioned service-acceptance mechanism covers SifuTutor and Nakngaji. Staff cannot accept on a parent’s behalf. Staff-created Requests send a secure acceptance link and keep commitment-fee payment and operational activation blocked until acceptance. Returning parents accept their first Nakngaji service scope and material published changes. Preserve the applicable version/hash, identity and Request evidence on the server; do not collect NRIC merely to prove acceptance. Why: explicit, attributable service acceptance. Source: corrective pack section 3.6.

## BR-102

**BR-102 — Renewal preserves purchased terms. SOURCE-DECLARED CONFIRMED DESIGN.** After the final purchased credit is consumed, prepare one hidden unpaid next invoice on the approved snapshotted terms; preparation is not auto-charging. Retiring/repricing a preset affects new selections, not an existing approved Request’s automatic continuation. Confirmed Request amendments remain staff-only in Phase 1; use the normal Change Request and next-cycle level-change rules, including their explicit first-unpaid-invoice exception. Preserve completed history and old credits. Source: corrective pack section 3.7.

## BR-103

**BR-103 — Passing assessment components is not final qualification. SOURCE-DECLARED CONFIRMED DESIGN.** Passing quiz and audio yields Ready for final review; authorized staff alone sets Verified. New assessment versions do not automatically revoke existing verification; individual reassessment requires reason and audit. Three self-service attempts apply per platform definition version, with each reasoned staff unlock granting one additional attempt. Audio must be independently measurable at 120–180 seconds, at most 15 MB, and preserve immutable submissions/reviews. Each staff resubmission decision permits one linked recording; there is no numeric resubmission cap. Audio is restricted qualification history, with no public, marketing or AI-training use without separate permission. Source: corrective pack section 3.9; detailed format/content-review requirements remain in the source.

## BR-104

**BR-104 — Customer catalogue labels and internal identifiers have different roles. SOURCE-DECLARED CONFIRMED DESIGN.** Choose Quran Reading then Asas/Lancar; Other Subjects expose a direct subject choice without a customer-facing level. Iqra/Muqaddam/Al-Quran/Tajwid explain the learning level rather than becoming extra focus selections. Preserve existing SifuTutor subject IDs 138/361; Nakngaji catalogue records use their own stable identity. Launch rates in the pack are dated configuration, not proof of today’s runtime values. Source: corrective pack sections 2 and 3.3.
