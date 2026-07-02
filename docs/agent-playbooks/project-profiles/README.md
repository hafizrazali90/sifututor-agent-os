# Agent OS Project Profiles

These profiles are local adapters for product repos.

Plain meaning:

```text
The umbrella Agent OS is the shared system.
Each product profile explains how one repo actually builds, tests, deploys,
proves work, and defines done.
```

Profiles here are useful when a product repo cannot be edited yet, has a dirty
worktree, or needs an umbrella-level draft before promotion.

When a profile becomes verified, link it from the product repo's `AGENTS.md`,
`CLAUDE.md`, or a nearby project doc so agents working inside that repo can find
it before editing.

## Profiles

| Project | Profile | State |
| --- | --- | --- |
| `sifu-tutor` | [sifu-tutor.md](sifu-tutor.md) | profile verified in umbrella; linked from product repo |
| `ripple-suite` | [ripple-suite.md](ripple-suite.md) | profile verified in umbrella; linked from product repo |
| `kelas` / `kelasapp` | [kelas.md](kelas.md); [first-day developer setup](kelas-developer-first-day.md) | profile drafted in umbrella; product integration pushed on `feat/launch-readiness`, not rollout-verified |
