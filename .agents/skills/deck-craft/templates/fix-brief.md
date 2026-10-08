# Round <N> fix brief

Deck folder: <DECK>. Library: ~/Projects/Sifututor/.agents/skills/deck-craft/scripts/lib.py (do not edit). Slide modules: <list>.
Read docs/agent-playbooks/deck-craft.md first, and look at the reference contact sheets it names.
Source of truth: <SOURCE>. Never type a raw RM amount when a ledger token exists. Never invent a fact.

Reviews: <DECK>/review/r<N-1>/{design,management,technical,copy}.md. Apply every BLOCKER and MAJOR for your slides, plus every MINOR that is a quick, safe edit.

Decisions that win over any reviewer:
1. <one total, one basis, labelled>
2. <one term per thing: ...>
3. <voice rule>
4. ...

Loop per slide you change: edit, run `python3 ~/Projects/Sifututor/.agents/skills/deck-craft/scripts/build.py --mod=<module> --render <ids>`, look at png/<id>.png, then run `python3 ~/Projects/Sifututor/.agents/skills/deck-craft/scripts/lint.py <ids>` until it is clean. Render a few slides at a time. Edit only your module.

Report back, per slide: what changed, any review item you did not apply and why, and the final lint output.
