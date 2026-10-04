# Status page Stage 4: Telegram alerts and the 10:00 MYT summary

Prepared 04/10/2026 for Hafiz. Issue: hafizrazali90/sifututor-agent-os#240.
Status: PROPOSAL. Nothing here is approved or built. This file is preparation only.
Inputs: [build plan](status-page-build-plan.md), [PRD](status-page-prd.md), [user story US-MON-009](features/monitoring/user-stories.md).

## Where we are

Stages 0 and 1 are live at https://status.sifututor.my. The page reads Better Stack and Sentry every 5 minutes and stores each reading. Today nobody is told when something breaks; Hafiz has to open the page. Stage 4 makes the page tell him.

## What you get

| Message | When | Example (MYT) |
| --- | --- | --- |
| Incident | A system goes Down, or stays Degraded for 30 minutes | "Owner Analytics is down since 02:46 MYT. Last night's data update did not finish. Who is affected: owner dashboards show data from the last good night. https://status.sifututor.my" |
| Recovery | The same system has passed 2 readings in a row | "Owner Analytics is back since 05:12 MYT (down 2 h 26 min)." |
| Missing data | A source stops answering, or the page's own reading is older than 15 minutes | "The status page cannot see Sentry since 11:05 MYT. Error tracking for SIMS, Ripple and Learnest is unknown, not healthy." |
| Daily summary | Every day at 10:00 MYT | Verdict line, what needs you, counts, items running out within 30 days, Sentry allowance used |

Rules that keep it quiet (from the approved risk "Too many Telegram messages"):

- One open incident per system and kind. A system that stays down sends one message, not one every 5 minutes.
- Two readings in a row (10 minutes) before an incident opens or closes, so one failed check does not ping anyone.
- Degraded does not message for the first 30 minutes. It appears in the 10:00 summary if it clears sooner.
- At most 10 messages in one run. More than that becomes one rollup message.
- A message that fails to send is retried on the next run and is never marked as sent until Telegram confirms it.
- Messages carry system names, times and a link. Never names, phone numbers, log text or credentials.

## How it works (plain terms)

- The Worker that already runs every 5 minutes gets one more step after it saves a reading: compare this reading with the last one and the list of open incidents, then decide what to send.
- A new small table in the page's database (D1) remembers open incidents, when each message went out, and the Telegram message id. This is what stops repeats.
- A second timer at 02:00 UTC (10:00 MYT) sends the daily summary.
- The deciding logic is one pure function, `planAlerts(previousState, snapshot, now)`, returning the messages and the next state. It touches no network, so every rule is tested before any Telegram call exists.
- A dry-run setting writes the messages to the Worker log instead of sending them.

Known limit, stated plainly: if the Worker itself stops running, it cannot tell us. Two safety nets: the page turns every system to No data after 15 minutes (visible to anyone who opens it), and a missing 10:00 summary is itself the signal. A real outside watcher needs a Better Stack heartbeat, and the free plan has all 10 in use (the parked heartbeat decision on #240).

## Tests to write first (TDD, local only)

Each is a case from a real incident or a rule above.

1. Analytics nightly refresh failed (04/10 02:46): Down opens one incident, one message, no repeat on the next 20 readings.
2. Same incident recovers: one recovery message with the correct duration, then silence.
3. Ripple disk at 88% (03/10): Degraded for under 30 minutes sends nothing now; shows in the summary.
4. SIMS queue check failing 32 times with no user impact: one Degraded message after 30 minutes at most, not 32.
5. A check flapping ok, fail, ok, fail: no incident opens (needs 2 in a row).
6. Better Stack stops answering: one missing-data message, not one per system, and one recovery when it returns.
7. Reading older than 15 minutes: one missing-data message about the page itself.
8. Telegram returns an error: the incident stays unsent and is retried; it is never marked as sent.
9. 15 systems fail in one run: capped at 10 messages, the rest become one rollup.
10. Summary at 10:00 MYT: correct time, MYT labels, the optional-silent-check wording from the Stage 1 fix, nothing secret in the text.
11. Restart safety: the same reading processed twice (timer overlap) sends nothing twice.

## Setup you do (about 10 minutes, I guide each step)

1. In Telegram, message @BotFather, create a bot, copy the bot token.
2. Create a private group, add the bot, add the people who should be told (you, developers).
3. Get the group id (I give you a one-line way to read it without exposing the token).
4. Save the token and group id to a protected file on this Mac, never in chat. You run the script that stores them as Worker secrets `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`, the same way as the Better Stack and Sentry keys.

The bot only sends. It does not need to read group messages.

## Approvals, in order

Each is its own go. Nothing later happens until the earlier one is done and checked.

| # | Approval | What it allows | Touches |
| --- | --- | --- | --- |
| A1 | Build Stage 4 locally | Write the tests and code on a branch; fake Telegram only | Nothing live |
| A2 | You create the bot and group | Human step | Telegram |
| A3 | Store the two secrets | You run the secrets script | Cloudflare secrets |
| A4 | Deploy with alerts in dry-run | Adds the table, the 02:00 UTC timer and the code; messages go to the log only | The live Worker and D1 |
| A5 | One test message | A single "status page test" to the group | Telegram |
| A6 | Pause and resume one non-critical monitor (SIMS Pulse Dashboard) | Proves a real Degraded and recovery message end to end | One Better Stack monitor, for a few minutes |
| A7 | Turn alerts on | Switch dry-run off | Live alerts |
| A8 | Watch the first 10:00 MYT summary | Check it arrives once with the right content | Nothing new |

A real Down message cannot be provoked without breaking something real, so Down is proven by tests and by replaying the 04/10 Analytics incident into the dry-run, and then by the first genuine incident after A7.

## Rollback

- Turn dry-run back on (one setting), or redeploy the previous Worker version (one command).
- Remove the 02:00 UTC timer line and redeploy. The new table can stay; it is inert.
- The bot can be removed from the group at any time.

## Cost and limits

Telegram bot: free. Cloudflare free plan: to confirm against current limits before A4 (number of timers per Worker, requests per run, D1 writes). Record the limits in the repo as Stage 0 did.

## Decisions for Hafiz (one at a time, with my suggestion)

1. Should a Down message wake you at night? Suggestion: yes for Down and missing data, no for Degraded. Alternative: quiet hours 23:00 to 07:00 MYT with Down still sent.
2. Who joins the group? Suggestion: you and the developers who own systems.
3. Degraded delay: 30 minutes (suggested), or send at once?
4. Bot name. Suggestion: "Sifututor status".

## Dependencies and order

- The Stage 1 truthfulness fix (silent optional check is Degraded, Sentry zero errors is not an incident) should be released first, so alerts use the corrected states. It is prepared on branch `fix/240-truthful-rollup-and-sentry-proof` in `sifututor-status` and awaits your release approval.
- Stage 3 (server collectors) is not required for Stage 4. Alerts cover everything the page sees today.
