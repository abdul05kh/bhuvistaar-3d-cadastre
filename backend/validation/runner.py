from uuid import UUID, uuid4
from typing import Sequence
from backend.domain.validation import ValidationIssue
from backend.domain.parcel import ParentParcel
from backend.domain.spatial_unit import SpatialUnit3D
from backend.domain.enums import IssueSeverity
from backend.validation.rules.base import BaseValidationRule
from backend.validation.rules.gate_a_geometry import (
    RuleGeo001NonEmpty,
    RuleGeo002ValidPolygon,
    RuleGeo003ExplicitCRS,
    RuleGeo004FiniteCoordinates
)
from backend.validation.rules.gate_a_vertical import (
    RuleVrt001ZOrder,
    RuleVrt003FloorOverlap
)
from backend.validation.rules.gate_a_topology import (
    RuleTop001ParentContainment
)
from backend.validation.rules.gate_a_identity import (
    RuleId001ParentUlpinIntegrity,
    RuleId002VuidUniqueness,
    RuleId003VuidDeterminism
)


from backend.validation.rules.gate_b_provenance import (
    RuleProv001ParentLinkage,
    RuleProv002EvidenceAttached,
    RuleProv003EvidenceIntegrity,
    RuleProv004GenerationProvenance
)
from backend.domain.enums import GateType


class ValidationRunner:
    def __init__(self, rules: Sequence[BaseValidationRule] = None, gate: GateType = GateType.GATE_A, evidence_sources: dict = None):
        if rules is not None:
            self.rules = list(rules)
        elif gate == GateType.GATE_B:
            self.rules = [
                RuleProv001ParentLinkage(),
                RuleProv002EvidenceAttached(),
                RuleProv003EvidenceIntegrity(evidence_sources=evidence_sources),
                RuleProv004GenerationProvenance()
            ]
        else:
            # Default Gate A Rule Suite
            self.rules = [
                RuleGeo001NonEmpty(),
                RuleGeo002ValidPolygon(),
                RuleGeo003ExplicitCRS(),
                RuleGeo004FiniteCoordinates(),
                RuleVrt001ZOrder(),
                RuleVrt003FloorOverlap(),
                RuleTop001ParentContainment(),
                RuleId001ParentUlpinIntegrity(),
                RuleId002VuidUniqueness(),
                RuleId003VuidDeterminism()
            ]


    def execute(
        self,
        parcel: ParentParcel,
        units: Sequence[SpatialUnit3D],
        run_id: UUID = None
    ) -> list[ValidationIssue]:
        current_run_id = run_id or uuid4()
        all_issues: list[ValidationIssue] = []
        for rule in self.rules:
            issues = rule.evaluate(run_id=current_run_id, parcel=parcel, units=units)
            all_issues.extend(issues)
        return all_issues
