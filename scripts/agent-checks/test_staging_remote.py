#!/usr/bin/env python3
"""Tests for the box-side staging deploy program (issue #356).

The program runs on the staging boxes. Here it runs against a FAKE system
object, so no server, no git remote and no deploy controller is touched.
Negative controls (each must fail on a wrong implementation): a ref outside the
allowed patterns, a commit that is not at the remote tip, a migration with DROP,
a held lock, a STOP file, and any attempt to name production.
"""

from __future__ import annotations

from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import staging_remote as sr  # noqa: E402

SHA_A, SHA_B, SHA_C = "a" * 40, "b" * 40, "c" * 40


import contextlib  # noqa: E402
import io  # noqa: E402


class Quiet(unittest.TestCase):
    """The programs print progress lines; keep them out of the test run."""

    def setUp(self) -> None:
        stack = contextlib.ExitStack()
        stack.enter_context(contextlib.redirect_stdout(io.StringIO()))
        stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
        self.addCleanup(stack.close)


class ValidatorTests(unittest.TestCase):
    def test_sha_must_be_40_lowercase_hex(self) -> None:
        self.assertTrue(sr.valid_sha(SHA_A))
        for bad in ("", "a" * 39, "a" * 41, "A" * 40, "g" * 40, SHA_A + "\n", " " + SHA_A, "HEAD", "main"):
            self.assertFalse(sr.valid_sha(bad), bad)

    def test_ripple_ref_allows_only_release_issue_name(self) -> None:
        for good in ("release/1630-cx-audit", "release/1-x", "release/1581-request-timeline-r6"):
            self.assertTrue(sr.ripple_ref_ok(good), good)
        for bad in ("main", "staging", "prod", "production", "release/x-1", "release/1630", "release/1630-", "release/1630-A",
                    "release/1630-cx_audit", "feature/1630-x", "release/1630-x/y", "refs/heads/release/1630-x",
                    "release/1630-x;id", "release/1630-x y", "release/1630-" + "a" * 90, "-release/1-x", "release/1080-outreach"):
            self.assertFalse(sr.ripple_ref_ok(bad), bad)

    def test_sims_ref_allows_main_based_candidate_names_only(self) -> None:
        for good in ("release/3338-cf-authority-main", "test/3373-staging-candidate", "fix/3363-push-staging-serving",
                     "release-base/3338-staging-serving-77f3757", "chore/3294-staging-candidate", "release/2803-production-runtime"):
            self.assertTrue(sr.sims_ref_ok(good), good)
        for bad in ("main", "sifu-staging", "staging", "production", "test/3373-smoke", "fix/1-something", "feat/1-x",
                    "release/x-1", "release/3338", "test/staging-candidate", "release/3338-A", "release/3338-x y",
                    "release/3338-x;id", "../main", "refs/heads/main", "release/" + "a" * 100):
            self.assertFalse(sr.sims_ref_ok(bad), bad)

    def test_ref_ok_dispatches_by_target_and_rejects_unknown_target(self) -> None:
        self.assertTrue(sr.ref_ok("ripple", "release/1-x"))
        self.assertFalse(sr.ref_ok("ripple", "test/3373-staging-candidate"))
        self.assertTrue(sr.ref_ok("sims", "test/3373-staging-candidate"))
        for target in ("prod", "production", "staging", "", "RIPPLE"):
            self.assertFalse(sr.ref_ok(target, "release/1-x"), target)

    def test_targets_cannot_name_production(self) -> None:
        self.assertEqual(sr.TARGETS, ("ripple", "sims"))
        self.assertEqual(sr.MODES, ("normal", "redeploy-served"))
        for word in ("prod", "production", "live"):
            self.assertNotIn(word, sr.TARGETS)
            self.assertNotIn(word, sr.MODES)


class RipplePathGuardTests(unittest.TestCase):
    def test_human_only_files_are_found(self) -> None:
        changed = ["src/app/page.tsx", "src/lib/migrations/240_new.sql", "scripts/deployment/deploy-ripple-suite",
                   "package.json", "package-lock.json", "next.config.ts", ".npmrc", ".github/workflows/x.yml",
                   "ecosystem.config.js", "Dockerfile", "scripts/sims-identity-canary.ts", "scripts/run-outreach-queue.ts",
                   "docs/readme.md", "src/lib/migrations/README.md", "tests/e2e/a.spec.ts", "src/lib/migrations/sub/x.sql"]
        found = sr.ripple_human_only(changed)
        self.assertEqual(set(found), {"src/lib/migrations/240_new.sql", "scripts/deployment/deploy-ripple-suite", "package.json",
                                      "package-lock.json", "next.config.ts", ".npmrc", ".github/workflows/x.yml",
                                      "ecosystem.config.js", "Dockerfile", "scripts/sims-identity-canary.ts",
                                      "scripts/run-outreach-queue.ts"})

    def test_ordinary_app_files_are_allowed(self) -> None:
        self.assertEqual(sr.ripple_human_only(["src/app/page.tsx", "docs/a.md", "tests/x.test.ts", "public/a.png"]), [])

    def test_empty_change_is_allowed(self) -> None:
        self.assertEqual(sr.ripple_human_only([]), [])


