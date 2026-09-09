# SIMS Owner Analytics — Comprehensive Data Catalog (v4.1 Draft)

v4.1 source-of-truth note: schema comparison uses the nested `sifu-tutor`
repository at an explicitly recorded ref/SHA, never the umbrella workspace
SHA. Corrected Combined A reconciliation found 152 repository-created tables,
160 live tables, no repository-only tables and eight live-only tables. Of the
52 tables previously labelled production-only, 44 already exist in the local
`sifu-tutor/origin/main` migration history.

The detailed executable classification is generated at
`.agent-os/evidence/sims-owner-analytics/20260813T124159Z-a2r1/blueprint/`.
It currently includes 101 source tables across 21 datasets, with 1,322 allowed
or aggregate-only source fields and no pending classifications. This catalog
describes product intent; the generated field matrix remains the exact
grant/extraction authority.

Status: product/data design only; repository-derived; **no production query,
grant, copy, or infrastructure action is authorized**

Owner: Hafiz | Design partner: Codex | Future executor: Claude after approval

This catalog defines what the KVM8 owner business replica and owner MCP should
contain. The companion [`sims-analytics-replica-plan.md`](sims-analytics-replica-plan.md)
defines how data is moved, protected, verified, and approved.

## 1. Two separate products

### Owner v1 — build now after approval

- Initial users: Hafiz and one named business-owner partner.
- Real business records may include names, contact details, addresses, exact
  operational dates, human-facing identifiers, statuses, amounts, and linked
  records.
- Access is through a personal MCP token only. No SSH, MySQL, KVM8, updater,
  or production credential is given to either user.
- The MCP reads only the KVM8 business copy and is read-only.

### Ordinary-staff analytics — future, separate approval

- Staff must never reuse an owner token or query owner datasets directly.
- A staff product must use separate cleaned datasets/scopes with pseudonyms,
  reduced location/date detail, free-text removal, and aggregate-only finance
  where appropriate.
- The detailed staff-cleaning policy in section 9 is retained as future design
  input; it does not constrain owner v1.

## 2. Classification rules

Every live source column receives exactly one status in Bundle A:

| Status | Meaning |
|---|---|
| `owner-allow` | Useful business data that may be copied and returned to the two owners |
| `aggregate-only` | Useful only through an approved aggregate; individual values are not copied/returned |
| `exclude` | No sufficient analytics purpose or prohibited security/sensitivity class |
| `pending` | Business value or risk needs Hafiz's decision; no grant or copy until resolved |

### 2.1 Normally owner-allowed

- Real names and SIMS business identifiers.
- Email, phone/WhatsApp, business address, postcode, state and city.
- Exact business dates/times and lifecycle timestamps.
- Statuses, categories, types, flags, reasons represented as reviewed enums,
  and outcomes.
- Amounts, balances, rates, hours, durations, counts, and approved financial
  relationships.
- Relationships between parent, student, tutor, request, class, invoice,
  payment, report, support, and staff records.
- Operational notes/text only when the exact field has a concrete owner use
  and passes a secret/leak review.

### 2.2 Always excluded

- Passwords, including `plain_password`.
- Sessions, remember tokens, personal/API/OAuth tokens, reset codes, OTPs,
  verification/recovery codes, encryption/private keys, and secrets.
- Raw payment-gateway callbacks, signatures, hashes, and credentials.
- Raw device/notification tokens and notification provider credentials.
- Bank/payout authentication material. A bank name may be allowed; account
  numbers and payout credentials require a separate decision and default to
  excluded.
- Raw files, uploads, identity documents, profile images, payment proofs, and
  object paths that may grant access.
- Stack traces, raw request payloads, debug dumps, embeddings, and logs likely
  to contain secrets or uncontrolled personal data.
- Cache, queue, framework, Pulse/Telescope/debug, backup-control, settings,
  permission-administration, and other system tables without a named owner
  analytics use.

### 2.3 Pending rather than inferred

