#!/usr/bin/env python3
"""TDD tests for the routing catalog: pure data, but its internal
consistency (every workflow route has a playbook/risk/task-type entry, and
every playbook path actually comes from the PLAYBOOKS table) is exactly
the kind of thing a typo can silently break.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, HERE / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


catalog = load_module("catalog")


class CatalogConsistencyTest(unittest.TestCase):
    def test_every_workflow_route_has_a_required_playbooks_entry(self) -> None:
        for route in catalog.WORKFLOW_ROUTES:
            self.assertIn(route, catalog.REQUIRED_PLAYBOOKS_BY_ROUTE)

    def test_every_workflow_route_has_a_default_risk_entry(self) -> None:
        for route in catalog.WORKFLOW_ROUTES:
            self.assertIn(route, catalog.DEFAULT_RISK_BY_ROUTE)
            self.assertIn(catalog.DEFAULT_RISK_BY_ROUTE[route], catalog.RISK_LEVELS)

    def test_no_workflow_route_defaults_to_critical(self) -> None:
        # "critical" is reachable only through a forced deterministic
        # override (build spec: payment/auth/migration always forces
        # critical regardless of the classifier). No workflow route's
        # unconditional default may be "critical".
        for route in catalog.WORKFLOW_ROUTES:
            self.assertNotEqual(catalog.DEFAULT_RISK_BY_ROUTE[route], "critical")

    def test_every_workflow_route_has_a_default_task_type_entry(self) -> None:
        for route in catalog.WORKFLOW_ROUTES:
            self.assertIn(route, catalog.DEFAULT_TASK_TYPE_BY_ROUTE)
            self.assertIn(catalog.DEFAULT_TASK_TYPE_BY_ROUTE[route], catalog.TASK_TYPES)

    def test_required_playbooks_only_reference_the_documented_playbook_table(self) -> None:
        documented_paths = set(catalog.PLAYBOOKS.values())
        for paths in catalog.REQUIRED_PLAYBOOKS_BY_ROUTE.values():
            for path in paths:
                self.assertIn(path, documented_paths)

    def test_project_aliases_resolve_to_a_known_project(self) -> None:
        for alias, canonical in catalog.PROJECT_ALIASES.items():
            self.assertIn(canonical, catalog.KNOWN_PROJECTS, msg=f"alias {alias!r} -> {canonical!r}")

    def test_known_projects_have_no_duplicates(self) -> None:
        self.assertEqual(len(catalog.KNOWN_PROJECTS), len(set(catalog.KNOWN_PROJECTS)))


if __name__ == "__main__":
    unittest.main()
