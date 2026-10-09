# Staging Deploy From The Home PC

Owner of how the home PC deploys Ripple and SIMS STAGING, and how it closes the
staging gates S1, S2 and S3 of a release by itself (issue #356). Production is
never reachable from here and the production go is always Hafiz's.

## Plain summary

- The PC has its own key to the two staging boxes, the same access the Mac has.
- A plain script, not Claude, does the deploy. The safety is in the script and
  in the release loop, not in a special server user.
- The script knows two targets only, `ripple` and `sims`. There is no
  environment argument, so there is nothing to type that means production.
- Ripple: the PC deploys a release branch tip only when it is the exact commit
  on GitHub, contains what production serves, and adds no migration, deploy
  script or dependency file. Anything else is refused and a Mac session does it.
- SIMS: the PC deploys a main-based candidate branch. New migrations are
  scanned first, a database backup is taken, and a failed migration is rolled
  back and the previous code restored.
- Then the loop smoke tests staging itself (a scripted login and, with
  Playwright, the change smoke) and carries on to Prod readiness 100 percent.

## What the PC can and cannot do

| The PC can | The PC cannot, and why |
| --- | --- |
| Check a candidate against every staging rule (`check`) | Deploy production: there is no production target in the script, and no production key on the PC |
| Deploy Ripple staging with the sealed controller | Merge, or push to main: the loop never does either |
| Deploy SIMS staging following the staging runbook | Run a Ripple migration or a confirm phrase: those stay Mac sessions |
| Run an unattended SIMS migration lane (backup first, scan, rollback) | Run a SIMS migration that drops, renames, truncates, deletes all rows or changes a column: refused, a person runs it |
| Read back the deployed commit from the server | Run the SIMS test suite: the PC has no PHP, Composer or MySQL (run SIMS tests on the finch box or the Mac) |
| Run the normal smoke and the change smoke with Playwright | Roll back by itself except inside the SIMS migration lane |

## Access (recorded 09/10/2026, no key body here)

- Key: `~/.ssh/id_ed25519_pc_agent` on the PC (user `hafiz`, inside Ubuntu).
- Aliases in the PC's `~/.ssh/config`: `staging` (the KVM8 Ripple box, root) and
  `finch` (the SIMS staging box, root). Same logins as the Mac. Both were proven
  on 09/10/2026.
- Staging only. No production credential is on the PC and none may be copied
  there.
- To revoke: on both boxes remove the single line ending `homepc-agent 09/10/2026`
  from `/root/.ssh/authorized_keys`. Nothing else was added to either box.
- The PC keeps Claude's usual hooks and rules.

## The rules the script applies

Every rule is checked twice: on the PC first, then again on the box by
`staging_remote.py`, which is sent over ssh and trusts nothing from the PC.

| Rule | Ripple | SIMS |
| --- | --- | --- |
| Target and box | `ripple` on host `srv1297548` | `sims` on host `srv1701812` |
| STOP switch | `/etc/sifututor-pc-deploy/STOP` on the box, or `~/.config/sifututor/staging-deploy.STOP` on the PC | same |
| Branch name | `release/<issue>-<name>`, not `release/1080-*` | `release/<issue>-<name>`, `release-base/<issue>-<name>`, or a `test`, `fix`, `chore`, `feat` branch named `...staging-candidate` or `...staging-serving` |
| Exact commit | 40 hex characters and equal to the branch tip on GitHub | same, checked on the box after its own fetch |
| Release base | contains the commit production serves (`.serving-prod.json`) | contains the serving commit given in the readiness file, or, because SIMS records none, the `origin/main` tip (the report says which) |
| Nobody else is deploying | every deploy and migration lane lock is probed; the PC's own lock holds one deploy at a time | no installer, composer or artisan job is running by hand; the PC's own lock holds one deploy at a time |
| Nobody is mid-procedure | `repo-staging` sits clean on the commit staging serves | tracked files in the checkout are clean, no pending migration is already waiting |
| What may change | no new SQL migration, deploy script, `package.json`, lockfile, `next.config.*`, `.github/`, Dockerfile or ecosystem file | new migrations are allowed only if clean (below) |
| Build tree | no root-owned files in `node_modules` or `.next` (the controller refuses these after 3 seconds) | checkout owned by `www-data`, ownership script, runtime writable gate |
| Bounded run | 60 minutes | 40 minutes |
| Log | `/var/log/apps/ripple-staging-pc.log`, one line with who, what and when in MYT and UTC | `/var/log/sims-staging-pc-deploy.log`, same shape |
| Read-back | PM2 commit, `repo-staging` HEAD, the deploy log line and the local login page agree | HEAD, no pending migration, login page 200 or 302 and the queue worker active |

### Redeploy of the commit staging already serves

`--mode redeploy-served` skips only the release-base rule. It needs the commit
and ref staging serves right now (for Ripple PM2 and the deploy log must agree),
so it can never put different code on staging. It exists to prove the script on
a shared box, and for a repair redeploy after a build tree fix. Every other rule
still applies.

### The SIMS migration lane

1. Before anything runs, every migration the candidate would run (files not yet
   in the database) is scanned. The scanner reads only `up()` and refuses `drop`,
   `truncate`, `rename`, `delete from` or `->delete()`, `->change()` and `MODIFY`
   or `CHANGE` column rewrites (they can cut data), a shell call, and an Artisan
   wipe. A file it cannot read is refused. Tested on all 436 real migration
   files of sifu-tutor `origin/main`: 390 clean, 46 refused, every refusal a real
   drop, rename or column change.
2. After checkout and build, `migrate --pretend` prints the SQL and it is
   scanned again. Pending migrations that were not in the first scan stop the lane.
3. `php artisan db:backup --no-email --no-onedrive` runs as `www-data`. If it
   fails nothing is migrated and the previous code is put back.
4. `php artisan migrate --force`. On failure the lane counts how many of its own
   migrations actually ran and runs `migrate:rollback --step=<that number>`
   (never more, or older migrations would be undone), then puts the previous
   code back. If the rollback itself fails the state is `failed` and a person
   decides; the backup is recorded in the run log.
5. A plain update, an insert without a where clause and a seeder are not
   scanned: the lane never runs a seeder, and data statements stay a person's call.

## Gates S1, S2, S3 (and S4) in the loop

Create the readiness file with `--staging-deploy ripple|sims` and the loop owns
the staging gates. Without that flag S1 to S3 stay Mac gates, exactly as before.

| Gate | Owner | What the PC does | Evidence recorded |
| --- | --- | --- | --- |
| S1 candidate identified | pc | reads the branch tip on GitHub, runs `check` on the box | the exact ref and commit, and the box's `CHECK OK` line |
| S2 staging deployed | pc | `check` again, `start`, polls `status`, then `verify` | the `STARTED` line, the `RESULT` line with seconds, `VERIFY OK`, and the commit read back from the server |
| S3 staging smoke | pc | confirms staging still serves the commit, scripted login on the staging lane, then each change smoke command | each command, exit code and a masked output tail; lane values are never shown |
| S4 promotion holds the change | pc | Ripple: the branch contains the staged commit. SIMS: same changed lines on a different base (`git diff -U0` line sets, docs-only extras allowed) | the counts of staged, missing and extra lines |

S1 waits for items 2, 3, 4, 5, 7 and 8, so staging is not used for a candidate
that is still changing. A pushed fix, or a moved candidate branch, resets S1 to
S4 and staging is redeployed on the new commit. A refusal on the box blocks the
loop after the second try, with the box's own reason (for example "needs a Mac
session"). A stop (a `STOP` file) ends the polling but not a deploy already
running on the box; on `resume` the loop attaches to that run and never starts a
second one.

### The S3 environment (Playwright without sudo)

Every change smoke command runs with these set, so they are not forgotten:

```text
PLAYWRIGHT_HOST_PLATFORM_OVERRIDE=ubuntu24.04-x64
LD_LIBRARY_PATH=$HOME/.local/chromium-libs/root/usr/lib:$HOME/.local/chromium-libs/root/usr/lib/x86_64-linux-gnu
```

Plus `PLAYWRIGHT_BASE_URL` for the staging site and the lane values the test
harness reads (Ripple: `TEST_USER_EMAIL` and `TEST_USER_PASSWORD` from
`ripple-staging-smoke.conf`). A change smoke command must start with
`npx playwright test `, `npm run test:`, `bash scripts/qa/` or be `builtin:login`
or `builtin:page /path`, and must be one plain command with no shell characters.
A release with no change smoke command needs a named exception.

## Commands

Start a Ripple release on the staging route:

```bash
python3 scripts/agent-checks/release_readiness.py init --release "NAME" \
  --repo ripple-suite --branch release/<issue>-<name> --pr <n> --issue <issue> \
  --route staging-first --route-by "Hafiz, chat DD/MM/YYYY" \
  --serving-commit <sha from .serving-prod.json> \
  --approval "Hafiz, chat DD/MM/YYYY: push fixes to the release branch" \
  --staging-deploy ripple \
  --staging-approval "Hafiz, chat DD/MM/YYYY: PC may deploy STAGING only" \
  --staging-smoke-command "npm run test:staging-luna-auth-smoke" \
  --e2e-command "npx playwright test <spec>" --out readiness.json
python3 scripts/agent-checks/pc_release.py start readiness.json --dry-run
python3 scripts/agent-checks/pc_release.py start readiness.json
python3 scripts/agent-checks/pc_release.py deploy-status RELEASE_ID
```

Start a SIMS release (the candidate is a main-based branch; the PC has no PHP, so
item 4 is not applicable and the suite is the TypeScript check):

```bash
python3 scripts/agent-checks/release_readiness.py init --release "NAME" \
  --repo sifu-tutor --branch release/<issue>-<name> --pr <n> --issue <issue> \
  --route staging-first --route-by "Hafiz, chat DD/MM/YYYY" \
  --serving-commit <sha from git rev-parse HEAD on the production checkout> \
  --staging-deploy sims --staging-ref test/<issue>-staging-candidate \
  --staging-approval "Hafiz, chat DD/MM/YYYY: PC may deploy STAGING only" \
  --staging-smoke-command "builtin:login" \
  --na 4="PHP tests cannot run on the PC; SIMS tests run on the finch box or the Mac" \
  --e2e-exception "tooling unavailable: no PHP on the PC" --out readiness.json
```

SIMS Claude jobs (the drafting and review items) need the project to track
`.claude/settings.json`, which sifu-tutor does not yet, so for a SIMS release a
Mac session prepares the release pack and the loop owns the staging gates.

One-off use without the loop (Mac or PC):

```bash
python3 scripts/agent-checks/staging_deploy.py check  ripple --ref release/<issue>-<name> --sha <40 hex>
python3 scripts/agent-checks/staging_deploy.py deploy ripple --ref release/<issue>-<name> --sha <40 hex>
python3 scripts/agent-checks/staging_deploy.py status ripple
python3 scripts/agent-checks/staging_deploy.py verify ripple <40 hex>
python3 scripts/agent-checks/pc_release.py staging-switch ripple off   # STOP: new deploys refused
python3 scripts/agent-checks/pc_release.py staging-switch ripple on
```

## What it refuses, and who does it instead

| Refusal | Why | Who |
| --- | --- | --- |
| A Ripple release that adds or changes a migration | confirm-phrase lanes are written inside the controller | a Mac session |
| A Ripple release that changes deploy scripts, `package.json`, a lockfile, `next.config.*` | they change what the build runs as `deploy` | a Mac session |
| Any rollback | rollback goes through a frozen `release/<issue>-rollback-<sha8>` ref | a Mac session |
| A SIMS migration that drops, renames, truncates, deletes or changes a column | data loss risk | a Mac session |
| A release that does not contain the production base | a stale base would invalidate S4 | rebuild the branch |
| A deploy while a lock is held, a person is mid-procedure, or STOP is on | one deploy at a time on a shared box | wait, then retry |
| Production, main, or anything outside the two staging boxes | not in the script | Hafiz |

## Known limits

- Claude jobs on the PC have no `ssh` or deploy command on their allow list and
  cannot run the deploy script. But repo test code that a builder job runs is the
  same Ubuntu user, so treat the PC key as readable by that code. The key reaches
  the two staging boxes only; the production go and production credentials stay
  off the PC.
- A person (or a hook) can still change staging by hand at any time: the shared
  boxes are used by Mac sessions too. On 09/10/2026 a Mac session moved SIMS
  staging to a newer commit 36 seconds after the PC proof redeploy finished. The
  script reads and checks the box right before it acts and again at the end;
  it cannot stop someone acting between.
- Lane note (09/10/2026): the admin-style logins in `ripple-staging-smoke.conf`
  (Superadmin), `staging-smoke.conf` and `sims-staging-browser-qa.conf` were
  rejected by both staging sites that day (Ripple answered 401 "Invalid email or
  password"; SIMS sent the login back to `/login`). The scripted smoke therefore
  uses the non-admin `staging-lifecycle-qa.conf` login, which works on both
  sites. Hafiz re-sets the admin lane with `setup-sims-browser-qa-lane.sh`.
- STOP does not kill a deploy that is already running; only the box finishes it.
- A manual deploy by a person on the SIMS box takes no lock the PC can see; the
  process guard and the clean-checkout rule catch most overlaps, not all.
- The box program is left under `/var/lib/sifututor-pc-deploy/bin/` (one file
  per version, content-addressed, no secrets). Remove old ones with `rm`.
- A root session that runs a test in the staging app folder can leave root-owned
  files in `node_modules` and block the Ripple controller. The check names them;
  `chown -R deploy:deploy` on that one folder repairs it.

## Related

- [unattended-jobs.md](unattended-jobs.md) (the release readiness loop)
- [home-pc-worker.md](home-pc-worker.md) (the machine and its access)
- [agent-access-map.md](agent-access-map.md) (lane 42)
- [release-deploy-live-monitoring.md](release-deploy-live-monitoring.md)