- Special-needs, medical, emergency-contact, declaration, identity-document,
  tax/statutory, and similar highly sensitive person data.
- Long free-text notes, messages, reasons, descriptions, support conversations,
  report answers, and structured JSON payloads.
- Bank account numbers, tax IDs, NRIC/passport, exact GPS, and raw device/IP
  information.

Pending means absent from production grants and KVM8 until Hafiz explicitly
approves a named use. It does not mean “copy now and hide in MCP.”

## 3. Owner datasets

Each dataset below must support the applicable MCP operations: discovery,
description, search, paginated rows, aggregation, and freshness. Exact columns
are not guessed here; Bundle A compiles the live-verified field matrix.

### A. Students

Owner questions: find a student, see registration/active status, relate the
student to parent, staff, requests, classes, invoices and reports, and analyse
growth/retention.

Expected owner fields: student business ID, real name, parent link, assigned
staff link, contact fields that genuinely exist and are used, date of birth or
age, gender, school (subject to free-text review), status, registration/
creation/update/deletion dates, and relationship counts.

Default exclusions: passwords/tokens (if any), special-needs/medical detail,
unreviewed notes, identity files and media.

### B. Parents

Owner questions: find/contact a parent, understand assigned staff, children,
requests, classes, invoices, payments and support history, and analyse
acquisition/activity/payment behaviour.

Expected owner fields: parent business ID, real/display name, email, phone/
WhatsApp, address/postcode/state/city, gender, DOB/age where useful, assigned
staff, status, creation/update/last-login/deletion dates, and linked record
counts.

Default exclusions: password/session/token/reset/verification fields, raw
device tokens, identity documents, media, and unreviewed remarks.

### C. Tutors and tutor supply

Owner questions: find/contact a tutor, assess eligibility and supply, view
subjects/levels/curricula/languages/availability, understand engagement,
applications, assignments and class activity.

Expected owner fields from `tutors`: tutor business ID, name, email, phone/
WhatsApp, address/postcode/state/city, age/DOB, gender, marital status,
status/verification/suspension, join/creation/update/last-login dates,
response/application/engagement measures, and links to business activity.

Expected supporting data from `tutor_services`, `tutor_subjects`,
`tutor_languages`, `tutor_curricula`, `tutor_availability_slots`, and the
reviewed portion of `tutor_education`: level, mode, city, curriculum, language
and proficiency, subject, confirmation/inference flags, preference rank,
teaching experience, availability day/time, qualification/category,
institution/academic field/year where business-useful.

Default exclusions/pending: password/auth fields, bank credentials, NRIC/
passport and identity files, declarations, emergency contacts, raw profile
embeddings/media, and unreviewed free text. Individual owner-authorised tutor
finance is available through dataset J.

### D. Staff and ownership

Owner questions: identify the staff member responsible for a parent/request,
analyse workload and lifecycle, and understand department/designation/status.

Expected owner fields: staff business ID, real name, work contact, department,
designation, type, employment/status dates, active/deleted state, and links to
assigned parents, requests, actions and support cases.

Default exclusions/pending: login credentials, emergency/medical fields,
home-address detail without a business use, bank/tax/statutory identifiers,
HR documents and termination narrative. Individual owner-authorised staff
finance is available through dataset K.

### E. Tutor requests, matching and assignment

Owner questions: find a request, see who requested/owns/teaches it, understand
the demand and rate, follow the lifecycle, measure conversion/time, inspect
matching/application/broadcast/reassignment history, and identify stalled work.

Expected owner data from `tutor_requests`, `tutor_request_students`,
`tutor_request_addresses`, `tutor_request_activities`,
`tutor_request_broadcasts`, `tutor_match_scores`, `tutor_reassignments`, and
`level_change_requests`: human-facing request ID, parent/student/tutor/staff
links, subject/level/mode/location, schedule/preferences in reviewed
structured fields, class duration/count/hours, parent-facing rates/amounts,
status/application/phase, approval/reactivation/pause/inactive dates,
application/match/broadcast outcomes, score/round/channel, reassignment and
level-change state, and derived response/conversion durations.