class MigrationScannerTests(unittest.TestCase):
    CREATE = """<?php
use Illuminate\\Database\\Migrations\\Migration;
use Illuminate\\Support\\Facades\\Schema;
return new class extends Migration {
    public function up(): void
    {
        Schema::create('widgets', function ($table) {
            $table->id();
            $table->string('name');
            $table->timestamps();
        });
    }
    public function down(): void
    {
        Schema::dropIfExists('widgets');
    }
};
"""

    def wrap(self, up_body: str, down_body: str = "") -> str:
        return ("<?php\nreturn new class extends Migration {\n    public function up(): void\n    {\n" + up_body +
                "\n    }\n    public function down(): void\n    {\n" + down_body + "\n    }\n};\n")

    def test_a_plain_create_table_migration_is_clean_even_though_down_drops(self) -> None:
        self.assertEqual(sr.scan_migration(self.CREATE), [])

    def test_add_column_is_clean(self) -> None:
        text = self.wrap("Schema::table('widgets', function ($t) { $t->string('colour')->nullable(); $t->index('colour'); });")
        self.assertEqual(sr.scan_migration(text), [])

    def test_drop_statements_in_up_are_refused(self) -> None:
        cases = {
            "Schema::drop('widgets');": "drop",
            "Schema::dropIfExists('widgets');": "drop",
            "Schema::dropColumns('widgets', ['a']);": "drop",
            "Schema::table('w', function ($t) { $t->dropColumn('a'); });": "drop",
            "Schema::table('w', function ($t) { $t->dropForeign(['a']); });": "drop",
            "Schema::table('w', function ($t) { $t->dropIndex('i'); });": "drop",
            "Schema::table('w', function ($t) { $t->dropUnique('i'); });": "drop",
            "Schema::table('w', function ($t) { $t->dropPrimary(); });": "drop",
            "Schema::table('w', function ($t) { $t->dropConstrainedForeignId('a'); });": "drop",
            "Schema::table('w', function ($t) { $t->dropTimestamps(); });": "drop",
            "DB::statement('DROP TABLE widgets');": "drop",
            "DB::statement('drop table if exists widgets');": "drop",
            "DB::unprepared('ALTER TABLE w DROP COLUMN a');": "drop",
            "DB::statement(\"DROP INDEX i ON w\");": "drop",
            "DB::statement('DROP DATABASE x');": "drop",
        }
        for body, word in cases.items():
            findings = sr.scan_migration(self.wrap(body))
            self.assertTrue(findings, body)
            self.assertTrue(any(word in f.lower() for f in findings), (body, findings))

    def test_truncate_rename_and_delete_all_are_refused(self) -> None:
        cases = [
            "DB::table('widgets')->truncate();",
            "DB::statement('TRUNCATE TABLE widgets');",
            "DB::statement('truncate widgets');",
            "Schema::rename('widgets', 'gadgets');",
            "Schema::table('w', function ($t) { $t->renameColumn('a', 'b'); });",
            "Schema::table('w', function ($t) { $t->renameIndex('a', 'b'); });",
            "DB::statement('RENAME TABLE a TO b');",
            "DB::statement('ALTER TABLE a RENAME TO b');",
            "DB::statement('ALTER TABLE a RENAME COLUMN x TO y');",
            "DB::statement('DELETE FROM widgets');",
            "DB::statement('delete from widgets where 1=1');",
            "DB::table('widgets')->delete();",
            "Widget::query()->delete();",
            "DB::statement('ALTER TABLE a MODIFY x INT');",
            "DB::statement('ALTER TABLE a CHANGE x y INT');",
        ]
        for body in cases:
            self.assertTrue(sr.scan_migration(self.wrap(body)), body)

    def test_artisan_wipe_and_shell_calls_are_refused(self) -> None:
        for body in ("Artisan::call('migrate:fresh');", "Artisan::call('migrate:reset');", "Artisan::call('db:wipe');",
                     "exec('rm -rf /');", "shell_exec('ls');", "system('ls');", "passthru('ls');", "proc_open('ls', [], $p);",
                     "Artisan::call('db:seed');"):
            self.assertTrue(sr.scan_migration(self.wrap(body)), body)

    def test_column_change_is_refused_because_it_can_cut_data(self) -> None:
        text = self.wrap("Schema::table('w', function ($t) { $t->string('a', 10)->change(); });")
        self.assertTrue(sr.scan_migration(text))

    def test_drops_in_comments_and_down_do_not_count(self) -> None:
        text = self.wrap("// Schema::dropIfExists('x');\n/* DB::statement('DROP TABLE x'); */\n# DROP TABLE y\n"
                         "Schema::create('a', function ($t) { $t->id(); });",
                         "Schema::dropIfExists('a'); DB::statement('TRUNCATE a');")
        self.assertEqual(sr.scan_migration(text), [])

    def test_braces_inside_strings_do_not_end_up_early(self) -> None:
        text = self.wrap("$x = '}'; $y = \"{\"; Schema::dropIfExists('boom');")
        self.assertTrue(sr.scan_migration(text))

    def test_a_drop_hidden_after_a_closure_in_up_is_found(self) -> None:
        text = self.wrap("Schema::table('w', function ($t) { if (true) { $t->string('a'); } });\nSchema::dropIfExists('z');")
        self.assertTrue(sr.scan_migration(text))

    def test_no_up_method_cannot_be_proved_and_is_refused(self) -> None:
        self.assertTrue(sr.scan_migration("<?php\nreturn new class { public function go() {} };\n"))
        self.assertTrue(sr.scan_migration(""))

    def test_unterminated_up_is_refused(self) -> None:
        self.assertTrue(sr.scan_migration("<?php\nreturn new class { public function up() { Schema::create('a', fn() => 1);\n"))

    def test_up_with_return_type_and_attributes_is_found(self) -> None:
        text = "<?php\nclass M extends Migration {\n  public function down(): void { Schema::dropIfExists('a'); }\n" \
               "  public function up () : void {\n    Schema::dropIfExists('b');\n  }\n}\n"
        self.assertTrue(sr.scan_migration(text))

    def test_case_insensitive_sql(self) -> None:
        self.assertTrue(sr.scan_migration(self.wrap("DB::statement('DrOp TaBlE x');")))

    def test_pretend_sql_scan_finds_destructive_statements(self) -> None:
        self.assertEqual(sr.scan_sql("create table `a` (`id` int)\nalter table `b` add `c` int"), [])
        self.assertTrue(sr.scan_sql("drop table `a`"))
        self.assertTrue(sr.scan_sql("alter table `a` drop column `b`"))
        self.assertTrue(sr.scan_sql("truncate table `a`"))
        self.assertTrue(sr.scan_sql("delete from `a`"))
        self.assertTrue(sr.scan_sql("rename table `a` to `b`"))
        self.assertTrue(sr.scan_sql("alter table `a` rename column `x` to `y`"))
        self.assertTrue(sr.scan_sql("alter table `a` modify `x` int"))

    def test_heredoc_sql_is_scanned(self) -> None:
        text = self.wrap("DB::unprepared(<<<SQL\nDROP TABLE x;\nSQL);")
        self.assertTrue(sr.scan_migration(text))


class MigrationChangeTests(unittest.TestCase):
    def test_added_files_are_collected_and_other_changes_flagged(self) -> None:
        lines = ["A\tdatabase/migrations/2026_10_01_000001_create_a.php",
                 "A\tdatabase/migrations/2026_10_01_000002_create_b.php",
                 "M\tdatabase/migrations/2026_01_01_000001_old.php",
                 "D\tdatabase/migrations/2026_01_01_000002_old.php",
                 "R100\tdatabase/migrations/2026_01_01_000003_old.php\tdatabase/migrations/2026_01_01_000004_new.php",
                 "A\tdatabase/seeders/X.php", "M\tapp/Foo.php"]
        added, others = sr.split_migration_changes(lines)
        self.assertEqual(added, ["database/migrations/2026_10_01_000001_create_a.php", "database/migrations/2026_10_01_000002_create_b.php"])
        self.assertEqual(len(others), 3)

    def test_nothing_changed(self) -> None:
        self.assertEqual(sr.split_migration_changes(["M\tapp/Foo.php"]), ([], []))


# ----------------------------------------------------------------- fakes ----

import datetime as dt  # noqa: E402
import json  # noqa: E402


class FakeSys:
    """A box that does nothing real. Rules answer commands; everything the program does is recorded."""

    def __init__(self, host: str) -> None:
        self.host = host
        self.files: dict[str, str] = {}
        self.dirs: set[str] = set()
        self.held: set[str] = set()
        self.links: set[str] = set()
        self.owners: dict[str, tuple[str, int]] = {}
        self.rules: list = []
        self.calls: list[list[str]] = []
        self.logged: list[str] = []
        self.free = 200 * 1024 * 1024
        self.spawned: list[tuple[list[str], str, int | None]] = []
        self.bounded: list[list[str]] = []
        self.bounded_result = (0, False)
        self.take_lock_result: int | None = 9
        self.moment = dt.datetime(2026, 10, 9, 5, 30, 0, tzinfo=dt.timezone.utc)
        self.listing: dict[str, list[str]] = {}

    def when(self, *words: str, rc: int = 0, out: str = "", fn=None) -> None:
        self.rules.insert(0, (words, rc, out, fn))

    def run(self, argv, *, timeout=None, cwd=None, env=None):
        self.calls.append(list(argv))
        line = " ".join(argv)
        for words, rc, out, fn in self.rules:
            if all(w in line for w in words):
                return fn(argv) if fn else (rc, out)
        return 0, ""

    def ran(self, *words: str) -> list[list[str]]:
        return [c for c in self.calls if all(w in " ".join(c) for w in words)]

    def hostname(self): return self.host
    def now(self): return self.moment
    def exists(self, path): return path in self.files or path in self.dirs or path in self.links
    def is_link(self, path): return path in self.links
    def owner_mode(self, path): return self.owners.get(path, ("root", 0o755))
    def read_text(self, path, limit=0):
        if path not in self.files:
            raise OSError(path)
        return self.files[path]
    def read_tail(self, path, nbytes=0): return self.read_text(path)
    def write_text(self, path, text): self.files[path] = text
    def append_line(self, path, line): self.logged.append(line)
    def mkdir(self, path, mode=0o755): self.dirs.add(path)
    def remove(self, path): self.files.pop(path, None)
    def listdir(self, path): return list(self.listing.get(path, []))
    def free_kb(self, path): return self.free
    def lock_held(self, path): return path in self.held
    def take_lock(self, path): return self.take_lock_result
    def spawn_detached(self, argv, log_path, keep_fd):
        self.spawned.append((list(argv), log_path, keep_fd))
        return 4242
    def run_bounded(self, argv, timeout, kill_after=120.0):
        self.bounded.append(list(argv))
        return self.bounded_result
    def self_path(self): return "/var/lib/sifututor-pc-deploy/bin/staging_deploy-abc.py"
    def sleep(self, seconds): pass


BASE = "/opt/deploy/ripple-suite"
REF = "release/1700-proof"
SERVED = "d" * 40
PROD = "e" * 40
JLIST = json.dumps([{"name": "other-app", "pm2_env": {"status": "online", "SECRET_THING": "hunter2"}},
                    {"name": "ripple-suite-staging", "pm2_env": {"status": "online", "RIPPLE_DEPLOY_COMMIT": SERVED,
                                                                   "DATABASE_URL": "postgres://u:pw@h/db"}}])


