# Critical Save: Billing Cycle Revamp

Date: 2026-06-06
Project: SIMS (`sifu-tutor`)
Status: read-only design and diagnosis consolidation; no implementation approved

## Current State

- Workspace branch checked: `main`.
- `sifu-tutor` branch checked: `main`.
- `sifu-tutor/.claude/tasks/active.json`: no active task.
- This session involved invoice, billing-cycle, class allocation, and production-data repair design, so future work must stay in critical-lane Phase A until Hafiz approves implementation.

## Durable Lesson

For the SIMS billing-cycle revamp, invoice-cycle allocation must be based on consumed sessions only:

- Consumed: `attended`, `verify`
- Not consumed: `scheduled`, `cancelled`, `postponed`, `refunded`

A shared `InvoiceCycleAllocator` should assign and rebalance class `parent_invoice_id` across all create, edit, cancel, postpone, attend, and verify flows. Scheduled rows must not permanently fill invoice capacity and push later verified classes into future empty invoices.

TREQ-227936 is an explicit acceptance case:

- Package size: 4 sessions
- Consumed sessions: 14 verified classes
- Expected allocation:
  - invoice 1: sessions 1-4
  - invoice 2: sessions 5-8
  - invoice 3: sessions 9-12
  - invoice 4: sessions 13-14
  - invoice 5: Not Scheduled / empty

The bug pattern is that a future invoice can show verified activity because scheduled/cancelled/postponed rows temporarily filled an earlier invoice and the later verified class was never rebalanced back.

## Recommended Next Step

Before implementation, add the billing-cycle revamp PRD/build plan section for:

1. `InvoiceCycleAllocator`
2. consumed-session-only allocation
3. rebalancing after cancellation/postponement/verification
4. TREQ-227936 as an explicit acceptance scenario
5. read-only production repair/report command before any write repair

## Watchouts

- Do not mutate paid invoice document dates.
- Do not delete or move paid invoices without explicit repair approval.
- Any production repair must start as read-only audit output.
- Keep SIMS as the invoice/class source of truth; notification or Finch work is secondary.

## Koda Fallback

Koda health passed, but memory search and memory store timed out during save-session. This file is the fallback save note.
