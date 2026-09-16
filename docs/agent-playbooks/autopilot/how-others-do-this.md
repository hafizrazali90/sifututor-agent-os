# How other people do this, and what we took

Researched 16/09/2026 on Hafiz's instruction: "can u do research online on how
we should do this properly, and how other people actually do this, on github or
something."

Three worlds turned out to be relevant: Figma design linters, design-system
governance in CI, and the practice around multi-agent LLM systems. We were
ahead of the first, behind the second, and roughly aligned with the third
without having read any of it.

---

## 1. Figma design linters

[Design Lint](https://github.com/destefanis/design-lint) is the open-source
original. What it checks is narrower than ours: layers not using a style, for
fills, text, effects, strokes, and a configurable border radius.

Three of its design decisions are worth copying, and two we already had by
accident:

| Theirs | Ours |
|---|---|
| Groups and slices are skipped entirely, because styles apply to the children | We skip phone chrome and note frames the same way |
| **Locked layers are never linted** | We have no equivalent, and no way to mark a node as deliberate |
| **A person can ignore one error, or every error of that type, and it persists** | Our exemptions are constants inside the scripts |
| Custom rules are functions you import into the controller | Ours are functions in one file per subject |

[FigmaLint](https://github.com/southleft/figmalint) adds an AI pass for
"design system compliance, accessibility, and developer readiness", and Figma
itself now ships a
[design QA agent](https://www.figma.com/solutions/ai-design-qa-agent/) that
scans a Ready-for-Dev page for style, token and touch-target compliance.

**Where we are ahead.** None of them read the rendered pixels, walk a screen's
promises, or compare a Malay screen against its English one. Our six checks
cover things no off-the-shelf linter does, because they are about this product.

**Where we are behind.** Ignoring. Every one of these tools lets a human mark
something as deliberate and have that survive. Ours cannot, so a correct thing
gets reported forever, or the rule gets loosened for everyone.

---

## 2. Design-system governance in CI

[anto-amezquita/design-system](https://github.com/anto-amezquita/design-system)
is the clearest example: a solo-maintained, token-first system with three CI
gates.

- **Token lint**: no raw hex, no primitive leakage, no hardcoded motion or
  spacing. Blocks the build.
- **Contrast check**: WCAG AA across all four theme combinations. Fails the
  build.
- **Component registry**: a component that ships without documentation fails
  the build.

Two ideas from it we did not have:

**"Agent-safe governance."** Their words: every governance script gives
specific, actionable failures, so nothing requires a human to interpret vague
CI output. That is the difference between a red cross and a line that says
which screen, which value, and what it should be. Our checks mostly do this;
`links.figma.py` did not, and it is now labelled a list rather than a fault
detector.

**A committed snapshot for staleness.** `figma:status` compares the tokens
against `figma/sync-state.json` in the repo, so drift is detectable offline and
shows up in a diff. We hit the live API every time, which is slow and leaves no
record of what changed between two runs. **Not yet taken; it is the best idea
here that we have not done.**

[tokenlinter](https://github.com/KanthalaS/tokenlinter) does the same for W3C
DTCG tokens with WCAG contrast built in, and uses the exit-code contract that
made our whole check suite ungateable until today: **0 clean, 1 problems
found.**

---

## 3. Making a check trustworthy

The most useful reading of the lot, and the thing that goes straight into how
we work. From
[Crafting Trustworthy Custom Linter Rules](https://dev.to/beefedai/crafting-trustworthy-custom-linter-rules-36l8)
and the ESLint and typescript-eslint
[rule-tester](https://typescript-eslint.io/packages/rule-tester/) practice:

1. **Prototype with unit tests.** Every rule ships with valid and invalid
   cases. A rule with no test that fails is not a rule.
2. **Corpus validation.** Run it over the whole repository, label 200 to 500
   findings by hand, compute precision.
3. **Canary.** Warnings or bot comments only, never a hard failure.
4. **Gradual enforcement.** Flip to error only after the false-positive count
   is observed to be low. Teams aim for the high nineties before automatic
   enforcement.
5. **Prevention over triage.** Anchor to structure, not to strings. Exclude
   fixtures and mocks with globs rather than loosening the rule.
6. **Every rule documents its rationale, a bad and good example, and the fix.**

**We did none of steps 2, 3 or 4.** `artwork.figma.py` was written, believed
and acted on the same hour, at 15% precision. Nine of its first thirteen
findings were photographs, which fill their box on purpose.

Taken, on 16/09/2026:

- `research/check-precision.md` records the sample, the real count and the
  precision for every check.
- `scripts/checks.sh` runs them in **BLOCKING**, **ADVISORY** and **LIST**
  tiers. A new check starts advisory and is promoted on evidence.
- Every script now returns 1 on findings and 0 when clean.
- Each check owes a **planted fault**: break one thing on purpose, confirm the
  check names it and exits 1, revert. Done for `dates.figma.py`, which had
  never once printed a finding and was therefore unproven.

The one idea we have not taken is unit-testing a rule against fixtures, because
our checks read one live Figma file over the API rather than a string of code.
The planted fault is the cheap substitute; a proper fixture would be a small
committed copy of a page's node tree.

---

## 4. Multi-agent systems

Anthropic's own guidance, summarised
[here](https://www.zenml.io/llmops-database/engineering-reliable-multi-agent-llm-systems-by-starting-simple),
and their
[code review product](https://www.infoq.com/news/2026/04/claude-code-review/),
which runs specialised agents in parallel then verifies and ranks their
findings before posting.

Where we already agree, without having read it:

| Their pattern | Ours |
|---|---|
| **Generator–verifier**: one agent answers, another verifies in a fresh context, which cuts self-confirmation | Two blind reviewers and a verifier that marks each finding CONFIRMED, WRONG or UNCHECKABLE |
| **Orchestrator–sub-agents**: bounded investigations, results synthesised, context kept from running away | Three research lanes that never see each other, then the chat writes the spec |
| Parallel specialised agents, each on a different class of issue | Six agents, one per lens |

Two things they do that we do not:

**They rank.** Findings are ordered before anyone reads them. We hand over
262 promises and 10,458 lines of copy review flat. Severity ordering is the
obvious next improvement and costs nothing.

**They evaluate the components in isolation.** Their guidance is explicit:
test each agent directly on representative inputs before integrating, and
re-run regression tests after any model or prompt change. **We have no
evaluation of any single agent, and we just rewrote seven prompts with no way
to tell whether they got better or worse.** That is the largest gap this
research exposed.

Their warning we should heed: more agents cost model calls, tokens, cache
reuse and latency, and add coordination errors. Start with a strong single
agent and add one only when context dilution, specialisation or parallelism
demands it. Our seven were added one at a time, each after a repeated escape,
which is the right reason, but nothing has ever measured whether any of them
earns its place.

Research direction worth watching:
[Agentic Design Review System](https://research.adobe.com/publication/agentic-design-review-system)
(AAAI 2026) proposes exactly our shape, multiple agents critiquing a design
under a meta-agent, and publishes DRS-BENCH to score it. A benchmark for design
critique is what we would need to answer "is the reviewer getting better".

---

## What this changed, same day

Done:

- exit codes on all six checks
- `check-precision.md`, with the tier and the evidence for each
- `checks.sh`, two tiers, only the trustworthy ones block
- planted-fault proof for `dates.figma.py`
- a real bug found while doing it: the surface check was comparing a block with
  itself and calling it invisible, four of its twelve findings

Still owed, in the order they are worth doing:

1. **Evaluate an agent in isolation.** Feed the reviewer a page with known
   faults and count what it finds. Without this, a prompt change is a guess.
2. **Rank findings by severity** before handing them over.
3. **A committed snapshot of the Figma file**, so drift between runs is a diff
   rather than a memory.
4. **An ignore list with a reason per entry**, so a deliberate thing can be
   marked deliberate without loosening a rule for everyone.
