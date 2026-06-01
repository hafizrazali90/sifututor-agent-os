# Monitor Production Logs Playbook

Use this when Hafiz asks to monitor production logs, check Sentry/BetterStack,
verify observability after a deploy, or watch for production regressions.

## Safety

- Default to read-only checks.
- Never read or modify `.env*`, production secrets, or `live/`.
- Do not deploy, merge, migrate, or edit production from this playbook.
- A log marker is allowed only when Hafiz asks for verification or when it is
  clearly useful; it writes one harmless Laravel `info` log.
- Do not print tokens. Report only whether tokens/config are present.
- Prefer public HTTP smoke checks over `php artisan route:list` on production;
  route-list can boot database-backed providers and create noisy log entries on
  cPanel/HostArmada.

## Standard Check

Run from the umbrella workspace:

```bash
.agents/skills/monitor-production-logs/scripts/prod-monitor.sh
```

For end-to-end log-channel proof:

```bash
.agents/skills/monitor-production-logs/scripts/prod-monitor.sh --marker
```

## What To Look For

Regression patterns from the 2026-05-29 production hotfix:

- FIUU declined callback trying to write `status = failed`
- `Call to undefined method App\Services\ClassService::getStuckClasses()`
- bundled FIUU callback calling protected `verifyBundledPayment()`
- new `production.ERROR` or `production.CRITICAL` after the latest marker
- `LOG_CHANNEL` not equal to `stack`
- `LOG_STACK` missing `daily` or `logtail`
- Logtail token or source-specific endpoint missing
- Sentry DSN missing

## Report Shape

Use plain language first:

```text
Production log watch:
- App is on commit <sha>, maintenance <on/off>.
- Sentry <active/not active>, BetterStack <active/not active>.
- New critical errors: <none/list>.
- Old hotfix errors returned: <yes/no>.
- Git status: <clean or intentional server-only files>.
- Next: <watch longer/fix issue/ask server admin>.
```

If an issue appears, explain:

1. what happened
2. what user/admin flow it affects
3. whether it is new or a known baseline
4. safest next action
