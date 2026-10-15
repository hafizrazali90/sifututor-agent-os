#!/usr/bin/env python3
"""Daily read-only money and work monitor per company (WP-28, Sifututor/sifu-tutor#3479).

Prints one report for Sifu Edu & Learning Sdn Bhd and Nakngaji Sdn Bhd with the thirteen go-live signals. Each signal
gives a count, an amount to the sen where money is involved, up to five example record ids and a status:
OK, CHECK, NOT DEPLOYED when the tables or columns one of its parts reads are not in production yet, or UNAVAILABLE
when one of its parts could not be read. A signal is OK only when every one of its parts was read and found nothing.
A before-go-live fallback reading is used only on a schema with none of the company columns; once one exists and the
full reading cannot run, the part is NOT DEPLOYED (company schema incomplete), never OK.

Database queries go through the existing read-only lanes, so this script never touches a database credential:
  - SIMS production: scripts/agent-access/sims-db-readonly-sql.sh (lane 4, SELECT-only account)
  - Ripple production: scripts/agent-access/ripple-prod-sql-readonly.sh (lane 40, forced read-only session)
Failures SIMS only logs are read from lane 14 (monitoring-readonly.conf): Sentry errors for the SIMS project, and the
Better Stack SIMS log source through its SQL query connection. Values from that file are used, never printed.
The report holds ids, counts and amounts only, never names, emails or phone numbers.

Usage:  scripts/agent-access/nakngaji-company-monitor.py [--json]
Exit:   0 every signal OK; 1 at least one CHECK or NOT DEPLOYED; 2 a database, a log lane or a query could not be read
"""

from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import io
import json
import math
import os
import re
import subprocess
import sys
import urllib.error
import urllib.parse
import urllib.request
from collections.abc import Callable
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
DATABASES = ("sims", "ripple")
LOG_SOURCES = ("sentry", "betterstack")
DB_NAMES = {"sims": "SIMS", "ripple": "Ripple", "sentry": "Sentry", "betterstack": "Better Stack"}
STATUSES = ("OK", "CHECK", "NOT DEPLOYED", "UNAVAILABLE")
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
    post: Callable[[list[dict]], list[dict]] | None = None  # turns raw rows into the standard columns
    # The company stamps a fallback reading ignores. Rule for every fallback that drops a company check or attributes
    # by the legacy rule: if any of these tables.columns is present the schema is a half-deployed go-live one, not the
    # legacy one, and this variant must not stand in for the full reading (NOT DEPLOYED, never OK). A fallback with
    # nothing here is only valid because the full reading differs from it by nothing but the company column itself.
    unless_present: dict[str, tuple[str, ...]] = field(default_factory=dict)


@dataclass(frozen=True)
class Part:
    key: str
    db: str
    label: str
    example_label: str
    variants: tuple[Variant, ...] = ()
    search: str = ""  # log parts: a Sentry search, or a ClickHouse condition on the Better Stack log line
    count_info: str = ""  # log parts: the info name for what they counted


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


# Company stamps on SIMS invoices and attempts, and on Ripple import batches and QuickBooks records. Their presence
# makes the before-go-live reading wrong even when the full reading cannot run (see Variant.unless_present).
SIMS_INVOICE_STAMPS = {
    "parent_invoices": ("brand_id", "legal_company_id"),
    "parent_payment_attempts": ("issuer_company_id",),
}
SIMS_CREDIT_STAMPS = {
    "parent_invoices": ("legal_company_id",),
    "referral_rewards": ("legal_company_id",),
}
RIPPLE_IMPORT_BATCH_STAMPS = {"import_batches": ("company_code",)}
RIPPLE_QB_STAMPS = {"pv_vouchers": ("company_code",), "qb_destinations": ("company_code",)}


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
            unless_present=SIMS_INVOICE_STAMPS,
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
            unless_present=RIPPLE_IMPORT_BATCH_STAMPS,
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
            unless_present=SIMS_INVOICE_STAMPS,
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
            unless_present=SIMS_CREDIT_STAMPS,
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
            unless_present=RIPPLE_IMPORT_BATCH_STAMPS,
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
# 7. Payout differences between the approved selection and the bank file (Ripple, last 45 days of files).
#    Each file's total, count and paying company are compared with its linked payments. A company file (one made
#    with a paying company, WP-16) must also carry its selection fingerprint, and every payment in it must match the
#    latest approval: the fingerprint is recomputed here from the source records with Ripple's own rules
#    (tutor-payments/lib/company-payments.ts slipSelectionFingerprint and fileSelectionFingerprint), never trusted.

def js_number(value) -> float:
    """JavaScript Number(value) for the values the fingerprint reads."""
    if value is None:
        return 0.0
    if isinstance(value, bool):
        return float(value)
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if text == "":
        return 0.0
    try:
        return float(text) if text.lower().lstrip("+-") not in ("inf", "infinity", "nan") else math.nan
    except ValueError:
        return math.nan


def js_round(value: float):
    """JavaScript Math.round (halves go up); NaN and infinities become null as JSON.stringify writes them."""
    if math.isnan(value) or math.isinf(value):
        return None
    low = math.floor(value)
    return int(low + 1 if value - low >= 0.5 else low)


def js_integer(value):
    number = js_number(value)
    if math.isnan(number) or math.isinf(number):
        return None
    return int(number) if number.is_integer() else number


