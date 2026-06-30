# Agent OS Project Profile Template

Use this template for a product repo's local Agent OS profile.

Plain meaning:

```text
This is the small local adapter that tells the shared Agent OS how this repo
actually works.
```

Do not copy the whole umbrella Agent OS into the product repo. Keep shared rules
in the umbrella repo and keep this profile focused on local facts.

## Profile Status

| Field | Value |
| --- | --- |
| Project | `<repo name>` |
| Adoption state | `<not adopted | baseline present | profile drafted | profile verified | ready for internal agent use | ready for developer staff use>` |
| Last verified | `<YYYY-MM-DD or not yet>` |
| Verified by | `<person/agent>` |
| Main owner | `<Hafiz/team/person if known>` |
| Profile location | `<AGENTS.md, CLAUDE.md, docs/...>` |

## Plain Summary

```text
<One short paragraph explaining what this repo does, who uses it, and what kind
of work usually happens here.>
```

## Repo Facts

| Field | Value |
| --- | --- |
| Purpose | `<what this project is for>` |
| Primary users | `<staff/admin/tutor/parent/student/customer/internal>` |
| Stack/runtime | `<Laravel/Next/React Native/etc>` |
| Main source docs | `<AGENTS.md, CLAUDE.md, TESTING.md, docs/...>` |
| Active task state | `<none | .claude/tasks/active.json | other>` |
| Important modules | `<short list>` |
| Known local conventions | `<routing, naming, testing, branch, release habits>` |

## Commands

Use exact commands when verified. Use `unknown` when not verified.

| Purpose | Command | Verified? | Notes |
| --- | --- | --- | --- |
| Install/setup | `<command or unknown>` | `<yes/no>` | `<note>` |
| Lint/typecheck | `<command or unknown>` | `<yes/no>` | `<note>` |
| Unit/feature tests | `<command or unknown>` | `<yes/no>` | `<note>` |
| E2E/human-journey tests | `<command or unknown>` | `<yes/no>` | `<note>` |
| Build | `<command or unknown>` | `<yes/no>` | `<note>` |
| Local dev server | `<command or unknown>` | `<yes/no>` | `<note>` |

## Evidence Expectations

| Work type | Expected proof |
| --- | --- |
| Docs-only | `<readback/checks>` |
| Backend/API | `<tests/API evidence/contract proof>` |
| Browser UI | `<Playwright/browser/screenshot/human journey>` |
| Mobile | `<unit/screen/simulator/device/API evidence>` |
| Critical lane | `<read-only diagnosis first, approval, negative/idempotency/contract evidence>` |
| Release/deploy | `<version/SHA, smoke, monitoring/log evidence>` |

## Critical Lanes

List areas that require read-only diagnosis first and explicit approval before
implementation.

| Lane | Why it is sensitive | Required approval/evidence |
| --- | --- | --- |
| `<auth/payment/invoice/etc>` | `<risk>` | `<approval and proof>` |

## Access And Boundaries

| Area | Rule |
| --- | --- |
| Safe read-only access | `<docs, local files, read-only wrappers, monitoring reads, etc>` |
| Forbidden paths | `<.env*, live/, secrets, raw credentials, etc>` |
| Push/PR/merge/deploy | `<approval boundary>` |
| Production data/actions | `<boundary>` |
| Staff/developer access | `<who can use this repo and under what profile>` |

## Deploy And Release

| Field | Value |
| --- | --- |
| Deploy path | `<manual, script, CI, webhook, unknown>` |
| Environments | `<local/staging/prod/dev/etc>` |
| Release proof | `<what proves code is deployed>` |
| Smoke proof | `<what user/API journey proves it works>` |
| Monitoring proof | `<logs/Sentry/BetterStack/etc>` |

## What Done Means

Write this in plain language.

```text
<For this repo, done normally means...>
```

Also name what is not done:

```text
<Example: committed is not pushed; pushed is not merged; merged is not deployed;
deployed is not live-checked.>
```

## Known Gaps

| Gap | Impact | Recommended next |
| --- | --- | --- |
| `<unknown command/doc/evidence/access>` | `<why it matters>` | `<how to verify/fix>` |

## Verification Notes

Use this section when changing the profile.

```text
Checked:
- <file/command/evidence>

Still unknown:
- <gap>

Recommended next:
- <one next action>
```
