"""Knowledge-lifecycle classification module (issue #167, Bundle 6).

A standalone classification layer for candidate memories, ranked recall,
and Session Map archive proposals. See `classifier.py`, `ranking.py`, and
`archive_classifier.py` for the three pieces, and
`.agent-os/handoffs/bundle-6-build-spec.md` for the scope boundary this
module was built against, and `bundle-6-correction-spec.md` for the
review corrections applied.

NOT WIRED. Nothing here is called from the memory-flush hooks, any
session-map flow, or any Koda read/write path. The Claude extraction
subprocess in memory-flush is not replaced and Koda's own ranking is not
changed. Integration (shadow mode first) is deferred to a later bundle.

This `__init__.py` exists only so `python3 -m unittest discover` (run from
the parent `decision-layer/` directory) recurses into this subdirectory;
every module here still loads standalone via `importlib.util` in the
sibling decision-layer modules' own convention, so nothing here requires
being imported as a package.
"""
