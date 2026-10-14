#!/usr/bin/env python3
"""Daily read-only money and work monitor per company (WP-28, Sifututor/sifu-tutor#3479).

Prints one report for Sifu Edu & Learning Sdn Bhd and Nakngaji Sdn Bhd with the eleven go-live signals. Each signal
gives a count, an amount to the sen where money is involved, up to five example record ids and a status:
OK, CHECK, or NOT DEPLOYED when the tables or columns it reads are not in production yet.

Every query goes through the existing read-only lanes, so this script never touches a credential:
  - SIMS production: scripts/agent-access/sims-db-readonly-sql.sh (lane 4, SELECT-only account)
  - Ripple production: scripts/agent-access/ripple-prod-sql-readonly.sh (lane 40, forced read-only session)
The report holds ids, counts and amounts only, never names, emails or phone numbers.

Usage:  scripts/agent-access/nakngaji-company-monitor.py [--json]
Exit:   0 nothing to check, 1 at least one CHECK, 2 a database could not be read
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import os
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path
from zoneinfo import ZoneInfo

ACCESS = Path(__file__).resolve().parent
MYT = ZoneInfo("Asia/Kuala_Lumpur")

SIFU = "sifu_edu_learning"
NAK = "nakngaji_sdn_bhd"
UNRECORDED = "unrecorded"
COMPANY_NAMES = {
    SIFU: "Sifu Edu & Learning Sdn Bhd",
    NAK: "Nakngaji Sdn Bhd",
    UNRECORDED: "Company not recorded",
}
BRAND_TO_COMPANY = {"sifututor": SIFU, "nakngaji": NAK}
DB_NAMES = {"sims": "SIMS", "ripple": "Ripple"}
STANDARD_COLUMNS = {"company", "n", "amount_sen", "ex", "needs_check"}

BEFORE_GO_LIVE_SIMS = "before go-live schema, company from the request brand"
BEFORE_GO_LIVE_RIPPLE = "before go-live schema, Ripple has no company yet so every row counts as Sifu Edu & Learning"


class QueryError(RuntimeError):
    pass


@dataclass(frozen=True)
class Variant:
    requires: dict[str, tuple[str, ...]]
    sql: str
    basis: str = ""


@dataclass(frozen=True)
class Part:
    key: str
    db: str
    label: str
    example_label: str
    variants: tuple[Variant, ...]


@dataclass(frozen=True)
class Signal:
    key: str
    title: str
    parts: tuple[Part, ...]
    money: bool = True
    count_label: tuple[str, str] = ("", "")
    companies: tuple[str, ...] = (SIFU, NAK)
    note: str = ""


# ---------------------------------------------------------------------------------------------------------------
# Shared SQL pieces. SIMS stores and compares times in MYT (NOW() on the read-only session is MYT).

SIMS_INVOICE_COMPANY_GO_LIVE = """CASE WHEN lc.code IS NOT NULL THEN lc.code
            WHEN pi.id IS NULL AND tr.id IS NULL THEN NULL
            WHEN b.code = 'nakngaji' THEN 'nakngaji_sdn_bhd' ELSE 'sifu_edu_learning' END"""
SIMS_REQUEST_COMPANY = """CASE WHEN tr.id IS NULL THEN NULL
            WHEN b.code = 'nakngaji' THEN 'nakngaji_sdn_bhd' ELSE 'sifu_edu_learning' END"""


def ripple_ids(column: str, order: str = "") -> str:
    return f"array_to_string((array_agg({column} ORDER BY {order or column} DESC))[1:5], ',')"


def ripple_sen(expression: str) -> str:
    return f"(round(coalesce(sum({expression}), 0) * 100))::bigint"


def sims_sen(expression: str) -> str:
    return f"CAST(ROUND(COALESCE(SUM({expression}), 0) * 100) AS SIGNED)"


# ---------------------------------------------------------------------------------------------------------------
# 1. Unmatched payments

UNMATCHED_RECEIPTS_WHERE = """WHERE r.sandbox = 0 AND r.provider_state <> 'failed'
  AND (r.application_state <> 'settled' OR r.requires_review = 1 OR r.needs_reconciliation = 1)
  AND r.created_at < NOW() - INTERVAL 2 HOUR
GROUP BY company"""

RECEIPT_COLUMNS = ("id", "sandbox", "provider_state", "application_state", "requires_review",
                   "needs_reconciliation", "created_at", "amount", "invoice_id", "attempt_id")

UNMATCHED_GATEWAY_RECEIPTS = Part(
    key="unmatched_payments.sims_gateway_receipts", db="sims", label="SIMS gateway receipts",
    example_label="gateway receipt",
    variants=(
        Variant(
            requires={
                "parent_payment_receipts": RECEIPT_COLUMNS,
                "parent_invoices": ("id", "request_id", "brand_id", "legal_company_id"),
                "parent_payment_attempts": ("id", "request_id", "issuer_company_id"),
                "tutor_requests": ("id", "brand_id"),
                "brands": ("id", "code"),
                "legal_companies": ("id", "code"),
            },
            sql=f"""SELECT {SIMS_INVOICE_COMPANY_GO_LIVE} AS company,
       COUNT(*) AS n, {sims_sen('r.amount')} AS amount_sen,
       SUBSTRING_INDEX(GROUP_CONCAT(r.id ORDER BY r.id DESC), ',', 5) AS ex
FROM parent_payment_receipts r
LEFT JOIN parent_invoices pi ON pi.id = r.invoice_id
LEFT JOIN parent_payment_attempts a ON a.id = r.attempt_id
LEFT JOIN tutor_requests tr ON tr.id = COALESCE(pi.request_id, a.request_id)
LEFT JOIN brands b ON b.id = COALESCE(pi.brand_id, tr.brand_id)
LEFT JOIN legal_companies lc ON lc.id = COALESCE(pi.legal_company_id, a.issuer_company_id)
{UNMATCHED_RECEIPTS_WHERE}""",
        ),
        Variant(
            requires={
                "parent_payment_receipts": RECEIPT_COLUMNS,
                "parent_invoices": ("id", "request_id"),
                "parent_payment_attempts": ("id", "request_id"),
                "tutor_requests": ("id", "brand_id"),
                "brands": ("id", "code"),
            },
            sql=f"""SELECT {SIMS_REQUEST_COMPANY} AS company,
       COUNT(*) AS n, {sims_sen('r.amount')} AS amount_sen,
       SUBSTRING_INDEX(GROUP_CONCAT(r.id ORDER BY r.id DESC), ',', 5) AS ex
