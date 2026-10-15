#!/usr/bin/env python3
"""Tests for scripts/agent-access/nakngaji-company-monitor.py (WP-28, Sifututor/sifu-tutor#3479).

Every test feeds fixture query results through a fake runner, so nothing touches a server. The guard test runs each
real query through the two read-only wrappers in their dry-run mode (no connection).
"""

from __future__ import annotations

import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE = ROOT / "scripts/agent-access/nakngaji-company-monitor.py"
spec = importlib.util.spec_from_file_location("nakngaji_company_monitor", MODULE)
monitor = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = monitor  # dataclasses look the module up while the file loads
spec.loader.exec_module(monitor)

SIFU = "sifu_edu_learning"
NAK = "nakngaji_sdn_bhd"


def schema_for(*signals, variant=0):
    """The columns that make the given variant of every part of these signals runnable."""
    schema: dict[str, dict[str, set[str]]] = {"sims": {}, "ripple": {}}
    for signal in signals:
        for part in signal.parts:
            if variant >= len(part.variants):
                continue
            for table, columns in part.variants[variant].requires.items():
                schema[part.db].setdefault(table, set()).update(columns)
    return schema


def full_schema(variant=0):
    return schema_for(*monitor.SIGNALS, variant=variant)


class FakeRunner:
    def __init__(self, schema, rows=None, errors=None):
        self.schema = schema
        self.rows = rows or {}
        self.errors = errors or {}
        self.calls: list[tuple[str, str]] = []

    def columns(self, db, tables):
        return {t: set(c) for t, c in self.schema[db].items() if t in tables}

    def query(self, db, sql, key):
        self.calls.append((db, key))
        if key in self.errors:
            raise monitor.QueryError(self.errors[key])
        return [dict(r) for r in self.rows.get(key, [])]

    def probe(self, source):
        if self.schema.get(source, True) is False:
            raise monitor.QueryError(f"{source} lane not readable in this test")

    def logs(self, source, search, key):
        return self.query(source, search, key)


def row(company, n, amount_sen=0, ex="", **extra):
    return {"company": company, "n": str(n), "amount_sen": str(amount_sen), "ex": ex, **{k: str(v) for k, v in extra.items()}}


def signal(key):
    return next(s for s in monitor.SIGNALS if s.key == key)


def result_for(report, key, company):
    return next(r for r in report.results if r.signal.key == key).companies[company]


class MoneyAndParsing(unittest.TestCase):
    def test_money_is_formatted_to_the_sen_without_floats(self):
        self.assertEqual(monitor.format_money(0), "RM0.00")
        self.assertEqual(monitor.format_money(5), "RM0.05")
        self.assertEqual(monitor.format_money(123457), "RM1,234.57")
        self.assertEqual(monitor.format_money(-1250), "-RM12.50")
        self.assertEqual(monitor.format_money(1414255529), "RM14,142,555.29")

    def test_sen_values_are_read_exactly(self):
        self.assertEqual(monitor.parse_sen("123457"), 123457)
        self.assertEqual(monitor.parse_sen("123457.00"), 123457)
        self.assertEqual(monitor.parse_sen(""), 0)
        self.assertEqual(monitor.parse_sen("NULL"), 0)
        with self.assertRaises(monitor.QueryError):
            monitor.parse_sen("12.5")  # a fraction of a sen means the query did not convert to sen

    def test_mysql_batch_output_is_parsed(self):
        text = "company\tn\tamount_sen\tex\nsifu_edu_learning\t3\t30000\t9,8,7\nNULL\t1\t500\t4\n"
        rows = monitor.parse_tsv(text)
        self.assertEqual(rows[0], {"company": SIFU, "n": "3", "amount_sen": "30000", "ex": "9,8,7"})
        self.assertIsNone(rows[1]["company"])

    def test_mysql_error_inside_output_is_a_query_error(self):
        with self.assertRaises(monitor.QueryError):
            monitor.parse_tsv("ERROR 1146 (42S02) at line 1: Table 'x.pending_extra_charges' doesn't exist\n")

    def test_psql_csv_output_is_parsed(self):
        rows = monitor.parse_csv('company,n,amount_sen,ex\nnakngaji_sdn_bhd,2,1250,"voucher 4,bill_item 9"\n,0,0,\n')
        self.assertEqual(rows[0]["ex"], "voucher 4,bill_item 9")
        self.assertIsNone(rows[1]["company"])

    def test_company_codes_and_brand_codes_are_normalised(self):
        self.assertEqual(monitor.normalise_company("nakngaji"), NAK)
        self.assertEqual(monitor.normalise_company("sifututor"), SIFU)
        self.assertEqual(monitor.normalise_company(NAK), NAK)
        self.assertEqual(monitor.normalise_company(None), monitor.UNRECORDED)
        self.assertEqual(monitor.normalise_company("something_else"), monitor.UNRECORDED)


class NotDeployed(unittest.TestCase):
    def test_every_signal_is_not_deployed_when_no_table_exists(self):
        runner = FakeRunner({"sims": {}, "ripple": {}})
        report = monitor.build_report(runner)
        for result in report.results:
            self.assertTrue(result.companies)
            if all(p.db in monitor.LOG_SOURCES for p in result.signal.parts):
                continue  # a log-only signal needs no table, so a missing table cannot make it NOT DEPLOYED
            for company, line in result.companies.items():
                self.assertEqual(line.status, "NOT DEPLOYED", f"{result.signal.key} {company}")
        db_calls = [c for c in runner.calls if c[0] in ("sims", "ripple")]
        self.assertEqual(db_calls, [], "no database query may run when its tables are missing")

    def test_missing_column_is_named(self):
        schema = full_schema()
        schema["sims"]["pending_extra_charges"].discard("legal_company_id")
        report = monitor.build_report(FakeRunner(schema))
        line = result_for(report, "extra_charges_waiting", SIFU)
        self.assertEqual(line.status, "NOT DEPLOYED")
        self.assertIn("pending_extra_charges.legal_company_id", " ".join(line.notes))

    def test_go_live_signals_are_not_deployed_on_todays_schema(self):
        report = monitor.build_report(FakeRunner(full_schema(variant=1)))
        for key in ("extra_charges_waiting", "rejected_clock_ins", "carried_deductions", "owed_to_nakngaji"):
            self.assertEqual(result_for(report, key, NAK).status, "NOT DEPLOYED", key)

    def test_report_text_says_not_deployed_and_alerts(self):
        report = monitor.build_report(FakeRunner({"sims": {}, "ripple": {}}))
        text = monitor.render_text(report)
        self.assertIn("NOT DEPLOYED", text)
        self.assertIn("Sifu Edu & Learning Sdn Bhd", text)
        self.assertIn("Nakngaji Sdn Bhd", text)
        self.assertEqual(monitor.exit_code(report), 1, "a signal that was not checked is never a success")


