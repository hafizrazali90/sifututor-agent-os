# Sandcastle as the runner for the home PC

## What was proposed

Use `mattpocock/sandcastle` (`@ai-hero/sandcastle`, version 0.12.0) to run
builder and reviewer agents in sealed containers on the home PC, instead of our
own small runner.

## Why it is out of scope

- It has no spend control. There is no budget flag and no cumulative cost, and
  the only caps are an iteration limit and a 10 minute idle timeout.
- It runs Claude with permission prompts turned off inside the container, so the
  container is the only boundary.
- Open issue #1010 in its repository shows that code written inside the
  container can run on the host through the shared `.git` folder. No fix is
  shipped.
- The default branch strategy edits the real working folder.
- Its sample flow merges branches and closes issues with no human step, which
  breaks our rule of no unattended merges.
- It does not know our rules, approvals or finish states. It is a place to run
  an agent, not a rulebook.
- One maintainer, version 0.12.0, 100 or more open issues.

Study: the Sandcastle comparison page of 08/10/2026 (private artifact).

## What would change our mind

A shipped spend cap, a hardened git folder (no shared hooks or config between
container and host), and a trial on a throwaway repository with Podman, a fresh
copy per job and no push token that shows it beats our runner on a real job.

## Decided

08/10/2026 (MYT), Hafiz: build our own small runner (issue #305) and copy the
ideas, not the code.