FROM parent_payment_receipts r
LEFT JOIN parent_invoices pi ON pi.id = r.invoice_id
LEFT JOIN parent_payment_attempts a ON a.id = r.attempt_id
LEFT JOIN tutor_requests tr ON tr.id = COALESCE(pi.request_id, a.request_id)
LEFT JOIN brands b ON b.id = tr.brand_id
{UNMATCHED_RECEIPTS_WHERE}""",
            basis=BEFORE_GO_LIVE_SIMS,
        ),
    ),
)

SUSPENSE_COLUMNS = ("id", "bank_transaction_id", "gateway_transaction_id", "amount", "status", "created_at")
SUSPENSE_SELECT = f"""count(*) AS n, {ripple_sen('si.amount')} AS amount_sen, {ripple_ids('si.id')} AS ex,
       count(*) FILTER (WHERE si.created_at > now() - interval '1 day') AS new_last_day
FROM suspense_items si"""

UNMATCHED_BANK_SUSPENSE = Part(
    key="unmatched_payments.ripple_bank_suspense", db="ripple", label="Ripple bank and gateway suspense",
    example_label="suspense item",
    variants=(
        Variant(
            requires={
                "suspense_items": SUSPENSE_COLUMNS,
                "bank_transactions": ("id", "batch_id"),
                "gateway_transactions": ("id", "batch_id"),
                "import_batches": ("id", "company_code"),
            },
            sql=f"""SELECT coalesce(ib.company_code, 'sifu_edu_learning') AS company, {SUSPENSE_SELECT}
LEFT JOIN bank_transactions bt ON bt.id = si.bank_transaction_id
LEFT JOIN gateway_transactions gt ON gt.id = si.gateway_transaction_id
LEFT JOIN import_batches ib ON ib.id = coalesce(bt.batch_id, gt.batch_id)
WHERE si.status IN ('open', 'pending_write_off')
GROUP BY 1""",
        ),
        Variant(
            requires={"suspense_items": SUSPENSE_COLUMNS},
            sql=f"""SELECT 'sifu_edu_learning' AS company, {SUSPENSE_SELECT}
WHERE si.status IN ('open', 'pending_write_off')
GROUP BY 1""",
            basis=BEFORE_GO_LIVE_RIPPLE,
        ),
    ),
)

# ---------------------------------------------------------------------------------------------------------------
# 2. Callback mismatches: an unresolved amount mismatch, or an attempt whose issuing company is not the invoice's

ATTEMPT_COLUMNS = ("id", "request_id", "status", "resolved_at")
CALLBACK_MISMATCHES = Part(
    key="callback_mismatches.sims_attempts", db="sims", label="SIMS payment attempts", example_label="payment attempt",
    variants=(
        Variant(
            requires={
                "parent_payment_attempts": ATTEMPT_COLUMNS + ("issuer_company_id",),
                "parent_payment_attempt_items": ("attempt_id", "invoice_id", "snapshot_amount"),
                "parent_invoices": ("id", "request_id", "brand_id", "legal_company_id"),
                "tutor_requests": ("id", "brand_id"),
                "brands": ("id", "code"),
                "legal_companies": ("id", "code"),
            },
            sql=f"""SELECT {SIMS_INVOICE_COMPANY_GO_LIVE} AS company,
       COUNT(DISTINCT a.id) AS n, {sims_sen('i.snapshot_amount')} AS amount_sen,
       SUBSTRING_INDEX(GROUP_CONCAT(DISTINCT a.id ORDER BY a.id DESC), ',', 5) AS ex
FROM parent_payment_attempts a
LEFT JOIN parent_payment_attempt_items i ON i.attempt_id = a.id
LEFT JOIN parent_invoices pi ON pi.id = i.invoice_id
LEFT JOIN tutor_requests tr ON tr.id = COALESCE(pi.request_id, a.request_id)
LEFT JOIN brands b ON b.id = COALESCE(pi.brand_id, tr.brand_id)
LEFT JOIN legal_companies lc ON lc.id = pi.legal_company_id
WHERE (a.status = 'mismatch_review' AND a.resolved_at IS NULL)
   OR (a.issuer_company_id IS NOT NULL AND pi.legal_company_id IS NOT NULL AND a.issuer_company_id <> pi.legal_company_id)
GROUP BY company""",
        ),
        Variant(
            requires={
                "parent_payment_attempts": ATTEMPT_COLUMNS,
                "parent_payment_attempt_items": ("attempt_id", "invoice_id", "snapshot_amount"),
                "parent_invoices": ("id", "request_id"),
                "tutor_requests": ("id", "brand_id"),
                "brands": ("id", "code"),
            },
            sql=f"""SELECT {SIMS_REQUEST_COMPANY} AS company,
       COUNT(DISTINCT a.id) AS n, {sims_sen('i.snapshot_amount')} AS amount_sen,
       SUBSTRING_INDEX(GROUP_CONCAT(DISTINCT a.id ORDER BY a.id DESC), ',', 5) AS ex
