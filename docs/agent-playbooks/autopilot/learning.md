# How this gets better

A run that does not change the rules has taught us nothing.

## The four signals

**1. A confirmed finding of a new kind.** A twin found something real that
no written rule would have caught. Write the rule. It goes in
`design/design-review-rules.md` with the board that caused it, the way every
rule in that file already does. Next flow, the mistake cannot recur.

**2. A wrong finding.** A twin reported something the verifier disproved.
Log it in `misses.md` with what the twin measured and what was actually
there. When one twin produces several of the same kind, its instructions get
a line about that trap. Today's example: a twin measured a card's bottom
edge by scanning up from the bottom of the image and hit the action bar
instead. That became the paragraph in `autopilot-twin.md` about checking you
measured the right thing.

**3. An escape.** Hafiz found something every twin passed. This is the most
valuable signal in the system and the only one that proves the twins are not
yet him. It becomes a new check in `hafiz-profile.md`, worded as a question a
reviewer can ask of any screen, and it is added to the eight. Record his
actual words.

**4. Drift.** A decision was written down and not drawn. The verifier caught
it. If drift happens twice in one flow, the drawing step is wrong, not the
verifier: the chat starts reading the change log back before each export.

## The scoreboard

One row per flow, filled in after his review. This is how we know whether
any of it works.

| Flow | Boards | Findings raised | Confirmed | Wrong | Rounds | Escapes |
|---|---|---|---|---|---|---|
| Teaching a class | 23 | | | | 3 | |
| Getting paid | 16 | | | | 4 | |
| Asking staff | 37 | | | | 4 | |

**Escapes is the number that matters.** Everything else is process. If
escapes fall flow over flow, the twins are learning him. If escapes stay
flat while findings rise, the twins are getting noisier, not sharper, and
the profile needs work rather than the prompts.

## The rule for adding a seventh agent

Do not add one on a hunch. Add one when the same kind of escape happens in
two flows running. If copy escapes twice, a writer joins. If Malay escapes
twice, a Malay writer joins. If a decision is overruled twice on business
grounds no agent could know, that is not a missing agent, that is a decision
that should have been marked **needs Hafiz** and was not.

## What never changes without him

The eight checks can grow. The rules can grow. But a decision recorded in a
flow spec as his is never quietly reversed by a later run. If a new fact
contradicts an old decision of his, the run keeps his decision, draws it his
way, and puts the contradiction in the decision log.
