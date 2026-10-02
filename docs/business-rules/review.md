# Business-rule compilation and local workflow protection

Requested by Hafiz after repeated agent confusion: multiple students selected
on one Request were being interpreted as separate classes. Expected behaviour
is one shared scheduled class with all participants. Author: Codex. Issue:
[Agent OS #241](https://github.com/hafizrazali90/sifututor-agent-os/issues/241).

## Review package

| Business meaning | Technical change |
| --- | --- |
| Agents read intended rules before interpreting implementation | Shared AGENTS and context-authority route to the business-rule index |
| One lesson with three students stays one shared class | Declared-example validator rejects student multiplication, missing participants and code-only authority |
| Old memories and drafts cannot silently become policy | 104-rule register preserves status; 74-record full-memory audit; unresolved decisions collected |
| Existing product owners remain authoritative | Central index points to domain sources, rather than replacing every product rulebook |
| Both agents use the same route | Existing Claude AGENTS import and Codex shared entry tested by navigation fixtures |

## Scope and storage

- Repository owner entry: [README.md](README.md).
- Sourced compilation: [register.md](register.md).
- Attributed rationale: [decision-reasons.md](decision-reasons.md), with unknowns explicit.
- Provenance inventory: [sources.json](sources.json), 149 candidate documents.
- Full memory metadata: [memory-audit.md](memory-audit.md), 74 records.
- Remaining policy/source questions: [open-decisions.md](open-decisions.md).
- Historical research trail: [reconciliation.md](reconciliation.md).
- Human research view: [Pages register](https://chatgpt.com/space/page_8ab8bb4a21ac819189634d6470a4831a).

This is a bounded compilation of available evidence. All 149 discovered
candidate locators are inventoried; 240 selected passages were extracted in
the initial catalogue, followed by focused decision/source reconciliation.
It is not a claim of full semantic review of every document line or every
historical conversation. Draft, unrelated operational, duplicated and source-gap
material does not become policy merely because it was indexed. Unresolved
current-policy questions remain explicitly excluded from automatic authority.

## Verification

- Fourteen focused unit/negative-fixture tests passed, including shared lessons,
  distinct Requests, participant multiplication, missing participants, bad
  authority references, malformed examples and broken entry-point detection.
- The proposal CLI passed against the documented three-student/one-lesson
  example. Its output explicitly states that application behaviour is untested.
- Navigation check: 22/22 evaluated checks passed, including new NAV-24 and
  NAV-25 for Codex/Claude business-rule loading; twelve product-checkout
  scenarios were unavailable in this standalone worktree, not counted as passed.
- `git diff --check` passed. The shared pre-commit guard completed; nothing was
  staged, so its staged-secret check is not proof of a staged release bundle.
  TESTING/release-doc manifest checks reported unavailable, not passed.
- Full `workflow-doctor.sh` ran and reported one failure: CL-050, the installed
  global Claude adapter contains an ambiguous relative communication-playbook
  pointer in `~/.claude/CLAUDE.md`. The same adapter check fails from the unchanged
  canonical checkout. It is outside these changes and was not bypassed or
  silently repaired. The whole-machine doctor is therefore **not green**.

These checks prove source structure, shared navigation and declared
acceptance-example validation. No fresh paid Claude/Codex model evaluation or
application E2E was run. No UI changed; screenshots are not relevant. The
workflow checker is included in normal Agent OS health runs. Product E2E
exception: not user-facing application work.

Adversarial self-review checked that the validator does not certify source
approval merely from a count, that source gaps remain visible, that its positive
case preserves all participants, and that negative examples fail. This is
not an independent second-agent review. Koda rule mem_0303 was updated in place
to preserve business authority, exact source retrieval and autonomous routine
continuation; the update was read-back verified by the helper.

## Release state and limits

Activated locally in the primary umbrella on 3 October 2026:
`/Users/hafizrazali/Projects/Sifututor/docs/business-rules/README.md`.
The original isolated worktree remains a preserved pre-activation snapshot.
Original branch: `docs/241-business-rule-authority`. Base:
`fa0098dbe382c72f9335d26684d1197515d79eeb`. Session:
`01a0fd50-8f18-7450-82f1-f3577be0eb1e`.

The primary umbrella now contains the verified document/fixture changes, still
uncommitted. Product repositories are unchanged. New umbrella sessions reach
the index through shared AGENTS; already-running agents must reread it. The
global Claude communication link was corrected to an unambiguous workspace
path and all eight installed-adapter checks pass.
No commit, push, PR, merge, deployment, application change, production-data
write, financial-policy change or outbound notification is included.

The original local stop point was extended by Hafiz asking for practical task
completion; the rulebook is now activated in the primary workspace. Product regression tests and integration/release
are separate future work; this checker cannot guarantee model compliance or
application behaviour. Preserve this uncommitted worktree for review.

## Primary-workspace activation checks

Fourteen focused tests passed again in the primary checkout. The declared
example and task-scoped diff checks pass. Navigation reports 24/34 evaluated
checks passed, zero failures and ten pre-existing product-adapter advisories;
these advisories are not passes. Umbrella NAV-24/25 both pass. The isolated
worktree doctor result above is historical; its CL-050 failure is fixed.
The full primary-workspace doctor completed with three reported issues: the
existing September 22 Jev session map lacks required fields (reported both
in health and the map check), and the Finch active-task pointer is dangling.
These files were untouched. Broader machine health remains non-green; this
does not invalidate the passing business-rule/umbrella-loading checks.

## Business answers received, 3 October 2026

All three clarification questions are resolved by Hafiz: one-month resignation
notice (BR-025); whole shared-class payout settled together without individual
student component deferral (BR-063); and collection Done with a separate open
service follow-up while classes remain held (BR-091). The register and open
questions now reflect these decisions. Other draft/source gaps remain recorded.
No further clarification is required for the agreed documentation/local-protection
stop point. This does not approve draft product work or execute financial changes.
