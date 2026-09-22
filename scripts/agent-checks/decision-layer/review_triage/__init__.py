"""Review and evidence triage: a bounded advisory classification module.

See `triage.py` for the entry point and `.agent-os/handoffs/bundle-5-build-spec.md`
(issue #166) for the task specification this module implements.

This `__init__.py` exists only so `python3 -m unittest discover` (run from
the parent `decision-layer/` directory) recurses into this package and
picks up its tests alongside Bundle 1's. Every module in this package still
imports its siblings with plain flat imports (after inserting its own
directory onto `sys.path`), matching the rest of `decision-layer/` -- this
file adds no package-relative import behavior of its own.
"""
