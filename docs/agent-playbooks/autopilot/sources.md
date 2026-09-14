# What the agents read

Every twin and every designer run loads these. Ordered by authority: a rule
higher in this list wins.

| Source | Path | What it gives |
|---|---|---|
| His decisions in the flow spec | `design/specs/<flow>.md` | What he actually decided for this flow, in his words, dated |
| Design review rules | `design/design-review-rules.md` | 14 numbered rules, each traced to a mistake he caught |
| Design index | `design/INDEX.md` | Which document owns which subject, and what is stale |
| The contract | `design/DESIGN.md`, `design/specs/*.md` | Tokens, components, patterns, capitalisation, chips, banners |
| Reference evidence | `design/references/me-plus-system.md`, `grab-density-and-illustration.md` | Measured colours, sizes and behaviours from the apps he named |
| Benchmark | `design/reviews/benchmark-2026-09-14.md` | Our screens beside Me+, Airbnb, Fiverr, Uber, Wise |
| Working with Hafiz | `docs/agent-playbooks/working-with-hafiz.md` | 776 lines: how he wants to be talked to, approval boundaries, close-out |
| Local memory | `~/.claude/projects/-Users-hafizrazali-Projects-Sifututor/memory/*.md` | 30+ distilled corrections, each with why and how to apply |
| Koda memory | `memory_search` or `scripts/agent-checks/koda search` | Cross-project lessons and past decisions |
| Mission ledgers | `docs/agent-playbooks/mission-ledger/*.md` | Parked decisions and remembered follow-ups per project |
| Production | `~/.config/sifututor/agent-access/database-readonly.conf` | The numbers behind every design claim |
| His profile | `docs/agent-playbooks/autopilot/hafiz-profile.md` | What he rejects, how he escalates, the eight things he checks |

Rules for reading them:

- A twin quotes the source when it raises a finding. A finding with no
  source is dropped.
- When two sources disagree, the newer dated decision in the flow spec wins,
  and the older document gets stamped rather than silently overruled.
- Production numbers beat opinion. If a twin claims a behaviour, the
  designer checks the database before changing anything.