class SignalsOnTheGoLiveSchema(unittest.TestCase):
    """One fixture per signal, on the full go-live schema."""

    def run_signal(self, key, rows, errors=None):
        runner = FakeRunner(full_schema(), rows, errors)
        return monitor.build_report(runner), runner

    def test_unmatched_payments_adds_sims_and_ripple_parts_to_the_sen(self):
        report, _ = self.run_signal("unmatched_payments", {
            "unmatched_payments.sims_gateway_receipts": [row(SIFU, 2, 30050, "15,14"), row(NAK, 1, 12550, "16")],
            "unmatched_payments.ripple_bank_suspense": [row(SIFU, 3, 1, "7,6,5", new_last_day=1)],
        })
        sifu = result_for(report, "unmatched_payments", SIFU)
        self.assertEqual((sifu.status, sifu.count, sifu.amount_sen), ("CHECK", 5, 30051))
        self.assertEqual(sifu.examples[:2], ["gateway receipt 15", "gateway receipt 14"])
        self.assertEqual(len(sifu.examples), 5)
        nak = result_for(report, "unmatched_payments", NAK)
        self.assertEqual((nak.status, nak.count, nak.amount_sen), ("CHECK", 1, 12550))

    def test_signal_with_no_rows_is_ok(self):
        report, _ = self.run_signal("callback_mismatches", {})
        line = result_for(report, "callback_mismatches", NAK)
        self.assertEqual((line.status, line.count, line.amount_sen), ("OK", 0, 0))

    def test_callback_mismatches(self):
        report, _ = self.run_signal("callback_mismatches", {
            "callback_mismatches.sims_attempts": [row(NAK, 1, 25000, "901")],
        })
        line = result_for(report, "callback_mismatches", NAK)
        self.assertEqual((line.status, line.amount_sen, line.examples), ("CHECK", 25000, ["payment attempt 901"]))
        self.assertEqual(result_for(report, "callback_mismatches", SIFU).status, "OK")

    def test_failed_credit_allocation(self):
        report, _ = self.run_signal("failed_credit_allocation", {
            "failed_credit_allocation.sims_cross_company_transfers": [row(SIFU, 1, 4000, "33")],
            "failed_credit_allocation.ripple_fee_allocations": [row(NAK, 1, 15000, "2")],
        })
        self.assertEqual(result_for(report, "failed_credit_allocation", SIFU).amount_sen, 4000)
        self.assertEqual(result_for(report, "failed_credit_allocation", NAK).status, "CHECK")

    def test_rejected_clock_ins_count_holds_and_have_no_money(self):
        report, _ = self.run_signal("rejected_clock_ins", {
            "rejected_clock_ins.sims_holds": [row(NAK, 2, 0, "12,11", classes_due=3)],
        })
        line = result_for(report, "rejected_clock_ins", NAK)
        self.assertEqual((line.status, line.count), ("CHECK", 2))
        self.assertIn("classes_due=3", " ".join(line.info))
        self.assertNotIn("RM", monitor.render_text(report).split("Rejected clock-ins")[1].splitlines()[0])

    def test_followup_cases_older_than_72_hours(self):
        report, _ = self.run_signal("followup_cases_72h", {
            "followup_cases_72h.sims_cases": [row(SIFU, 4, 0, "1,2,3,4")],
        })
        self.assertEqual(result_for(report, "followup_cases_72h", SIFU).count, 4)

    def test_extra_charges_waiting(self):
        report, _ = self.run_signal("extra_charges_waiting", {
            "extra_charges_waiting.sims_pending_charges": [row(NAK, 1, 1250, "70", past_one_month_end=2)],
        })
        line = result_for(report, "extra_charges_waiting", NAK)
        self.assertEqual((line.status, line.amount_sen), ("CHECK", 1250))


    def test_carried_deductions_only_check_when_old(self):
        report, _ = self.run_signal("carried_deductions", {
            "carried_deductions.ripple_notes": [row(SIFU, 3, 9000, "5,4,3", needs_check=0), row(NAK, 1, 800, "9", needs_check=1)],
        })
        sifu = result_for(report, "carried_deductions", SIFU)
        self.assertEqual((sifu.status, sifu.count, sifu.amount_sen), ("OK", 3, 9000))
        self.assertEqual(result_for(report, "carried_deductions", NAK).status, "CHECK")

    def test_quickbooks_sync_failures(self):
        report, _ = self.run_signal("quickbooks_sync_failures", {
            "quickbooks_sync_failures.ripple_qb": [row(SIFU, 2, 10000, "voucher 4,bill_item 9")],
        })
        self.assertEqual(result_for(report, "quickbooks_sync_failures", SIFU).examples, ["voucher 4", "bill_item 9"])

    def test_owed_to_nakngaji_balance(self):
        report, _ = self.run_signal("owed_to_nakngaji", {
            "owed_to_nakngaji.sims_collection_ledger": [row(NAK, 1, -150, "2026-11", this_month_sen=98765)],
        })
        line = result_for(report, "owed_to_nakngaji", NAK)
        self.assertEqual((line.status, line.amount_sen), ("CHECK", -150))
        self.assertIn("this_month_amount=RM987.65", " ".join(line.info))
        balanced, _ = self.run_signal("owed_to_nakngaji", {
            "owed_to_nakngaji.sims_collection_ledger": [row(NAK, 0, 0, "", this_month_sen=500)],
        })
        self.assertEqual(result_for(balanced, "owed_to_nakngaji", NAK).status, "OK")

    def test_myinvois_list_counts(self):
        report, _ = self.run_signal("myinvois_counts", {
            "myinvois_counts.ripple_myinvois": [
                row(SIFU, 0, 0, "", waiting_to_file=120, waiting_to_file_sen=1234500, submitted=3),
                row(NAK, 1, 0, "77", waiting_to_file=4, waiting_to_file_sen=500, submitted=0),
            ],
        })
        sifu = result_for(report, "myinvois_counts", SIFU)
        self.assertEqual(sifu.status, "OK")
        self.assertIn("waiting_to_file=120", " ".join(sifu.info))
        self.assertIn("waiting_to_file_amount=RM12,345.00", " ".join(sifu.info))
        self.assertEqual(result_for(report, "myinvois_counts", NAK).status, "CHECK")

    def test_rows_without_a_company_get_their_own_section(self):
        report, _ = self.run_signal("unmatched_payments", {
            "unmatched_payments.sims_gateway_receipts": [row(None, 1, 100, "3")],
        })
        line = result_for(report, "unmatched_payments", monitor.UNRECORDED)
        self.assertEqual(line.status, "CHECK")
        self.assertIn("Company not recorded", monitor.render_text(report))

    def test_failed_query_is_unavailable_and_names_the_part(self):
        report, _ = self.run_signal("quickbooks_sync_failures", {}, errors={"quickbooks_sync_failures.ripple_qb": "timeout"})
        line = result_for(report, "quickbooks_sync_failures", SIFU)
        self.assertEqual(line.status, "UNAVAILABLE")
        self.assertIn("query failed", " ".join(line.notes))
        self.assertEqual(monitor.exit_code(report), 2)


