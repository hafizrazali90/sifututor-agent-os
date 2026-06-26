# Session Save — sifu-tutor FIUU ordering-guard payment hotfix

- **Date:** 2026-06-18
- **Project:** sifu-tutor
- **Save level:** Critical Save
- **Reason:** Payment webhook behavior, production deploy, and production invoice data repair.

## What Happened

- Staff reported cases where FIUU showed payment successful but SIMS still showed the invoice as unpaid.
- Root cause was confirmed in the FIUU webhook handler: a successful FIUU callback could be rejected after payment capture if an older invoice for the same request was still unpaid.
- The rejected callback returned HTTP 200, so FIUU stopped retrying while SIMS kept the target invoice unpaid.
- PR `Sifututor/sifu-tutor#1609` removed the post-payment ordering guard from the webhook handler.
- The PR was merged into `main` and deployed to production at `696cb0704`.
- A read-only production audit found historical ordering-guard rejection evidence; two confirmed affected invoices were repaired after Hafiz approved the production data repair.

## Durable Lesson

Payment ordering rules belong before payment initiation, not after the bank or FIUU has already confirmed a successful payment. Webhook handlers must treat successful payment callbacks as money-record reconciliation events: do not silently reject them with HTTP 200 unless the case is deliberately moved into a visible manual-review workflow with Finance/Admin alerting.

## Evidence

- PR: `Sifututor/sifu-tutor#1609`
- Production deploy SHA: `696cb0704`
- Regression coverage confirmed the newer invoice is marked paid even when an older invoice remains unpaid.
- Focused verification passed for the FIUU ordering-guard regression and direct-pay callback behavior.
- Production backup completed before deploy.
- Production deploy completed: pull, Composer install, npm install, build, migration check, optimize, and queue restart.
- Production smoke passed: `/login` and `/up` returned `200`; production mode was on, debug was off, maintenance was off, and no migrations were pending.
- Production data repair backup completed before invoice repair.
- Repair verification confirmed the two restored FIUU transaction IDs were attached exactly once after repair.

## Current Production State

- Production `main` head after deploy: `696cb0704`.
- PR `#1609` is merged.
- Two historical affected invoices were repaired after explicit approval.
- The older unpaid invoices that triggered the former guard were left unpaid.
- No parent notification was sent by the manual repair.

## Remaining Work

- Ask Finance/Admin to spot-check the two repaired invoices in SIMS.
- Open the follow-up for FIUU `mismatch_review` alerting and an Operations Centre pending-payment-review queue.
- Sync the hotfix into `sifu-staging`, because production `main` is ahead of staging for this payment fix.
- Continue treating production failed notification jobs and production untracked backup artifacts as separate housekeeping items.

## Mission Ledger

- Added `SIMS-FIUU-PAYMENT-REVIEW-001` for the `mismatch_review` alert/dashboard follow-up.

## Koda Status

- Koda health check passed, but the memory search/store step timed out during save-session. This file is the fallback durable save note.
