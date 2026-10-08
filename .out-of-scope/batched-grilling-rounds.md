# Batched question rounds in grilling

## What was proposed

Adopt the `grilling` format from `mattpocock/skills`: ask every ready question
together in one numbered round, each with a recommended answer.

## Why it is out of scope

- Hafiz's rule is one small point per message, with the decision question in a
  question box. A round of many questions breaks it.
- Many questions at once make the decision harder to follow for someone who
  knows logic and data but not code.
- The question box is required by our rules; his skill rejects the native
  question tool.

## What would change our mind

Hafiz changing the discussion pace rule, or a task where a batch of independent,
low-stakes questions is clearly faster for him.

What we did take from it: a done condition, a rule to look facts up instead of
asking, and "do not act until Hafiz confirms" (issue #293).

## Decided

08/10/2026 (MYT), Hafiz: adapt `grill-me`; keep one question at a time.
