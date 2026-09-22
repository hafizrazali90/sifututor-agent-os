#!/usr/bin/env python3
"""Negative fixtures for the PR #172 review correction: critical lanes are
never delegated to a provider.

One fixture per critical lane (`.agent-os/handoffs/bundle-2-correction-spec.md`,
required change 1), plus the two secret-filter paths. Every test scripts a
`FakeProvider` and proves it was never dispatched to (`call_count == 0`),
that the response says so (`provider_called is False`), that risk is
`critical`, and that the reason names the lane. "High sensitivity" is not
permission to transmit; nothing in a critical lane ever becomes a provider
request.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import unittest

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent
for _path in (HERE, PARENT):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))


def load_module(name, where=HERE):
    spec = importlib.util.spec_from_file_location(name, where / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


catalog = load_module("catalog")
deterministic = load_module("deterministic")
shadow_router = load_module("shadow_router")
provider_fake = load_module("provider_fake", where=PARENT)
config_module = load_module("config", where=PARENT)

# Built by concatenation, like test_secret_filter.py, so the staged-diff
# guard never sees a token-shaped literal in this file.
FIXTURE_ANTHROPIC_STYLE = "sk-ant-api03-" + "a" * 12 + "b" * 12


def test_config(**overrides):
    cfg = config_module.load_config(env={})
    cfg.update(overrides)
    return cfg


class CriticalLaneNeverReachesProviderMixin:
    """Shared assertions: scripted FakeProvider untouched, deterministic
    provider reported, risk critical, reason names the lane."""

    lane: str = ""
    text: str = ""

    def assert_never_delegated(self, text: str, lane: str) -> dict:
        fake = provider_fake.FakeProvider(scenario="ok")
        response = shadow_router.route(text, provider=fake, config=test_config())
        self.assertEqual(fake.call_count, 0)
        self.assertFalse(response["provider_called"])
        self.assertEqual(response["risk_level"]["value"], "critical")
        self.assertTrue(response["risk_level"]["forced"])
        self.assertEqual(response["risk_level"]["lane"], lane)
        self.assertEqual(response["risk_level"]["reason"], f"critical_lane:{lane}")
        self.assertEqual(response["workflow_route"]["provider"], "deterministic")
        self.assertFalse(response["workflow_route"]["fallback_used"])
        self.assertFalse(response["workflow_route"]["authoritative"])
        self.assertIn(response["workflow_route"]["value"], catalog.WORKFLOW_ROUTES)
        self.assertIn(f"risk_override:critical_lane:{lane}", response["deterministic_overrides_applied"])
        self.assertEqual(response["observability"]["provider"], "deterministic")
        return response

    def test_lane_is_never_delegated(self) -> None:
        self.assert_never_delegated(self.text, self.lane)


class Lane01PaymentsTest(CriticalLaneNeverReachesProviderMixin, unittest.TestCase):
    lane = "payments"
    text = "Update the commission payout logic for July, the invoice totals look wrong"

    def test_route_is_still_the_classifiers_own_top_pick(self) -> None:
        response = self.assert_never_delegated(
            "The payout screen is broken - clicking Verify does nothing and the console shows an error",
            "payments",
        )
        self.assertEqual(response["workflow_route"]["value"], "diagnosis")
        self.assertEqual(response["task_type"], "bugfix")


class Lane02AuthTest(CriticalLaneNeverReachesProviderMixin, unittest.TestCase):
    lane = "auth"
    text = "Can you change how tutor login sessions expire and which roles and permissions apply?"


class Lane03ProductionMigrationTest(CriticalLaneNeverReachesProviderMixin, unittest.TestCase):
    lane = "production_migration"
    text = "Write a migration to add a column to the tutors table and run it on production"


class Lane04DestructiveActionTest(CriticalLaneNeverReachesProviderMixin, unittest.TestCase):
    lane = "destructive_action"
    text = "Truncate the old audit table, then rm -rf the export folder and force-push the cleanup"


class Lane05MobileApiContractTest(CriticalLaneNeverReachesProviderMixin, unittest.TestCase):
    lane = "mobile_api_contract"
    text = "Change the response shape of the mobile API endpoint for class listings"


class Lane06SecretsCredentialsTest(CriticalLaneNeverReachesProviderMixin, unittest.TestCase):
    lane = "secrets_credentials"
    text = "Rotate the API key in the .env file on staging"


class Lane07PrivateProductionDataTest(CriticalLaneNeverReachesProviderMixin, unittest.TestCase):
    lane = "private_production_data"
    text = "Export the parent records with phone numbers from the prod DB dump"


class Lane08ApprovalDecisionTest(CriticalLaneNeverReachesProviderMixin, unittest.TestCase):
    lane = "approval_decision"
    text = "Approve this, merge it, and deploy it to production tonight"


class SecretFilterFiresBeforeAnyProviderRequestTest(CriticalLaneNeverReachesProviderMixin, unittest.TestCase):
    """Bundle 1's secret filter runs in `route()` itself, before a provider
    request is even constructed -- not only inside `engine.decide()`."""

    def test_credential_shaped_content_is_never_delegated(self) -> None:
        # "key" alone is not a lane keyword, so this proves the filter
        # path rather than keyword detection.
        self.assert_never_delegated("Here is the key " + FIXTURE_ANTHROPIC_STYLE + ", can you check it?", "secrets_credentials")

    def test_pii_shaped_content_is_never_delegated(self) -> None:
        # An email address is PII-shaped; no keyword lane matches it.
        self.assert_never_delegated(
            "Can you look up why someone@example.com keeps getting the wrong rating average?",
            "private_production_data",
        )

    def test_lane_is_never_delegated(self) -> None:
        # The mixin's generic case is covered by the two explicit tests above.
        self.assert_never_delegated("The student's IC is 900101-14-5566, check the record", "private_production_data")


class NonCriticalTextStillReachesTheProviderTest(unittest.TestCase):
    """Sanity check for the negative fixtures above: the same scripted
    provider IS dispatched to when nothing critical is present, so the
    zero call counts above are meaningful."""

    def test_plain_non_critical_text_is_delegated_exactly_once(self) -> None:
        fake = provider_fake.FakeProvider(scenario="ok")
        response = shadow_router.route(
            "Please build a new report screen for tutor ratings", provider=fake, config=test_config()
        )
        self.assertEqual(fake.call_count, 1)
        self.assertTrue(response["provider_called"])
        self.assertIsNone(response["risk_level"]["lane"])
        self.assertEqual(response["workflow_route"]["provider"], "fake")


if __name__ == "__main__":
    unittest.main()
