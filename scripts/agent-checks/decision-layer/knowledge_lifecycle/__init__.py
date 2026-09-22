"""Knowledge-lifecycle classification module (issue #167, Bundle 6).

A standalone classification layer for candidate memories, ranked recall,
and Session Map archive proposals. See `classifier.py`, `ranking.py`, and
`archive_classifier.py` for the three pieces, and
`.agent-os/handoffs/bundle-6-build-spec.md` for the scope boundary this
module was built against.

This `__init__.py` exists only so `python3 -m unittest discover` (run from
the parent `decision-layer/` directory) recurses into this subdirectory;
every module here still loads standalone via `importlib.util` in the
sibling decision-layer modules' own convention, so nothing here requires
being imported as a package.
"""
