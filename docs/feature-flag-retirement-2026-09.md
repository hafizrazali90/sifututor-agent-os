# Feature flag retirement review (30/09/2026)

Scope: SIMS (`sifu-tutor` origin/main `7bb4ea582`, same SHA as production) and
Ripple (`ripple-suite` origin/main `98ecb587`). Status: diagnosed only, nothing
changed.

## Decisions (walk-through with Hafiz, 30/09/2026)

Approach: fix the reset mechanism first, then remove flags one by one.

| # | Flag | Decision |
|---|---|---|
| 0 | #2803 payment controls (4) | Restored ON in production 04:41 MYT; evidence on #2904 |
| 1 | sims.operations_centre_enabled | Remove, make permanent |
| 2 | features.enhanced_data_collection_enabled | Remove, make permanent |
| 3 | billing.allocator_write_enabled | Remove; repair commands get their own write guard |
| 4 | billing.parent_draft_visibility_enabled | Remove, make permanent |
| 5 | billing.payment_attempt_snapshot_enabled | Remove, make permanent |
| 6 | billing.scheduled_invoice_decoupling_enabled | Remove, make permanent |
| 7 | billing.commitment_fee_public_payment_links_enabled | Remove, make permanent |
| 8 | billing.tutor_commitment_fee_public_payment_links_enabled | Remove; eligibility mode stays a setting |
| 9 | integration.signed_event_delivery_enabled | Keep as the SIMS-to-Ripple breaker, protect |
| 10 | settings.ReferralSettings.enabled | Keep as business setting; fix seeder to never truncate |
| 11 | live_media group (#2328) | Keep until every collection is remote, then remove as a group |

## Why flags keep switching off

### SIMS
- Flags are frozen into `bootstrap/cache/config.php`. Every deploy's Composer
  step deletes that cache, and the rebuild only sees the shell environment
  plus the env file.
- The protected rebuild (`scripts/deployment/optimize-preserving-billing-flags.sh`)
  carries only 17 flags forward. About 18 others fall back to their code
  default (mostly OFF) unless they are also written in the env file.
- A plain `php artisan optimize` skips that wrapper entirely. The 28/09
  helpdesk release (#2948) records a plain "optimize" step.
- `db:seed` truncates `settings`, wiping DB flags (referral, auth PIN,
  matching notifications). The staging runbook calls it "safe".
- Rollback docs are broken: 10 CRM admission keys were hard-coded true on
  15/09 (606e35479), but the wrapper still injects their dead env names.

Live evidence (production config cache, read-only):

| Flag | 26/09 smoke | 29/09 preflight | 30/09 now |
|---|---|---|---|
| invoice_checkout_tracking_enabled | ON | ? | off |
| invoice_checkout_continuation_enabled | ON | ? | off |
| invoice_recovery_receipts_enabled | ON | ON | off |
| invoice_recovery_uncertain_retry_enabled | ON | off | off |

Config cache last rebuilt 2026-09-30 04:24 server time.

### Ripple
- PM2 now starts the app with an env allowlist (#997). A flag shipped in code
  before it is added to `RIPPLE_APP_ENV_KEYS` reads OFF even when set.
  Happened twice (offer links, Finch broadcast).
- Config helper scripts write fixed values. Re-running
  `configure-finch-tutor-activity.cjs` sets SYNC and UI back to false.
- Nine old migrations use `ON CONFLICT DO UPDATE SET enabled = FALSE`.
  Migration 167 neutralised this for 20 retired CRM keys; a re-run or
  rollback of the others still resets.
- Runtime-refresh rollback restores old PM2 env and only warns.

## SIMS: live ON today (candidates to make permanent)

| Flag | Storage | Since | Note |
|---|---|---|---|
| features.enhanced_data_collection_enabled | env, unprotected | 17/06 | |
| sims.operations_centre_enabled | env, unprotected | 07/06 | 404 when off |
| billing.allocator_write_enabled | env, validated | 07/06 | critical: billing |
| billing.parent_draft_visibility_enabled | env, validated | 07/06 | critical: billing |
| billing.payment_attempt_snapshot_enabled | env, validated | 07/06 | critical: payments |
| billing.scheduled_invoice_decoupling_enabled | env, carried | 27/07 | default already true |
| billing.commitment_fee_public_payment_links_enabled | env, validated | 14/07 | |
| billing.tutor_commitment_fee_public_payment_links_enabled | env, validated | 17/07 | |
| billing.invoice_checkout_pending_resume_enabled | env, carried | 22/09 | new |
| billing.invoice_checkout_assumed_unpaid_recovery_enabled | env, carried | 22/09 | labelled "emergency" |
| integration.signed_event_delivery_enabled | env, validated | 29/07 | |
| services.ripple.support_context_enabled | root file | 12/09 | |
| services.ripple.pic_initialization_enabled | root file | 07/09 | |
| live_media remote writes, canaries, replication | rollout file | 01/09 | |
| settings.ReferralSettings.enabled | DB | 28/07 | seed wipes it |

## SIMS: keep as switches (not rollout flags)

- `integration.command_admission_enabled`: master Ripple-to-SIMS breaker.
- `tutor_auth.legacy_otp_bridge_enabled`: ON; retire the bridge itself once
  old app traffic drains, not make it permanent.
- `phone-identity.review_account.enabled`: App Store review login.
- One-off write gates, all OFF by design: repair, payment merge, transfer
  reset, credit backfill, request-type repair, stale-application cleanup,
  subject-history write, Stage 0B harness and canary. Delete with their
  one-off commands once finished.

## SIMS: OFF and never launched (out of scope)

Tuition advance, promotions, subject-profile matching, same-row postpone,
linking v2, onboarding handoff, auto-release, billing notifications and
WhatsApp, suspension, follow-up, pause auto-resume, paid-cycle hold and
relink, MyInvois, workforce admission and governance, first-class
notification delivery, attendance location, trusted-device PIN, matching
notifications, mark-attended lock, local-writes block.

Dead: `live_media.prepared_image_optimization_enabled` has no reader.

## Ripple

Live values not read: the Ripple env file read was blocked by the secret
guard, and the only Ripple DB lane covers four migration views.

| Flag | Storage | Since | Note |
|---|---|---|---|
| TUTOR_OUTREACH_WORKER_ENABLED | env | 20/09 | prod doc says keep false |
| TUTOR_OUTREACH_REQUEST_FIRST_ENABLED | env | 25/09 | |
| TUTOR_OUTREACH_OFFER_LINKS_ENABLED | env | 27/09 | |
| TUTOR_OUTREACH_EXECUTION | env | 29/09 | legacy or pgboss |
| FINCH_TUTOR_BROADCAST_ENABLED | env | 19/09 | |
| FINCH_TUTOR_ACTIVITY_SYNC_ENABLED / _UI_ENABLED | env | 17/09 | helper resets |
| FINCH_WHATSAPP_ACTIVITY_SYNC_ENABLED | env | 19/09 | |
| FINCH_CONTEXT_ENABLED | env | 12/09 | |
| WORKFORCE_PERMISSION_GOVERNANCE_ENABLED | env | 26/08 | |
| USE_NEON | env | early | plan says remove |
| crm.sims_command_admission | DB | 30/07 | master breaker, keep |
| crm.request_progress_ui | DB | 15/09 | 0 readers, deploy requires FALSE: delete |
| crm_settings.crm_v3_create_enabled | DB | 068a | legacy routes |
| crm_settings.first_class_monitoring_enabled | DB | 04/08 | deploy requires true |
| crm_settings.polling_enabled | DB | v2 | ops kill switch, keep |
| tutor_onboarding_settings.enabled | DB | 08/09 | |
| workforce_access_projection_state.enforcement_enabled | DB | 05/08 | |
| revenue_runtime_settings | DB | 26/08 | staged rollout + kill switch |
| sealed recovery flags (legacy correction, historical recovery) | DB | Aug | one-time, keep sealed |
| knowledge_packs.kill_switch_engaged, outreach pause/global stop | DB/file | | ops controls, keep |

Already done: 20 mature CRM flags retired by migration 167 (#971).
