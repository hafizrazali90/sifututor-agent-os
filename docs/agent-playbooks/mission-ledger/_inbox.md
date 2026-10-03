# Mission Ledger Inbox

Use this file for quick capture when the project, parent mission, or next action
is not clear yet. During save-session or task-router, move items into a project
file when they become clear.

## Captured Items

Captured 04/10/2026 from the monitoring production release (umbrella issue #240, which stays open). Parent mission: #240. Detail: `.agent-os/handoffs/2026-10-03-monitoring-production-ledger-claude.md` and the addendum beside it.

- Ripple browser error capture: allowlist is fixed (ripple-suite #1493) but no `NEXT_PUBLIC_SENTRY_*` values are set on the server and the page security policy (connect-src) blocks the provider; `SENTRY_RELEASE` is a static label. Needs a reviewed CSP change and a full release. Not started.
- Ripple running app: no error has been seen delivered to Sentry yet; only the flag and DSN presence are proven.
- Analytics: after the 05/10 02:13 MYT run, confirm exit 0 and no `production_guard_failed`; open follow-up sims-owner-analytics #118 (reconcile-tail test, in-snapshot idle gaps, measure the real source idle limit).
- Finch box disk (finch host, shared with Analytics and SIMS staging): the Finch MSSQL backup folder holds 91 GB in 511 files and grows by a nightly differential; no retention owner found. Finch is reuse-only here, so this needs its own task.
- Kelasapp staging logging and Sentry: Hafiz chose production only; the staging Sentry project has never received an event.
- LLS staging: rebuild or retire is still Hafiz's decision (answered "not yet").
- Not built: uptime monitors for LLS and others, SSL and domain expiry heartbeats, Telegram route, automatic investigator, central collection of SIMS log-loss counters.
- Email receipt for the LLS website and Ripple Sentry test alerts not confirmed by Hafiz.