FROM parent_payment_attempts a
LEFT JOIN parent_payment_attempt_items i ON i.attempt_id = a.id
LEFT JOIN parent_invoices pi ON pi.id = i.invoice_id
LEFT JOIN tutor_requests tr ON tr.id = COALESCE(pi.request_id, a.request_id)
LEFT JOIN brands b ON b.id = tr.brand_id
WHERE a.status = 'mismatch_review' AND a.resolved_at IS NULL
GROUP BY company""",
            basis=BEFORE_GO_LIVE_SIMS,
        ),
    ),
)

# ---------------------------------------------------------------------------------------------------------------
# 3. Failed credit allocation. No single failure record exists, so this reads the two places a failure shows:
#    credit moved between the two companies in SIMS (never allowed), and Ripple fee allocations that failed.

CROSS_COMPANY_CREDIT = Part(
    key="failed_credit_allocation.sims_cross_company_transfers", db="sims",
    label="SIMS credit moved across companies", example_label="",
    variants=(
        Variant(
            requires={
                "payment_transfers": ("id", "source_invoice_id", "target_invoice_id", "amount_at_transfer",
                                      "reverted_at", "deleted_at"),
                "referral_reward_allocations": ("id", "referral_reward_id", "parent_invoice_id", "amount"),
                "referral_rewards": ("id", "legal_company_id"),
                "parent_invoices": ("id", "legal_company_id"),
                "legal_companies": ("id", "code"),
            },
            sql=f"""SELECT lc.code AS company, COUNT(*) AS n, {sims_sen('x.amount')} AS amount_sen,
       SUBSTRING_INDEX(GROUP_CONCAT(x.ref ORDER BY x.id DESC), ',', 5) AS ex
FROM (
  SELECT pt.id, CONCAT('transfer ', pt.id) AS ref, pt.amount_at_transfer AS amount, s.legal_company_id AS company_id
  FROM payment_transfers pt
  JOIN parent_invoices s ON s.id = pt.source_invoice_id
  JOIN parent_invoices t ON t.id = pt.target_invoice_id
  WHERE pt.reverted_at IS NULL AND pt.deleted_at IS NULL
    AND s.legal_company_id IS NOT NULL AND t.legal_company_id IS NOT NULL AND s.legal_company_id <> t.legal_company_id
  UNION ALL
  SELECT ra.id, CONCAT('referral allocation ', ra.id), ra.amount, rr.legal_company_id
  FROM referral_reward_allocations ra
  JOIN referral_rewards rr ON rr.id = ra.referral_reward_id
  JOIN parent_invoices pi ON pi.id = ra.parent_invoice_id
  WHERE rr.legal_company_id IS NOT NULL AND pi.legal_company_id IS NOT NULL AND rr.legal_company_id <> pi.legal_company_id
) x
LEFT JOIN legal_companies lc ON lc.id = x.company_id
GROUP BY company""",
        ),
        Variant(
            requires={
                "payment_transfers": ("id", "source_invoice_id", "target_invoice_id", "amount_at_transfer",
                                      "reverted_at", "deleted_at"),
                "parent_invoices": ("id", "request_id"),
                "tutor_requests": ("id", "brand_id"),
                "brands": ("id", "code"),
            },
            sql=f"""SELECT IF(sb.code = 'nakngaji', 'nakngaji_sdn_bhd', 'sifu_edu_learning') AS company,
       COUNT(*) AS n, {sims_sen('pt.amount_at_transfer')} AS amount_sen,
       SUBSTRING_INDEX(GROUP_CONCAT(CONCAT('transfer ', pt.id) ORDER BY pt.id DESC), ',', 5) AS ex
FROM payment_transfers pt
JOIN parent_invoices s ON s.id = pt.source_invoice_id
JOIN parent_invoices t ON t.id = pt.target_invoice_id
LEFT JOIN tutor_requests sr ON sr.id = s.request_id
LEFT JOIN tutor_requests tr ON tr.id = t.request_id
LEFT JOIN brands sb ON sb.id = sr.brand_id
LEFT JOIN brands tb ON tb.id = tr.brand_id
WHERE pt.reverted_at IS NULL AND pt.deleted_at IS NULL
  AND COALESCE(sb.code, 'sifututor') <> COALESCE(tb.code, 'sifututor')
GROUP BY company""",
            basis=BEFORE_GO_LIVE_SIMS,
        ),
    ),
)

FEE_ALLOCATION_COLUMNS = ("id", "customer_receipt_id", "amount_sen", "status")
FEE_ALLOCATION_SELECT = f"""count(*) AS n, coalesce(sum(a.amount_sen), 0)::bigint AS amount_sen, {ripple_ids('a.id')} AS ex
FROM receipt_commitment_fee_allocations a"""
FEE_ALLOCATIONS = Part(
    key="failed_credit_allocation.ripple_fee_allocations", db="ripple",
    label="Ripple commitment fee receipt allocations failed or held for review", example_label="fee allocation",
    variants=(
        Variant(
            requires={
                "receipt_commitment_fee_allocations": FEE_ALLOCATION_COLUMNS,
                "customer_receipts": ("id", "bank_transaction_id"),
                "bank_transactions": ("id", "batch_id"),
                "import_batches": ("id", "company_code"),
            },
            sql=f"""SELECT coalesce(ib.company_code, 'sifu_edu_learning') AS company, {FEE_ALLOCATION_SELECT}
LEFT JOIN customer_receipts cr ON cr.id = a.customer_receipt_id
LEFT JOIN bank_transactions bt ON bt.id = cr.bank_transaction_id
LEFT JOIN import_batches ib ON ib.id = bt.batch_id
WHERE a.status IN ('failed', 'needs_review')
GROUP BY 1""",
        ),
        Variant(
            requires={"receipt_commitment_fee_allocations": FEE_ALLOCATION_COLUMNS},
            sql=f"""SELECT 'sifu_edu_learning' AS company, {FEE_ALLOCATION_SELECT}
WHERE a.status IN ('failed', 'needs_review')
GROUP BY 1""",
            basis=BEFORE_GO_LIVE_RIPPLE,
        ),
    ),
)

# ---------------------------------------------------------------------------------------------------------------
# 4. Rejected clock-ins: open holds past their block time; classes due on those requests could not be started.

HOLDS = Part(
    key="rejected_clock_ins.sims_holds", db="sims", label="SIMS class holds blocking clock-in", example_label="hold",
    variants=(
        Variant(
            requires={
                "request_payment_holds": ("id", "tutor_request_id", "block_at", "lifted_at"),
                "tutor_requests": ("id", "brand_id"),
                "brands": ("id", "code"),
                "classes": ("id", "request_id", "date", "clock_in", "status", "deleted_at"),
            },
            sql=f"""SELECT {SIMS_REQUEST_COMPANY} AS company,
       COUNT(*) AS n, 0 AS amount_sen,
       SUBSTRING_INDEX(GROUP_CONCAT(h.id ORDER BY h.id DESC), ',', 5) AS ex,
       COALESCE(SUM((SELECT COUNT(*) FROM classes c
          WHERE c.request_id = h.tutor_request_id AND c.deleted_at IS NULL AND c.status = 'scheduled'
            AND c.clock_in IS NULL AND c.date BETWEEN DATE(h.block_at) AND CURDATE())), 0) AS classes_due