class ReleaseSteps(unittest.TestCase):
    def test_todays_schema_uses_the_before_go_live_variant_and_says_so(self):
        runner = FakeRunner(full_schema(variant=1), {
            "unmatched_payments.sims_gateway_receipts": [row(SIFU, 3, 30000, "3,2,1")],
        })
        report = monitor.build_report(runner)
        line = result_for(report, "unmatched_payments", SIFU)
        self.assertEqual(line.count, 3)
        self.assertTrue(any("before go-live" in n for n in line.notes))

    def test_half_deployed_signal_runs_the_deployed_part_and_names_the_missing_one(self):
        schema = full_schema()
        del schema["sims"]["payment_transfers"]
        del schema["sims"]["referral_reward_allocations"]
        report = monitor.build_report(FakeRunner(schema, {
            "failed_credit_allocation.ripple_fee_allocations": [row(SIFU, 1, 100, "8")],
        }))
        line = result_for(report, "failed_credit_allocation", SIFU)
        self.assertEqual(line.status, "CHECK")
        self.assertTrue(any("not deployed" in n for n in line.notes))


class Output(unittest.TestCase):
    def test_json_output_is_machine_readable(self):
        report = monitor.build_report(FakeRunner(full_schema(), {
            "callback_mismatches.sims_attempts": [row(NAK, 1, 25000, "901")],
        }))
        data = json.loads(monitor.render_json(report))
        entry = next(s for s in data["signals"] if s["key"] == "callback_mismatches")
        self.assertEqual(entry["companies"][NAK]["amount_sen"], 25000)
        self.assertEqual(entry["companies"][NAK]["status"], "CHECK")

    def test_main_prints_and_returns_the_exit_code(self):
        runner = FakeRunner({"sims": {}, "ripple": {}})
        out = io.StringIO()
        with redirect_stdout(out):
            code = monitor.main([], runner=runner)
        self.assertEqual(code, 1, "nothing deployed is not a success")
        self.assertIn("Exit code 1", out.getvalue())
        self.assertIn("read only", out.getvalue())

    def test_report_holds_ids_only(self):
        for sig in monitor.SIGNALS:
            for part in sig.parts:
                for variant in part.variants:
                    low = variant.sql.lower()
                    for word in ("email", "phone", "parent_name", "customer_name", "payee_name", "sender_name", "tutor_name", "ic_"):
                        self.assertNotIn(word, low, f"{part.key} selects {word}")


# ---------------------------------------------------------------------------------------------------------------
# Payout fingerprints: the same rules as Ripple (tutor-payments/lib/company-payments.ts), run on seeded records

# Computed with Ripple's slipSelectionFingerprint / fileSelectionFingerprint code in Node, not with this module.
RIPPLE_FINGERPRINTS = {
    "approved90": "e97aa53549c44b6ce86308dc0971c992ecf7efa9ae602a67ad1ae6802aff460b",
    "now100": "52745e8eac57e91b19398581d344d1ae710915cf634c011d4e32767d4fb7f25d",
    "mixed": "76a3b25a17a110b84ba85a8768ab3a4334478950c1e68d42e436dd1bd3a17aa3",
    "file_now100": "60f3c673afb0dc643551e547267ff1a4fb2500510c4c5238c2f9116434ee4d13",
    "file_two": "294ebd7dd09ec7d45adbe39bc171d88a2e11d059b1f52c6774bbb218107ce35e",
}
APPROVED_90 = {"slip_id": 501, "tutor_id": 77, "payer_company_code": NAK, "net_amount": "90.00",
               "classes": [[9002, "40.00"], [9001, "50.00"]], "bonuses": [], "notes": []}
NOW_100 = dict(APPROVED_90, net_amount="100.00", classes=[[9002, "50.00"], [9001, "50.00"]])
MIXED = {"slip_id": 7, "tutor_id": 3, "payer_company_code": None, "net_amount": "1.005",
         "classes": [[5, "0.29"], [2, "10.10"]], "bonuses": [[4, 12.5], [4, "2.35"]],
         "notes": [[9, "deduction", "3.00"], [1, "addition", "0.07"]]}


