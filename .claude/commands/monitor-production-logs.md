Use the Sifututor production log monitoring workflow.

Follow:

```text
docs/agent-playbooks/monitor-production-logs.md
```

Default command:

```bash
.agents/skills/monitor-production-logs/scripts/prod-monitor.sh
```

If the user asks to verify end-to-end log flow, run:

```bash
.agents/skills/monitor-production-logs/scripts/prod-monitor.sh --marker
```

Rules:
- Do not read or modify `.env*`, production secrets, or `live/`.
- Do not deploy, migrate, merge, or edit production from this command.
- Do not print tokens.
- Explain results in natural language.