Default exclusions/pending: raw broadcast message/body, embeddings/parsed
signals, unrestricted special requests/preferences/reasons/comments and secret
contact routing data. Approved tutor rates and commission fields may be
returned to the two owners.

### F. Classes and attendance

Owner questions: find a class, relate it to request/student/tutor/invoice,
understand planned versus actual delivery, verify attendance, cancellation,
extension and payment coverage, and analyse tutor utilisation.

Expected owner data from `classes` and `class_attendance_logs`: class business
ID, request/student/tutor/invoice links, sequence, exact scheduled/actual dates
and times, planned/actual duration, clock-in/out measures, extension, status,
paid flag, class amount, attendance log type/timestamps, and deleted state.

Default exclusions/pending: proof images/files, raw GPS/device data and
unreviewed attendance notes. Approved tutor commission boosts may be returned
to the two owners.

### G. Parent invoices

Owner questions: find an invoice, identify the parent/request/classes, see
amounts and payment state, investigate aging/transfers/adjustments, and analyse
revenue and collections.

Expected owner fields from `parent_invoices`: invoice business number/ID,
parent/request/old-request/transfer relationships, invoice type, invoice total,
amount due, status, parent visibility, payment method, receiving-account
category, exact invoice/billing/due/payment dates, days-to-pay/overdue aging,
LHDN submission status/reference/date where business-useful, and deleted state.

Default exclusions: gateway/auth secrets, raw callbacks, attachments/proofs,
and unreviewed remarks/notes. Transaction identifiers are allowed only when
they are business investigation references and not authentication material.

### H. Parent payment attempts and items

Owner questions: investigate a checkout attempt, relate it to invoices,
understand success/failure/mismatch/retry behavior, and reconcile value/timing.

Expected owner data from `parent_payment_attempts` and
`parent_payment_attempt_items`: safe business attempt/order reference,
parent/request/invoice links, status, amount/currency, rules version, exact
creation/callback/resolution dates, durations, mismatch category/resolution
state, and item snapshot amounts/statuses/dates.

Always exclude: raw callback bodies, signatures, credentials, snapshot hashes,
and any value that can authenticate or replay a gateway operation. Raw
mismatch/resolution text is pending field review.

### I. Parent finance movements

Owner questions: trace fees, deductions, adjustments, transfers and refunds,
identify who/what/when/amount/status, and reconcile affected invoices/classes.

Expected owner data:

- `parent_commitment_fees`: parent/request, amount, payment date, receiving
  account category, status, waived/refunded state;
- `parent_invoice_deductions`: invoice, amount and reviewed category;
- `invoice_adjustments`: adjustment/invoice/credit-invoice, type/category,
  amount, status and approval/resolution dates;
- `payment_transfers`: source/target invoice, amount, payment date/method and
  reverted state/date;
- `refunds`: refund/parent/class, amount, date, status and approved actor link.

Default exclusions/pending: gateway credentials, proofs, structured raw
payloads, and unrestricted descriptions/reasons/resolution text.

### J. Tutor finance

Source candidates: `tutor_invoices`, `tutor_payments`,
`tutor_payment_break_downs`, `tutor_payment_additions`,
`tutor_payment_deductions`, `tutor_payment_journal_summary`, `tutor_bonuses`,
and `tutor_commitment_fees`.

Owner-allowed rows and aggregates: tutor identity/link, business invoice and
payment references, covered classes/period, gross amount, additions,
deductions, bonuses, commission, paid/net amount, hours, status/category,
payment dates and timeliness. Bank credentials, account numbers, payment
proofs/files, raw transaction authentication data and unrestricted
descriptions remain excluded.

### K. Staff finance

Source candidates: `staff_payments`, `staff_commissions`,
`staff_commission_payments`, `staff_commission_payment_additions`,
`staff_commission_payment_break_downs`, and
`staff_commission_payment_deductions`.

