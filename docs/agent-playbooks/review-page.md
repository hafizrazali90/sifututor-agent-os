# Review Page

The review page is the one page Hafiz reads to understand a change. Claude and
Codex both make it, at two moments:

- **`plan` mode, before coding:** what we will change and why, so Hafiz can
  steer before work is spent.
- **`ship` mode, before deploy:** what was built and proven, so Hafiz can
  confirm it and give the deploy go.

Plain meaning:

```text
The plan page says "this is what I will build".
The ship page says "this is what I built, here is the proof, may it go live".
Hafiz reads either one in about two minutes.
```

This playbook owns both modes. It replaces the old "review page before deploy"
rule, which now points here. Rules set by Hafiz on 13/10/2026.

## Reference Model

The model is the CRM build review page published on 13/10/2026 as an Artifact:
https://claude.ai/artifact/7nstkTYymzQyiJsBTopLoz. Its renderer was
`outputs/crm-build-review-2026-10-12/review-staging/render.py`, which turns one
`status.json` data file into the page, and the staff guide style came from
`outputs/crm-build-review-2026-10-12/staff-guide/build.py`. Those output files
are not in Git; reuse them when they are on the machine. The useful idea is the
split: data in one file, the page rendered from it, so the page is rebuilt in
seconds when a fact changes instead of being edited by hand.

## When To Make Each Page

| Change | Plan page | Ship page |
| --- | --- | --- |
| Anything staff, parents or tutors will see on screen (new or changed screen, state, label, flow) | **Automatic**, before coding | Yes |
| Behind-the-scenes fix (backend, job, data, performance, no visible change) | Not needed | Yes |
| Urgent production fix | Not needed | Yes |
| Tiny text change (a word or label, no layout or flow change) | Not needed | Yes |
| Agent OS, docs-only or tooling change with no shippable product effect | Not needed | Not needed |

"Automatic" means the agent makes the plan page without being asked. A ship
page is due before any deploy and at the end of every session that produced
shippable work.

## Waiting Or Working: The Non-Blocking Rule

The page never becomes a new approval queue. What the agent does after
publishing depends on whether Hafiz already gave the go for this goal:

| Situation | What the agent does |
| --- | --- |
| Hafiz has **not** said proceed, go or end-to-end for this goal | Publish the plan page, send the link, and **wait for his ok** before coding. |
| Hafiz **has** said proceed, go or end-to-end | Publish the page, open it for him, and **keep working without waiting**. He reviews in parallel; when he comments, adjust the work and the page. |

Once Hafiz gave the go, never stop for small approvals. Ask only for:

- new scope beyond the goal he approved;
- the production go (a production deploy, or anything else that changes live);
- a destructive action;
- a business rule that is not settled.

The ship page is still a gate: no deploy until Hafiz confirms it (`AGENTS.md`,
"Communication With Hafiz"). The exceptions are a production deploy Hafiz
already told you to go to (agreed 17/10/2026: still make the page and leave it
open, but do not wait for his confirmation), and a staging deploy Hafiz
already approved for this release, such as a PC release run with
`--staging-deploy` ([unattended-jobs.md](unattended-jobs.md)); its staging
screenshots then go on the ship page. Other work, such as fixes and tests,
carries on while he reads it.

## Plan Page

One page, readable in two minutes. For each change, one block with:

1. **Business meaning and technical detail, side by side.** Left: what changes
   for staff, parents, tutors or money, and why it matters. Right: what the code
   and data will do, in natural language, read in its real order.
2. **Today's real screen.** A screenshot from staging, or from production
   through a read-only path, with every personal detail masked (see Privacy).
3. **The proposed screen, beside it.** Built from the real app components with
   fictional data (see Proposed Screens). Label it "proposed".
4. **Decisions needed.** Each one as a short question with two or three options
   and the recommendation. If none, say "none".
5. **Risks.** What could go wrong for users or data, and what is not yet known.
6. **Done means.** The finish state (local, PR-open, staging, live) and the
   acceptance example, with business-rule IDs when they apply.
7. **Evidence plan.** Which tests, browser checks, E2E and staging checks will
   prove it, and any named exception.

Open the page with a three-line summary: the goal, how many changes, and how
many decisions Hafiz must make.

## Ship Page

What was built, after the adversarial review and its fixes. For each change:

1. **Business meaning and technical detail, side by side**, as built.
2. **Real screenshots of every UI change**: each new or changed screen and
   state, desktop and phone where relevant, from staging when the release went
   there, otherwise from the real styled app running locally with fictional
   data. An unstyled test harness is never evidence.