FROM request_payment_holds h
LEFT JOIN tutor_requests tr ON tr.id = h.tutor_request_id
LEFT JOIN brands b ON b.id = tr.brand_id
WHERE h.lifted_at IS NULL AND h.block_at IS NOT NULL AND h.block_at <= NOW()
GROUP BY company""",
        ),
    ),
)

# ---------------------------------------------------------------------------------------------------------------
# 5. Open follow-up cases older than 72 hours (already in production; the company comes from the request brand)

FOLLOWUPS = Part(
    key="followup_cases_72h.sims_cases", db="sims", label="SIMS follow-up cases", example_label="case",
    variants=(
        Variant(
            requires={
                "request_followup_cases": ("id", "tutor_request_id", "status", "resolved_at", "created_at"),
                "tutor_requests": ("id", "brand_id"),
                "brands": ("id", "code"),
            },
            sql=f"""SELECT {SIMS_REQUEST_COMPANY} AS company,
       COUNT(*) AS n, 0 AS amount_sen,
       SUBSTRING_INDEX(GROUP_CONCAT(f.id ORDER BY f.created_at), ',', 5) AS ex
FROM request_followup_cases f
LEFT JOIN tutor_requests tr ON tr.id = f.tutor_request_id
LEFT JOIN brands b ON b.id = tr.brand_id
WHERE f.status <> 'resolved' AND f.resolved_at IS NULL AND f.created_at < NOW() - INTERVAL 72 HOUR
GROUP BY company""",
        ),
    ),
)

# ---------------------------------------------------------------------------------------------------------------
# 6. Extra charges waiting more than one month end. A charge may wait one month end while a payment is in
#    progress (FS-9.6); one approved before the start of last month has waited through two.

EXTRA_CHARGES = Part(
    key="extra_charges_waiting.sims_pending_charges", db="sims", label="SIMS pending extra charges",
    example_label="extra charge",
    variants=(
        Variant(
            requires={
                "pending_extra_charges": ("id", "legal_company_id", "amount_sen", "status", "approved_at"),
                "legal_companies": ("id", "code"),
            },
            sql="""SELECT lc.code AS company,
       SUM(p.approved_at < DATE_FORMAT(NOW() - INTERVAL 1 MONTH, '%Y-%m-01')) AS n,
       CAST(COALESCE(SUM(IF(p.approved_at < DATE_FORMAT(NOW() - INTERVAL 1 MONTH, '%Y-%m-01'), p.amount_sen, 0)), 0) AS SIGNED) AS amount_sen,
       SUBSTRING_INDEX(GROUP_CONCAT(IF(p.approved_at < DATE_FORMAT(NOW() - INTERVAL 1 MONTH, '%Y-%m-01'), p.id, NULL) ORDER BY p.approved_at), ',', 5) AS ex,
       COUNT(*) AS past_one_month_end
FROM pending_extra_charges p
LEFT JOIN legal_companies lc ON lc.id = p.legal_company_id
WHERE p.status IN ('approved', 'waiting') AND p.approved_at < DATE_FORMAT(NOW(), '%Y-%m-01')
GROUP BY company""",
        ),
    ),
)

# ---------------------------------------------------------------------------------------------------------------
# 7. Payout differences between the approved selection and the bank file (Ripple, last 45 days of files)

PAYOUT_TOTALS = """count(s.id) AS slips, coalesce(sum(s.net_amount), 0) AS slips_total"""
PAYOUT_FINAL = f"""SELECT company, count(*) FILTER (WHERE differs) AS n,
       (round(coalesce(sum(abs(total_amount - slips_total)) FILTER (WHERE differs), 0) * 100))::bigint AS amount_sen,
       array_to_string((array_agg(id ORDER BY id DESC) FILTER (WHERE differs))[1:5], ',') AS ex,
       count(*) AS files_checked
FROM checked GROUP BY company"""
PAYOUTS = Part(
    key="payout_differences.ripple_bank_files", db="ripple", label="Ripple tutor payment bank files",
    example_label="bank file batch",
    variants=(
        Variant(
            requires={
                "tutor_payment_csv_batches": ("id", "status", "created_at", "total_amount", "slip_count",
                                              "payer_company_code", "selection_fingerprint"),
                "tutor_payment_slips": ("id", "csv_batch_id", "net_amount", "payer_company_code"),
                "tutor_payment_audit_log": ("slip_id", "action", "details"),
            },
            sql=f"""WITH files AS (
  SELECT b.id, coalesce(b.payer_company_code, 'sifu_edu_learning') AS company, b.total_amount, b.slip_count,
         {PAYOUT_TOTALS},
         coalesce(bool_or(s.payer_company_code IS DISTINCT FROM b.payer_company_code), false) AS company_differs,
         coalesce(bool_or(b.selection_fingerprint IS NOT NULL AND NOT EXISTS (
           SELECT 1 FROM tutor_payment_audit_log l
           WHERE l.slip_id = s.id AND l.action IN ('slip_approved', 'payment_approved')
             AND l.details->>'selection_fingerprint' IS NOT NULL)), false) AS approval_missing
  FROM tutor_payment_csv_batches b
  LEFT JOIN tutor_payment_slips s ON s.csv_batch_id = b.id
  WHERE b.status <> 'superseded' AND b.created_at > now() - interval '45 days'
  GROUP BY b.id, b.payer_company_code, b.total_amount, b.slip_count),
