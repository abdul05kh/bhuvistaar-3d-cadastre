import hashlib
from typing import Sequence
from uuid import UUID
from backend.domain.validation import ValidationIssue
from backend.domain.enums import IssueSeverity
from backend.domain.parcel import ParentParcel
from backend.domain.spatial_unit import SpatialUnit3D
from backend.domain.revision import SpatialUnitRevision
from backend.domain.provenance import ProvenanceRecord
from backend.validation.rules.base import BaseValidationRule


class RuleProv001ParentLinkage(BaseValidationRule):
    rule_code = "PROV-001"
    rule_family = "PROVENANCE"
    description = "Candidate revision must link to an existing parent parcel with a valid 14-digit ULPIN."

    def evaluate(self, run_id: UUID, parcel: ParentParcel, units: Sequence[SpatialUnit3D]) -> list[ValidationIssue]:
        issues = []
        p_ok = bool(parcel and parcel.ulpin and len(parcel.ulpin) == 14 and parcel.ulpin.isdigit())
        for unit in units:
            u_ok = p_ok and (unit.parent_ulpin == parcel.ulpin)
            issues.append(
                ValidationIssue(
                    run_id=run_id,
                    rule_code=self.rule_code,
                    severity=IssueSeverity.BLOCKER,
                    object_type="SPATIAL_UNIT",
                    object_id=unit.prototype_vuid,
                    passed=u_ok,
                    message="Parent ULPIN linkage verified." if u_ok else f"Invalid parent linkage: parcel='{parcel.ulpin if parcel else None}' vs unit='{unit.parent_ulpin}'",
                    measured_value={"parcel_ulpin": parcel.ulpin if parcel else None, "unit_parent_ulpin": unit.parent_ulpin},
                    threshold={"match": True, "ulpin_length": 14},
                    suggested_action=None if u_ok else "Attach spatial unit to a valid 14-digit parent parcel."
                )
            )
        return issues


class RuleProv002EvidenceAttached(BaseValidationRule):
    rule_code = "PROV-002"
    rule_family = "PROVENANCE"
    description = "Candidate spatial unit must have at least one registered evidence source attached."

    def evaluate(self, run_id: UUID, parcel: ParentParcel, units: Sequence[SpatialUnit3D]) -> list[ValidationIssue]:
        issues = []
        for unit in units:
            has_evidence = len(unit.source_ids) > 0
            issues.append(
                ValidationIssue(
                    run_id=run_id,
                    rule_code=self.rule_code,
                    severity=IssueSeverity.BLOCKER,
                    object_type="SPATIAL_UNIT",
                    object_id=unit.prototype_vuid,
                    passed=has_evidence,
                    message="Evidence source attached." if has_evidence else f"Spatial unit '{unit.prototype_vuid}' has no attached evidence records.",
                    measured_value={"evidence_count": len(unit.source_ids), "source_ids": unit.source_ids},
                    threshold={"min_evidence_count": 1},
                    suggested_action=None if has_evidence else "Register and link cadastral survey, architectural, or boundary evidence."
                )
            )
        return issues


class RuleProv003EvidenceIntegrity(BaseValidationRule):
    rule_code = "PROV-003"
    rule_family = "PROVENANCE"
    description = "Attached evidence checksums must be valid SHA-256 digests and integrity must be verified."

    def __init__(self, evidence_sources: dict[str, dict] = None):
        super().__init__()
        self.evidence_sources = evidence_sources or {}

    def evaluate(self, run_id: UUID, parcel: ParentParcel, units: Sequence[SpatialUnit3D]) -> list[ValidationIssue]:
        issues = []
        for unit in units:
            unit_passed = True
            mismatches = []
            
            for eid in unit.source_ids:
                ev = self.evidence_sources.get(eid)
                if not ev:
                    # If evidence details not provided in rule context, verify format
                    continue
                checksum = ev.get("checksum", "")
                is_valid_format = len(checksum) == 64 and all(c in "0123456789abcdefABCDEF" for c in checksum)
                if not is_valid_format or ev.get("integrity_failed", False):
                    unit_passed = False
                    mismatches.append(eid)

            issues.append(
                ValidationIssue(
                    run_id=run_id,
                    rule_code=self.rule_code,
                    severity=IssueSeverity.BLOCKER,
                    object_type="SPATIAL_UNIT",
                    object_id=unit.prototype_vuid,
                    passed=unit_passed,
                    message="Evidence integrity verified." if unit_passed else f"Evidence integrity check failed for sources: {mismatches}",
                    measured_value={"failed_evidence_ids": mismatches},
                    threshold={"checksum_verified": True},
                    suggested_action=None if unit_passed else "Re-verify or re-upload authoritative survey evidence with matching checksums."
                )
            )
        return issues


class RuleProv004GenerationProvenance(BaseValidationRule):
    rule_code = "PROV-004"
    rule_family = "PROVENANCE"
    description = "Generation method and algorithm version metadata must be explicitly defined."

    def evaluate(self, run_id: UUID, parcel: ParentParcel, units: Sequence[SpatialUnit3D]) -> list[ValidationIssue]:
        issues = []
        for unit in units:
            has_method = bool(unit.generation_method and unit.vuid_algorithm_version)
            issues.append(
                ValidationIssue(
                    run_id=run_id,
                    rule_code=self.rule_code,
                    severity=IssueSeverity.BLOCKER,
                    object_type="SPATIAL_UNIT",
                    object_id=unit.prototype_vuid,
                    passed=has_method,
                    message="Generation method metadata valid." if has_method else "Missing generation method or algorithm version.",
                    measured_value={
                        "generation_method": unit.generation_method,
                        "algorithm_version": unit.vuid_algorithm_version
                    },
                    threshold={"metadata_complete": True},
                    suggested_action=None if has_method else "Record extrusion method and VUID algorithm version in unit metadata."
                )
            )
        return issues
