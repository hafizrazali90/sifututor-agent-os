# Weekly Delivery Report

Use this playbook when Hafiz asks what shipped this week, what is blocked, or
for a weekly development/delivery report.

Plain meaning: this is a factual team health report, not a staff scorecard.

## Product Decision

- Keep the workflow because a reliable weekly view helps Hafiz see shipped
  outcomes, blockers, and missing evidence.
- Never rank people or report per-person commits, pull-request counts, lines,
  files changed, speed scores, or AI usage.
- Names may appear only as operational owners of a decision or blocker.
- Keep raw collected data local and private. A shareable report contains product
  outcomes, blockers, decisions, evidence links, and collection coverage only.
- The Sifututor Agent OS owns this workflow. GitHub is the current data source;
  an agent creates the narrative only after reading the linked work.

## Collect

Run the tracked collector from the umbrella workspace, naming each repository
that belongs in the report:

```bash
python3 scripts/agent-checks/weekly-delivery-data.py \
  --since YYYY-MM-DD --asof YYYY-MM-DD \
  --repo Sifututor/ripple-suite \
  --repo Sifututor/sifu-tutor > /tmp/weekly-delivery.json
```

The explicit repository list prevents a missing checkout from silently removing
a product from the report. The output records collection status per repository.

## Interpret Collection Health

| Status | Meaning | May publish? |
| --- | --- | --- |
| `available` | Every source worked and at least one merged PR was found. | Yes. |
| `quiet` | Every source worked and zero merged PRs were found. | Yes, as a quiet week. |
| `partial` | Some source or completeness check failed. | No; name the failed repositories. |
| `unavailable` | No source produced trustworthy data. | No; report a collection failure. |

Never translate `partial` or `unavailable` into “nothing shipped.” The collector
returns exit code 4 for those states and sets `shareable_summary_allowed` false.

## Write The Report

Use this order:

1. **Plain-language summary:** the most important outcome and the main risk.
2. **What reached users:** product, user-visible outcome, proof link, and highest
   proven state such as merged, deployed, live-smoked, or monitored.
3. **Still in progress:** meaningful work that did not reach users yet.
4. **Blocked or waiting:** blocker, practical impact, owner, and next action.
5. **Decisions needed:** only genuine choices Hafiz must make.
6. **Coverage:** date window and repository collection states.

PR titles are evidence, not final prose. Read enough linked work to describe the
user or operational result honestly. A merged PR is not automatically deployed.

## Evidence And Stop Rule

Before sharing:

- every named shipped outcome has a link and an honest release state;
- all expected repositories are present in the collection manifest;
- the collector reports `available` or `quiet`;
- no individual productivity score or inferred performance judgment appears.

If collection is partial or unavailable, stop publication, explain which source
failed, and retry or repair the source. Do not ask Hafiz to interpret incomplete
data as a report.