Owner-allowed rows and aggregates: staff identity/link, payment/commission
business reference, covered period, salary/payroll and commission components,
additions/deductions, employer statutory amounts, status and payment dates.
Bank account/authentication data, tax/statutory identifiers, proofs/files and
unrestricted HR text remain excluded.

### L. Learning reports

Owner questions: identify expected/submitted/late/waived/expired reports,
relate them to student/tutor/request/subject, and assess progress/compliance.

Expected owner data from `expected_reports` and `student_reports`: report
business ID, tutor/student/request/subject/question links, report type, period,
milestone, exact due/submitted/waived/expired dates, status/source, lateness,
deleted state and reviewed enumerated answers.

Pending: raw free-text answers, waiver reasons/actor detail, attachments and
content that may contain child health/identity information.

### M. Follow-up, support and app quality

Owner questions: find a case/ticket, identify the affected business record and
responsible staff, understand priority/status/outcome, detect recurring issues,
and measure resolution time.

Expected owner data from `request_followup_cases`, `request_followup_logs`,
`tickets`, and `app_issue_reports`: business case/ticket ID,
request/user-type/approved person/staff links, issue tag/category/type,
department, priority, status/outcome/source, next action, screen/endpoint
family, app/version/device/OS category, exact occurred/detected/resolved dates,
and resolution duration.

Pending: titles, subjects, descriptions, messages, resolutions, reasons,
remarks and photos. Always exclude raw stack traces, auth values, request
payloads and secrets.

### N. Communications, product use and content

Useful owner analytics:

- `notification_logs`: type, user type, channel, status, safe reason code,
  reference type, date and delivery latency; individual recipient link only
  where it supports a named delivery investigation;
- `user_activities` / `user_logs`: module/action/status/function/date and
  approved actor/entity links without secret/raw-value payloads;
- `banner_logs`: banner, action/view/click, user type and date without raw IP,
  user agent or device fingerprint;
- `whatsapp_budget_tracking`: period, messages, estimated cost, budget and
  tightened flag;
- CMS/configuration candidates (`banners`, `blogs`, `news`, `faqs`, `policies`,
  `sliders`, `push_notifications`, `alert_templates`): publication,
  verification, type and date analytics; content/URLs require a concrete use;
- `referrals`, `referral_codes`, `bonus_rules`, `commission_rules`: safe
  business rule/category, conversion/bonus counts/amounts/dates; secret codes
  and raw config payloads excluded;
- `bulk_rate_upgrade_runs`, `bulk_rate_upgrade_row_logs`,
  `bulk_rate_upgrade_action_details`, `billing_repair_log`: run/action/result
  counts, dates and reviewed business links; old/new values, raw notes and
  actors require field review.

### O. Consent

`consent_records` may support category/version/grant/withdrawal/date analysis.
Raw IP, device, policy hash, security payload and uncontrolled user/entity
identifiers are excluded or pending. Owner row-level consent access requires a
named compliance use; otherwise publish closed-period aggregates.

### P. Reference/master data

Expected complete approved reference rows: `states`, `cities`,
`city_adjacencies`, `subjects`, `levels`, `curricula`, `languages`,
`exam_names`, `report_questions`, reviewed non-secret `lookups`, and bank name
from `banks`. Reference prices such as online/in-person level prices are useful
business facts. Settings/configuration payloads are not reference data.

## 4. Literal table disposition

This list prevents Claude from silently ignoring a table or treating an old
eight-table foundation as complete.

### Owner row candidates

