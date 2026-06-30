# Profile Assignment Record Template

Use this template in the private profile registry, not as a public committed
record of real people.

Recommended private registry:

```text
~/.config/sifututor/agent-os/profile-assignments.md
```

Do not store secrets, tokens, `.env*` values, raw credentials, customer private
data, or production payloads in this record.

Follow `docs/agent-playbooks/agent-os-profile-registry-operations.md` when
creating, updating, reviewing, auditing, downgrading, suspending, or closing a
real record.

## Record

| Field | Value |
| --- | --- |
| Person/agent | `<name or agent id>` |
| Profile | `<Owner / Hafiz | Internal agent | Developer staff - reader/QA | Developer staff - builder | Support / ordinary staff | Advanced operations>` |
| Project/service boundary | `<repo, service, or scope>` |
| Purpose | `<why this profile is needed>` |
| Connected tools | `<tools connected for this profile>` |
| Probe/check evidence | `<probe command/result summary, no secrets>` |
| Capability states | `<available/fallback/unknown/not_connected/blocked/forbidden>` |
| Explicitly blocked | `<what remains blocked even if connected>` |
| Approval source | `<chat, issue, PR, handoff, or none needed>` |
| Activated on | `<YYYY-MM-DD>` |
| Review point | `<date or event>` |
| Lifecycle state | `<active | downgraded | suspended | upgraded | closed>` |
| Last reviewed | `<YYYY-MM-DD or not yet>` |
| Notes | `<short operational note, no secrets>` |

## Review Log

| Date | Decision | Reason | Next review |
| --- | --- | --- | --- |
| `<YYYY-MM-DD>` | `<keep/downgrade/suspend/upgrade/close>` | `<why>` | `<date/event/none>` |
