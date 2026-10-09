---
description: List the skills in plain language, grouped by job, with how to run each one
---

Show Hafiz the skill list below exactly as written, then stop. Do not run any skill and do not re-research the list. It is generated from `docs/agent-playbooks/skill-tips.json`; if Hafiz says one is missing or wrong, fix that file and this one together.

If he adds a word after the command (for example `/skills test`), show only the matching group.

## How to run one

- In Claude, type `/name` (for example `/verify`). You can add words after it.
- In Codex, type `$name` instead. Entries marked (Codex only) or (Claude only) work in one tool.
- You do not have to remember them. While we work, a one-line Tip appears after a skill is used and a Suggestion appears when one could help.
- Project skills (the ones starting `ripple-`, `sifu-`, `rn-`, `lls-`) are called for you by `/task-router`, `/qa`, `/commit` and `/verify`. You rarely type them.


## Start work

- `/task-router`: Picks the right way to do a job (bug fix, new feature, small change, docs) before any work starts, so no step is skipped.
- `/triage` (Claude only): Goes through open GitHub issues one by one, labels them and marks which ones are ready to build.
- `/to-issues` (Claude only): Turns an agreed plan into separate GitHub issues, each small enough to build and check on its own.
- `/research` (Claude only): Sends a background helper to read the real sources about a question and writes the findings as a note with links.
- `/grill-me` (Claude only): Asks you hard questions about a plan, one at a time, until the weak spots are found.
- `/domain-modeling` (Claude only): Checks the words we use against the project glossary and proposes one precise word when two things share a name.
- `/repo-onboard` (Claude only): Scans a project and its database once to build a starting knowledge pack: summary, memories and a review checklist.
- `/next` (Claude only): Shows the next build prompt that is ready to start and how far the overall build has got.
- `$quick-check` (Codex only): Checks that the Claude and Codex workflow system is healthy and wired correctly before you start.

## Build

- `/implement` (Claude only): Builds one agreed piece of work from its ticket: test first, reviewed, and committed on its own branch.
- `/tdd` (Claude only): Builds a feature test first: write one failing check, make it pass, then repeat in small steps.
- `/diagnose`: Finds the real cause of a bug step by step before anything is changed.
- `/graphify` (Claude only): Turns code, documents or images into a map of connected ideas that you can ask questions about.
- `/write-a-skill` (Claude only): Creates a new skill with the right structure and description so it gets picked up later.

## Test

- `/qa`: Runs the project's quality checks and smoke tests and tells you whether the work meets the standard.
- `/verify`: Proves with evidence that the work really does what was asked, before QA, review or commit.
- `/browser-test` (Claude only): Opens a real browser, clicks through the pages like a person, takes screenshots and judges them.
- `/qa-audit` (Claude only): Finds which parts of a project have no tests, ranks the risks and fills the biggest gaps first.
- `/test-coverage-audit` (Claude only): Checks whether the files you just changed have tests listed in the project's TESTING.md.
- `/testcases` (Claude only): Writes manual test cases that a first-time tester can run without knowing the system.
- `/mobile-pre-push-qa` (Claude only): Reads a backend change and lists what could break in the mobile app that is already live. Project: sifu-tutor.

## Review

- `/review`: Gives finished work an independent risk check before commit, push, merge or deploy.
- `/sims-ui-audit`: Checks a SIMS screen for spacing, tables, filters and disabled states, with screenshots as proof. Project: sifu-tutor.

## Commit and wrap up

- `/commit`: Prepares a commit with the exact file list, the safety checks and the right message format.
- `/save-session`: Saves what we learned today into memory and updates the project notes so the next chat starts informed.
- `/snapshot`: Saves the goal, next steps and key files before the chat is compacted, so work can resume without losing the thread.
- `/handoff`: Packs the current work into a note that another Claude, Codex or person can pick up without asking you again.
- `/session-summary` (Claude only): Writes the full story of a session: what was reported, found, corrected and finally done.
- `$session-map` (Codex only): Keeps a map of several goals in one session so you can always see what is open and how to return.

## Operations and reports

- `/weekly-report` (Claude only): Summarises what shipped this week and what is blocked as a short team report.
- `$weekly-delivery` (Codex only): Summarises what shipped this week and what is blocked as a short team report.
- `/prod-audit` (Claude only): Audits a live system for health, security, code quality and deployment habits and ranks the problems found.
- `/monitor-production-logs`: After a release, watches Sentry and BetterStack for new errors, especially in payments and the mobile API.
- `/koda-audit` (Claude only): Checks the health of the shared memory (Koda), finds stale, duplicate or misplaced entries and proposes a cleanup.
- `/self-improve` (Claude only): Looks at repeated failures and past corrections and proposes which ones should become permanent rules, one by one for your approval.
- `/workflow-improvement`: Fixes the working system itself (skills, hooks, playbooks) when an agent keeps making the same mistake.

## Design

- `/brainstorm` (Claude only): Explores what you really want and the real options before any code is written, then agrees a design.
- `$product-design` (Codex only): Takes a feature from idea to requirements, UX and build prompts before anything is built.
- `/lite-prd` (Claude only): Turns an idea into a ten-section product requirements document and reviews the user stories with you.
- `/prd-clarifier` (Claude only): Asks 5 to 35 structured questions to remove the unclear parts of a PRD before screens are designed.
- `/prd-to-ux` (Claude only): Turns a PRD into a UX specification by looking at it through six designer mindsets.
- `/ux-to-prompts` (Claude only): Turns a UX spec into ordered build prompts, showing how hard each is and what depends on what.
- `/prototype` (Claude only): Builds a quick throwaway version to answer one question, such as whether a flow feels right.
- `/autopilot` (Claude only): Designs a whole app flow end to end: research, every screen in Figma, two reviewers, fixes and one review pack.
- `/doc-design` (Claude only): Gives proposals, reports and one-pagers the Learnest Lab look, starting from a storyboard.
- `/identity-design` (Claude only): Designs a logo or brand identity properly: brief, options, checks, review and trademark search.
- `/fal-illustration` (Claude only): Generates flat vector illustrations in the app's style for banners and empty states.
- `/deck-craft`: Builds or repairs a slide deck so every slide is a real graphic, then lints the layout and runs four reviewers.

## Ask for help

- `/zoom-out` (Claude only): Steps back and explains how an unfamiliar part of the code fits into the whole system.
- `/wizard` (Claude only): Builds a step-by-step script that walks you through things only a human can do, like setting up accounts or secrets.
- `/wait-what` (Claude only): Use it when the last message did not land: it says the same thing again in plain terms.
- `/teach` (Claude only): Teaches you a new skill or concept, using this workspace as the example.
- `/to-questionnaire` (Claude only): Turns a decision you cannot make alone into questions for one other person, such as Finance or a developer.