`students`, `parents`, `tutors`, `staff`, `tutor_services`, `tutor_subjects`,
`tutor_languages`, `tutor_curricula`, `tutor_availability_slots`, reviewed
`tutor_education`, structured `tutor_declarations` (completion records without
declaration text), `tutor_emergency_contacts`, `tutor_requests`,
`tutor_request_students`,
`tutor_request_activities`, `tutor_request_addresses`,
`tutor_request_broadcasts`, `tutor_match_scores`, `tutor_reassignments`,
`level_change_requests`, `classes`, `class_attendance_logs`,
`class_lifecycle_events`, structured `session_notes`,
`parent_invoices`, `parent_payment_attempts`,
`parent_payment_attempt_items`, `parent_commitment_fees`,
`parent_commitment_fee_payment_attempts`, `parent_commitment_fee_refunds`,
`parent_invoice_deductions`, `invoice_adjustments`, `payment_transfers`,
`refunds`, `expected_reports`, `student_reports`, `request_followup_cases`,
`request_followup_logs`, `request_amendments`,
`stale_tutor_request_run_items`, `tutor_request_creation_batches`,
`tutor_request_creation_batch_items`, `tutor_request_owner_states`,
`tutor_request_verification_exceptions`, `tutor_onboarding_cases`,
`tutor_onboarding_events`, `tutor_share_journey_events`, `tickets`, and
`app_issue_reports`.

### Owner finance candidates

`tutor_invoices`, `tutor_payments`, `tutor_payment_break_downs`,
`tutor_payment_additions`, `tutor_payment_deductions`,
`tutor_payment_journal_summary`, `tutor_bonuses`, `tutor_commitment_fees`,
`tutor_commitment_fee_payment_attempts`,
`tutor_commitment_fee_offline_submissions`, `onboarding_hour_exclusions`,
`staff_payments`, `staff_commissions`, `staff_commission_payments`,
`staff_commission_payment_additions`,
`staff_commission_payment_break_downs`, and
`staff_commission_payment_deductions`.

### Operational/content candidates requiring per-field review

aggregate `consent_records`, structured `notification_logs`,
`user_activities`, `user_logs`,
`banner_logs`, `whatsapp_budget_tracking`, `banners`, `blogs`, `news`, `faqs`,
`policies`, `sliders`, `push_notifications`, `alert_templates`, `referrals`,
`referral_codes`, `referral_rewards`, `referral_reward_allocations`,
`bonus_rules`, `commission_rules`,
`bulk_rate_upgrade_runs`, `bulk_rate_upgrade_row_logs`,
`bulk_rate_upgrade_action_details`, and `billing_repair_log`.

### Safe reference candidates

`states`, `cities`, `city_adjacencies`, `subjects`, `levels`, `curricula`,
`languages`, `exam_names`, `report_questions`, reviewed `lookups`, and
bank-name-only `banks`.

For the newly included operational tables, “structured” is literal: status,
amount, date, actor/business references, reason codes and lifecycle fields are
included. Raw callback bodies, metadata/changes/financial-impact JSON,
fingerprints/hashes/idempotency keys, provider error messages, session topics
or concerns, free-form reasons/notes and receiving-account material remain
excluded unless Hafiz later approves one named field with a leak test.

### Always excluded or deny-by-default

`users`, `sessions`, `password_reset_tokens`, `password_resets`,
`personal_access_tokens`, `verification_codes`, `api_clients`,
`device_tokens`, `onedrive_tokens`, permission/role pivots, `media`, `cache`,
`cache_locks`, `jobs`, `job_batches`, `failed_jobs`, `pulse_aggregates`,
`pulse_entries`, `pulse_values`, `backup_logs`, `settings`,
`setting_audit_logs`, `notifications`, `staff_notifications`,
`notification_preferences`, `notification_types`, and other auth/security/
framework/administration tables discovered in Bundle A.

`tutor_emergency_contacts` is included for the two owners' duty-of-care use.
`tutor_declarations` exposes only record identity/tutor linkage/timestamps so
owners can assess declaration completion; the declaration text remains
excluded as unbounded health/legal free text.

## 5. Delivery slices

The owner product is comprehensive, but implementation is sliced to reduce the
blast radius of mistakes:

1. **Identity and references:** students, parents, tutors, staff and safe
   master data.
2. **Operations:** tutor supply, requests/matching, classes and attendance.
3. **Parent finance:** invoices, payment attempts/items and movements.
4. **Finance:** individual and aggregate tutor/staff finance for the two
   authorised owners, excluding credentials, bank/payout authentication data,
   secrets and proofs/files.