checked AS (
  SELECT *, (total_amount <> slips_total OR slip_count <> slips OR company_differs OR approval_missing) AS differs FROM files)
{PAYOUT_FINAL}""",
        ),
        Variant(
            requires={
                "tutor_payment_csv_batches": ("id", "status", "created_at", "total_amount", "slip_count"),
                "tutor_payment_slips": ("id", "csv_batch_id", "net_amount"),
            },
            sql=f"""WITH files AS (
  SELECT b.id, 'sifu_edu_learning' AS company, b.total_amount, b.slip_count, {PAYOUT_TOTALS}
  FROM tutor_payment_csv_batches b
  LEFT JOIN tutor_payment_slips s ON s.csv_batch_id = b.id
  WHERE b.status <> 'superseded' AND b.created_at > now() - interval '45 days'
  GROUP BY b.id, b.total_amount, b.slip_count),
checked AS (
  SELECT *, (total_amount <> slips_total OR slip_count <> slips) AS differs FROM files)
{PAYOUT_FINAL}""",
            basis=BEFORE_GO_LIVE_RIPPLE + "; totals and counts only, no approved fingerprint yet",
        ),
    ),
)

# ---------------------------------------------------------------------------------------------------------------
# 8. Carried-forward deductions waiting for the company's next payment; CHECK only when older than 35 days

CARRIED = Part(
    key="carried_deductions.ripple_notes", db="ripple", label="Ripple carried-forward deduction notes",
    example_label="note",
    variants=(
        Variant(
            requires={
                "tutor_payment_notes": ("id", "slip_id", "type", "amount", "note_status", "created_at",
                                        "payer_company_code", "carried_from_note_id"),
            },
            sql=f"""SELECT coalesce(payer_company_code, 'sifu_edu_learning') AS company,
       count(*) AS n, {ripple_sen('amount')} AS amount_sen, {ripple_ids('id')} AS ex,
       count(*) FILTER (WHERE created_at < now() - interval '35 days') AS needs_check
FROM tutor_payment_notes
WHERE carried_from_note_id IS NOT NULL AND type = 'deduction' AND note_status = 'approved' AND slip_id IS NULL
GROUP BY 1""",
        ),
    ),
)

# ---------------------------------------------------------------------------------------------------------------
# 9. QuickBooks sync failures: vouchers and tutor bill items with a sync error, revenue rows that failed unretried

QB_FAILED_REVENUE_ROW = """r.result_status = 'failed'
    AND NOT EXISTS (SELECT 1 FROM revenue_qb_batch_rows x WHERE x.retry_of_batch_row_id = r.id)"""
QB_FINAL = f"""SELECT company, count(*) AS n, {ripple_sen('amt')} AS amount_sen, {ripple_ids('ref', 'id')} AS ex
FROM f GROUP BY company"""
QB_REVENUE_COLUMNS = ("id", "batch_id", "final_amount", "result_status", "retry_of_batch_row_id")
QUICKBOOKS = Part(
    key="quickbooks_sync_failures.ripple_qb", db="ripple", label="Ripple QuickBooks sync", example_label="",
    variants=(
        Variant(
            requires={
                "pv_vouchers": ("id", "amount_myr", "qb_sync_error", "company_code", "qb_destination_id"),
                "pv_tutor_bill_items": ("id", "pv_id", "amount_myr", "qb_sync_error", "qb_destination_id"),
                "qb_destinations": ("id", "company_code"),
                "revenue_qb_batch_rows": QB_REVENUE_COLUMNS,
                "revenue_qb_batches": ("id", "qb_destination_id"),
            },
            sql=f"""WITH f AS (
  SELECT v.id, 'voucher ' || v.id AS ref, v.amount_myr AS amt,
         coalesce(v.company_code, d.company_code, 'sifu_edu_learning') AS company
  FROM pv_vouchers v LEFT JOIN qb_destinations d ON d.id = v.qb_destination_id
  WHERE v.qb_sync_error IS NOT NULL
  UNION ALL
  SELECT i.id, 'bill_item ' || i.id, i.amount_myr, coalesce(v.company_code, d.company_code, 'sifu_edu_learning')
  FROM pv_tutor_bill_items i JOIN pv_vouchers v ON v.id = i.pv_id
  LEFT JOIN qb_destinations d ON d.id = coalesce(i.qb_destination_id, v.qb_destination_id)
  WHERE i.qb_sync_error IS NOT NULL
  UNION ALL
  SELECT r.id, 'revenue_row ' || r.id, r.final_amount, coalesce(d.company_code, 'sifu_edu_learning')
  FROM revenue_qb_batch_rows r JOIN revenue_qb_batches b ON b.id = r.batch_id
  LEFT JOIN qb_destinations d ON d.id = b.qb_destination_id
  WHERE {QB_FAILED_REVENUE_ROW})
{QB_FINAL}""",
        ),
        Variant(
            requires={
                "pv_vouchers": ("id", "amount_myr", "qb_sync_error"),
                "pv_tutor_bill_items": ("id", "amount_myr", "qb_sync_error"),
                "revenue_qb_batch_rows": QB_REVENUE_COLUMNS,
            },
            sql=f"""WITH f AS (
  SELECT id, 'voucher ' || id AS ref, amount_myr AS amt, 'sifu_edu_learning' AS company
  FROM pv_vouchers WHERE qb_sync_error IS NOT NULL
  UNION ALL
  SELECT id, 'bill_item ' || id, amount_myr, 'sifu_edu_learning' FROM pv_tutor_bill_items WHERE qb_sync_error IS NOT NULL
  UNION ALL
  SELECT r.id, 'revenue_row ' || r.id, r.final_amount, 'sifu_edu_learning' FROM revenue_qb_batch_rows r
  WHERE {QB_FAILED_REVENUE_ROW})
{QB_FINAL}""",
            basis=BEFORE_GO_LIVE_RIPPLE,
        ),
    ),
)

# ---------------------------------------------------------------------------------------------------------------
# 10. Owed to Nakngaji versus recorded transfers. Count = closed months (MYT) with no confirmed transfer;
#     amount = closed-month ledger total minus confirmed transfers (0 when settled).

CLOSED_MONTH = "l.period < DATE_FORMAT(NOW(), '%Y-%m')"
NO_CONFIRMED_TRANSFER = """NOT EXISTS (SELECT 1 FROM collection_transfers t
       WHERE t.to_company_id = lc.id AND t.period = l.period AND t.confirmed_at IS NOT NULL)"""
OWED = Part(
    key="owed_to_nakngaji.sims_collection_ledger", db="sims", label="SIMS collection ledger and transfers",
    example_label="month",
    variants=(
        Variant(
            requires={
                "collection_ledger_entries": ("id", "owed_to_company_id", "amount_sen", "period"),
                "collection_transfers": ("id", "to_company_id", "period", "amount_transferred_sen", "confirmed_at"),
                "legal_companies": ("id", "code"),
            },
            sql=f"""SELECT lc.code AS company,
  (SELECT COUNT(DISTINCT l.period) FROM collection_ledger_entries l
     WHERE l.owed_to_company_id = lc.id AND {CLOSED_MONTH} AND {NO_CONFIRMED_TRANSFER}) AS n,
  COALESCE((SELECT SUM(l.amount_sen) FROM collection_ledger_entries l WHERE l.owed_to_company_id = lc.id AND {CLOSED_MONTH}), 0)
  - COALESCE((SELECT SUM(t.amount_transferred_sen) FROM collection_transfers t
              WHERE t.to_company_id = lc.id AND t.confirmed_at IS NOT NULL), 0) AS amount_sen,
  (SELECT SUBSTRING_INDEX(GROUP_CONCAT(DISTINCT l.period ORDER BY l.period DESC), ',', 5) FROM collection_ledger_entries l
     WHERE l.owed_to_company_id = lc.id AND {CLOSED_MONTH} AND {NO_CONFIRMED_TRANSFER}) AS ex,
  COALESCE((SELECT SUM(l.amount_sen) FROM collection_ledger_entries l
     WHERE l.owed_to_company_id = lc.id AND l.period = DATE_FORMAT(NOW(), '%Y-%m')), 0) AS this_month_sen