class PayoutFingerprintRules(unittest.TestCase):
    def test_slip_fingerprint_is_the_one_ripple_computes(self):
        self.assertEqual(monitor.slip_selection_fingerprint(APPROVED_90), RIPPLE_FINGERPRINTS["approved90"])
        self.assertEqual(monitor.slip_selection_fingerprint(NOW_100), RIPPLE_FINGERPRINTS["now100"])
        self.assertEqual(monitor.slip_selection_fingerprint(MIXED), RIPPLE_FINGERPRINTS["mixed"])

    def test_file_fingerprint_is_the_one_ripple_computes(self):
        now, mixed = RIPPLE_FINGERPRINTS["now100"], RIPPLE_FINGERPRINTS["mixed"]
        self.assertEqual(monitor.file_selection_fingerprint([now]), RIPPLE_FINGERPRINTS["file_now100"])
        self.assertEqual(monitor.file_selection_fingerprint([mixed, now]), RIPPLE_FINGERPRINTS["file_two"])


RIPPLE_PAYOUT_DDL = """
CREATE TABLE tutor_payment_csv_batches (id int PRIMARY KEY, status text NOT NULL, created_at timestamptz NOT NULL DEFAULT now(),
  total_amount numeric(12,2) NOT NULL, slip_count int NOT NULL, payer_company_code text, selection_fingerprint text);
CREATE TABLE tutor_payment_slips (id int PRIMARY KEY, tutor_id int NOT NULL, csv_batch_id int, net_amount numeric(12,2) NOT NULL,
  payer_company_code text, bonus_details jsonb);
CREATE TABLE tutor_slip_classes (id serial PRIMARY KEY, slip_id int NOT NULL, sims_class_id int NOT NULL,
  sims_commission numeric(10,2) NOT NULL, resolved_amount numeric(10,2), class_status text NOT NULL);
CREATE TABLE tutor_payment_notes (id int PRIMARY KEY, slip_id int, type text NOT NULL, amount numeric(10,2) NOT NULL,
  note_status text NOT NULL);
CREATE TABLE tutor_payment_audit_log (id serial PRIMARY KEY, slip_id int, action text NOT NULL, details jsonb);
"""


class PsqlRunner:
    """Runs the monitor's real Ripple SQL on a throwaway local Postgres; SIMS has no tables here."""

    def __init__(self, socket_dir, port):
        self.base = ["psql", "-X", "-q", "-h", socket_dir, "-p", str(port), "-U", "postgres", "-d", "postgres",
                     "-v", "ON_ERROR_STOP=1", "--csv"]

    def run(self, sql):
        done = subprocess.run(self.base + ["-c", sql], capture_output=True, text=True, timeout=60)
        if done.returncode != 0:
            raise monitor.QueryError(done.stderr.strip()[:300])
        return done.stdout

    def columns(self, db, tables):
        if db != "ripple":
            return {}
        found = {}
        for r in monitor.parse_csv(self.run(monitor.schema_sql(db, tables))):
            found.setdefault(r["t"], set()).add(r["c"])
        return found

    def query(self, db, sql, key):
        return monitor.parse_csv(self.run(sql))

    def probe(self, source):
        return None

    def logs(self, source, search, key):
        return []