5. **Quality and support:** reports, follow-ups, tickets and app issues.
6. **Business intelligence:** communications, usage, content, referrals,
   consent and controlled operational logs.

A slice appears in `list_datasets()` only after its exact fields, grants,
destination DDL, extraction/reconciliation, leak tests, useful-answer tests,
and freshness behavior pass. An unbuilt slice is reported as unavailable, not
silently omitted or described as complete.

## 6. Useful-answer requirement

For every dataset, the implementation appendix must include at least:

1. one detailed record lookup by a real owner-facing identifier;
2. one relationship question crossing approved datasets;
3. one aggregate/trend question;
4. one date-range/filter question;
5. one empty/not-found/stale case;
6. expected fields and redaction behavior;
7. the synthetic fixture that proves the answer before real data.

The tests must show that business usefulness survived the security filtering.
A leak-free but unusable dataset does not pass.

## 7. Engineering completion requirement

Before Claude may implement a slice, Bundle A must provide for every source
table/column in that slice:

1. live read-only schema/type/index evidence;
2. classification and named owner use;
3. exact allowed source columns and explicit denial list;
4. exact extraction SQL and destination DDL;
5. null/default/enum/date/timezone/decimal handling;
6. incremental/full-refresh/aggregate mode, deletes and reconciliation;
7. required source indexes and successful query plan;
8. MCP search/filter/sort/return/aggregate capabilities;
9. useful-answer tests and negative/leak tests; and
10. approval reference.

No catalog prose by itself authorizes a production grant or data copy.

## 8. Special correctness rules

- `tutors.last_login_at` is the app-written field; do not invent
  `last_login`.
- Do not assume `tutor_invoices` contains `invoice_total` or `payment_date`;
  live/repository evidence must identify the real finance fields before
  implementation.
- Commented-out or unapplied index migrations are not production indexes.
- Timestamp-bypassing writes require L1/L2/L3 reconciliation; `updated_at`
  polling alone is not acceptance evidence.
- Human-facing IDs, database IDs and foreign keys are different concepts.
  The field matrix must name which one is returned and which one is cursor-only.
- Decimal money remains decimal, never floating-point.
- Source timezone, destination timezone and displayed timezone are explicit.
- Hard and soft deletes are defined per table; no generic delete assumption.
- Raw text/JSON is denied until its values—not only its column name—are
  sampled through an approved, non-leaking classification process.

## 9. Future ordinary-staff cleaning policy

This section is not owner-v1 scope. It exists to prevent future staff access
from being implemented by simply handing out an owner token.

For staff datasets, normally:

- replace real person and internal IDs with stable pseudonyms;
- remove names, email, phone/WhatsApp, NRIC/passport, exact address/postcode/
  GPS and direct searchable identifiers;
- reduce person dates to age bands/months and operational dates to the minimum
  useful precision;
- keep amounts/statuses/categories/durations/relationships only where privacy
  risk is acceptable;
- remove unrestricted notes/messages/reasons/payloads/files;
- for the **future ordinary-staff product only**, keep individual tutor
  earnings and staff payroll aggregate-only unless Hafiz separately approves a
  role-specific staff purpose; the owner-v1 approval does not flow to staff;
- apply minimum-cohort/differencing controls where small groups can identify a
  person;
- store cleaned staff data separately and give the staff MCP no owner-table
  privilege.

The staff recipient list, role matrix, token registry, exact transformations,
leak tests, useful-answer tests and approval bundles require a new reviewed
plan. Owner-v1 approval never authorizes them.

## 10. Repository evidence and remaining uncertainty

This catalog was derived without production access from current model
`$fillable`/relationship definitions under `sifu-tutor/app/Models/` and schema
migrations under `sifu-tutor/database/migrations/`. Models and migrations can
drift from live MySQL. Bundle A live read-only evidence is therefore the
authority for actual columns, types, indexes, size, data quality and query
plans.
