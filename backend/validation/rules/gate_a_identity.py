from typing import Sequence
from uuid import UUID
from backend.domain.validation import ValidationIssue
from backend.domain.enums import IssueSeverity
from backend.domain.parcel import ParentParcel
from backend.domain.spatial_unit import SpatialUnit3D
from backend.validation.rules.base import BaseValidationRule
from backend.vuid.generator import generate_prototype_vuid


class RuleId001ParentUlpinIntegrity(BaseValidationRule):
    rule_code = "ID-001"
    rule_family = "IDENTITY"
    description = "Parent ULPIN must exist, match parent parcel, and be exactly 14 numeric digits."

    def evaluate(self, run_id: UUID, parcel: ParentParcel, units: Sequence[SpatialUnit3D]) -> list[ValidationIssue]:
        issues = []
        p_valid = bool(parcel.ulpin and len(parcel.ulpin) == 14 and parcel.ulpin.isdigit())
        issues.append(
            ValidationIssue(
                run_id=run_id,
                rule_code=self.rule_code,
                severity=IssueSeverity.BLOCKER,
                object_type="PARENT_PARCEL",
                object_id=parcel.ulpin,
                passed=p_valid,
                message="Parent ULPIN format is valid." if p_valid else f"Parent ULPIN '{parcel.ulpin}' is invalid (must be 14 digits).",
                measured_value={"ulpin": parcel.ulpin, "length": len(parcel.ulpin)},
                threshold={"format": "14 numeric digits"},
                suggested_action=None if p_valid else "Verify official Bhu-Aadhaar 14-digit identifier."
            )
        )
        
        for unit in units:
            u_match = unit.parent_ulpin == parcel.ulpin
            issues.append(
                ValidationIssue(
                    run_id=run_id,
                    rule_code=self.rule_code,
                    severity=IssueSeverity.BLOCKER,
                    object_type="SPATIAL_UNIT",
                    object_id=unit.prototype_vuid,
                    passed=u_match,
                    message="Unit parent ULPIN correctly matches parent parcel." if u_match else f"Unit parent ULPIN '{unit.parent_ulpin}' does not match parcel '{parcel.ulpin}'.",
                    measured_value={"unit_parent_ulpin": unit.parent_ulpin, "parcel_ulpin": parcel.ulpin},
                    threshold={"match": True},
                    suggested_action=None if u_match else "Relink spatial unit to authoritative parent parcel."
                )
            )
        return issues


class RuleId002VuidUniqueness(BaseValidationRule):
    rule_code = "ID-002"
    rule_family = "IDENTITY"
    description = "Prototype VUIDs must be unique across all spatial units."

    def evaluate(self, run_id: UUID, parcel: ParentParcel, units: Sequence[SpatialUnit3D]) -> list[ValidationIssue]:
        issues = []
        seen_vuids: dict[str, list[str]] = {}
        for unit in units:
            seen_vuids.setdefault(unit.prototype_vuid, []).append(unit.level_code)
            
        for vuid, levels in seen_vuids.items():
            is_unique = len(levels) == 1
            issues.append(
                ValidationIssue(
                    run_id=run_id,
                    rule_code=self.rule_code,
                    severity=IssueSeverity.BLOCKER,
                    object_type="SPATIAL_UNIT",
                    object_id=vuid,
                    passed=is_unique,
                    message="Prototype VUID is unique." if is_unique else f"Duplicate prototype VUID '{vuid}' assigned to multiple units: {levels}",
                    measured_value={"count": len(levels), "levels": levels},
                    threshold={"count": 1},
                    suggested_action=None if is_unique else "Regenerate units with distinct geometry or level codes."
                )
            )
        return issues


class RuleId003VuidDeterminism(BaseValidationRule):
    rule_code = "ID-003"
    rule_family = "IDENTITY"
    description = "VUID must be reproducible and match the deterministic hash calculation."

    def evaluate(self, run_id: UUID, parcel: ParentParcel, units: Sequence[SpatialUnit3D]) -> list[ValidationIssue]:
        issues = []
        for unit in units:
            # Recompute expected VUID from unit geometry and vertical bounds
            expected_res = generate_prototype_vuid(
                parent_ulpin=unit.parent_ulpin,
                unit_class="BLDG",
                level_code=unit.level_code,
                footprint_geom=unit.footprint_geom,
                z_min=unit.z_min,
                z_max=unit.z_max,
                algorithm_version=unit.vuid_algorithm_version
            )
            
            is_deterministic = (
                unit.prototype_vuid == expected_res.prototype_vuid and
                unit.vuid_full_hash == expected_res.vuid_full_hash
            )
            
            issues.append(
                ValidationIssue(
                    run_id=run_id,
                    rule_code=self.rule_code,
                    severity=IssueSeverity.BLOCKER,
                    object_type="SPATIAL_UNIT",
                    object_id=unit.prototype_vuid,
                    passed=is_deterministic,
                    message="VUID matches deterministic derivation." if is_deterministic else f"VUID mismatch: stored '{unit.prototype_vuid}', expected '{expected_res.prototype_vuid}'",
                    measured_value={"stored_vuid": unit.prototype_vuid, "computed_vuid": expected_res.prototype_vuid},
                    threshold={"match": True},
                    suggested_action=None if is_deterministic else "Recompute VUID using canonical geometry pipeline."
                )
            )
        return issues
