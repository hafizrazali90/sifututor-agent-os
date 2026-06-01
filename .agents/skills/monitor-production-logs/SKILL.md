---
name: monitor-production-logs
description: Use when Hafiz asks Codex to monitor Sifututor production logs, check Sentry or BetterStack after a deploy, watch for FIUU/mobile API regressions, verify production observability, or run a post-release production health check. Must follow docs/agent-playbooks/monitor-production-logs.md.
---

# Monitor Production Logs

Use this skill for production log watch, post-deploy monitoring, and
observability verification for `sifu-tutor`.

## Core Rule

Read and follow:

```text
docs/agent-playbooks/monitor-production-logs.md
```

Default to read-only checks. Do not read or modify `.env*`, production secrets,
or `live/`. Do not deploy, merge, migrate, or edit production unless Hafiz asks
for that separately and the relevant critical-lane workflow is followed.

## Helper Script

For deterministic checks, run:

```bash
.agents/skills/monitor-production-logs/scripts/prod-monitor.sh
```

Optional marker mode writes one harmless Laravel `info` log marker to confirm
normal app logs are flowing through the active channel:

```bash
.agents/skills/monitor-production-logs/scripts/prod-monitor.sh --marker
```

## Human-Facing Alias

```text
Claude: /monitor-production-logs
Codex: $monitor-production-logs
```
