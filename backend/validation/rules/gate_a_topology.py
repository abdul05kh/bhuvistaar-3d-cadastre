from typing import Sequence
from uuid import UUID
from backend.domain.validation import ValidationIssue
from backend.domain.enums import IssueSeverity
from backend.domain.parcel import ParentParcel
from backend.domain.spatial_unit import SpatialUnit3D
from backend.validation.rules.base import BaseValidationRule
from backend.geometry.topology import verify_parent_containment
from backend.config import settings


class RuleTop001ParentContainment(BaseValidationRule):
    rule_code = "TOP-001"
    rule_family = "TOPOLOGY"
    description = (
        "Child spatial unit footprint must be completely contained within the parent parcel boundary. "
        "Does NOT silently clip geometry; reports exact uncontained area for human review."
    )

    def evaluate(self, run_id: UUID, parcel: ParentParcel, units: Sequence[SpatialUnit3D]) -> list[ValidationIssue]:
        issues = []
        tolerance = settings.PLANAR_CONTAINMENT_TOLERANCE_M
        
        for unit in units:
            is_contained, exterior_area_sqm, diff_geom = verify_parent_containment(
                child=unit.footprint_geom,
                parent=parcel.geometry,
                tolerance=tolerance
            )
            
            if is_contained:
                issues.append(
                    ValidationIssue(
                        run_id=run_id,
                        rule_code=self.rule_code,
                        severity=IssueSeverity.INFO,
                        object_type="SPATIAL_UNIT",
                        object_id=unit.prototype_vuid,
                        passed=True,
                        message=f"Unit footprint is completely contained within parent parcel '{parcel.ulpin}'.",
                        measured_value={"exterior_area_sqm": 0.0},
                        threshold={"max_exterior_area_sqm": tolerance},
                        suggested_action=None
                    )
                )
            else:
                issues.append(
                    ValidationIssue(
                        run_id=run_id,
                        rule_code=self.rule_code,
                        severity=IssueSeverity.BLOCKER,
                        object_type="SPATIAL_UNIT",
                        object_id=unit.prototype_vuid,
                        passed=False,
                        message=(
                            f"Footprint of unit {unit.prototype_vuid} extends beyond parent parcel '{parcel.ulpin}'. "
                            f"Detected {exterior_area_sqm} sq.m exterior boundary encroachment. "
                            f"Candidate geometry was not auto-clipped."
                        ),
                        measured_value={
                            "exterior_area_sqm": exterior_area_sqm,
                            "exterior_wkt": diff_geom.wkt if diff_geom else None
                        },
                        threshold={"max_exterior_area_sqm": tolerance},
                        suggested_action=(
                            "Review survey boundaries and adjust candidate footprint to lie strictly "
                            "within authoritative parcel boundary."
                        )
                    )
                )
        return issues