def js_sen(value):
    return js_round(js_number(value) * 100)


def slip_selection_fingerprint(selection: dict) -> str:
    """Ripple's slipSelectionFingerprint: payer, class lines, bonus shares, notes and net, in sen, in a fixed order."""
    classes = sorted(([js_integer(c[0]), js_sen(c[1])] for c in selection["classes"]), key=lambda c: c[0] or 0)
    bonuses = sorted(([js_integer(b[0]), js_sen(b[1])] for b in selection["bonuses"]),
                     key=lambda b: (b[0] or 0, b[1] or 0))
    notes = sorted(([js_integer(n[0]), str(n[1]), js_sen(n[2])] for n in selection["notes"]), key=lambda n: n[0] or 0)
    canonical = {
        "slip_id": selection["slip_id"],
        "tutor_id": selection["tutor_id"],
        "payer_company_code": selection.get("payer_company_code"),
        "net_sen": js_sen(selection["net_amount"]),
        "classes": classes,
        "bonuses": bonuses,
        "notes": notes,
    }
    return hashlib.sha256(json.dumps(canonical, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()


def file_selection_fingerprint(slip_fingerprints: list[str]) -> str:
    """Ripple's fileSelectionFingerprint: the sorted fingerprints of the file's payments."""
    return hashlib.sha256(json.dumps(sorted(slip_fingerprints), separators=(",", ":")).encode()).hexdigest()


def sen_exact(value) -> int:
    number = Decimal(str(value).strip()) * 100
    if number != number.to_integral_value():
        raise QueryError(f"amount is not in whole sen: {value!r}")
    return int(number)


PAYOUT_COUNTERS = ("payments_changed_since_approval", "approvals_missing", "file_fingerprints_missing",
                   "file_fingerprints_differ")


def payout_rows(rows: list[dict]) -> list[dict]:
    """One raw row per payment in each file (a file with no payments has one row with no slip_id) -> per company:
    n = files that differ, amount = total of those files, ex = their ids, and what was checked."""
    files: dict[int, dict] = {}
    company_files = "file_company" in (rows[0] if rows else {})
    for r in rows:
        f = files.setdefault(int(r["batch_id"]), {"row": r, "slips": []})
        if r.get("slip_id") not in (None, ""):
            f["slips"].append(r)
    out: dict[str, dict] = {}
    for batch_id in sorted(files, reverse=True):
        f = files[batch_id]
        head, slips = f["row"], f["slips"]
        file_company = head.get("file_company") or None
        company = file_company or SIFU
        agg = out.setdefault(company, {"company": company, "n": 0, "amount_sen": 0, "ex": [], "files_checked": 0,
                                       **({k: 0 for k in PAYOUT_COUNTERS} if company_files else {})})
        agg["files_checked"] += 1
        total = sen_exact(head["total_amount"])
        differs = total != sum(sen_exact(s["net_amount"]) for s in slips) or parse_int(head["slip_count"]) != len(slips)
        if company_files:
            differs |= any((s.get("slip_company") or None) != file_company for s in slips)
        if company_files and file_company is not None:
            file_fingerprint = head.get("file_fingerprint") or None
            if file_fingerprint is None:
                agg["file_fingerprints_missing"] += 1
                differs = True
            fingerprints = []
            for s in slips:
                fingerprint = slip_selection_fingerprint({
                    "slip_id": int(s["slip_id"]),
                    "tutor_id": js_integer(s["tutor_id"]),
                    "payer_company_code": s.get("slip_company") or None,
                    "net_amount": s["net_amount"],
                    "classes": json.loads(s.get("classes") or "[]"),
                    "bonuses": json.loads(s.get("bonuses") or "[]"),
                    "notes": json.loads(s.get("notes") or "[]"),
                })
                fingerprints.append(fingerprint)
                approved = s.get("approved_fingerprint") or None
                if approved is None:
                    agg["approvals_missing"] += 1
                    differs = True
                elif approved != fingerprint:
                    agg["payments_changed_since_approval"] += 1
                    differs = True
            if file_fingerprint is not None and file_selection_fingerprint(fingerprints) != file_fingerprint:
                agg["file_fingerprints_differ"] += 1
                differs = True
        if differs:
            agg["n"] += 1
            agg["amount_sen"] += total
            agg["ex"].append(str(batch_id))
    return [dict(a, ex=",".join(a["ex"][:5])) for a in out.values()]


PAYOUT_WINDOW = "b.status <> 'superseded' AND b.created_at > now() - interval '45 days'"
PAYOUT_SELECTION = """CASE WHEN b.payer_company_code IS NOT NULL AND s.id IS NOT NULL THEN (
         SELECT coalesce(json_agg(json_build_array(c.sims_class_id, coalesce(c.resolved_amount, c.sims_commission)::text)), '[]')
           FROM tutor_slip_classes c WHERE c.slip_id = s.id AND c.class_status = 'included') END AS classes,
       CASE WHEN b.payer_company_code IS NOT NULL AND s.id IS NOT NULL THEN (
         SELECT coalesce(json_agg(json_build_array(
                  CASE WHEN e ? 'sims_bonus_id' THEN e->'sims_bonus_id' ELSE '"undefined"'::jsonb END,
                  CASE WHEN e ? 'amount' THEN e->'amount' ELSE '"undefined"'::jsonb END)), '[]')
           FROM jsonb_array_elements(CASE WHEN jsonb_typeof(s.bonus_details) = 'array' THEN s.bonus_details ELSE '[]'::jsonb END) e
          WHERE e->>'action' = 'included') END AS bonuses,
       CASE WHEN b.payer_company_code IS NOT NULL AND s.id IS NOT NULL THEN (
         SELECT coalesce(json_agg(json_build_array(n.id, n.type, n.amount::text)), '[]')
           FROM tutor_payment_notes n WHERE n.slip_id = s.id AND n.note_status = 'approved') END AS notes,
       (SELECT l.details->>'selection_fingerprint' FROM tutor_payment_audit_log l
         WHERE l.slip_id = s.id AND l.action IN ('slip_approved', 'payment_approved')
         ORDER BY l.id DESC LIMIT 1) AS approved_fingerprint"""

PAYOUTS = Part(
    key="payout_differences.ripple_bank_files", db="ripple", label="Ripple tutor payment bank files",
    example_label="bank file batch",
    variants=(
        Variant(
            requires={
                "tutor_payment_csv_batches": ("id", "status", "created_at", "total_amount", "slip_count",
                                              "payer_company_code", "selection_fingerprint"),
                "tutor_payment_slips": ("id", "tutor_id", "csv_batch_id", "net_amount", "payer_company_code",
                                        "bonus_details"),
                "tutor_slip_classes": ("slip_id", "sims_class_id", "resolved_amount", "sims_commission", "class_status"),
                "tutor_payment_notes": ("id", "slip_id", "type", "amount", "note_status"),
                "tutor_payment_audit_log": ("id", "slip_id", "action", "details"),
            },
            sql=f"""SELECT b.id AS batch_id, b.payer_company_code AS file_company, b.total_amount::text AS total_amount,
       b.slip_count, b.selection_fingerprint AS file_fingerprint,
       s.id AS slip_id, s.tutor_id, s.payer_company_code AS slip_company, s.net_amount::text AS net_amount,
       {PAYOUT_SELECTION}
FROM tutor_payment_csv_batches b
LEFT JOIN tutor_payment_slips s ON s.csv_batch_id = b.id
WHERE {PAYOUT_WINDOW}
ORDER BY b.id, s.id""",
            post=payout_rows,
        ),
        Variant(
            requires={
                "tutor_payment_csv_batches": ("id", "status", "created_at", "total_amount", "slip_count"),
                "tutor_payment_slips": ("id", "csv_batch_id", "net_amount"),
            },
            sql=f"""SELECT b.id AS batch_id, b.total_amount::text AS total_amount, b.slip_count,
       s.id AS slip_id, s.net_amount::text AS net_amount
FROM tutor_payment_csv_batches b
LEFT JOIN tutor_payment_slips s ON s.csv_batch_id = b.id
WHERE {PAYOUT_WINDOW}
ORDER BY b.id, s.id""",
            basis=BEFORE_GO_LIVE_RIPPLE + "; totals and counts only, no approved fingerprint yet",
            post=payout_rows,
            unless_present={
                "tutor_payment_csv_batches": ("payer_company_code", "selection_fingerprint"),
                "tutor_payment_slips": ("payer_company_code",),
            },
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
            unless_present=RIPPLE_QB_STAMPS,
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

# ---------------------------------------------------------------------------------------------------------------
# 12. A Nakngaji invoice (NINV- number) whose Tutor Request has no brand. Brand lists are built from the request's
#     brand, so such a paid invoice sits in neither list while every other signal stays healthy (AUTO-DECISIONS CLEANUP-4).
#     NINV numbers are only issued for Nakngaji requests, so the company is Nakngaji by the number.

INVOICES_WITHOUT_BRAND = Part(
    key="invoices_without_brand.sims_invoices", db="sims", label="SIMS Nakngaji invoices without a brand",
    example_label="invoice",
    variants=(
        Variant(
            requires={
                "parent_invoices": ("id", "request_id", "invoice_number", "invoice_total", "deleted_at"),
                "tutor_requests": ("id", "brand_id"),
                "brands": ("id",),
            },
            sql=f"""SELECT 'nakngaji_sdn_bhd' AS company,
       COUNT(*) AS n, {sims_sen('pi.invoice_total')} AS amount_sen,
       SUBSTRING_INDEX(GROUP_CONCAT(pi.id ORDER BY pi.id DESC), ',', 5) AS ex
FROM parent_invoices pi
LEFT JOIN tutor_requests tr ON tr.id = pi.request_id
LEFT JOIN brands b ON b.id = tr.brand_id
WHERE pi.deleted_at IS NULL AND pi.invoice_number LIKE 'NINV-%'
  AND (tr.id IS NULL OR tr.brand_id IS NULL OR b.id IS NULL)
GROUP BY company""",
        ),
    ),
)

# ---------------------------------------------------------------------------------------------------------------
# Failures SIMS only logs (no table holds them). SIMS sends exceptions to Sentry but not its log lines (14 days of
# events on 15/10/2026: every one an exception, no log-channel events), so refusals and caught errors are read from
# the Better Stack SIMS log source. Each search covers the last 24 hours. The company comes from the company_code SIMS
# writes in the log context (CLEANUP-6, d50c8db92), then from the NINV-/PINV- prefix of the order id, order_id or
# invoice_number (NINV- is Nakngaji, PINV- is Sifu Edu & Learning); otherwise "Company not recorded".

def log_message_has(*phrases: str) -> str:
    return "(" + " OR ".join(f"positionCaseInsensitive(msg, '{p}') > 0" for p in phrases) + ")"


REFUSED_CALLBACKS = Part(
    key="callback_mismatches.betterstack_refused_callbacks", db="betterstack",
    label="Better Stack SIMS logs: FIUU callbacks refused for merchant, amount or company",
    example_label="invoice reference", count_info="refused_callbacks_logged",
    # PaymentController handleCallback / handleNotify log every refusal once, with the reason in context.result.
    search=(log_message_has("CALLBACK: Processing failed", "NOTIFY: Processing failed")
            + " AND match(lower(JSONExtractRaw(raw, 'monolog', 'context', 'result')), 'merchant|amount|company')"),
)
REFERRAL_ALLOCATION_LOGS = Part(
    key="failed_credit_allocation.betterstack_referral_allocation_errors", db="betterstack",
    label="Better Stack SIMS logs: pending referral credit allocation failed", example_label="invoice",
    count_info="allocation_errors_logged",
    # ParentInvoiceObserver::created and ClassService invoice activation catch the exception and log it.
    search=log_message_has("Pending referral credit allocation failed"),
)
REFERRAL_ALLOCATION_EXCEPTIONS = Part(
    key="failed_credit_allocation.sentry_referral_allocation_exceptions", db="sentry",
    label="Sentry SIMS errors: referral credit allocation exceptions", example_label="Sentry issue",
    count_info="allocation_exceptions",
    # EvaluateReferralBonus calls the allocation without a catch, so its exceptions reach Sentry.
    search='stack.function:"*allocatePendingForParent*"',
)
# The Tutor App actions that are a clock-in or class start: POST api/tutor/class/attendance and its bulk form. SIMS
# logs the action as "<METHOD> <route template>" (nakngaji_app_refused). Any other refused action is not a clock-in.
CLOCK_IN_ACTION_PATTERN = "^POST api/tutor/class/attendance(/bulk)?$"
_ACTION = "JSONExtractString(raw, 'monolog', 'context', 'action')"
# Both old-app signals: the answer text (responseCode 104) and the update-required code, plus the structured event.
OLD_BUILD_REFUSAL_LINE = (
    "(positionCaseInsensitive(raw, 'Please update the Tutor App') > 0 OR position(raw, 'APP_UPDATE_REQUIRED') > 0"
    " OR (position(raw, 'nakngaji_app_refused') > 0 AND JSONExtractString(raw, 'monolog', 'context', 'app') = 'tutor'))"
)
_SENTRY_OLD_BUILD = 'message:"*update the Tutor App*" OR message:"*APP_UPDATE_REQUIRED*"'
_SENTRY_CLOCK_IN_URL = 'url:"*/api/tutor/class/attendance" OR url:"*/api/tutor/class/attendance/bulk"'
OLD_BUILD_REFUSAL_LOGS = Part(
    key="rejected_clock_ins.betterstack_old_build_refusals", db="betterstack",
    label="Better Stack SIMS logs: clock-ins refused for an old Tutor App build", example_label="invoice reference",
    count_info="old_build_refusals_logged",
    search=f"{OLD_BUILD_REFUSAL_LINE} AND match({_ACTION}, '{CLOCK_IN_ACTION_PATTERN}')",
)
OLD_BUILD_REFUSAL_EVENTS = Part(
    key="rejected_clock_ins.sentry_old_build_refusals", db="sentry",
    label="Sentry SIMS errors: clock-ins refused for an old Tutor App build", example_label="Sentry issue",
    count_info="old_build_refusal_events",
    search=f"({_SENTRY_OLD_BUILD}) AND ({_SENTRY_CLOCK_IN_URL})",
)
OTHER_OLD_BUILD_REFUSAL_LOGS = Part(
    key="other_old_build_refusals.betterstack_old_build_refusals", db="betterstack",
    label="Better Stack SIMS logs: other Tutor App actions refused for an old build", example_label="invoice reference",
    count_info="other_old_build_refusals_logged",
    search=f"{OLD_BUILD_REFUSAL_LINE} AND NOT match({_ACTION}, '{CLOCK_IN_ACTION_PATTERN}')",
)
OTHER_OLD_BUILD_REFUSAL_EVENTS = Part(
    key="other_old_build_refusals.sentry_old_build_refusals", db="sentry",
    label="Sentry SIMS errors: other Tutor App actions refused for an old build", example_label="Sentry issue",
    count_info="other_old_build_refusal_events",
    search=f"({_SENTRY_OLD_BUILD}) AND !({_SENTRY_CLOCK_IN_URL})",
)

SIGNALS: tuple[Signal, ...] = (
    Signal("unmatched_payments", "Unmatched payments", (UNMATCHED_GATEWAY_RECEIPTS, UNMATCHED_BANK_SUSPENSE),
           count_label=("payment", "payments")),
    Signal("callback_mismatches", "Callback mismatches (amount, merchant or company)", (CALLBACK_MISMATCHES, REFUSED_CALLBACKS),
           count_label=("attempt or refused callback", "attempts or refused callbacks"),
           note="money is from the payment attempts; refused callbacks are counted from the logs"),
    Signal("failed_credit_allocation", "Failed credit allocation",
           (CROSS_COMPANY_CREDIT, FEE_ALLOCATIONS, REFERRAL_ALLOCATION_LOGS, REFERRAL_ALLOCATION_EXCEPTIONS),
           count_label=("record", "records"),
           note="read from credit moved across companies, failed fee allocations and logged allocation errors; "
                "no single failure record exists"),
    Signal("rejected_clock_ins", "Rejected clock-ins (holds and old-build refusals)",
           (HOLDS, OLD_BUILD_REFUSAL_LOGS, OLD_BUILD_REFUSAL_EVENTS), money=False,
           count_label=("hold or refusal", "holds or refusals"),
           note="old-build refusals are not stored in any database, so they are read from the logs; only a refusal "
                "whose logged action is a clock-in (class attendance) is counted here"),
    Signal("other_old_build_refusals", "Other old-build refusals (not clock-ins)",
           (OTHER_OLD_BUILD_REFUSAL_LOGS, OTHER_OLD_BUILD_REFUSAL_EVENTS), money=False,
           count_label=("refusal", "refusals"),
           note="other Tutor App actions refused for an old build (a refusal with no logged action lands here too)"),
    Signal("invoices_without_brand", "Nakngaji invoices whose Tutor Request has no brand", (INVOICES_WITHOUT_BRAND,),
           count_label=("invoice", "invoices"), companies=(NAK,),
           note="a NINV- invoice with no brand on its Tutor Request shows in neither brand list"),
    Signal("followup_cases_72h", "Open follow-up cases older than 72 hours", (FOLLOWUPS,), money=False,
           count_label=("case", "cases")),
    Signal("extra_charges_waiting", "Extra charges waiting more than one month end", (EXTRA_CHARGES,),
           count_label=("charge", "charges")),
    Signal("payout_differences", "Payout differences, approved selection vs bank file", (PAYOUTS,),
           count_label=("file differs", "files differ"), note="the amount is the total of the bank files that differ"),
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


# The only strings a log example may show: a record reference SIMS itself generates. Character classes only (no
# backslash), so the same text is a valid Python and ClickHouse (RE2) pattern. Shapes come from the SIMS code:
# ParentInvoiceNumber (PINV- digits, NINV- seven or more digits, a numbered try -2, a bundle joined by +),
# CommitmentFeeNumber (NCF- seven or more digits, PCF- twelve upper-case letters or digits, the old PCF- four digits,
# PCF-BACKFILL-<request>), the attempt references PBA-/PCFA-/TCFA-/TAPA- plus a ULID, and PIR- recovery references.
_INVOICE_NUMBER = "(?:PINV-[0-9]{1,10}|NINV-[0-9]{7,10})(?:-[0-9]{1,3})?"
_ULID = "[0-9a-hjkmnp-tv-zA-HJKMNP-TV-Z]{26}"
REFERENCE_PATTERN = (
    f"{_INVOICE_NUMBER}(?:[+]{_INVOICE_NUMBER})*"
    "|NCF-[0-9]{7,10}"
    "|PCF-(?:[A-Z0-9]{12}|[0-9]{4}|BACKFILL-[0-9]{1,10})"
    f"|(?:PBA|PCFA|TCFA|TAPA)-{_ULID}"
    "|PIR-(?:[0-9a-f]{28}|[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12})"
)
REFERENCE_SQL_PATTERN = f"^(?:{REFERENCE_PATTERN})$"
RECORD_ID_PATTERN = "[1-9][0-9]{0,8}"  # parent_invoice_id only: a database id, never user text
_REFERENCE = re.compile(REFERENCE_SQL_PATTERN)
_RECORD_ID = re.compile(f"^{RECORD_ID_PATTERN}$")
REFERENCE_FIELDS = ("orderid", "order_id", "invoice_number")  # in the order an example and a prefix are taken
LOG_COMPANY_VALUES = (SIFU, NAK, *BRAND_TO_COMPANY)


def is_record_reference(value) -> bool:
    return isinstance(value, str) and _REFERENCE.fullmatch(value) is not None


def log_company(company_code, ref_company) -> str | None:
    """A log line's company: the company_code in its context first, then the invoice-reference prefix."""
    for value in (company_code, ref_company):
        code = BRAND_TO_COMPANY.get(str(value or "").strip(), str(value or "").strip())
        if code in (SIFU, NAK):
            return code
    return None


def log_reference(row: dict) -> tuple[str, str | None]:
    """(example reference, company named by an invoice-number prefix) of one log row, from validated fields only.
    The reference is the first valid of orderid, order_id, invoice_number, parent_invoice_id; the prefix is read from
    the first of the first three that starts with NINV- or PINV-, so CLEANUP-6's invoice_number counts."""
    values = [str(row.get(k) or "").strip() for k in REFERENCE_FIELDS]
    valid = [v for v in values if is_record_reference(v)]
    parent = str(row.get("parent_invoice_id") or "").strip()
    if _RECORD_ID.fullmatch(parent):
        valid.append(parent)
    company = next((NAK if v.startswith("NINV-") else SIFU for v in valid if v.startswith(("NINV-", "PINV-"))), None)
    return (valid[0] if valid else ""), company


def resolve_log_rows(rows: list[dict]) -> list[dict]:
    """Better Stack rows per distinct (company_code, references) -> one row per company, counts summed. Examples are
    validated here as well as in the query; a count is always kept, even when its reference is dropped."""
    merged: dict[str | None, dict] = {}
    for r in rows:
        reference, prefix_company = log_reference(r)
        company = log_company(r.get("company_code"), prefix_company)
        out = merged.setdefault(company, {"company": company, "n": 0, "amount_sen": "0", "ex": []})
        out["n"] += parse_int(r.get("n"))
        if reference:
            out["ex"].append(reference)
    return [{**m, "n": str(m["n"]), "ex": ",".join(dict.fromkeys(m["ex"]))} for m in merged.values()]


def betterstack_sql(table: str, condition: str) -> str:
    """Counts matching SIMS log lines of the last day per company and reference; recent and archived rows, as Better
    Stack documents. Each reference field is blanked unless it is a validated record reference, so an arbitrary
    string a callback carried (an email, a phone number) never leaves Better Stack; the company is blanked unless
    it is one of ours."""
    window = "dt >= now() - INTERVAL 1 DAY"
    companies = ", ".join(f"'{c}'" for c in LOG_COMPANY_VALUES)

    def clean(column: str) -> str:
        return f"match({column}, '{REFERENCE_SQL_PATTERN}')"

    return f"""SELECT company_code, orderid, order_id, invoice_number, parent_invoice_id, count() AS n
FROM (
  SELECT if(c IN ({companies}), c, '') AS company_code,
         if({clean('o')}, o, '') AS orderid,
         if({clean('oi')}, oi, '') AS order_id,
         if({clean('i')}, i, '') AS invoice_number,
         if(match(p, '^{RECORD_ID_PATTERN}$'), p, '') AS parent_invoice_id
  FROM (
    SELECT JSONExtractString(raw, 'monolog', 'context', 'company_code') AS c,
           JSONExtractString(raw, 'monolog', 'context', 'orderid') AS o,
           JSONExtractString(raw, 'monolog', 'context', 'order_id') AS oi,
           JSONExtractString(raw, 'monolog', 'context', 'invoice_number') AS i,
           toString(JSONExtractInt(raw, 'monolog', 'context', 'parent_invoice_id')) AS p
    FROM (
      SELECT raw, JSONExtractString(raw, 'message') AS msg FROM remote({table}_logs) WHERE {window}
      UNION ALL
      SELECT raw, JSONExtractString(raw, 'message') AS msg FROM s3Cluster(primary, {table}_s3) WHERE _row_type = 1 AND {window}
    )
    WHERE {condition}
  )
)
GROUP BY company_code, orderid, order_id, invoice_number, parent_invoice_id
FORMAT JSONEachRow"""


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

MONITORING_CONF = ".config/sifututor/agent-access/monitoring-readonly.conf"
BETTERSTACK_QUERY_KEYS = ("BETTERSTACK_QUERY_HOST", "BETTERSTACK_QUERY_USERNAME", "BETTERSTACK_QUERY_PASSWORD",
                          "BETTERSTACK_SIMS_LOGS_TABLE")
SENTRY_KEYS = ("SENTRY_AUTH_TOKEN", "SENTRY_ORG_SLUG", "SENTRY_PROJECT_SLUG")
SENTRY_HOST = "https://de.sentry.io"  # the organisation lives in the EU region


class WrapperRunner:
    def __init__(self, timeout: int = 150, home: Path | None = None):
        self.timeout = timeout
        self.home = home or Path.home()
        self._conf: dict[str, str] | None = None
        self._sentry_project_id: str | None = None

    # Lane 14. Values are only ever passed to the API; error messages name keys, never values.
    def conf(self) -> dict[str, str]:
        if self._conf is None:
            path = self.home / MONITORING_CONF
            if not path.is_file():
                raise QueryError(f"lane 14 file ~/{MONITORING_CONF} is missing")
            values = {}
            for raw in path.read_text().splitlines():
                line = raw.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    values[key.strip().removeprefix("export ").strip()] = value.strip().strip('"').strip("'")
            self._conf = values
        return self._conf

    def _need(self, keys: tuple[str, ...], what: str) -> dict[str, str]:
        conf = self.conf()
        missing = [k for k in keys if not conf.get(k)]
        if missing:
            raise QueryError(f"lane 14 has no {what}; missing " + ", ".join(missing))
        return conf

    def _http(self, url: str, headers: dict[str, str], body: str | None = None) -> tuple[int, str]:
        request = urllib.request.Request(url, headers=headers, data=body.encode() if body is not None else None,
                                         method="POST" if body is not None else "GET")
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return response.status, response.read().decode()
        except urllib.error.HTTPError as exc:
            return exc.code, ""
        except (OSError, urllib.error.URLError) as exc:
            raise QueryError(f"could not connect ({type(exc).__name__})") from exc

    def _sentry(self, path: str, params: list[tuple[str, str]] | None = None):
        conf = self._need(SENTRY_KEYS, "Sentry read token")
        url = f"{SENTRY_HOST}/api/0/organizations/{conf['SENTRY_ORG_SLUG']}/{path}"
        if params:
            url += "?" + urllib.parse.urlencode(params)
        status, text = self._http(url, {"Authorization": f"Bearer {conf['SENTRY_AUTH_TOKEN']}",
                                        "Accept": "application/json"})
        if status != 200:
            raise QueryError(f"Sentry answered HTTP {status}")
        try:
            return json.loads(text)
        except json.JSONDecodeError as exc:
            raise QueryError("Sentry answer is not JSON") from exc

    def probe(self, source: str) -> None:
        if source == "sentry":
            slug = self._need(SENTRY_KEYS, "Sentry read token")["SENTRY_PROJECT_SLUG"]
            projects = self._sentry("projects/")
            found = [p for p in projects if isinstance(p, dict) and p.get("slug") == slug]
            if not found:
                raise QueryError(f"Sentry project {slug} not found")
            self._sentry_project_id = str(found[0]["id"])
        elif source == "betterstack":
            self._need(BETTERSTACK_QUERY_KEYS, "Better Stack query connection (Better Stack > Integrations > "
                                               "ClickHouse HTTP client, read only)")
        else:
            raise QueryError(f"unknown source {source}")

    def logs(self, source: str, search: str, key: str) -> list[dict]:
        if source == "sentry":
            base = [("dataset", "errors"), ("field", "count()"), ("project", self._sentry_project_id or ""),
                    ("statsPeriod", "24h"), ("query", search)]
            data = self._sentry("events/", base).get("data") or [{}]
            n = parse_int(data[0].get("count()"))
            if n == 0:
                return []
            top = self._sentry("events/", [("dataset", "errors"), ("field", "issue"), ("field", "count()"),
                                           ("project", self._sentry_project_id or ""), ("statsPeriod", "24h"),
                                           ("query", search), ("sort", "-count()"), ("per_page", "5")])
            issues = [str(r.get("issue")) for r in top.get("data") or [] if r.get("issue")]
            return [{"company": None, "n": str(n), "amount_sen": "0", "ex": ",".join(issues[:5])}]
        conf = self._need(BETTERSTACK_QUERY_KEYS, "Better Stack query connection")
        auth = base64.b64encode(f"{conf['BETTERSTACK_QUERY_USERNAME']}:{conf['BETTERSTACK_QUERY_PASSWORD']}".encode())
        status, text = self._http(conf["BETTERSTACK_QUERY_HOST"].rstrip("/") + "?output_format_pretty_row_numbers=0",
                                  {"Authorization": "Basic " + auth.decode(), "Content-Type": "text/plain"},
                                  betterstack_sql(conf["BETTERSTACK_SIMS_LOGS_TABLE"], search))
        if status != 200:
            raise QueryError(f"Better Stack answered HTTP {status}")
        return resolve_log_rows([json.loads(line) for line in text.splitlines() if line.strip()])

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
    partial: bool = False  # at least one part was not read


@dataclass
class SignalResult:
    signal: Signal
    companies: dict[str, CompanyLine]


@dataclass
class Report:
    run_at: datetime
    results: list[SignalResult]
    unreadable: list[str]
    reasons: dict[str, str] = field(default_factory=dict)


def missing_for(variant: Variant, schema: dict[str, set[str]]) -> list[str]:
    missing = []
    for table, columns in variant.requires.items():
        if table not in schema:
            missing.append(table)
            continue
        missing.extend(f"{table}.{c}" for c in columns if c not in schema[table])
    return missing


def present_for(variant: Variant, schema: dict[str, set[str]]) -> list[str]:
    """The go-live columns that exist although the full reading cannot run: an incomplete company schema, for which
    a fallback reading that skips a check must not be used."""
    return [f"{t}.{c}" for t, columns in variant.unless_present.items() for c in columns if c in schema.get(t, ())]


def info_text(key: str, value) -> str:
    if key.endswith("_sen"):
        return f"{key[:-4]}_amount={format_money(parse_sen(value))}"
    return f"{key}={parse_int(value):,}"


def evaluate(signal: Signal, schemas: dict[str, dict[str, set[str]] | None], runner,
             reasons: dict[str, str] | None = None) -> SignalResult:
    """A signal is OK for a company only when every part was read and found nothing for it (coverage per part)."""
    lines = {c: CompanyLine() for c in signal.companies}
    problems: dict[str, bool] = {}
    missed = {"NOT DEPLOYED": False, "UNAVAILABLE": False}
    part_notes: list[str] = []
    per_company_examples: dict[str, list[str]] = {}
    for part in signal.parts:
        schema = schemas.get(part.db)
        if schema is None:
            missed["UNAVAILABLE"] = True
            reason = (reasons or {}).get(part.db, "")
            part_notes.append(f"{part.label}: unavailable, {DB_NAMES[part.db]} could not be read"
                              + (f" ({reason})" if reason else ""))
            continue
        try:
            if part.db in LOG_SOURCES:
                rows = runner.logs(part.db, part.search, part.key)
            else:
                variant = next((v for v in part.variants
                                if not missing_for(v, schema) and not present_for(v, schema)), None)
                if variant is None:
                    missed["NOT DEPLOYED"] = True
                    missing = missing_for(part.variants[0], schema)
                    text = f"{part.label}: not deployed, missing {DB_NAMES[part.db]} " + ", ".join(missing)
                    if any(present_for(v, schema) for v in part.variants):
                        text += "; the company schema is incomplete, so this reading is not run"
                    part_notes.append(text)
                    continue
                if variant.basis:
                    part_notes.append(f"{part.label}: {variant.basis}")
                rows = runner.query(part.db, variant.sql, part.key)
                if variant.post:
                    rows = variant.post(rows)
        except QueryError as exc:
            missed["UNAVAILABLE"] = True
            part_notes.append(f"{part.label}: unavailable, query failed, {exc}")
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
            ids = [i.strip() for i in str(r.get("ex") or "").split(",") if i.strip()]
            prefix = f"{part.example_label} " if part.example_label else ""
            per_company_examples.setdefault(company, []).extend(prefix + i for i in ids)
            line.info.extend(info_text(k, v) for k, v in r.items() if k not in STANDARD_COLUMNS)
            if part.count_info:
                line.info.append(f"{part.count_info}={n:,}")
    for company, line in lines.items():
        if problems.get(company):
            line.status = "CHECK"
        elif missed["UNAVAILABLE"]:
            line.status = "UNAVAILABLE"
        elif missed["NOT DEPLOYED"]:
            line.status = "NOT DEPLOYED"
        else:
            line.status = "OK"
        line.partial = missed["UNAVAILABLE"] or missed["NOT DEPLOYED"]
        line.examples = per_company_examples.get(company, [])[:5]
        line.notes = list(part_notes)
        if signal.note:
            line.notes.append(signal.note)
    return SignalResult(signal, lines)


def build_report(runner, now: datetime | None = None) -> Report:
    schemas: dict[str, dict[str, set[str]] | None] = {}
    unreadable = []
    reasons: dict[str, str] = {}
    for db in DATABASES:
        try:
            schemas[db] = runner.columns(db, tables_for(db))
        except QueryError as exc:
            schemas[db] = None
            unreadable.append(db)
            reasons[db] = str(exc)
    for source in LOG_SOURCES:
        try:
            runner.probe(source)
            schemas[source] = {}
        except QueryError as exc:
            schemas[source] = None
            unreadable.append(source)
            reasons[source] = str(exc)
    results = [evaluate(s, schemas, runner, reasons) for s in SIGNALS]
    return Report(now or datetime.now(MYT), results, unreadable, reasons)


# ---------------------------------------------------------------------------------------------------------------
# Output

def company_order(report: Report) -> list[str]:
    order = [SIFU, NAK]
    if any(UNRECORDED in r.companies for r in report.results):
        order.append(UNRECORDED)
    return order


def headline(result: SignalResult, line: CompanyLine) -> str:
    signal = result.signal
    if line.status in ("NOT DEPLOYED", "UNAVAILABLE") and not (line.count or line.amount_sen or line.info):
        return signal.title
    text = f"{signal.title}: {line.count:,}"
    label = signal.count_label[0 if line.count == 1 else 1]
    if label:
        text += f" {label}"
    if signal.money:
        text += f", {format_money(line.amount_sen)}"
    if line.partial:
        text += " (not every part was read)"
    return text


def render_text(report: Report) -> str:
    out = [
        "Nakngaji and Sifututor company monitor (WP-28), read only",
        f"Run at {report.run_at.astimezone(MYT).strftime('%d/%m/%Y %H:%M')} MYT. Sources: SIMS production (lane 4), "
        "Ripple production (lane 40), Sentry and Better Stack SIMS logs for the last 24 hours (lane 14). "
        "Record ids only, no personal data.",
    ]
    for db in report.unreadable:
        reason = report.reasons.get(db, "")
        out.append(f"WARNING: {DB_NAMES[db]} could not be read" + (f" ({reason})" if reason else "")
                   + "; the signals that need it show UNAVAILABLE unless another part found something to check.")
    summary = []
    for company in company_order(report):
        out += ["", COMPANY_NAMES[company], "-" * len(COMPANY_NAMES[company])]
        counts = dict.fromkeys(STATUSES, 0)
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
        summary.append(f"{COMPANY_NAMES[company]}: " + ", ".join(f"{k} {counts[k]}" for k in STATUSES))
    out += ["", "Notes (how each signal was read today)", "--------------------------------------"]
    for result in report.results:
        notes = next(iter(result.companies.values())).notes
        if notes:
            out.append(f"  {result.signal.title}")
            out += [f"    - {note}" for note in notes]
    out += ["", "Summary", *[f"  {s}" for s in summary], f"  Exit code {exit_code(report)}: {EXIT_MEANING[exit_code(report)]}"]
    return "\n".join(out) + "\n"


def render_json(report: Report) -> str:
    return json.dumps({
        "run_at_myt": report.run_at.astimezone(MYT).isoformat(timespec="seconds"),
        "unreadable": report.unreadable,
        "unreadable_reasons": report.reasons,
        "exit_code": exit_code(report),
        "signals": [
            {
                "key": r.signal.key,
                "title": r.signal.title,
                "companies": {
                    c: {"status": l.status, "count": l.count, "amount_sen": l.amount_sen if r.signal.money else None,
                        "every_part_read": not l.partial, "examples": l.examples, "info": l.info, "notes": l.notes}
                    for c, l in r.companies.items()
                },
            }
            for r in report.results
        ],
    }, indent=2)


EXIT_MEANING = {
    0: "every signal OK",
    1: "something to check, or a signal not deployed",
    2: "a source or a query could not be read",
}


def exit_code(report: Report) -> int:
    lines = [l for r in report.results for l in r.companies.values()]
    if report.unreadable or any(l.status == "UNAVAILABLE" or "unavailable" in " ".join(l.notes) for l in lines):
        return 2
    if any(l.status != "OK" for l in lines):
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