@unittest.skipUnless(shutil.which("initdb") and shutil.which("pg_ctl") and shutil.which("psql"), "no local Postgres")
class PayoutQueryOnSeededRecords(unittest.TestCase):
    """The go-live payout query, run against seeded source records (codex review finding 1)."""

    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="wp28pg", dir="/tmp")
        data = os.path.join(cls.tmp, "data")
        subprocess.run(["initdb", "-D", data, "-U", "postgres", "--auth=trust", "-E", "UTF8", "--no-locale"],
                       check=True, capture_output=True)
        cls.port = 55400 + os.getpid() % 500
        subprocess.run(["pg_ctl", "-D", data, "-w", "-l", os.path.join(cls.tmp, "log"), "-o",
                        f"-c listen_addresses='' -k {cls.tmp} -p {cls.port}", "start"], check=True, capture_output=True)
        cls.data = data
        cls.runner = PsqlRunner(cls.tmp, cls.port)
        cls.runner.run(RIPPLE_PAYOUT_DDL)

    @classmethod
    def tearDownClass(cls):
        subprocess.run(["pg_ctl", "-D", cls.data, "-m", "fast", "-w", "stop"], capture_output=True)
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        self.runner.run("TRUNCATE tutor_payment_csv_batches, tutor_payment_slips, tutor_slip_classes, "
                        "tutor_payment_notes, tutor_payment_audit_log RESTART IDENTITY")

    def seed_now_100(self, file_fingerprint="current", approvals=("approved90",)):
        fp = {"current": RIPPLE_FINGERPRINTS["file_now100"], "missing": None}.get(file_fingerprint, file_fingerprint)
        fp_sql = "NULL" if fp is None else f"'{fp}'"
        self.runner.run(f"""
INSERT INTO tutor_payment_csv_batches VALUES (140, 'generated', now() - interval '2 days', 100.00, 1, '{NAK}', {fp_sql});
INSERT INTO tutor_payment_slips VALUES (501, 77, 140, 100.00, '{NAK}', '[]');
INSERT INTO tutor_slip_classes (slip_id, sims_class_id, sims_commission, resolved_amount, class_status) VALUES
  (501, 9001, 50.00, NULL, 'included'), (501, 9002, 45.00, 50.00, 'included'), (501, 9003, 30.00, NULL, 'excluded');
""")
        for name in approvals:
            details = "'{}'" if name is None else f"""'{{"selection_fingerprint": "{RIPPLE_FINGERPRINTS[name]}"}}'"""
            self.runner.run(f"INSERT INTO tutor_payment_audit_log (slip_id, action, details) "
                            f"VALUES (501, 'payment_approved', {details})")

    def payout(self, company=NAK):
        report = monitor.build_report(self.runner)
        return result_for(report, "payout_differences", company), report

    def test_finance_approved_rm90_but_slip_and_file_now_rm100_is_check(self):
        self.seed_now_100(approvals=("approved90",))
        line, report = self.payout()
        self.assertEqual(line.status, "CHECK")
        self.assertEqual((line.count, line.amount_sen, line.examples), (1, 10000, ["bank file batch 140"]))
        self.assertIn("payments_changed_since_approval=1", " ".join(line.info))
        self.assertNotEqual(monitor.exit_code(report), 0)

    def test_file_matching_the_latest_approval_is_ok(self):
        self.seed_now_100(approvals=("approved90", "now100"))
        line, _ = self.payout()
        self.assertEqual((line.status, line.count), ("OK", 0))
        self.assertIn("files_checked=1", " ".join(line.info))

    def test_an_older_matching_approval_does_not_hide_a_newer_one(self):
        self.seed_now_100(approvals=("now100", "approved90"))
        self.assertEqual(self.payout()[0].status, "CHECK")

    def test_missing_file_fingerprint_is_check(self):
        self.seed_now_100(file_fingerprint="missing", approvals=("now100",))
        line, _ = self.payout()
        self.assertEqual(line.status, "CHECK")
        self.assertIn("file_fingerprints_missing=1", " ".join(line.info))

    def test_missing_approval_fingerprint_is_check(self):
        self.seed_now_100(approvals=(None,))
        line, _ = self.payout()
        self.assertEqual(line.status, "CHECK")
        self.assertIn("approvals_missing=1", " ".join(line.info))

    def test_no_approval_at_all_is_check(self):
        self.seed_now_100(approvals=())
        self.assertEqual(self.payout()[0].status, "CHECK")

    def test_file_fingerprint_of_another_selection_is_check(self):
        self.seed_now_100(file_fingerprint=RIPPLE_FINGERPRINTS["file_two"], approvals=("now100",))
        line, _ = self.payout()
        self.assertEqual(line.status, "CHECK")
        self.assertIn("file_fingerprints_differ=1", " ".join(line.info))

    def test_bonus_shares_and_notes_count_in_the_fingerprint(self):
        # The same payment as MIXED (whose fingerprint is checked against Ripple above), paid by Sifu Edu & Learning.
        approved = monitor.slip_selection_fingerprint(dict(MIXED, payer_company_code=SIFU, net_amount="1.00"))
        self.runner.run(f"""
INSERT INTO tutor_payment_csv_batches VALUES (150, 'generated', now(), 1.00, 1, '{SIFU}', '{monitor.file_selection_fingerprint([approved])}');
INSERT INTO tutor_payment_slips VALUES (7, 3, 150, 1.00, '{SIFU}',
  '[{{"sims_bonus_id": 4, "amount": 12.5, "action": "included"}}, {{"sims_bonus_id": 4, "amount": "2.35", "action": "included"}},
    {{"sims_bonus_id": 8, "amount": 99, "action": "excluded"}}]');
INSERT INTO tutor_slip_classes (slip_id, sims_class_id, sims_commission, resolved_amount, class_status) VALUES
  (7, 5, 0.29, NULL, 'included'), (7, 2, 10.10, NULL, 'included');
INSERT INTO tutor_payment_notes VALUES (9, 7, 'deduction', 3.00, 'approved'), (1, 7, 'addition', 0.07, 'approved'),
  (2, 7, 'addition', 50.00, 'rejected');
""")
        self.runner.run(f"""INSERT INTO tutor_payment_audit_log (slip_id, action, details) VALUES (7, 'slip_approved',
  '{{"selection_fingerprint": "{approved}"}}')""")
        line, _ = self.payout(SIFU)
        self.assertEqual((line.status, line.count), ("OK", 0), line.info)
        self.runner.run("UPDATE tutor_payment_notes SET amount = 3.01 WHERE id = 9")
        self.assertEqual(self.payout(SIFU)[0].status, "CHECK")

    def test_totals_still_compared_and_files_without_a_company_need_no_fingerprint(self):
        self.runner.run("""
INSERT INTO tutor_payment_csv_batches VALUES (90, 'paid', now(), 60.00, 1, NULL, NULL), (91, 'paid', now(), 70.00, 1, NULL, NULL);
INSERT INTO tutor_payment_slips VALUES (1, 1, 90, 60.00, NULL, NULL), (2, 2, 91, 65.00, NULL, NULL);
""")
        line, _ = self.payout(SIFU)
        self.assertEqual((line.status, line.count, line.amount_sen, line.examples), ("CHECK", 1, 7000, ["bank file batch 91"]))


# ---------------------------------------------------------------------------------------------------------------
# Failures that live only in logs (codex review finding 2)

LOG_PARTS = {
    "callback_mismatches": "callback_mismatches.betterstack_refused_callbacks",
    "failed_credit_allocation": "failed_credit_allocation.betterstack_referral_allocation_errors",
    "rejected_clock_ins": "rejected_clock_ins.betterstack_old_build_refusals",
}


