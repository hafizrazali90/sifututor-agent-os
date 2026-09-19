# What the agents read

Every reviewer and every designer run loads these. Ordered by authority: a rule
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
| The product docs | `sifu-tutor/docs/features/<feature>/prd.md` and `backend-contract.md` on `origin/main` | The approved rules and the seeded launch values: rates, tiers, package prices, formulas |
| The code that does the thing | `sifu-tutor/app/**`, `sifututor_tutor/**` | What the system actually computes, when the PRD is silent or stale |
| Production | `~/.config/sifututor/agent-access/database-readonly.conf` | The numbers behind every design claim |
| His profile | `docs/agent-playbooks/autopilot/hafiz-profile.md` | What he rejects, how he escalates, the eight things he checks |

Rules for reading them:

- A reviewer quotes the source when it raises a finding. A finding with no
  source is dropped.
- When two sources disagree, the newer dated decision in the flow spec wins,
  and the older document gets stamped rather than silently overruled.
- Production numbers beat opinion. If a reviewer claims a behaviour, the
  designer checks the database before changing anything.


## The product docs were missing from this list until 16/09/2026

That omission caused the worst error of the run. A commission sheet was drawn
showing a Nakngaji tutor earning RM29 a session for the first seven and RM37
after, against a RM499 package. All three numbers were invented. They were
reverse-engineered from a figure already printed on another screen in the same
Figma file, so they were internally consistent and completely wrong.

`sifu-tutor/docs/features/nakngaji/prd.md` carries the approved rates, the
package prices and the 30%/70% split, and `backend-contract.md` carries the
formula. Both had been on `origin/main` for weeks. Neither was on this list, so
no agent read them.

**The rule that follows: a number's source must be upstream of the design.**
Production, a PRD, a backend contract, or code. **Another screen in the same
Figma file is not a source.** It is the same guess wearing a different hat. See
the amendment to B20 in `learning.md`.

## Before anything is marked "needs Hafiz", look it up

Two questions sat on the open list for days as things only he could answer.
Both were facts, and both were answered in minutes on 16/09/2026 without him:

- **How the commitment fee is first paid.** One query: 1,043 of 1,170 rows are
  RM100 and 1,157 of 1,163 tutors have exactly one. One file:
  `TutorCommitmentFeeAmount::resolve()`, default RM100.00. One payment, not a
  monthly one, and the drawn screen was right all along.
- **The Nakngaji rates.** In the PRD, as above.

A question reaches him only when it needs **judgement he holds and the systems
do not**: what the business wants, what a tutor would feel, what a Malay reader
would say. A question about what is true is a lookup, and marking it for him is
a failure of this step, not a courtesy.
