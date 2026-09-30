from typing import Sequence
from uuid import UUID
from backend.domain.validation import ValidationIssue
from backend.domain.enums import IssueSeverity
from backend.domain.parcel import ParentParcel
from backend.domain.spatial_unit import SpatialUnit3D
from backend.validation.rules.base import BaseValidationRule
from backend.geometry.topology import check_polygon_validity, check_finite_coordinates
from backend.geometry.crs import parse_and_validate_crs


class RuleGeo001NonEmpty(BaseValidationRule):
    rule_code = "GEO-001"
    rule_family = "GEOMETRY"
    description = "Geometry must not be empty or degenerate."

    def evaluate(self, run_id: UUID, parcel: ParentParcel, units: Sequence[SpatialUnit3D]) -> list[ValidationIssue]:
        issues = []
        # Check parcel
        is_empty = parcel.geometry is None or parcel.geometry.is_empty
        issues.append(
            ValidationIssue(
                run_id=run_id,
                rule_code=self.rule_code,
                severity=IssueSeverity.BLOCKER,
                object_type="PARENT_PARCEL",
                object_id=parcel.ulpin,
                passed=not is_empty,
                message="Parent parcel boundary is non-empty." if not is_empty else "Parent parcel geometry is empty.",
                measured_value={"is_empty": is_empty},
                threshold={"is_empty": False},
                suggested_action=None if not is_empty else "Provide a non-empty boundary polygon for the parcel."
            )
        )
        
        # Check child units
        for unit in units:
            unit_empty = unit.footprint_geom is None or unit.footprint_geom.is_empty
            issues.append(
                ValidationIssue(
                    run_id=run_id,
                    rule_code=self.rule_code,
                    severity=IssueSeverity.BLOCKER,
                    object_type="SPATIAL_UNIT",
                    object_id=unit.prototype_vuid,
                    passed=not unit_empty,
                    message="Spatial unit footprint is non-empty." if not unit_empty else f"Spatial unit {unit.prototype_vuid} has empty footprint.",
                    measured_value={"is_empty": unit_empty},
                    threshold={"is_empty": False},
                    suggested_action=None if not unit_empty else "Provide a valid non-empty building footprint."
                )
            )
        return issues


class RuleGeo002ValidPolygon(BaseValidationRule):
    rule_code = "GEO-002"
    rule_family = "GEOMETRY"
    description = "Polygon boundaries must be topologically valid according to OGC simple feature specifications."

    def evaluate(self, run_id: UUID, parcel: ParentParcel, units: Sequence[SpatialUnit3D]) -> list[ValidationIssue]:
        issues = []
        is_valid, reason = check_polygon_validity(parcel.geometry)
        issues.append(
            ValidationIssue(
                run_id=run_id,
                rule_code=self.rule_code,
                severity=IssueSeverity.BLOCKER,
                object_type="PARENT_PARCEL",
                object_id=parcel.ulpin,
                passed=is_valid,
                message="Parent parcel polygon topology is valid." if is_valid else f"Parent parcel topology invalid: {reason}",
                measured_value={"is_valid": is_valid, "reason": reason},
                threshold={"is_valid": True},
                suggested_action=None if is_valid else "Repair self-intersecting or bowtie rings in parcel boundary."
            )
        )
        
        for unit in units:
            u_valid, u_reason = check_polygon_validity(unit.footprint_geom)
            issues.append(
                ValidationIssue(
                    run_id=run_id,
                    rule_code=self.rule_code,
                    severity=IssueSeverity.BLOCKER,
                    object_type="SPATIAL_UNIT",
                    object_id=unit.prototype_vuid,
                    passed=u_valid,
                    message="Spatial unit polygon topology is valid." if u_valid else f"Unit {unit.prototype_vuid} topology invalid: {u_reason}",
                    measured_value={"is_valid": u_valid, "reason": u_reason},
                    threshold={"is_valid": True},
                    suggested_action=None if u_valid else "Correct invalid footprint geometry rings."
                )
            )
        return issues


class RuleGeo003ExplicitCRS(BaseValidationRule):
    rule_code = "GEO-003"
    rule_family = "GEOMETRY"
    description = "Spatial entities must declare an explicit projected coordinate system with linear units in metres."

    def evaluate(self, run_id: UUID, parcel: ParentParcel, units: Sequence[SpatialUnit3D]) -> list[ValidationIssue]:
        try:
            crs_obj = parse_and_validate_crs(parcel.crs)
            is_projected = crs_obj.is_projected
            passed = is_projected
            message = (
                f"CRS '{parcel.crs}' is an explicit projected coordinate reference system with linear units in metres."
                if passed else
                f"CRS '{parcel.crs}' is geographic (angular degrees). Metric spatial calculations require a projected CRS (e.g. EPSG:32643)."
            )
        except Exception as e:
            passed = False
            message = f"Invalid or unrecognized CRS '{parcel.crs}': {str(e)}"

        return [
            ValidationIssue(
                run_id=run_id,
                rule_code=self.rule_code,
                severity=IssueSeverity.BLOCKER,
                object_type="PARENT_PARCEL",
                object_id=parcel.ulpin,
                passed=passed,
                message=message,
                measured_value={"crs": parcel.crs},
                threshold={"projected_metric": True},
                suggested_action=None if passed else "Reproject parcel to a standard projected metric CRS (e.g. UTM Zone 43N / EPSG:32643)."
            )
        ]


class RuleGeo004FiniteCoordinates(BaseValidationRule):
    rule_code = "GEO-004"
    rule_family = "GEOMETRY"
    description = "All boundary coordinates must be finite real numbers (no NaN or Infinity values)."

    def evaluate(self, run_id: UUID, parcel: ParentParcel, units: Sequence[SpatialUnit3D]) -> list[ValidationIssue]:
        issues = []
        p_finite, p_reason = check_finite_coordinates(parcel.geometry)
        issues.append(
            ValidationIssue(
                run_id=run_id,
                rule_code=self.rule_code,
                severity=IssueSeverity.BLOCKER,
                object_type="PARENT_PARCEL",
                object_id=parcel.ulpin,
                passed=p_finite,
                message="All parcel coordinates are finite." if p_finite else f"Non-finite parcel coordinate: {p_reason}",
                measured_value={"finite": p_finite},
                threshold={"finite": True},
                suggested_action=None if p_finite else "Remove invalid floating-point values from coordinate array."
            )
        )
        
        for unit in units:
            u_finite, u_reason = check_finite_coordinates(unit.footprint_geom)
            issues.append(
                ValidationIssue(
                    run_id=run_id,
                    rule_code=self.rule_code,
                    severity=IssueSeverity.BLOCKER,
                    object_type="SPATIAL_UNIT",
                    object_id=unit.prototype_vuid,
                    passed=u_finite,
                    message="All unit coordinates are finite." if u_finite else f"Non-finite unit coordinate: {u_reason}",
                    measured_value={"finite": u_finite},
                    threshold={"finite": True},
                    suggested_action=None if u_finite else "Sanitize coordinate stream."
                )
            )
        return issues