def ripple_box(sha: str = SHA_A, ref: str = REF, served: str = SERVED, **kw) -> FakeSys:
    s = FakeSys("srv1297548")
    s.owners["/usr/local/bin/deploy-ripple-suite"] = ("root", 0o755)
    s.files[BASE + "/repo-staging/.git"] = ""
    s.files[BASE + "/.serving-prod.json"] = json.dumps({"commit": PROD, "other": "ignored"})
    s.files["/var/log/apps/ripple-suite-staging-deploy.log"] = (
        f"x\nDeploy complete: staging {served} (release:release/1581-old)\n")
    s.listing[BASE] = [".deploy-staging.lock", ".deploy-prod.lock", ".crm-x-staging-migration.lock", ".pc-staging-release.lock", "repo-staging"]
    s.when("ls-remote", out=f"{sha}\trefs/heads/{ref}\n")
    s.when("rev-parse", "refs/remotes/origin/" + ref, out=sha + "\n")
    s.when("pm2", "jlist", out=JLIST)
    s.when("rev-parse", "HEAD", out=served + "\n")
    s.when("status", "--porcelain", out="")
    s.when("diff", "--no-renames", out="src/app/page.tsx\ndocs/a.md\n")
    s.when("curl", out="200")
    s.when("id", "-u", "deploy", out="1001\n")
    s.dirs.update({"/var/www/staging/ripple-suite/node_modules", "/var/www/staging/ripple-suite/.next"})
    return s


class RippleCheckTests(Quiet):
    def check(self, s: FakeSys, ref: str = REF, sha: str = SHA_A, mode: str = "normal"):
        return sr.RippleRemote(s, "tester", "rel-1").check(ref, sha, mode, "")

    def assertRefused(self, s: FakeSys, text: str = "", **kw) -> None:
        with self.assertRaises(sr.Refused) as ctx:
            self.check(s, **kw)
        self.last_refusal = str(ctx.exception)
        self.assertIn(text, str(ctx.exception))
        self.assertTrue(any("REFUSED" in line for line in s.logged))

    def test_a_good_release_is_accepted_and_logged_in_myt(self) -> None:
        s = ripple_box()
        lines = self.check(s)
        self.assertIn("CHECK OK", lines[0])
        self.assertTrue(any("PREFLIGHT_OK" in l and "ts_myt=2026-10-09T13:30:00+0800" in l and "ts_utc=2026-10-09T05:30:00Z" in l
                            and "actor=tester" in l and "release=rel-1" in l for l in s.logged))

    def test_wrong_box_is_refused(self) -> None:
        s = ripple_box()
        s.host = "srv1701812"
        self.assertRefused(s, "not the ripple staging box")

    def test_stop_switch_refuses(self) -> None:
        s = ripple_box()
        s.files[sr.SWITCH_FILE] = "stop"
        self.assertRefused(s, "STOP switch")

    def test_ref_outside_the_allowed_patterns_is_refused(self) -> None:
        for bad in ("main", "staging", "prod", "release/1080-outreach", "test/3373-staging-candidate", "release/x"):
            s = ripple_box()
            self.assertRefused(s, "not an allowed", ref=bad)
            self.assertEqual(s.ran("ls-remote"), [], bad)

    def test_commit_must_be_the_remote_tip(self) -> None:
        s = ripple_box()
        s.when("ls-remote", out=f"{SHA_B}\trefs/heads/{REF}\n")
        self.assertRefused(s, "remote tip")
        s = ripple_box()
        s.when("ls-remote", out="")
        self.assertRefused(s, "remote tip")
        s = ripple_box()
        s.when("ls-remote", rc=128, out="fatal")
        self.assertRefused(s, "remote tip")

    def test_short_or_non_hex_commit_is_refused(self) -> None:
        for bad in ("abc1234", "G" * 40, SHA_A.upper()):
            self.assertRefused(ripple_box(), "40 lowercase hex", sha=bad)

    def test_a_held_deploy_lock_refuses_and_names_it(self) -> None:
        for name in (".deploy-staging.lock", ".deploy-prod.lock", ".crm-x-staging-migration.lock"):
            s = ripple_box()
            s.held.add(f"{BASE}/{name}")
            self.assertRefused(s, name)

    def test_own_lock_held_means_a_pc_deploy_is_running(self) -> None:
        s = ripple_box()
        s.held.add(BASE + "/.pc-staging-release.lock")
        self.assertRefused(s, "already running")

    def test_dirty_or_moved_checkout_means_a_person_is_mid_procedure(self) -> None:
        s = ripple_box()
        s.when("status", "--porcelain", out=" M src/x.ts\n")
        self.assertRefused(s, "not clean on the serving commit")
        s = ripple_box()
        s.when("rev-parse", "HEAD", out=SHA_C + "\n")
        self.assertRefused(s, "not clean on the serving commit")

    def test_migration_script_and_dependency_changes_need_a_mac_session(self) -> None:
        for path in ("src/lib/migrations/241_x.sql", "scripts/deployment/deploy-ripple-suite", "package.json", "package-lock.json",
                     "next.config.ts", ".github/workflows/a.yml"):
            s = ripple_box()
            s.when("diff", "--no-renames", out=f"src/app/page.tsx\n{path}\n")
            self.assertRefused(s, "Mac session")

    def test_release_must_contain_what_production_serves(self) -> None:
        s = ripple_box()
        s.when("merge-base", "--is-ancestor", rc=1)
        self.assertRefused(s, "does not contain the commit production serves")

    def test_unreadable_production_receipt_refuses(self) -> None:
        s = ripple_box()
        del s.files[BASE + "/.serving-prod.json"]
        self.assertRefused(s, "unreadable")

    def test_unknown_serving_commit_refuses(self) -> None:
        s = ripple_box()
        s.when("pm2", "jlist", out="[]")
        self.assertRefused(s, "unknown")

    def test_controller_must_be_root_owned_755_and_not_a_link(self) -> None:
        s = ripple_box()
        s.owners["/usr/local/bin/deploy-ripple-suite"] = ("deploy", 0o755)
        self.assertRefused(s, "root-owned mode 755")
        s = ripple_box()
        s.owners["/usr/local/bin/deploy-ripple-suite"] = ("root", 0o775)
        self.assertRefused(s, "root-owned mode 755")
        s = ripple_box()
        s.links.add("/usr/local/bin/deploy-ripple-suite")
        self.assertRefused(s, "symlink")

    def test_low_disk_refuses(self) -> None:
        s = ripple_box()
        s.free = 1024
        self.assertRefused(s, "20 GiB")

    def test_foreign_owned_files_in_the_build_tree_are_found_before_a_run_is_started(self) -> None:
        """The controller refuses after about 3 seconds when root left files in node_modules; say so at check time instead."""
        for tree in ("node_modules", ".next"):
            s = ripple_box()
            s.when("find", "-uid", fn=lambda argv, tree=tree: (0, f"/var/www/staging/ripple-suite/{tree}/.vite/x\n"
                                                                  if f"/var/www/staging/ripple-suite/{tree}" in argv else ""))
            self.assertRefused(s, "foreign-owned files")
            self.assertIn(tree, str(self.last_refusal))

    def test_a_clean_build_tree_passes_the_ownership_check(self) -> None:
        s = ripple_box()
        self.assertIn("CHECK OK", self.check(s)[0])
        self.assertTrue(s.ran("find", "-uid"))

    def test_pm2_secrets_never_reach_the_log_or_output(self) -> None:
        s = ripple_box()
        lines = self.check(s)
        blob = "\n".join(lines + s.logged)
        for secret in ("hunter2", "postgres://", "DATABASE_URL", "SECRET_THING"):
            self.assertNotIn(secret, blob)

    def test_redeploy_served_skips_only_the_production_containment(self) -> None:
        s = ripple_box(sha=SERVED, ref="release/1581-old")
        s.when("merge-base", "--is-ancestor", rc=1)
        lines = self.check(s, ref="release/1581-old", sha=SERVED, mode="redeploy-served")
        self.assertIn("skipped: redeploy of the commit staging already serves", lines[0])
        self.assertEqual(s.ran("merge-base"), [])

    def test_redeploy_served_refuses_a_different_commit(self) -> None:
        s = ripple_box(sha=SHA_A)
        s.when("merge-base", "--is-ancestor", rc=1)
        self.assertRefused(s, "redeploy-served needs the commit and ref", mode="redeploy-served")

    def test_redeploy_served_refuses_when_the_deploy_log_names_another_ref(self) -> None:
        s = ripple_box(sha=SERVED, ref="release/1700-proof")
        self.assertRefused(s, "redeploy-served needs the commit and ref", ref="release/1700-proof", sha=SERVED, mode="redeploy-served")

    def test_redeploy_served_still_applies_every_other_rule(self) -> None:
        s = ripple_box(sha=SERVED, ref="release/1581-old")
        s.held.add(BASE + "/.deploy-staging.lock")
        self.assertRefused(s, ".deploy-staging.lock", ref="release/1581-old", sha=SERVED, mode="redeploy-served")
        s = ripple_box(sha=SERVED, ref="release/1581-old")
        s.files[sr.SWITCH_FILE] = "x"
        self.assertRefused(s, "STOP", ref="release/1581-old", sha=SERVED, mode="redeploy-served")

    def test_unknown_mode_is_refused(self) -> None:
        self.assertRefused(ripple_box(), "mode must be one of", mode="prod")