class LogReadings(unittest.TestCase):
    def test_each_log_only_failure_has_a_sentry_or_betterstack_part(self):
        for key, part_key in LOG_PARTS.items():
            sources = {p.db for p in signal(key).parts}
            self.assertIn("betterstack", sources, key)
            self.assertIn(part_key, {p.key for p in signal(key).parts})
        self.assertIn("sentry", {p.db for p in signal("failed_credit_allocation").parts})
        self.assertIn("sentry", {p.db for p in signal("rejected_clock_ins").parts})
        self.assertIn("update the tutor app", " ".join(p.search for p in signal("rejected_clock_ins").parts).lower())

    def test_unreadable_log_lane_is_unavailable_never_ok(self):
        schema = full_schema()
        schema["betterstack"] = False
        report = monitor.build_report(FakeRunner(schema))
        for key in LOG_PARTS:
            for company in (SIFU, NAK):
                line = result_for(report, key, company)
                self.assertEqual(line.status, "UNAVAILABLE", f"{key} {company}")
                self.assertIn("Better Stack", " ".join(line.notes))
        self.assertEqual(monitor.exit_code(report), 2)
        self.assertIn("UNAVAILABLE", monitor.render_text(report))

    def test_logged_refusals_are_check_and_attributed_to_the_company(self):
        report = monitor.build_report(FakeRunner(full_schema(), {
            LOG_PARTS["callback_mismatches"]: [row(NAK, 2, 0, "NINV-1000002,NINV-1000001")],
        }))
        nak = result_for(report, "callback_mismatches", NAK)
        self.assertEqual((nak.status, nak.count), ("CHECK", 2))
        self.assertEqual(nak.examples, ["invoice reference NINV-1000002", "invoice reference NINV-1000001"])
        self.assertEqual(result_for(report, "callback_mismatches", SIFU).status, "OK")

    def test_sentry_events_without_a_company_get_their_own_section(self):
        report = monitor.build_report(FakeRunner(full_schema(), {
            "rejected_clock_ins.sentry_old_build_refusals": [row(None, 3, 0, "SIMS-SIFU-TUTOR-9Z")],
        }))
        line = result_for(report, "rejected_clock_ins", monitor.UNRECORDED)
        self.assertEqual((line.status, line.count), ("CHECK", 3))

    def run_wrapper(self, conf_text, responses):
        home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, home, True)
        conf = Path(home, ".config/sifututor/agent-access/monitoring-readonly.conf")
        conf.parent.mkdir(parents=True)
        conf.write_text(conf_text)
        calls = []

        class Http(monitor.WrapperRunner):
            def _http(self, url, headers, body=None):
                calls.append((url, headers, body))
                for prefix, answer in responses:
                    if url.startswith(prefix):
                        return answer
                raise monitor.QueryError("unexpected url")

        return Http(home=Path(home)), calls

    def test_betterstack_without_a_query_connection_is_unavailable_and_prints_no_secret(self):
        runner, calls = self.run_wrapper("SENTRY_AUTH_TOKEN=s3cr3t-value\nBETTERSTACK_TELEMETRY_TOKEN=t0ken-value\n", [])
        with self.assertRaises(monitor.QueryError) as caught:
            runner.probe("betterstack")
        message = str(caught.exception)
        self.assertIn("BETTERSTACK_QUERY_USERNAME", message)
        self.assertNotIn("s3cr3t", message)
        self.assertNotIn("t0ken", message)
        self.assertEqual(calls, [])

    def test_missing_lane_file_is_unavailable(self):
        home = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, home, True)
        with self.assertRaises(monitor.QueryError):
            monitor.WrapperRunner(home=Path(home)).probe("sentry")

    def test_betterstack_query_is_bounded_and_read_per_company(self):
        conf = ("BETTERSTACK_QUERY_HOST=https://eu-nbg-2-connect.betterstackdata.com\nBETTERSTACK_QUERY_USERNAME=u\n"
                "BETTERSTACK_QUERY_PASSWORD=p\nBETTERSTACK_SIMS_LOGS_TABLE=t547964_test_php\n")
        answer = (200, '{"company":"nakngaji_sdn_bhd","n":"2","ex":"NINV-1000002"}\n{"company":"","n":"1","ex":""}\n')
        runner, calls = self.run_wrapper(conf, [("https://eu-nbg-2-connect.betterstackdata.com", answer)])
        part = next(p for p in signal("callback_mismatches").parts if p.db == "betterstack")
        runner.probe("betterstack")
        rows = runner.logs("betterstack", part.search, part.key)
        self.assertEqual([(r["company"], r["n"]) for r in rows], [(NAK, "2"), (None, "1")])
        url, headers, body = calls[-1]
        self.assertTrue(headers["Authorization"].startswith("Basic "))
        self.assertIn("INTERVAL 1 DAY", body)
        self.assertIn("t547964_test_php_logs", body)
        self.assertTrue(body.lstrip().upper().startswith("SELECT"))

    def test_sentry_reading_counts_events_and_lists_issue_ids(self):
        conf = "SENTRY_AUTH_TOKEN=x\nSENTRY_ORG_SLUG=org\nSENTRY_PROJECT_SLUG=sims-sifu-tutor\n"
        runner, calls = self.run_wrapper(conf, [
            ("https://de.sentry.io/api/0/organizations/org/projects/", (200, '[{"slug": "sims-sifu-tutor", "id": "45"}]')),
            ("https://de.sentry.io/api/0/organizations/org/events/?dataset=errors&field=count%28%29&",
             (200, '{"data": [{"count()": 4}]}')),
            ("https://de.sentry.io/api/0/organizations/org/events/", (200, '{"data": [{"issue": "SIMS-SIFU-TUTOR-9Z", "count()": 4}]}')),
        ])
        part = next(p for p in signal("rejected_clock_ins").parts if p.db == "sentry")
        runner.probe("sentry")
        rows = runner.logs("sentry", part.search, part.key)
        self.assertEqual(rows, [{"company": None, "n": "4", "amount_sen": "0", "ex": "SIMS-SIFU-TUTOR-9Z"}])
        self.assertTrue(all("statsPeriod=24h" in c[0] for c in calls if "/events/" in c[0]))
        self.assertTrue(all("project=45" in c[0] for c in calls if "/events/" in c[0]))

    def test_sentry_reading_with_no_events_returns_no_rows(self):
        conf = "SENTRY_AUTH_TOKEN=x\nSENTRY_ORG_SLUG=org\nSENTRY_PROJECT_SLUG=sims-sifu-tutor\n"
        runner, _ = self.run_wrapper(conf, [
            ("https://de.sentry.io/api/0/organizations/org/projects/", (200, '[{"slug": "sims-sifu-tutor", "id": "45"}]')),
            ("https://de.sentry.io/api/0/organizations/org/events/", (200, '{"data": [{"count()": 0}]}')),
        ])
        part = next(p for p in signal("rejected_clock_ins").parts if p.db == "sentry")
        runner.probe("sentry")
        self.assertEqual(runner.logs("sentry", part.search, part.key), [])


