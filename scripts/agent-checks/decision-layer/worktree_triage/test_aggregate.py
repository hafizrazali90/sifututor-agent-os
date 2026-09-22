#!/usr/bin/env python3
"""TDD tests for worktree_triage.aggregate: a read-only, human-readable
grouped summary over a batch of classify_entry() results. Performs no
deletion, park, or close action -- report only.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_module(name, directory=HERE):
    spec = importlib.util.spec_from_file_location(name, directory / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


classifier = load_module("classifier")
aggregate = load_module("aggregate")
fixtures = load_module("fixtures")
provider_fake = load_module("provider_fake", HERE.parent)


def _classify_mixed_batch():
    fake = provider_fake.FakeProvider(scenario="ok")
    entries = [
        (fixtures.STALE_LEASE_ENTRY, {}),
        (
            fixtures.OBSOLETE_TASK_POINTER_ENTRY,
            {
                "task_freshness": fixtures.OBSOLETE_TASK_POINTER_FRESHNESS[
                    fixtures.OBSOLETE_TASK_POINTER_ENTRY["worktree"]
                ]
            },
        ),
        (fixtures.GENERATED_DEPENDENCY_BLOCKER_ENTRY, {}),
        (fixtures.MERGED_BRANCH_ENTRY, {}),
        (fixtures.UNCERTAIN_ENTRY, {"provider": fake}),
        (fixtures.ACTIVE_LEASE_ENTRY, {}),
    ]
    return [classifier.classify_entry(entry, **kwargs) for entry, kwargs in entries]


class AggregateGroupingTest(unittest.TestCase):
    def test_groups_a_mixed_batch_by_bucket_with_counts(self) -> None:
        results = _classify_mixed_batch()
        summaries = aggregate.aggregate(results)
        by_bucket = {summary.bucket: summary.count for summary in summaries}
        self.assertEqual(
            by_bucket,
            {
                "stale_lease": 1,
                "obsolete_task_pointer": 1,
                "generated_dependency_blocker": 1,
                "merged_branch": 1,
                "uncertain": 1,
                "preserve": 1,
            },
        )

    def test_examples_name_the_actual_worktree_paths(self) -> None:
        results = _classify_mixed_batch()
        summaries = aggregate.aggregate(results)
        stale_lease_summary = next(s for s in summaries if s.bucket == "stale_lease")
        self.assertIn(fixtures.STALE_LEASE_ENTRY["worktree"], stale_lease_summary.examples)

    def test_aggregate_performs_no_action_of_its_own(self) -> None:
        """aggregate() must be a pure read/report function: calling it
        must not require or accept any deletion/park/close capability."""
        import inspect

        signature = inspect.signature(aggregate.aggregate)
        self.assertEqual(list(signature.parameters), ["results"])


class RenderSummaryTest(unittest.TestCase):
    def test_render_summary_is_human_readable_and_mentions_every_bucket(self) -> None:
        results = _classify_mixed_batch()
        text = aggregate.render_summary(results)
        self.assertIn("6 entries classified", text)
        for bucket in (
            "stale_lease",
            "obsolete_task_pointer",
            "generated_dependency_blocker",
            "merged_branch",
            "uncertain",
            "preserve",
        ):
            self.assertIn(bucket, text)

    def test_render_summary_of_empty_batch_does_not_error(self) -> None:
        text = aggregate.render_summary([])
        self.assertIsInstance(text, str)
        self.assertTrue(text)


if __name__ == "__main__":
    unittest.main()