class RippleRunTests(Quiet):
    def test_start_checks_then_spawns_a_detached_runner_that_keeps_the_lock(self) -> None:
        s = ripple_box()
        lines = sr.RippleRemote(s, "pc-loop", "rel-1").start(REF, SHA_A, "normal", "")
        self.assertTrue(lines[0].startswith("STARTED run=20261009T053000Z-aaaaaaaa"))
        argv, log, fd = s.spawned[0]
        self.assertEqual(fd, 9)
        self.assertIn("_run", argv)
        self.assertIn("--lock-fd", argv)
        self.assertEqual(argv[argv.index("--lock-fd") + 1], "9")
        self.assertTrue(log.endswith("run.log"))
        state = json.loads(s.files[next(p for p in s.files if p.endswith("state.json"))])
        self.assertEqual((state["state"], state["sha"], state["ref"]), ("starting", SHA_A, REF))

    def test_the_runner_command_line_that_start_builds_is_understood_by_the_program(self) -> None:
        s = ripple_box()
        sr.RippleRemote(s, "pc-loop", "rel-1").start(REF, SHA_A, "normal", "")
        argv = s.spawned[0][0]
        self.assertEqual(argv[2:5], ["remote", "ripple", "_run"])
        s.held.add(BASE + "/.pc-staging-release.lock")
        s.when("pm2", "jlist", out=JLIST.replace(SERVED, SHA_A))
        s.when("rev-parse", "HEAD", out=SHA_A + "\n")
        s.files["/var/log/apps/ripple-suite-staging-deploy.log"] = f"Deploy complete: staging {SHA_A} (release:{REF})\n"
        self.assertEqual(sr.main(argv[2:], s, lambda line: None), 0)
        self.assertEqual(s.bounded[0][-5:], ["staging", "--release-ref", REF, "--commit", SHA_A])
        state = json.loads(s.files[next(p for p in s.files if p.endswith("state.json"))])
        self.assertEqual(state["status"], "ok")

    def test_start_refuses_when_the_wrapper_lock_is_taken(self) -> None:
        s = ripple_box()
        s.take_lock_result = None
        with self.assertRaises(sr.Refused):
            sr.RippleRemote(s).start(REF, SHA_A, "normal", "")
        self.assertEqual(s.spawned, [])

    def test_start_runs_no_deploy_when_a_rule_refuses(self) -> None:
        s = ripple_box()
        s.files[sr.SWITCH_FILE] = "x"
        with self.assertRaises(sr.Refused):
            sr.RippleRemote(s).start(REF, SHA_A, "normal", "")
        self.assertEqual(s.spawned, [])
        self.assertEqual(s.bounded, [])

    def test_the_controller_command_names_staging_and_nothing_else(self) -> None:
        s = ripple_box()
        s.held.add(BASE + "/.pc-staging-release.lock")  # the runner holds it
        box = sr.RippleRemote(s, "pc-loop", "rel-1")
        s.when("pm2", "jlist", out=JLIST.replace(SERVED, SHA_A))
        s.when("rev-parse", "HEAD", out=SHA_A + "\n")
        s.files["/var/log/apps/ripple-suite-staging-deploy.log"] = f"Deploy complete: staging {SHA_A} (release:{REF})\n"
        box.write_state("20261009T053000Z-aaaaaaaa", run="x")
        box.run_body("20261009T053000Z-aaaaaaaa", REF, SHA_A, "normal", "", 9)
        argv = s.bounded[0]
        self.assertEqual(argv, ["sudo", "-n", "-u", "deploy", "/usr/local/bin/deploy-ripple-suite", "staging", "--release-ref", REF,
                                "--commit", SHA_A])
        joined = " ".join(argv)
        for word in ("prod", "--replace-serving", "--code-only", "--runtime-refresh", "--staging-main-commit", "CONFIRM"):
            self.assertNotIn(word, joined)

    def test_result_ok_needs_the_read_back_to_agree(self) -> None:
        for agree, expected in ((True, "ok"), (False, "failed")):
            s = ripple_box()
            s.held.add(BASE + "/.pc-staging-release.lock")
            box = sr.RippleRemote(s)
            runid = "20261009T053000Z-aaaaaaaa"
            box.write_state(runid, run=runid)
            served = SHA_A if agree else SERVED
            s.when("pm2", "jlist", out=JLIST.replace(SERVED, served))
            s.when("rev-parse", "HEAD", out=SHA_A + "\n")
            s.files["/var/log/apps/ripple-suite-staging-deploy.log"] = f"Deploy complete: staging {SHA_A} (release:{REF})\n"
            box.run_body(runid, REF, SHA_A, "normal", "", 9)
            state = json.loads(s.files[box.run_dir(runid) + "/state.json"])
            self.assertEqual(state["status"], expected)
            self.assertIn("RESULT run=" + runid, state["result_line"])

    def test_a_failing_or_timed_out_controller_is_reported_as_such(self) -> None:
        for result, expected in (((1, False), "failed"), ((124, True), "timeout")):
            s = ripple_box()
            s.held.add(BASE + "/.pc-staging-release.lock")
            s.bounded_result = result
            box = sr.RippleRemote(s)
            runid = "20261009T053000Z-aaaaaaaa"
            box.write_state(runid, run=runid)
            box.run_body(runid, REF, SHA_A, "normal", "", 9)
            self.assertEqual(json.loads(s.files[box.run_dir(runid) + "/state.json"])["status"], expected)

    def test_the_runner_refuses_to_run_without_the_lock(self) -> None:
        s = ripple_box()
        box = sr.RippleRemote(s)
        runid = "20261009T053000Z-aaaaaaaa"
        box.write_state(runid, run=runid)
        box.run_body(runid, REF, SHA_A, "normal", "", 9)
        self.assertEqual(s.bounded, [])

    def test_status_reports_running_finished_and_died(self) -> None:
        s = ripple_box()
        box = sr.RippleRemote(s)
        runid = "20261009T053000Z-aaaaaaaa"
        s.listing[sr.STATE_DIR + "/runs"] = [f"ripple-{runid}", "sims-20261009T000000Z-bbbbbbbb"]
        box.write_state(runid, run=runid, state="running", step="controller")
        s.files[box.run_dir(runid) + "/run.log"] = "line one\npassword=hunter2 here\n"
        self.assertIn("state=died", box.status_lines(None)[0])
        s.held.add(BASE + "/.pc-staging-release.lock")
        lines = box.status_lines(None)
        self.assertIn("state=running", lines[0])
        self.assertNotIn("hunter2", "\n".join(lines))
        box.write_state(runid, state="finished", result_line="RESULT run=x status=ok exit=0 seconds=5")
        s.held.clear()
        self.assertIn("RESULT run=x status=ok", "\n".join(box.status_lines(runid)))

    def test_status_with_no_runs(self) -> None:
        self.assertIn("state=none", sr.RippleRemote(ripple_box()).status_lines(None)[0])

    def test_bad_run_id_is_refused(self) -> None:
        with self.assertRaises(sr.Refused):
            sr.RippleRemote(ripple_box()).status_lines("../../etc")

    def test_verify_needs_every_record_to_agree(self) -> None:
        s = ripple_box(served=SHA_A)
        s.when("pm2", "jlist", out=JLIST.replace(SERVED, SHA_A))
        s.files["/var/log/apps/ripple-suite-staging-deploy.log"] = f"Deploy complete: staging {SHA_A} (release:{REF})\n"
        ok, text = sr.RippleRemote(s).verify(SHA_A, REF)
        self.assertTrue(ok, text)
        self.assertIn("VERIFY OK", text)
        for mutate in ("pm2", "head", "log", "http", "offline", "ref"):
            s2 = ripple_box(served=SHA_A)
            s2.files["/var/log/apps/ripple-suite-staging-deploy.log"] = f"Deploy complete: staging {SHA_A} (release:{REF})\n"
            s2.when("pm2", "jlist", out=JLIST.replace(SERVED, SHA_A))
            if mutate == "pm2":
                s2.when("pm2", "jlist", out=JLIST)
            elif mutate == "head":
                s2.when("rev-parse", "HEAD", out=SHA_B + "\n")
            elif mutate == "log":
                s2.files["/var/log/apps/ripple-suite-staging-deploy.log"] = f"Deploy complete: staging {SHA_B} (release:{REF})\n"
            elif mutate == "http":
                s2.when("curl", out="502")
            elif mutate == "offline":
                s2.when("pm2", "jlist", out=JLIST.replace(SERVED, SHA_A).replace('"online"', '"stopped"', 1).replace('"status": "online", "RIPPLE', '"status": "stopped", "RIPPLE'))
            elif mutate == "ref":
                pass
            ok2, text2 = sr.RippleRemote(s2).verify(SHA_A, "release/9999-other" if mutate == "ref" else REF)
            self.assertFalse(ok2, mutate)
            self.assertIn("VERIFY FAILED", text2)

    def test_switch_off_on_show(self) -> None:
        s = ripple_box()
        box = sr.RippleRemote(s, "hafiz")
        self.assertIn("OFF", box.switch("show")[0])
        box.switch("off")
        self.assertIn(sr.SWITCH_FILE, s.files)
        self.assertIn("ON", box.switch("show")[0])
        box.switch("on")
        self.assertNotIn(sr.SWITCH_FILE, s.files)
        with self.assertRaises(sr.Refused):
            box.switch("maybe")