3. **Test and Codex results** with real numbers: tests, E2E or the named
   exception, the cold review or Codex review verdict, negative controls, and
   baseline failures that are not this change.
4. **Decisions the agent made on his behalf**, so he can overrule them.
5. **Risks, limits and what is not yet proven** (for example staging-only
   proof).
6. **Release state**: local, committed, PR-open, merged, staging, live, using
   the state words in [agent-os-state-model.md](agent-os-state-model.md).
7. **Approvals still needed**, exactly: for example "production go", "the
   migration", "merge PR 1630".

Open with the same three-line summary. In the PC release loop, this page is
item 11 of [unattended-jobs.md](unattended-jobs.md) and Hafiz's confirmation
closes gate G1.

## Proposed Screens: Real Components Only

A proposed screen must be built from the real app, never drawn:

- Render the real components of the project (its pages, design system, styles)
  with fictional data, then screenshot the result. Good sources, best first: a
  local or staging build with seeded fictional records; the project's component
  preview or test fixture pages, if styled like the app; a branch build of the
  change itself.
- Never use a hand-drawn sketch, an invented HTML mockup, an image generator or
  a design tool frame as "the proposed screen". If the real components cannot be
  rendered yet, say so on the page, show today's screen only, and describe the
  change in words. Do not fill the gap with an invented picture.
- Every number, label and notification on the proposed screen comes from
  production evidence, an approved specification, a backend contract or current
  code, never from another mockup ([product-design.md](product-design.md),
  "Identity And Design Automation Boundary").
- Use the agreed words in [GLOSSARY.md](../../GLOSSARY.md) on the screen and in
  the page.

## Privacy

- Pages are **private Artifacts by default** (Claude). Codex uses the equivalent
  private page or a local HTML file. Share more widely only when Hafiz asks.
- **Screenshots never show real personal data.** Mask names, phone numbers,
  emails, addresses, IC numbers, payment details and children's details before
  the image leaves the machine. Prefer fictional data; when a real screen must
  be shown, mask it in the image, not only in the caption.
- Production screenshots use a read-only path from
  [agent-access-map.md](agent-access-map.md). Never capture a credential, token
  or `.env*` value in an image, DOM dump or accessibility tree.
- An address is private at every stage: show the Area or "Online" only.

## Writing Rules

- Malaysian time everywhere, written like `16:36 MYT`.
- The agreed glossary words; never the listed alternatives.
- No em dashes.
- Plain sentences: use the real term and define it once
  ([agent-os-communication.md](agent-os-communication.md), "Technical In
  Natural Language").

## Publishing

1. Build the page. Keep its data in one file (for example `status.json`) and
   render the page from it, so it can be rebuilt quickly.
2. Publish it as a private Artifact (Claude) or the equivalent private page
   (Codex), and keep the local source path.
3. Open it for Hafiz automatically
   ([agent-os-communication.md](agent-os-communication.md), "Open Review
   Artifacts Automatically") and send the link and the local path in chat.
4. Apply the non-blocking rule above: wait, or keep working.
5. When a fact changes (a decision taken, a test result, a new screenshot),
   update the data file and republish the same page.

## Checklist

Plan mode:

- [ ] The change is visible on screen, so the plan page is due.
- [ ] Three-line summary at the top.
- [ ] Every change has business and technical side by side.
- [ ] Today's real screen for each change, masked.
- [ ] Proposed screen from real components with fictional data, or an honest
      "cannot render yet" note; nothing hand-drawn.
- [ ] Decisions with options and a recommendation, or "none".
- [ ] Risks, done means and evidence plan.
- [ ] Private, MYT times, glossary words, no em dashes.
- [ ] Published, opened for Hafiz, link sent; waited or kept working according
      to whether he gave the go.

Ship mode:

- [ ] Adversarial review finished and its findings fixed first.
- [ ] Real screenshots of every UI change, desktop and phone where relevant.
- [ ] Test, E2E and Codex or cold review results with real numbers.
- [ ] Decisions made on his behalf, risks and what is not proven.
- [ ] Release state and exact approvals still needed.
- [ ] Private, masked, MYT times, glossary words, no em dashes.
- [ ] Published and opened; no deploy until Hafiz confirms, apart from a
      staging deploy he already approved for this release, or a production
      deploy he already told you to go to.

## Skill

Claude: `/review-page plan <project>` or `/review-page ship <project>`.
Codex: `$review-page plan <project>` or `$review-page ship <project>`. The skill
is a thin pointer to this playbook (`.agents/skills/review-page/SKILL.md`).