FROM legal_companies lc WHERE lc.code = 'nakngaji_sdn_bhd'""",
        ),
    ),
)

# ---------------------------------------------------------------------------------------------------------------
# 11. MyInvois list counts. Count = submissions that failed or need correction; the list sizes are information.

MYINVOIS_READY = """ri.invoice_state = 'eligible' AND ri.myinvois_status = 'not_submitted'
    AND ri.data_health_status NOT IN ('blocked', 'stale') AND ris.service_month IS NOT NULL"""
MYINVOIS_FAILED = "status IN ('projection_failed', 'needs_correction')"


def myinvois_sql(invoice_company: str, submission_company: str) -> str:
    return f"""WITH ready AS (
  SELECT {invoice_company} AS company, count(*) AS waiting, {ripple_sen('ris.final_invoice_amount')} AS waiting_sen
  FROM revenue_invoices ri JOIN revenue_invoice_snapshots ris ON ris.id = ri.latest_snapshot_id
  WHERE {MYINVOIS_READY}
  GROUP BY 1),
subs AS (
  SELECT {submission_company} AS company,
         count(*) FILTER (WHERE {MYINVOIS_FAILED}) AS failed,
         count(*) FILTER (WHERE status NOT IN ('projection_failed', 'needs_correction', 'cancelled')) AS submitted,
         array_to_string((array_agg(id ORDER BY id DESC) FILTER (WHERE {MYINVOIS_FAILED}))[1:5], ',') AS ex
  FROM revenue_myinvois_submissions GROUP BY 1)
SELECT coalesce(r.company, s.company) AS company, coalesce(s.failed, 0) AS n, 0 AS amount_sen,
       coalesce(s.ex, '') AS ex, coalesce(r.waiting, 0) AS waiting_to_file,
       coalesce(r.waiting_sen, 0) AS waiting_to_file_sen, coalesce(s.submitted, 0) AS submitted