class CliTests(Quiet):
    def run_cli(self, argv: list[str], s: FakeSys | None = None) -> tuple[int, str]:
        out: list[str] = []
        code = sr.main(argv, s or ripple_box(), out.append)
        return code, "\n".join(out)

    def test_check_through_the_command_line(self) -> None:
        code, text = self.run_cli(["remote", "ripple", "check", REF, SHA_A])
        self.assertEqual(code, 0, text)
        self.assertIn("CHECK OK", text)

    def test_production_is_not_a_target_or_a_mode(self) -> None:
        for argv in (["remote", "prod", "check", REF, SHA_A], ["remote", "production", "start", REF, SHA_A],
                     ["remote", "staging", "check", REF, SHA_A]):
            with self.assertRaises(SystemExit):
                self.run_cli(argv)
        code, text = self.run_cli(["remote", "ripple", "check", REF, SHA_A, "--mode", "prod"])
        self.assertEqual(code, 2)
        self.assertIn("mode must be one of", text)

    def test_a_refusal_exits_2_and_prints_the_reason(self) -> None:
        code, text = self.run_cli(["remote", "ripple", "check", "main", SHA_A])
        self.assertEqual(code, 2)
        self.assertTrue(text.startswith("REFUSED:"))

    def test_runner_call_needs_a_run_id_and_a_lock_fd(self) -> None:
        code, _ = self.run_cli(["remote", "ripple", "_run", "bad", REF, SHA_A, "normal"])
        self.assertEqual(code, 2)
        code, _ = self.run_cli(["remote", "ripple", "_run", "20261009T053000Z-aaaaaaaa", REF, SHA_A, "normal"])
        self.assertEqual(code, 2)

    def test_verify_through_the_command_line(self) -> None:
        s = ripple_box(served=SHA_A)
        s.when("pm2", "jlist", out=JLIST.replace(SERVED, SHA_A))
        s.files["/var/log/apps/ripple-suite-staging-deploy.log"] = f"Deploy complete: staging {SHA_A} (release:{REF})\n"
        code, text = self.run_cli(["remote", "ripple", "verify", SHA_A], s)
        self.assertEqual(code, 0, text)
        code, text = self.run_cli(["remote", "ripple", "verify", "nope"], s)
        self.assertEqual(code, 2)


# ------------------------------------------------------------------ sims ----

APP = "/var/www/staging/sifu-tutor"
SIMS_REF = "test/3373-staging-candidate"
CUR = "1" * 40
MAIN_TIP = "2" * 40
CLEAN_MIG = TEST_CLEAN = MigrationScannerTests.CREATE
DROP_MIG = MigrationScannerTests().wrap("Schema::dropIfExists('widgets');")
M_OLD = "database/migrations/2026_01_01_000001_old.php"
M_NEW1 = "database/migrations/2026_10_09_000001_create_a.php"
M_NEW2 = "database/migrations/2026_10_09_000002_create_b.php"


class SimsBox(FakeSys):
    """A SIMS staging box that remembers which migrations ran, so the lane can be exercised for real."""

    def __init__(self, sha: str = SHA_A, ref: str = SIMS_REF, cur: str = CUR, new_files: list[str] | None = None,
                 texts: dict[str, str] | None = None) -> None:
        super().__init__("srv1701812")
        self.sha, self.ref, self.cur = sha, ref, cur
        self.head = cur
        self.done = {"2026_01_01_000001_old"}
        self.tree = {cur: [M_OLD], sha: [M_OLD] + (new_files or [])}
        self.texts = texts or {f: CLEAN_MIG for f in (new_files or [])}
        self.owners[APP] = ("www-data", 0o755)
        self.files[APP + "/artisan"] = ""
        self.ps_out = "  PID COMMAND\n  1 /sbin/init\n  900 php-fpm: pool www\n"
        self.migrate_effect = "all"       # all | none | partial
        self.rollback_ok = True
        self.fail = set()                 # command words that exit 1
        self.sequence: list[str] = []
        self.pretend_out = "create table `a` (`id` int)"
        self._rules()

    def _rules(self) -> None:
        self.when("config --get remote.origin.url", out="git@github.com:Sifututor/sifu-tutor.git\n")
        self.when("artisan env", out="INFO The application environment is [staging].\n")
        self.when("rev-parse HEAD", fn=lambda a: (0, self.head + "\n"))
        self.when("status --porcelain", out="")
        self.when("fetch")
        self.when("rev-parse refs/remotes/origin/" + self.ref, out=self.sha + "\n")
        self.when("rev-parse refs/remotes/origin/main", out=MAIN_TIP + "\n")
        self.when("merge-base --is-ancestor")
        self.when("cat-file -e")
        self.when("ps -eo", fn=lambda a: (0, self.ps_out))
        self.when("tinker", fn=lambda a: (0, "json: " + "\n" + json.dumps(sorted(self.done)) + "\n"))
        self.when("ls-tree", fn=lambda a: (0, "\n".join(self.tree.get(next((r for r in self.tree if r in " ".join(a)), ""), [M_OLD])) + "\n"))
        self.when(" show ", fn=lambda a: (0, self.texts.get(a[-1].split(":", 1)[1], "")))
        self.when("diff --no-renames --name-status", fn=lambda a: (0, "".join(f"A\t{f}\n" for f in self.tree[self.sha] if f not in self.tree[self.cur])))
        self.when("migrate:status --pending", fn=lambda a: (0, self.pending_text()))
        self.when("migrate --pretend", fn=lambda a: (0, self.pretend_out))
        self.when("migrate --force", fn=self.do_migrate)
        self.when("migrate:rollback", fn=self.do_rollback)
        self.when("checkout --detach", fn=self.do_checkout)
        self.when("curl", out="200")
        self.when("systemctl is-active", out="active\n")

    def pending_text(self) -> str:
        pending = [self.stem(f) for f in self.tree.get(self.head, []) if self.stem(f) not in self.done]
        if not pending:
            return "\n   INFO  No pending migrations.  \n"
        return "\n".join(f"  {n} ........ Pending" for n in pending) + "\n"

    @staticmethod
    def stem(path: str) -> str:
        return path.rsplit("/", 1)[-1].removesuffix(".php")

    def do_checkout(self, argv):
        self.head = argv[-1]
        return 0, ""

    def do_migrate(self, argv):
        pending = [self.stem(f) for f in self.tree[self.head] if self.stem(f) not in self.done]
        if self.migrate_effect == "all":
            self.done.update(pending)
            return 0, "DONE"
        if self.migrate_effect == "partial":
            self.done.add(pending[0])
        return 1, "SQLSTATE failed"

    def do_rollback(self, argv):
        n = int(next(a for a in argv if a.startswith("--step=")).split("=")[1])
        self.rolled_back_steps = n
        if not self.rollback_ok:
            return 1, "rollback failed"
        for name in sorted(self.done - {"2026_01_01_000001_old"}, reverse=True)[:n]:
            self.done.discard(name)
        return 0, "ok"

    def run(self, argv, *, timeout=None, cwd=None, env=None):
        line = " ".join(argv)
        for word in self.fail:
            if word in line:
                self.calls.append(list(argv))
                self.sequence.append("FAIL " + word)
                return 1, "boom"
        for key in ("check-checkout-ownership", "install-and-optimize", "db:backup", "migrate --pretend", "migrate --force",
                    "migrate:rollback", "config:clear", "cache:clear", "route:clear", "view:clear", "queue:restart",
                    "check-runtime-writable", "checkout --detach"):
            if key in line:
                self.sequence.append(key + (" " + argv[-1] if key == "checkout --detach" else ""))
        return super().run(argv, timeout=timeout, cwd=cwd, env=env)


