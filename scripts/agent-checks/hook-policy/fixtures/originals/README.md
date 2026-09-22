# Frozen originals for parity testing

Two kinds of "original" are used by `tests/test_parity_*.py`:

1. **Live, in-repo originals** — `.claude/hooks/validate-branch-name.py`,
   `.claude/hooks/conventional-commits.py`, and
   `scripts/agent-checks/codex-pre-tool-use.py` all live inside *this*
   repository already. Parity tests invoke them directly, by their real
   path, as a subprocess — never a copy. If those files change, the parity
   tests re-validate against whatever they currently say. This directory
   does not duplicate them.

2. **Snapshots of sub-project files** (this directory) — `ripple-suite`'s
   `quality-gate.py` and `workflow-gate.py` live in a sibling repository
   (`~/Projects/Sifututor/ripple-suite`, not this one) and cannot be
   referenced by path from a portable test. Each snapshot here is a
   byte-for-byte copy taken on the date in its header comment, used only so
   the parity tests are hermetic and reviewable inside this PR. They are
   inert fixture data, never imported by `hook-policy` itself, and never
   executed except by `subprocess.run([...])` from a test. If the real
   sub-project file changes, these snapshots go stale silently — that is a
   known, accepted limitation of a frozen fixture, not a bug; re-sync them
   by hand next time this module's parity claims need re-verifying.
