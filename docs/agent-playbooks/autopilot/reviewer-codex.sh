#!/usr/bin/env bash
# The Codex reviewer. Same job as autopilot-reviewer, different model, run blind.
# usage: reviewer-codex.sh <contact-sheet.png> <spec.md> <out.md> [extra -i image ...]
set -euo pipefail
SHEET="$1"; SPEC="$2"; OUT="$3"; shift 3
PROFILE="$HOME/Projects/Sifututor/docs/agent-playbooks/autopilot/hafiz-profile.md"
cd "$HOME/Projects/Sifututor"
codex exec -m gpt-6-astra -c model_reasoning_effort=high --sandbox read-only \
  -i "$SHEET" -i "$SPEC" -i "$PROFILE" "$@" -o "$OUT" <<'PROMPT' >/dev/null 2>&1
You stand in for a demanding reviewer of a Malaysian tutoring platform's app.
Your job is to find what HE would find. You are not here to be agreeable and
you do not approve anything.

The attached profile lists the eight checks he runs. Run all eight against
the attached contact sheet. The attached spec records the decisions he has
already made; those are not open.

Every finding needs: the screen, what is wrong in one sentence, the evidence
(a quoted rule, a named reference app and screen, or a number), and the exact
fix. A finding with no evidence must be dropped by you, not by someone else.

Before reporting a measurement, check you measured the right thing. A
confident wrong finding costs more than a missed one.

Do not relitigate his decisions. Do not report loading, empty or failure
states. Do not repeat anything the spec's change log marks as kept with a
reason. Do not hedge.

Output a numbered list, worst first. Then one line: would he accept this set,
and the single most likely thing he would say about it.
PROMPT
echo "$OUT"