def sims_check(s: SimsBox, ref: str = SIMS_REF, sha: str = SHA_A, mode: str = "normal", base: str = ""):
    return sr.SimsRemote(s, "tester", "rel-1").check(ref, sha, mode, base)


class SimsCheckTests(Quiet):
    def refused(self, s: SimsBox, text: str, **kw) -> None:
        with self.assertRaises(sr.Refused) as ctx:
            sims_check(s, **kw)
        self.assertIn(text, str(ctx.exception))

    def test_good_main_based_candidate_is_accepted_and_says_where_the_base_came_from(self) -> None:
        lines = sims_check(SimsBox())
        self.assertIn("CHECK OK", lines[0])
        self.assertIn("no serving commit is recorded for SIMS; origin/main tip used", lines[0])

    def test_a_serving_commit_from_the_readiness_file_is_the_base_when_given(self) -> None:
        s = SimsBox()
        lines = sims_check(s, base=SHA_C)
        self.assertIn("serving commit given in the readiness file", lines[0])
        self.assertEqual(s.ran("refs/remotes/origin/main"), [])

    def test_candidate_not_containing_the_base_is_refused(self) -> None:
        s = SimsBox()
        s.when("merge-base --is-ancestor", rc=1)
        self.refused(s, "does not contain")
        s = SimsBox()
        s.when("merge-base --is-ancestor", rc=1)
        self.refused(s, "does not contain", base=SHA_C)

    def test_refs_outside_the_candidate_patterns_are_refused_before_any_fetch(self) -> None:
        for bad in ("main", "sifu-staging", "staging", "production", "feat/1-x", "test/3373-other"):
            s = SimsBox(ref=bad) if bad else SimsBox()
            self.refused(s, "not an allowed sims staging ref", ref=bad)
            self.assertEqual(s.ran("fetch"), [], bad)

    def test_commit_must_be_the_remote_tip(self) -> None:
        s = SimsBox()
        s.when("rev-parse refs/remotes/origin/" + SIMS_REF, out=SHA_B + "\n")
        self.refused(s, "remote tip")

    def test_stop_switch_and_wrong_box(self) -> None:
        s = SimsBox()
        s.files[sr.SWITCH_FILE] = "x"
        self.refused(s, "STOP switch")
        s = SimsBox()
        s.host = "srv1297548"
        self.refused(s, "not the sims staging box")

    def test_checkout_must_be_owned_by_the_app_user_and_clean_and_staging(self) -> None:
        s = SimsBox()
        s.owners[APP] = ("root", 0o755)
        self.refused(s, "not owned by www-data")
        s = SimsBox()
        s.when("status --porcelain", out=" M app/X.php\n")
        self.refused(s, "local changes")
        s = SimsBox()
        s.when("artisan env", out="INFO The application environment is [production].\n")
        self.refused(s, "not staging")
        s = SimsBox()
        s.when("config --get remote.origin.url", out="git@github.com:someone/else.git\n")
        self.refused(s, "git remote")

    def test_a_deploy_started_by_hand_blocks(self) -> None:
        for word in ("/bin/sh scripts/deployment/install-and-optimize-protected-runtime.sh /var/www/x", "php artisan migrate --force",
                     "composer install --no-dev"):
            s = SimsBox()
            s.ps_out += f"  4321 {word}\n"
            self.refused(s, "running by hand")

    def test_pending_migrations_already_in_the_database_block(self) -> None:
        s = SimsBox()
        s.tree[CUR] = [M_OLD, M_NEW1]  # current code has a migration the database has not run
        self.refused(s, "pending migration")

    def test_a_pending_migration_with_drop_is_refused_and_named(self) -> None:
        s = SimsBox(new_files=[M_NEW1], texts={M_NEW1: DROP_MIG})
        self.refused(s, "create_a")
        self.refused(SimsBox(new_files=[M_NEW1], texts={M_NEW1: DROP_MIG}), "drop")

    def test_one_bad_file_among_clean_ones_still_refuses(self) -> None:
        s = SimsBox(new_files=[M_NEW1, M_NEW2], texts={M_NEW1: CLEAN_MIG, M_NEW2: DROP_MIG})
        self.refused(s, "create_b")

    def test_an_already_applied_migration_is_not_scanned(self) -> None:
        s = SimsBox(new_files=[M_NEW1], texts={M_NEW1: DROP_MIG})
        s.done.add("2026_10_09_000001_create_a")
        lines = sims_check(s)
        self.assertIn("migrations to run: 0", lines[0])

    def test_clean_pending_migrations_are_accepted_and_counted(self) -> None:
        s = SimsBox(new_files=[M_NEW1, M_NEW2])
        self.assertIn("migrations to run: 2", sims_check(s)[0])

    def test_unreadable_migration_state_refuses(self) -> None:
        s = SimsBox()
        s.when("tinker", rc=1, out="boom")
        self.refused(s, "cannot read the migration state")

    def test_redeploy_served_skips_the_base_rule_only(self) -> None:
        s = SimsBox(sha=CUR)
        s.when("merge-base --is-ancestor", rc=1)
        self.assertIn("skipped: redeploy", sims_check(s, sha=CUR, mode="redeploy-served")[0])
        self.assertEqual(s.ran("merge-base"), [])
        s = SimsBox(sha=SHA_A)
        self.refused(s, "redeploy-served needs the commit staging serves now", mode="redeploy-served")
        s = SimsBox(sha=CUR)
        s.files[sr.SWITCH_FILE] = "x"
        self.refused(s, "STOP", sha=CUR, mode="redeploy-served")


def as_app_owner(argv: list[str]) -> bool:
    return argv[:4] == ["runuser", "-u", "www-data", "--"]


