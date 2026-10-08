#!/usr/bin/env python3
"""Tests for scripts/agent-access/ripple-prod-sql-readonly.sh (lane 40).

The guard must accept ordinary read queries (including words like create or update inside strings or column names),
and must refuse every way out of read-only mode. All tests use the dry-run switch, so nothing touches a server.
"""

import os
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = Path(os.environ.get("RIPPLE_SQL_SCRIPT", ROOT / "scripts/agent-access/ripple-prod-sql-readonly.sh"))


def run(sql, **env):
    e = dict(os.environ, RIPPLE_PROD_SQL_DRY_RUN="1", **env)
    r = subprocess.run(["bash", str(SCRIPT), sql], capture_output=True, text=True, env=e)
    return r.returncode, r.stdout.strip(), r.stderr.strip()


ACCEPT = [
    "SELECT count(*) FROM crm_leads",
    "select 1;",
    "  SELECT id, updated_at, deleted_at FROM crm_leads WHERE action = 'create' AND note ILIKE '%update%'",
    "WITH recent AS (SELECT * FROM crm_leads LIMIT 5) SELECT * FROM recent",
    "EXPLAIN SELECT * FROM crm_leads",
    "SHOW server_version",
    "TABLE crm_leads",
    "VALUES (1),(2)",
    "SELECT current_setting('transaction_read_only')",
    "SELECT * FROM tutor_payment_slips WHERE status NOT IN ('voided','discarded')",
]

REFUSE = {
    "write statement": "UPDATE crm_leads SET name = 'x'",
    "insert": "INSERT INTO crm_leads(id) VALUES (1)",
    "drop": "DROP TABLE crm_leads",
    "two statements": "SELECT 1; SELECT 2",
    "write after read": "SELECT 1; DELETE FROM crm_leads",
    "go read write": "SELECT 1 FROM (SELECT 1) t; BEGIN READ WRITE",
    "read write word": "WITH x AS (SELECT 1) SELECT * FROM x -- start transaction read write",
    "transaction setting": "SELECT set_config('default_transaction_read_only','off',false)",
    "set session": "SET SESSION CHARACTERISTICS AS TRANSACTION READ WRITE",
    "set role": "SET ROLE postgres",
    "reset": "RESET ALL",
    "begin": "BEGIN",
    "copy to program": "COPY (SELECT 1) TO PROGRAM 'id'",
    "server file read": "SELECT pg_read_file('/etc/passwd')",
    "large object": "SELECT lo_import('/etc/passwd')",
    "dblink": "SELECT * FROM dblink('host=x','select 1') AS t(a int)",
    "terminate": "SELECT pg_terminate_backend(123)",
    "empty": "   ",
}


class RippleProdSqlGuard(unittest.TestCase):
    def test_ordinary_read_queries_are_accepted(self):
        for sql in ACCEPT:
            code, out, err = run(sql)
            self.assertEqual((code, out), (0, "accepted"), f"{sql!r}: {err}")

    def test_every_way_out_of_read_only_is_refused(self):
        for label, sql in REFUSE.items():
            code, out, err = run(sql)
            self.assertEqual(code, 3, f"{label}: {sql!r} -> {code} {out} {err}")
            self.assertTrue(err.startswith("refused:"), label)

    def test_bad_database_or_alias_name_is_refused(self):
        self.assertEqual(run("select 1", RIPPLE_PROD_DB="x; drop")[0], 2)
        self.assertEqual(run("select 1", RIPPLE_PROD_SQL_SSH_ALIAS="a b")[0], 2)

    def test_ssh_command_forces_read_only_and_a_timeout(self):
        text = SCRIPT.read_text()
        self.assertIn("default_transaction_read_only=on", text)
        self.assertIn("statement_timeout=60000", text)
        self.assertIn("runuser -u postgres", text)


if __name__ == "__main__":
    unittest.main()