# ---------------------------------------------------------------------------------------------------------------
# WP-28c: company_code attribution and clock-in-only refusals (the line shapes SIMS writes since CLEANUP-6, c080d3133)

def sims_log_line(message, context, level="warning"):
    """A Better Stack row as SIMS writes it: Laravel context sits at raw.monolog.context."""
    return json.dumps({"message": message, "level": level, "monolog": {"context": context, "level_name": level.upper()}})


def refusal_line(action, *, app="tutor", reason="below_minimum_version", company_code=NAK):
    answer = f"Please update the {app.title()} App to continue"
    return sims_log_line("Nakngaji app refused: " + answer, {
        "event": "nakngaji_app_refused", "app": app, "reason": reason, "action": action,
        "app_version": "1.0.0", "minimum_version": "9.0.0", "brand_code": "nakngaji", "company_code": company_code,
        "tutor_request_id": 123, "class_id": 456, "tutor_id": 789})


def context_of(raw):
    return json.loads(raw)["monolog"]["context"]


class CompanyCodeAndClockInRefusals(unittest.TestCase):
    CLOCK_IN_ACTIONS = ("POST api/tutor/class/attendance", "POST api/tutor/class/attendance/bulk")
    OTHER_ACTIONS = ("POST api/tutor/request/apply", "POST api/tutor/class/mark-attended", "POST api/tutor/submit-report",
                     "POST api/tutor/class/backdate", "POST api/tutor/class/update-status")

    def test_company_code_in_the_context_is_used_before_the_invoice_prefix(self):
        # A PBA- order reference carries no NINV-/PINV- prefix; company_code is the only thing that names the company.
        refused_callback = sims_log_line("❌ CALLBACK: Processing failed", {
            "result": {"success": False, "message": "Payment merchant does not match.", "code": 400},
            "event": "fiuu_callback_refused", "orderid": "PBA-0123456789", "company_code": NAK,
            "invoice_ids": [1], "invoice_numbers": ["PINV-980558"]}, "error")
        context = context_of(refused_callback)
        self.assertEqual(monitor.log_company(context["company_code"], ""), NAK)
        # company_code wins over a prefix that disagrees with it
        self.assertEqual(monitor.log_company(NAK, SIFU), NAK)
        self.assertEqual(monitor.log_company(SIFU, NAK), SIFU)

    def test_invoice_prefix_is_only_the_fallback(self):
        self.assertEqual(monitor.log_company("", NAK), NAK)
        self.assertEqual(monitor.log_company(None, SIFU), SIFU)
        self.assertIsNone(monitor.log_company("", ""))
        self.assertIsNone(monitor.log_company("some_other_company", ""))

    def test_log_rows_are_merged_per_company_after_attribution(self):
        rows = monitor.resolve_log_rows([
            {"company_code": NAK, "ref_company": "", "n": "2", "ex": "PBA-1"},
            {"company_code": "", "ref_company": NAK, "n": "1", "ex": "NINV-7"},
            {"company_code": SIFU, "ref_company": "", "n": "4", "ex": ""},
            {"company_code": "", "ref_company": "", "n": "3", "ex": ""},
        ])
        by_company = {r["company"]: (r["n"], r["ex"]) for r in rows}
        self.assertEqual(by_company, {NAK: ("3", "PBA-1,NINV-7"), SIFU: ("4", ""), None: ("3", "")})

    def test_betterstack_query_reads_company_code_from_the_context(self):
        sql = monitor.betterstack_sql("t1", "1 = 1")
        self.assertIn("JSONExtractString(raw, 'monolog', 'context', 'company_code')", sql)
        self.assertIn("'NINV-%'", sql)
        self.assertIn("FORMAT JSONEachRow", sql)

    def test_betterstack_rows_with_a_company_code_come_back_attributed(self):
        conf = ("BETTERSTACK_QUERY_HOST=https://eu-nbg-2-connect.betterstackdata.com\nBETTERSTACK_QUERY_USERNAME=u\n"
                "BETTERSTACK_QUERY_PASSWORD=p\nBETTERSTACK_SIMS_LOGS_TABLE=t547964_test_php\n")
        answer = (200, '{"company_code":"nakngaji_sdn_bhd","ref_company":"","n":"2","ex":"PBA-1"}\n'
                       '{"company_code":"","ref_company":"sifu_edu_learning","n":"1","ex":"PINV-9"}\n')
        runner, _ = LogReadings.run_wrapper(self, conf, [("https://eu-nbg-2-connect.betterstackdata.com", answer)])
        part = next(p for p in signal("callback_mismatches").parts if p.db == "betterstack")
        rows = runner.logs("betterstack", part.search, part.key)
        self.assertEqual(sorted((r["company"], r["n"]) for r in rows), [(NAK, "2"), (SIFU, "1")])

    def test_clock_in_actions_match_and_other_tutor_actions_do_not(self):
        import re
        pattern = re.compile(monitor.CLOCK_IN_ACTION_PATTERN)
        for action in self.CLOCK_IN_ACTIONS:
            self.assertTrue(pattern.search(context_of(refusal_line(action))["action"]), action)
        for action in self.OTHER_ACTIONS + ("", "GET api/tutor/class/attendance-status", "POST api/tutor/class/attendance-extra"):
            self.assertFalse(pattern.search(context_of(refusal_line(action))["action"]), action)

    def old_build_parts(self):
        clock_in = next(p for p in signal("rejected_clock_ins").parts if p.key.endswith("betterstack_old_build_refusals"))
        other_signal = signal("other_old_build_refusals")
        other = next(p for p in other_signal.parts if p.db == "betterstack")
        return clock_in, other

    def test_clock_in_line_counts_only_class_attendance_actions(self):
        clock_in, other = self.old_build_parts()
        self.assertIn(monitor.CLOCK_IN_ACTION_PATTERN, clock_in.search)
        self.assertNotIn("NOT match(", clock_in.search)
        self.assertIn("NOT match(", other.search)
        self.assertIn(monitor.CLOCK_IN_ACTION_PATTERN, other.search)

    def test_both_old_app_refusal_signals_are_still_searched_for(self):
        for part in self.old_build_parts():
            self.assertIn("Please update the Tutor App", part.search)
            self.assertIn("APP_UPDATE_REQUIRED", part.search)
            self.assertIn("nakngaji_app_refused", part.search)
        sentry = next(p for p in signal("other_old_build_refusals").parts if p.db == "sentry")
        self.assertIn("update the Tutor App", sentry.search)
        self.assertIn("APP_UPDATE_REQUIRED", sentry.search)

    def test_other_refusals_get_their_own_line_and_are_not_clock_ins(self):
        report = monitor.build_report(FakeRunner(full_schema(), {
            "other_old_build_refusals.betterstack_old_build_refusals": [row(NAK, 3)],
        }))
        other = result_for(report, "other_old_build_refusals", NAK)
        self.assertEqual((other.status, other.count), ("CHECK", 3))
        clock_in = result_for(report, "rejected_clock_ins", NAK)
        self.assertEqual((clock_in.status, clock_in.count), ("OK", 0))
        text = monitor.render_text(report)
        self.assertIn("Other old-build refusals", text)

    def test_clock_in_refusals_do_not_appear_on_the_other_line(self):
        report = monitor.build_report(FakeRunner(full_schema(), {
            "rejected_clock_ins.betterstack_old_build_refusals": [row(NAK, 2)],
        }))
        self.assertEqual(result_for(report, "rejected_clock_ins", NAK).count, 2)
        self.assertEqual(result_for(report, "other_old_build_refusals", NAK).status, "OK")

    def test_unreadable_log_lane_makes_the_other_line_unavailable(self):
        schema = full_schema()
        schema["betterstack"] = False
        report = monitor.build_report(FakeRunner(schema))
        self.assertIn(result_for(report, "other_old_build_refusals", NAK).status, ("UNAVAILABLE",))