class SimsRunTests(Quiet):
    RUN = "20261009T053000Z-aaaaaaaa"

    def run_deploy(self, s: SimsBox, sha: str = SHA_A, mode: str = "normal") -> dict:
        s.held.add(sr.SimsRemote.own_lock)
        box = sr.SimsRemote(s, "pc-loop", "rel-1")
        box.write_state(self.RUN, run=self.RUN)
        box.run_body(self.RUN, SIMS_REF, sha, mode, "", 9)
        return json.loads(s.files[box.run_dir(self.RUN) + "/state.json"])

    def test_a_code_only_deploy_follows_the_runbook_in_order_and_never_migrates(self) -> None:
        s = SimsBox()
        state = self.run_deploy(s)
        self.assertEqual(state["status"], "ok", state)
        order = ["checkout" if k.startswith("checkout --detach") else k for k in s.sequence]
        self.assertEqual(order, ["check-checkout-ownership", "checkout", "install-and-optimize", "config:clear", "cache:clear",
                                 "route:clear", "view:clear", "queue:restart", "check-runtime-writable"])
        self.assertFalse(s.ran("db:backup"), "no backup without migrations")
        self.assertFalse(s.ran("migrate --force"))

    def test_every_application_command_runs_as_the_app_user_and_git_is_never_root(self) -> None:
        s = SimsBox()
        self.run_deploy(s)
        for argv in s.calls:
            joined = " ".join(argv)
            if argv[0] in ("ps", "curl", "systemctl") or "check-checkout-ownership" in joined or "check-runtime-writable" in joined:
                continue
            self.assertTrue(as_app_owner(argv), argv)
        self.assertTrue(s.ran("check-checkout-ownership"))
        for argv in s.ran("git"):
            self.assertTrue(as_app_owner(argv), argv)

    def test_the_gate_scripts_run_with_the_app_owner_flag(self) -> None:
        s = SimsBox()
        self.run_deploy(s)
        self.assertTrue(s.ran("check-runtime-writable.sh", "--owner=www-data"))
        self.assertTrue(s.ran("check-checkout-ownership.sh", "--owner=www-data"))
        self.assertTrue(s.ran("--uncached-staging"))

    def test_nothing_in_the_deploy_can_name_production_or_cache_config(self) -> None:
        s = SimsBox()
        self.run_deploy(s)
        blob = "\n".join(" ".join(a) for a in s.calls)
        for word in ("production", "--force-with", "config:cache", "route:cache", "db:seed", "reset --hard"):
            self.assertNotIn(word, blob)

    def test_migrations_run_pretend_then_backup_then_migrate(self) -> None:
        s = SimsBox(new_files=[M_NEW1, M_NEW2])
        state = self.run_deploy(s)
        self.assertEqual(state["status"], "ok", state)
        keys = [k for k in s.sequence if k in ("migrate --pretend", "db:backup", "migrate --force")]
        self.assertEqual(keys, ["migrate --pretend", "db:backup", "migrate --force"])
        self.assertIn("migrations_run=2", state["result_line"])
        backup = s.ran("db:backup")[0]
        self.assertIn("--no-email", backup)
        self.assertIn("--no-onedrive", backup)
        self.assertTrue(as_app_owner(backup))

    def test_a_destructive_statement_in_the_pretend_output_stops_before_backup_and_migrate(self) -> None:
        s = SimsBox(new_files=[M_NEW1])
        s.pretend_out = "alter table `widgets` drop column `colour`"
        state = self.run_deploy(s)
        self.assertEqual(state["status"], "failed")
        self.assertEqual(state["exit"], 70)
        self.assertFalse(s.ran("db:backup"))
        self.assertFalse(s.ran("migrate --force"))
        self.assertEqual(s.head, CUR, "the previous code is put back")

    def test_a_failed_backup_means_nothing_is_migrated(self) -> None:
        s = SimsBox(new_files=[M_NEW1])
        s.fail.add("db:backup")
        state = self.run_deploy(s)
        self.assertEqual(state["status"], "failed")
        self.assertFalse(s.ran("migrate --force"))
        self.assertEqual(s.head, CUR)

    def test_a_failed_migration_rolls_back_only_what_ran_then_restores_the_code(self) -> None:
        s = SimsBox(new_files=[M_NEW1, M_NEW2])
        s.migrate_effect = "partial"
        state = self.run_deploy(s)
        self.assertEqual(state["status"], "failed")
        self.assertTrue(s.ran("migrate:rollback", "--step=1"))
        self.assertFalse(s.ran("--step=2"), "rolling back more than ran would undo older migrations")
        self.assertEqual(s.done, {"2026_01_01_000001_old"})
        self.assertEqual(s.head, CUR)

    def test_a_failed_migration_that_ran_nothing_is_not_rolled_back(self) -> None:
        s = SimsBox(new_files=[M_NEW1])
        s.migrate_effect = "none"
        state = self.run_deploy(s)
        self.assertEqual(state["status"], "failed")
        self.assertFalse(s.ran("migrate:rollback"))
        self.assertEqual(s.head, CUR)

    def test_a_failed_rollback_leaves_the_code_for_a_person(self) -> None:
        s = SimsBox(new_files=[M_NEW1, M_NEW2])
        s.migrate_effect = "partial"
        s.rollback_ok = False
        state = self.run_deploy(s)
        self.assertEqual(state["status"], "failed")
        self.assertNotEqual(s.head, CUR, "no automatic code restore over a half-rolled-back schema")

    def test_a_failed_install_restores_the_previous_code(self) -> None:
        s = SimsBox()
        calls = {"n": 0}

        def flaky(argv):
            calls["n"] += 1
            return (1, "npm failed") if calls["n"] == 1 else (0, "")
        s.when("install-and-optimize", fn=flaky)
        state = self.run_deploy(s)
        self.assertEqual(state["status"], "failed")
        self.assertEqual(s.head, CUR)
        self.assertEqual(calls["n"], 2, "the installer ran once for the candidate and once for the previous code")

    def test_an_unexpected_pending_migration_after_checkout_stops_the_lane(self) -> None:
        s = SimsBox()
        s.when("migrate:status --pending", out="  2026_12_12_000001_surprise ..... Pending\n")
        state = self.run_deploy(s)
        self.assertEqual(state["status"], "failed")
        self.assertFalse(s.ran("migrate --force"))

    def test_stop_switch_before_checkout_refuses_without_touching_the_code(self) -> None:
        s = SimsBox()
        s.files[sr.SWITCH_FILE] = "x"
        state = self.run_deploy(s)
        self.assertEqual(state["status"], "refused")
        self.assertFalse(s.ran("checkout --detach"))

    def test_ownership_failure_stops_before_checkout(self) -> None:
        s = SimsBox()
        s.fail.add("check-checkout-ownership")
        state = self.run_deploy(s)
        self.assertEqual(state["status"], "failed")
        self.assertFalse(s.ran("checkout --detach"))

    def test_read_back_must_agree_or_the_run_fails(self) -> None:
        for mutate in ("login", "worker", "head"):
            s = SimsBox()
            if mutate == "login":
                s.when("curl", out="500")
            elif mutate == "worker":
                s.when("systemctl is-active", out="failed\n")
            else:
                s.when("rev-parse HEAD", out=SHA_B + "\n")
            state = self.run_deploy(s)
            self.assertEqual(state["status"], "failed", mutate)

    def test_a_redeploy_of_the_served_commit_changes_no_schema(self) -> None:
        s = SimsBox(sha=CUR)
        state = self.run_deploy(s, sha=CUR, mode="redeploy-served")
        self.assertEqual(state["status"], "ok", state)
        self.assertFalse(s.ran("migrate --force"))
        self.assertFalse(s.ran("db:backup"))

    def test_a_runner_that_cannot_read_the_current_commit_changes_nothing(self) -> None:
        s = SimsBox()
        s.when("rev-parse HEAD", rc=128, out="fatal")
        state = self.run_deploy(s)
        self.assertEqual(state["status"], "failed")
        self.assertFalse(s.ran("checkout --detach"))

    def test_sims_start_spawns_a_detached_runner(self) -> None:
        s = SimsBox()
        lines = sr.SimsRemote(s, "pc-loop", "rel-1").start(SIMS_REF, SHA_A, "normal", "")
        self.assertTrue(lines[0].startswith("STARTED run="))
        self.assertEqual(s.spawned[0][2], 9)

    def test_sims_verify_reads_head_pending_login_and_worker(self) -> None:
        s = SimsBox(sha=CUR)
        ok, text = sr.SimsRemote(s).verify(CUR)
        self.assertTrue(ok, text)
        s.when("migrate:status --pending", out="  2026_12_12_000001_x ..... Pending\n")
        self.assertFalse(sr.SimsRemote(s).verify(CUR)[0])


# ------------------------------------------------- scratch fixture (real git) ----

import getpass  # noqa: E402
import os  # noqa: E402
import shutil  # noqa: E402
import subprocess  # noqa: E402
import tempfile  # noqa: E402
from unittest import mock  # noqa: E402

FAKE_ARTISAN = r"""#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
app = Path(__file__).resolve().parent
state = app / ".fixture-state"
state.mkdir(exist_ok=True)
ran_path, log = state / "ran.json", state / "calls.log"
ran = json.loads(ran_path.read_text()) if ran_path.exists() else ["2026_01_01_000001_old"]
files = sorted(p.stem for p in (app / "database" / "migrations").glob("*.php"))
pending = [f for f in files if f not in ran]
args = sys.argv[1:]
with open(log, "a") as fh:
    fh.write(" ".join(args) + "\n")
cmd = args[0] if args else ""
if cmd == "env":
    print("   INFO  The application environment is [staging].")
elif cmd == "tinker":
    print(json.dumps(ran))
elif cmd == "migrate:status":
    print("\n   INFO  No pending migrations.  " if not pending else "\n".join(f"  {n} ........ [1] Pending" for n in pending))
elif cmd == "migrate" and "--pretend" in args:
    for n in pending:
        print((state / "pretend.txt").read_text() if (state / "pretend.txt").exists() else f"create table `t_{n[-6:]}` (`id` int)")
elif cmd == "migrate":
    fail = (state / "fail_migrate").exists()
    for n in pending:
        ran.append(n)
        ran_path.write_text(json.dumps(ran))
        if fail:
            print("SQLSTATE: boom"); sys.exit(1)
    ran_path.write_text(json.dumps(ran))
    print("DONE")
elif cmd == "migrate:rollback":
    step = int(next(a for a in args if a.startswith("--step=")).split("=")[1])
    base = ["2026_01_01_000001_old"]
    keep = ran[:-step] if step else ran
    ran_path.write_text(json.dumps(keep or base))
    print("rolled back")
elif cmd == "db:backup":
    (state / "backup.done").write_text("x")
    print("backup ok")
else:
    print("ok " + cmd)
"""

CLEAN_FIXTURE_MIGRATION = MigrationScannerTests.CREATE


class FixtureSys(sr.RealSys):
    def hostname(self):
        return sr.EXPECT_HOST["sims"]


