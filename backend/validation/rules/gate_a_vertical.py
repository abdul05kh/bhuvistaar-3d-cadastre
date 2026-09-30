from typing import Sequence
from uuid import UUID
from backend.domain.validation import ValidationIssue
from backend.domain.enums import IssueSeverity
from backend.domain.parcel import ParentParcel
from backend.domain.spatial_unit import SpatialUnit3D
from backend.validation.rules.base import BaseValidationRule
from backend.config import settings


class RuleVrt001ZOrder(BaseValidationRule):
    rule_code = "VRT-001"
    rule_family = "VERTICAL"
    description = "Lower vertical boundary (z_min) must be strictly less than upper boundary (z_max)."

    def evaluate(self, run_id: UUID, parcel: ParentParcel, units: Sequence[SpatialUnit3D]) -> list[ValidationIssue]:
        issues = []
        for unit in units:
            passed = unit.z_min < unit.z_max
            issues.append(
                ValidationIssue(
                    run_id=run_id,
                    rule_code=self.rule_code,
                    severity=IssueSeverity.BLOCKER,
                    object_type="SPATIAL_UNIT",
                    object_id=unit.prototype_vuid,
                    passed=passed,
                    message=(
                        f"Vertical interval valid for {unit.prototype_vuid} (height: {unit.height_m}m)."
                        if passed else
                        f"Inverted or zero vertical interval: z_min ({unit.z_min}) >= z_max ({unit.z_max})."
                    ),
                    measured_value={"z_min": unit.z_min, "z_max": unit.z_max, "height_m": unit.height_m},
                    threshold={"z_min_less_than_z_max": True},
                    suggested_action=None if passed else "Correct floor boundary elevation values."
                )
            )
        return issues


class RuleVrt003FloorOverlap(BaseValidationRule):
    rule_code = "VRT-003"
    rule_family = "VERTICAL"
    description = (
        "Semantic validation policy for mutually-exclusive adjacent floor strata: "
        "vertical intervals must not overlap beyond tolerance (gap < -0.001m triggers BLOCKER)."
    )

    def evaluate(self, run_id: UUID, parcel: ParentParcel, units: Sequence[SpatialUnit3D]) -> list[ValidationIssue]:
        issues = []
        if len(units) < 2:
            return issues
            
        # Group units by building/mass or sort ordered mutually-exclusive floor intervals by z_min
        sorted_units = sorted(units, key=lambda u: (u.z_min, u.z_max))
        tolerance = settings.ADJACENCY_TOLERANCE_M  # 0.001m
        
        for i in range(len(sorted_units) - 1):
            curr = sorted_units[i]
            nxt = sorted_units[i + 1]
            
            # gap = next.z_min - current.z_max
            gap = round(float(nxt.z_min - curr.z_max), 3)
            
            if gap < -tolerance:
                # Collision / Overlap defect
                overlap_m = round(abs(gap), 3)
                issues.append(
                    ValidationIssue(
                        run_id=run_id,
                        rule_code=self.rule_code,
                        severity=IssueSeverity.BLOCKER,
                        object_type="SPATIAL_UNIT",
                        object_id=nxt.prototype_vuid,
                        passed=False,
                        message=(
                            f"Vertical overlap conflict between level '{curr.level_code}' ({curr.z_min}m–{curr.z_max}m) "
                            f"and level '{nxt.level_code}' ({nxt.z_min}m–{nxt.z_max}m): "
                            f"detected {overlap_m}m overlap (gap={gap}m < -{tolerance}m)."
                        ),
                        measured_value={
                            "gap_m": gap,
                            "overlap_m": overlap_m,
                            "lower_level": curr.level_code,
                            "lower_vuid": curr.prototype_vuid,
                            "upper_level": nxt.level_code,
                            "upper_vuid": nxt.prototype_vuid
                        },
                        threshold={"min_gap_m": -tolerance},
                        suggested_action="Adjust floor boundary interval based on survey evidence."
                    )
                )
            elif -tolerance <= gap <= tolerance:
                # Acceptable adjacency
                issues.append(
                    ValidationIssue(
                        run_id=run_id,
                        rule_code=self.rule_code,
                        severity=IssueSeverity.INFO,
                        object_type="SPATIAL_UNIT",
                        object_id=nxt.prototype_vuid,
                        passed=True,
                        message=(
                            f"Levels '{curr.level_code}' and '{nxt.level_code}' satisfy vertical adjacency "
                            f"(gap={gap}m within +/-{tolerance}m)."
                        ),
                        measured_value={"gap_m": gap},
                        threshold={"min_gap_m": -tolerance},
                        suggested_action=None
                    )
                )
            else:
                # gap > tolerance
                issues.append(
                    ValidationIssue(
                        run_id=run_id,
                        rule_code=self.rule_code,
                        severity=IssueSeverity.WARN,
                        object_type="SPATIAL_UNIT",
                        object_id=nxt.prototype_vuid,
                        passed=True,
                        message=(
                            f"Vertical gap of {gap}m detected between level '{curr.level_code}' "
                            f"and level '{nxt.level_code}'."
                        ),
                        measured_value={"gap_m": gap},
                        threshold={"min_gap_m": -tolerance},
                        suggested_action="Verify if structural slab or plenum gap is intended by design."
                    )
                )
        return issues
