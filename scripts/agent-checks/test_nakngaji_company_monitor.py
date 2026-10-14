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
            for company, line in result.companies.items():
                self.assertEqual(line.status, "NOT DEPLOYED", f"{result.signal.key} {company}")
        self.assertEqual(runner.calls, [], "no signal query may run when its tables are missing")

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

    def test_report_text_says_not_deployed(self):
        report = monitor.build_report(FakeRunner({"sims": {}, "ripple": {}}))
        text = monitor.render_text(report)
        self.assertIn("NOT DEPLOYED", text)
        self.assertIn("Sifu Edu & Learning Sdn Bhd", text)
        self.assertIn("Nakngaji Sdn Bhd", text)
        self.assertEqual(monitor.exit_code(report), 0)


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

    def test_payout_differences(self):
        report, _ = self.run_signal("payout_differences", {
            "payout_differences.ripple_bank_files": [row(NAK, 1, 2525, "140")],
        })
        line = result_for(report, "payout_differences", NAK)
        self.assertEqual((line.status, line.amount_sen, line.examples), ("CHECK", 2525, ["bank file batch 140"]))

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

    def test_failed_query_is_check_and_names_the_part(self):
        report, _ = self.run_signal("quickbooks_sync_failures", {}, errors={"quickbooks_sync_failures.ripple_qb": "timeout"})
        line = result_for(report, "quickbooks_sync_failures", SIFU)
        self.assertEqual(line.status, "CHECK")
        self.assertIn("query failed", " ".join(line.notes))
        self.assertEqual(monitor.exit_code(report), 1)


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
        self.assertEqual(code, 0)
        self.assertIn("read only", out.getvalue())

    def test_report_holds_ids_only(self):
        for sig in monitor.SIGNALS:
            for part in sig.parts:
                for variant in part.variants:
                    low = variant.sql.lower()
                    for word in ("email", "phone", "parent_name", "customer_name", "payee_name", "sender_name", "tutor_name", "ic_"):
                        self.assertNotIn(word, low, f"{part.key} selects {word}")


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