class SimsScratchFixtureTests(Quiet):
    """The SIMS lane against a real git repository, a real scanner and real subprocesses, with fake artisan and runuser."""

    def git(self, cwd: Path, *args: str) -> str:
        env = {**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@e",
               "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_SYSTEM": "/dev/null"}
        return subprocess.run(["git", *args], cwd=cwd, env=env, capture_output=True, text=True, check=True).stdout.strip()

    def setUp(self) -> None:
        super().setUp()
        self.tmp = Path(tempfile.mkdtemp(prefix="sims-fixture-"))
        self.addCleanup(shutil.rmtree, self.tmp, True)
        bin_dir = self.tmp / "bin"
        bin_dir.mkdir()
        for name, body in (("runuser", '#!/bin/sh\nshift 3\nexec "$@"\n'), ("php", '#!/bin/sh\nexec python3 "$@"\n'),
                           ("curl", '#!/bin/sh\necho 200\n'), ("systemctl", '#!/bin/sh\necho active\n')):
            (bin_dir / name).write_text(body)
            (bin_dir / name).chmod(0o755)
        patcher = mock.patch.dict(os.environ, {"PATH": f"{bin_dir}{os.pathsep}{os.environ['PATH']}", "GIT_CONFIG_GLOBAL": "/dev/null",
                                               "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_TERMINAL_PROMPT": "0"})
        patcher.start()
        self.addCleanup(patcher.stop)
        origin = self.tmp / "origin.git"
        self.app = self.tmp / "app"
        self.git(self.tmp, "init", "-q", "--bare", "-b", "main", str(origin))
        self.git(self.tmp, "clone", "-q", str(origin), str(self.app))
        (self.app / "database" / "migrations").mkdir(parents=True)
        (self.app / "scripts" / "deployment").mkdir(parents=True)
        (self.app / "database" / "migrations" / "2026_01_01_000001_old.php").write_text(CLEAN_FIXTURE_MIGRATION)
        for script in ("check-checkout-ownership.sh", "install-and-optimize-protected-runtime.sh", "check-runtime-writable.sh"):
            path = self.app / "scripts" / "deployment" / script
            path.write_text('#!/bin/sh\necho "$0 $@" >> "$(dirname "$0")/../../.fixture-state/scripts.log"\nexit 0\n')
            path.chmod(0o755)
        (self.app / "artisan").write_text(FAKE_ARTISAN)
        (self.app / "artisan").chmod(0o755)
        (self.app / ".fixture-state").mkdir()
        (self.app / ".gitignore").write_text(".fixture-state/\n")
        self.git(self.app, "add", "-A")
        self.git(self.app, "commit", "-qm", "base")
        self.git(self.app, "push", "-q", "origin", "main")
        self.base = self.git(self.app, "rev-parse", "HEAD")

    def candidate(self, name: str, files: dict[str, str]) -> str:
        branch = f"test/9{name}-staging-candidate"
        self.git(self.app, "checkout", "-q", "-b", branch, "main")
        for rel, text in files.items():
            (self.app / "database" / "migrations" / rel).write_text(text)
        self.git(self.app, "add", "-A")
        self.git(self.app, "commit", "-qm", f"candidate {name}")
        sha = self.git(self.app, "rev-parse", "HEAD")
        self.git(self.app, "push", "-q", "origin", branch)
        self.git(self.app, "checkout", "-q", "--detach", self.base)  # staging serves the base
        self.git(self.app, "branch", "-q", "-D", branch)
        return branch

    def box(self) -> sr.SimsRemote:
        tmp = self.tmp

        class Fixture(sr.SimsRemote):
            app = str(tmp / "app")
            owner = getpass.getuser()
            remote_url = str(tmp / "origin.git")
            own_lock = str(tmp / "sims.lock")
            log_path = str(tmp / "deploy.log")
            busy_words = ()

            def www(self, *argv):
                return ["runuser", "-u", "www-data", "--", *argv]

        for target, value in (("STATE_DIR", str(tmp / "state")), ("SWITCH_FILE", str(tmp / "STOP"))):
            patcher = mock.patch.object(sr, target, value)
            patcher.start()
            self.addCleanup(patcher.stop)
        return Fixture(FixtureSys(), "tester", "rel-1")

    def deploy(self, branch: str, box: sr.SimsRemote | None = None) -> dict:
        box = box or self.box()
        sha = self.git(self.app, "ls-remote", "origin", f"refs/heads/{branch}").split()[0]
        fd = box.s.take_lock(box.own_lock)
        self.assertIsNotNone(fd)
        self.addCleanup(os.close, fd)
        box.preflight(branch, sha, "normal", "", own_lock_counts=False)
        box.s.mkdir(box.run_dir("20261009T053000Z-aaaaaaaa"))
        box.write_state("20261009T053000Z-aaaaaaaa", run="x")
        box.run_body("20261009T053000Z-aaaaaaaa", branch, sha, "normal", "", fd)
        return json.loads((Path(box.run_dir("20261009T053000Z-aaaaaaaa")) / "state.json").read_text()) | {"sha": sha}

    def state_file(self, name: str) -> str:
        path = self.app / ".fixture-state" / name
        return path.read_text() if path.exists() else ""

    def test_a_clean_migration_is_scanned_backed_up_then_migrated_and_the_head_moves(self) -> None:
        branch = self.candidate("1", {"2026_10_09_000001_create_widgets.php": CLEAN_FIXTURE_MIGRATION})
        state = self.deploy(branch)
        self.assertEqual(state["status"], "ok", state)
        self.assertEqual(self.git(self.app, "rev-parse", "HEAD"), state["sha"])
        self.assertIn("2026_10_09_000001_create_widgets", json.loads(self.state_file("ran.json")))
        calls = self.state_file("calls.log").splitlines()
        order = [c.split(" ")[0] + (" pretend" if "--pretend" in c else "") for c in calls if c.split(" ")[0] in ("migrate", "db:backup")]
        self.assertEqual(order, ["migrate pretend", "db:backup", "migrate"])
        self.assertTrue(self.state_file("backup.done"))
        self.assertIn("--uncached-staging", self.state_file("scripts.log"))
        self.assertIn("--owner=", self.state_file("scripts.log"))

    def test_a_dropping_migration_is_refused_at_check_time_from_the_real_git_object(self) -> None:
        branch = self.candidate("2", {"2026_10_09_000002_drop_things.php": MigrationScannerTests().wrap("Schema::dropIfExists('widgets');")})
        box = self.box()
        sha = self.git(self.app, "ls-remote", "origin", f"refs/heads/{branch}").split()[0]
        with self.assertRaises(sr.Refused) as ctx:
            box.check(branch, sha, "normal", "")
        self.assertIn("drop_things", str(ctx.exception))
        self.assertEqual(self.git(self.app, "rev-parse", "HEAD"), self.base, "nothing was checked out")
        self.assertNotIn("migrate", self.state_file("calls.log").replace("migrate:status", ""))

    def test_a_pretend_output_with_a_drop_stops_before_backup_and_restores_the_code(self) -> None:
        branch = self.candidate("3", {"2026_10_09_000003_alter.php": CLEAN_FIXTURE_MIGRATION})
        (self.app / ".fixture-state" / "pretend.txt").write_text("alter table `x` drop column `y`")
        state = self.deploy(branch)
        self.assertEqual(state["status"], "failed")
        self.assertFalse(self.state_file("backup.done"))
        self.assertEqual(self.git(self.app, "rev-parse", "HEAD"), self.base)

    def test_a_failure_halfway_rolls_back_only_what_ran_and_restores_the_previous_code(self) -> None:
        branch = self.candidate("4", {"2026_10_09_000004_a.php": CLEAN_FIXTURE_MIGRATION, "2026_10_09_000005_b.php": CLEAN_FIXTURE_MIGRATION})
        (self.app / ".fixture-state" / "fail_migrate").write_text("x")
        state = self.deploy(branch)
        self.assertEqual(state["status"], "failed")
        calls = self.state_file("calls.log")
        self.assertIn("migrate:rollback --step=1 --force", calls)
        self.assertNotIn("--step=2", calls)
        self.assertEqual(json.loads(self.state_file("ran.json")), ["2026_01_01_000001_old"])
        self.assertEqual(self.git(self.app, "rev-parse", "HEAD"), self.base)
        self.assertTrue(self.state_file("backup.done"), "the backup was taken before the migration")

    def test_the_real_system_lock_probe_sees_a_held_lock_and_a_free_one(self) -> None:
        s = FixtureSys()
        lock = str(self.tmp / "probe.lock")
        self.assertFalse(s.lock_held(lock))
        fd = s.take_lock(lock)
        self.assertTrue(s.lock_held(lock))
        self.assertIsNone(s.take_lock(lock), "a second holder is refused")
        os.close(fd)
        self.assertFalse(s.lock_held(lock))


if __name__ == "__main__":
    unittest.main()