FROM ready r FULL JOIN subs s ON s.company = r.company"""


MYINVOIS_INVOICE_COLUMNS = ("id", "latest_snapshot_id", "invoice_state", "myinvois_status", "data_health_status")
MYINVOIS_SNAPSHOT_COLUMNS = ("id", "service_month", "final_invoice_amount", "source_values")
MYINVOIS = Part(
    key="myinvois_counts.ripple_myinvois", db="ripple", label="Ripple MyInvois list and submissions",
    example_label="submission",
    variants=(
        Variant(
            requires={
                "revenue_invoices": MYINVOIS_INVOICE_COLUMNS,
                "revenue_invoice_snapshots": MYINVOIS_SNAPSHOT_COLUMNS,
                "revenue_myinvois_submissions": ("id", "status", "company_code"),
            },
            sql=myinvois_sql("coalesce(ris.source_values->>'companyCode', 'sifu_edu_learning')",
                             "coalesce(company_code, 'sifu_edu_learning')"),
        ),
        Variant(
            requires={
                "revenue_invoices": MYINVOIS_INVOICE_COLUMNS,
                "revenue_invoice_snapshots": MYINVOIS_SNAPSHOT_COLUMNS,
                "revenue_myinvois_submissions": ("id", "status"),
            },
            sql=myinvois_sql("'sifu_edu_learning'", "'sifu_edu_learning'"),
            basis=BEFORE_GO_LIVE_RIPPLE,
        ),
    ),
)

SIGNALS: tuple[Signal, ...] = (
    Signal("unmatched_payments", "Unmatched payments", (UNMATCHED_GATEWAY_RECEIPTS, UNMATCHED_BANK_SUSPENSE),
           count_label=("payment", "payments")),
    Signal("callback_mismatches", "Callback mismatches (amount or company)", (CALLBACK_MISMATCHES,),
           count_label=("attempt", "attempts")),
    Signal("failed_credit_allocation", "Failed credit allocation", (CROSS_COMPANY_CREDIT, FEE_ALLOCATIONS),
           count_label=("record", "records"),
           note="read from credit moved across companies and failed fee allocations; no single failure record exists"),
    Signal("rejected_clock_ins", "Rejected clock-ins (holds)", (HOLDS,), money=False, count_label=("hold blocking", "holds blocking"),
           note="refusals of old Tutor App builds are not stored in any database; watch Sentry for them"),
    Signal("followup_cases_72h", "Open follow-up cases older than 72 hours", (FOLLOWUPS,), money=False,
           count_label=("case", "cases")),
    Signal("extra_charges_waiting", "Extra charges waiting more than one month end", (EXTRA_CHARGES,),
           count_label=("charge", "charges")),
    Signal("payout_differences", "Payout differences, approved selection vs bank file", (PAYOUTS,),
           count_label=("file differs", "files differ")),
    Signal("carried_deductions", "Carried-forward deductions", (CARRIED,), count_label=("waiting", "waiting"),
           note="CHECK only when one has waited more than 35 days"),
    Signal("quickbooks_sync_failures", "QuickBooks sync failures", (QUICKBOOKS,), count_label=("record", "records")),
    Signal("owed_to_nakngaji", "Owed to Nakngaji vs recorded transfers", (OWED,), count_label=("month without a confirmed transfer", "months without a confirmed transfer"),
           companies=(NAK,)),
    Signal("myinvois_counts", "MyInvois list counts", (MYINVOIS,), money=False, count_label=("failed submission", "failed submissions")),
)


# ---------------------------------------------------------------------------------------------------------------
# Parsing and formatting

def format_money(sen: int) -> str:
    sign = "-" if sen < 0 else ""
    whole, cents = divmod(abs(sen), 100)
    return f"{sign}RM{whole:,}.{cents:02d}"


def parse_sen(value) -> int:
    if value is None or str(value).strip() in ("", "NULL"):
        return 0
    try:
        number = Decimal(str(value).strip())
    except InvalidOperation as exc:
        raise QueryError(f"not a number: {value!r}") from exc
    if number != number.to_integral_value():
        raise QueryError(f"amount is not in whole sen: {value!r}")
    return int(number)


def parse_int(value) -> int:
    return parse_sen(value)


def normalise_company(value) -> str:
    if value is None:
        return UNRECORDED
    code = str(value).strip()
    code = BRAND_TO_COMPANY.get(code, code)
    return code if code in (SIFU, NAK) else UNRECORDED


def parse_tsv(text: str) -> list[dict]:
    lines = [line for line in text.splitlines() if line.strip()]
    for line in lines:
        if line.startswith("ERROR") or line.startswith("refused:"):
            raise QueryError(line[:200])
    if not lines:
        return []
    header = lines[0].split("\t")
    rows = []
    for line in lines[1:]:
        values = [None if v == "NULL" else v for v in line.split("\t")]
        rows.append(dict(zip(header, values)))
    return rows


def parse_csv(text: str) -> list[dict]:
    reader = csv.DictReader(io.StringIO(text))
    return [{k: (None if v == "" and k == "company" else v) for k, v in r.items()} for r in reader]


def schema_sql(db: str, tables: list[str]) -> str:
    names = ", ".join(f"'{t}'" for t in sorted(tables))
    if db == "sims":
        return ("SELECT TABLE_NAME AS t, COLUMN_NAME AS c FROM information_schema.COLUMNS "
                f"WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME IN ({names})")
    return ("SELECT table_name AS t, column_name AS c FROM information_schema.columns "
            f"WHERE table_schema = 'public' AND table_name IN ({names})")


def all_queries(db: str):
    for signal in SIGNALS:
        for part in signal.parts:
            if part.db == db:
                for variant in part.variants:
                    yield variant.sql, part.key


def tables_for(db: str) -> list[str]:
    names = set()
    for signal in SIGNALS:
        for part in signal.parts:
            if part.db == db:
                for variant in part.variants:
                    names.update(variant.requires)
    return sorted(names)


# ---------------------------------------------------------------------------------------------------------------
# Runner: the real one calls the read-only wrappers; tests pass a fake with the same two methods.

class WrapperRunner:
    def __init__(self, timeout: int = 150):
        self.timeout = timeout

    def _run(self, db: str, sql: str) -> list[dict]:
        if db == "sims":
            cmd = [str(ACCESS / "sims-db-readonly-sql.sh"), sql]
            env = dict(os.environ)
        else:
            cmd = [str(ACCESS / "ripple-prod-sql-readonly.sh"), sql]
            env = dict(os.environ, RIPPLE_PROD_SQL_FORMAT="csv", LC_ALL="C")
        try:
            done = subprocess.run(cmd, capture_output=True, text=True, timeout=self.timeout, env=env)
        except subprocess.TimeoutExpired as exc:
            raise QueryError("timed out") from exc
        if done.returncode != 0:
            lines = [l for l in done.stderr.splitlines() if l.strip() and not l.startswith(("perl:", "\t", "  ", "are supported"))]
            raise QueryError((lines[-1] if lines else f"exit {done.returncode}")[:200])
        return parse_tsv(done.stdout) if db == "sims" else parse_csv(done.stdout)

    def columns(self, db: str, tables: list[str]) -> dict[str, set[str]]:
        found: dict[str, set[str]] = {}
        for r in self._run(db, schema_sql(db, tables)):
            found.setdefault(r["t"], set()).add(r["c"])
        return found

    def query(self, db: str, sql: str, key: str) -> list[dict]:
        return self._run(db, sql)


# ---------------------------------------------------------------------------------------------------------------
# Building the report

@dataclass
class CompanyLine:
    status: str = "OK"
    count: int = 0
    amount_sen: int = 0
    examples: list[str] = field(default_factory=list)
    info: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)


@dataclass
class SignalResult:
    signal: Signal
    companies: dict[str, CompanyLine]


@dataclass
class Report:
    run_at: datetime
    results: list[SignalResult]
    unreadable: list[str]


def missing_for(variant: Variant, schema: dict[str, set[str]]) -> list[str]:
    missing = []
    for table, columns in variant.requires.items():
        if table not in schema:
            missing.append(table)
            continue
        missing.extend(f"{table}.{c}" for c in columns if c not in schema[table])
    return missing


def info_text(key: str, value) -> str:
    if key.endswith("_sen"):
        return f"{key[:-4]}_amount={format_money(parse_sen(value))}"
    return f"{key}={parse_int(value):,}"


def evaluate(signal: Signal, schemas: dict[str, dict[str, set[str]] | None], runner) -> SignalResult:
    lines = {c: CompanyLine() for c in signal.companies}
    ran = False
    problems: dict[str, bool] = {}
    part_notes: list[str] = []
    per_company_examples: dict[str, list[str]] = {}
    for part in signal.parts:
        schema = schemas.get(part.db)
        if schema is None:
            ran = True
            part_notes.append(f"{part.label}: query failed, {DB_NAMES[part.db]} could not be read")
            for c in lines:
                problems[c] = True
            continue
        variant = next((v for v in part.variants if not missing_for(v, schema)), None)
        if variant is None:
            missing = missing_for(part.variants[0], schema)
            part_notes.append(f"{part.label}: not deployed, missing {DB_NAMES[part.db]} " + ", ".join(missing))
            continue
        ran = True
        if variant.basis:
            part_notes.append(f"{part.label}: {variant.basis}")
        try:
            rows = runner.query(part.db, variant.sql, part.key)
        except QueryError as exc:
            part_notes.append(f"{part.label}: query failed, {exc}")
            for c in lines:
                problems[c] = True
            continue
        for r in rows:
            company = normalise_company(r.get("company"))
            if company not in lines:
                if company != UNRECORDED and parse_int(r.get("n")) == 0 and parse_sen(r.get("amount_sen")) == 0:
                    continue
                lines[company] = CompanyLine()
            line = lines[company]
            n = parse_int(r.get("n"))
            amount = parse_sen(r.get("amount_sen"))
            line.count += n
            line.amount_sen += amount
            if "needs_check" in r:
                flagged = parse_int(r.get("needs_check")) > 0
            else:
                flagged = n > 0 or amount != 0
            problems[company] = problems.get(company, False) or flagged
            ids = [i.strip() for i in (r.get("ex") or "").split(",") if i.strip()]
            prefix = f"{part.example_label} " if part.example_label else ""
            per_company_examples.setdefault(company, []).extend(prefix + i for i in ids)
            line.info.extend(info_text(k, v) for k, v in r.items() if k not in STANDARD_COLUMNS)
    for company, line in lines.items():
        if not ran:
            line.status = "NOT DEPLOYED"
        else:
            line.status = "CHECK" if problems.get(company) else "OK"
        line.examples = per_company_examples.get(company, [])[:5]
        line.notes = list(part_notes)
        if signal.note:
            line.notes.append(signal.note)
    return SignalResult(signal, lines)


def build_report(runner, now: datetime | None = None) -> Report:
    schemas: dict[str, dict[str, set[str]] | None] = {}
    unreadable = []
    for db in ("sims", "ripple"):
        try:
            schemas[db] = runner.columns(db, tables_for(db))
        except QueryError:
            schemas[db] = None
            unreadable.append(db)
    results = [evaluate(s, schemas, runner) for s in SIGNALS]
    return Report(now or datetime.now(MYT), results, unreadable)


# ---------------------------------------------------------------------------------------------------------------
# Output

def company_order(report: Report) -> list[str]:
    order = [SIFU, NAK]
    if any(UNRECORDED in r.companies for r in report.results):
        order.append(UNRECORDED)
    return order


def headline(result: SignalResult, line: CompanyLine) -> str:
    signal = result.signal
    if line.status == "NOT DEPLOYED":
        return signal.title
    text = f"{signal.title}: {line.count:,}"
    label = signal.count_label[0 if line.count == 1 else 1]
    if label:
        text += f" {label}"
    if signal.money:
        text += f", {format_money(line.amount_sen)}"
    return text


def render_text(report: Report) -> str:
    out = [
        "Nakngaji and Sifututor company monitor (WP-28), read only",
        f"Run at {report.run_at.astimezone(MYT).strftime('%d/%m/%Y %H:%M')} MYT. Sources: SIMS production (lane 4), "
        "Ripple production (lane 40). Record ids only, no personal data.",
    ]
    for db in report.unreadable:
        out.append(f"WARNING: {DB_NAMES[db]} could not be read; its signals show CHECK.")
    summary = []
    for company in company_order(report):
        out += ["", COMPANY_NAMES[company], "-" * len(COMPANY_NAMES[company])]
        counts = {"OK": 0, "CHECK": 0, "NOT DEPLOYED": 0}
        for result in report.results:
            line = result.companies.get(company)
            if line is None:
                continue
            counts[line.status] += 1
            out.append(f"  {line.status:<13} {headline(result, line)}")
            pad = " " * 16
            if line.examples:
                out.append(f"{pad}examples: {', '.join(line.examples)}")
            if line.info:
                out.append(f"{pad}{'; '.join(line.info)}")
        summary.append(f"{COMPANY_NAMES[company]}: OK {counts['OK']}, CHECK {counts['CHECK']}, "
                       f"NOT DEPLOYED {counts['NOT DEPLOYED']}")
    out += ["", "Notes (how each signal was read today)", "--------------------------------------"]
    for result in report.results:
        notes = next(iter(result.companies.values())).notes
        if notes:
            out.append(f"  {result.signal.title}")
            out += [f"    - {note}" for note in notes]
    out += ["", "Summary", *[f"  {s}" for s in summary]]
    return "\n".join(out) + "\n"


def render_json(report: Report) -> str:
    return json.dumps({
        "run_at_myt": report.run_at.astimezone(MYT).isoformat(timespec="seconds"),
        "unreadable": report.unreadable,
        "signals": [
            {
                "key": r.signal.key,
                "title": r.signal.title,
                "companies": {
                    c: {"status": l.status, "count": l.count, "amount_sen": l.amount_sen if r.signal.money else None,
                        "examples": l.examples, "info": l.info, "notes": l.notes}
                    for c, l in r.companies.items()
                },
            }
            for r in report.results
        ],
    }, indent=2)


def exit_code(report: Report) -> int:
    if report.unreadable:
        return 2
    if any(l.status == "CHECK" for r in report.results for l in r.companies.values()):
        return 1
    return 0


def main(argv: list[str] | None = None, runner=None) -> int:
    parser = argparse.ArgumentParser(description="Daily read-only monitor per company (WP-28).")
    parser.add_argument("--json", action="store_true", help="print JSON instead of text")
    args = parser.parse_args(argv)
    report = build_report(runner or WrapperRunner())
    sys.stdout.write(render_json(report) + "\n" if args.json else render_text(report))
    return exit_code(report)


if __name__ == "__main__":
    raise SystemExit(main())