# ---------------------------------------------------------------------------------------------------------------
# Coverage per part (codex review finding 3)

class CoveragePerPart(unittest.TestCase):
    def test_review_scenario_sims_credit_missing_and_ripple_clean_is_not_ok(self):
        schema = full_schema()
        del schema["sims"]["payment_transfers"]
        del schema["sims"]["referral_reward_allocations"]
        report = monitor.build_report(FakeRunner(schema, {}))
        for company in (SIFU, NAK):
            line = result_for(report, "failed_credit_allocation", company)
            self.assertEqual(line.status, "NOT DEPLOYED", company)
            self.assertIn("SIMS credit moved across companies: not deployed", " ".join(line.notes))
        self.assertNotEqual(monitor.exit_code(report), 0)

    def test_one_unreadable_part_makes_the_signal_unavailable(self):
        report = monitor.build_report(FakeRunner(full_schema(), {}, errors={
            "unmatched_payments.ripple_bank_suspense": "timeout"}))
        self.assertEqual(result_for(report, "unmatched_payments", NAK).status, "UNAVAILABLE")
        self.assertEqual(monitor.exit_code(report), 2)

    def test_a_problem_found_still_shows_check_when_another_part_was_missed(self):
        schema = full_schema()
        schema["sentry"] = False
        report = monitor.build_report(FakeRunner(schema, {
            LOG_PARTS["rejected_clock_ins"]: [row(NAK, 1, 0, "")]}))
        line = result_for(report, "rejected_clock_ins", NAK)
        self.assertEqual(line.status, "CHECK")
        self.assertIn("unavailable", " ".join(line.notes).lower())

    def test_every_part_read_and_clean_is_ok_and_exits_zero(self):
        report = monitor.build_report(FakeRunner(full_schema(), {}))
        for result in report.results:
            for company, line in result.companies.items():
                self.assertEqual(line.status, "OK", f"{result.signal.key} {company}")
        self.assertEqual(monitor.exit_code(report), 0)

    def test_summary_counts_unavailable(self):
        schema = full_schema()
        schema["betterstack"] = False
        text = monitor.render_text(monitor.build_report(FakeRunner(schema)))
        self.assertRegex(text, r"Nakngaji Sdn Bhd: OK \d+, CHECK \d+, NOT DEPLOYED \d+, UNAVAILABLE 4")


class Guards(unittest.TestCase):
    """Every query must pass the read-only wrapper guards (dry run, no connection)."""

    def test_every_ripple_query_passes_the_lane_40_guard(self):
        script = ROOT / "scripts/agent-access/ripple-prod-sql-readonly.sh"
        for sql, key in monitor.all_queries("ripple"):
            r = subprocess.run(["bash", str(script), sql], capture_output=True, text=True,
                               env=dict(os.environ, RIPPLE_PROD_SQL_DRY_RUN="1"))
            self.assertEqual((r.returncode, r.stdout.strip()), (0, "accepted"), f"{key}: {r.stderr}")

    def test_every_sims_query_passes_the_lane_4_guard(self):
        script = ROOT / "scripts/agent-access/sims-db-readonly-sql.sh"
        with tempfile.TemporaryDirectory() as home:
            conf = Path(home, ".config/sifututor/agent-access/database-readonly.conf")
            conf.parent.mkdir(parents=True)
            conf.write_text("")
            env = dict(os.environ, HOME=home, SIMS_DB_SQL_DRY_RUN="1")
            probe = subprocess.run(["bash", str(script), "SELECT 1"], capture_output=True, text=True, env=env)
            if probe.returncode == 2 and "mysql" in probe.stderr:
                self.skipTest("no mysql 8 client on this machine")
            for sql, key in monitor.all_queries("sims"):
                r = subprocess.run(["bash", str(script), sql], capture_output=True, text=True, env=env)
                self.assertEqual(r.returncode, 0, f"{key}: {r.stderr}")
                self.assertIn("guard accepted", r.stdout)

    def test_schema_queries_pass_the_guards_too(self):
        self.assertTrue(monitor.schema_sql("sims", ["a"]).lower().startswith("select"))
        self.assertTrue(monitor.schema_sql("ripple", ["a"]).lower().startswith("select"))


if __name__ == "__main__":
    unittest.main()
