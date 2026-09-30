"""Unit tests for Ruleset Versioning (Slice 4)."""
from backend.validation.rules.base import BaseValidationRule
from backend.validation.rules.gate_a_vertical import RuleVrt003FloorOverlap
from backend.validation.rules.gate_a_geometry import RuleGeo001NonEmpty
from backend.validation.rules.gate_a_topology import RuleTop001ParentContainment
from backend.validation.runner import ValidationRunner


def test_rules_have_explicit_versioning():
    """All validation rules must declare explicit rule_version and ruleset_version."""
    vrt = RuleVrt003FloorOverlap()
    assert vrt.rule_version == "1.0.0"
    assert vrt.ruleset_version == "1.0.0"

    geo = RuleGeo001NonEmpty()
    assert geo.rule_version == "1.0.0"
    assert geo.ruleset_version == "1.0.0"

    top = RuleTop001ParentContainment()
    assert top.rule_version == "1.0.0"
    assert top.ruleset_version == "1.0.0"


def test_validation_runner_executes_versioned_ruleset():
    """ValidationRunner must preserve ruleset_version in execution."""
    runner = ValidationRunner()
    for rule in runner.rules:
        assert hasattr(rule, "rule_version")
        assert rule.rule_version == "1.0.0"
        assert rule.ruleset_version == "1.0.0"
