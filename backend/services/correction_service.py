from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from shapely.geometry import shape, Polygon
from backend.domain.revision import SpatialUnitRevision
from backend.domain.enums import UnitStatus, SemanticType, AuditAction, GateType
from backend.domain.validation_run import ValidationRun
from backend.repository.revision_repository import RevisionRepository
from backend.repository.unit_repository import SpatialUnitRepository
from backend.repository.parcel_repository import ParcelRepository
from backend.repository.validation_run_repository import ValidationRunRepository
from backend.repository.issue_repository import IssueRepository
from backend.services.provenance_service import ProvenanceService
from backend.services.audit_service import AuditService
from backend.geometry.extrusion import compute_volumetric_extrusion
from backend.geometry.topology import check_finite_coordinates, check_polygon_validity
from backend.vuid.generator import generate_prototype_vuid
from backend.validation.runner import ValidationRunner
from backend.schemas.governance_contracts import CorrectionSubmitRequest, CorrectionResponse
from backend.exceptions import RevisionNotFoundError, InvalidGeometryError


class CorrectionService:
    def __init__(self, db: Session):
        self.db = db
        self.revision_repo = RevisionRepository(db)
        self.unit_repo = SpatialUnitRepository(db)
        self.parcel_repo = ParcelRepository(db)
        self.val_run_repo = ValidationRunRepository(db)
        self.issue_repo = IssueRepository(db)
        self.prov_service = ProvenanceService(db)
        self.audit_service = AuditService(db)
        self.runner = ValidationRunner()

    def apply_correction(self, revision_id: UUID, request: CorrectionSubmitRequest) -> CorrectionResponse:
        predecessor = self.revision_repo.find_by_id(revision_id)
        if not predecessor:
            raise RevisionNotFoundError(str(revision_id))

        if request.role and request.role.upper() == "VIEWER":
            raise ApprovalBlockedError(
                f"Unauthorized role '{request.role}'. Applying corrections requires REVIEWER or ADMIN role.",
                details={"role": request.role}
            )

        if request.actor_context == "AI_AUTONOMOUS" or "AI" in request.reviewer_id.upper():
            raise ApprovalBlockedError(
                "AI IS NOT THE AUTHORITY: Autonomous corrections by AI agents are strictly prohibited.",
                details={"actor_context": request.actor_context, "reviewer_id": request.reviewer_id}
            )

        # Determine corrected values, falling back to predecessor values
        z_min = float(request.z_min) if request.z_min is not None else predecessor.z_min
        z_max = float(request.z_max) if request.z_max is not None else predecessor.z_max
        if z_min >= z_max:
            raise ValueError(f"Corrected z_min ({z_min}) must be strictly less than z_max ({z_max}).")
        if z_min < -100.0 or z_max > 5000.0:
            raise ValueError(f"Elevation range ({z_min}m to {z_max}m) exceeds realistic terrestrial boundaries.")

        if request.footprint is not None:
            footprint_poly = shape(request.footprint)
            if not isinstance(footprint_poly, Polygon):
                raise InvalidGeometryError("Corrected footprint must be a valid Polygon.")
            finite_ok, finite_err = check_finite_coordinates(footprint_poly)
            if not finite_ok:
                raise InvalidGeometryError(f"Corrected footprint coordinate error: {finite_err}")
            valid_ok, valid_err = check_polygon_validity(footprint_poly)
            if not valid_ok:
                raise InvalidGeometryError(f"Corrected footprint topology error: {valid_err}")
        else:
            footprint_poly = predecessor.footprint_geom

        semantic = SemanticType(request.semantic_type) if request.semantic_type else predecessor.semantic_type

        # 1. Recompute volumetric metrics
        metrics = compute_volumetric_extrusion(
            polygon=footprint_poly,
            z_min=z_min,
            z_max=z_max
        )

        # 2. Recalculate deterministic Prototype VUID for the new geometry/bounds
        vuid_res = generate_prototype_vuid(
            parent_ulpin=predecessor.parent_ulpin,
            unit_class="BLDG",
            level_code=predecessor.level_code,
            footprint_geom=footprint_poly,
            z_min=z_min,
            z_max=z_max
        )

        # 3. Create NEW revision (predecessor is left completely untouched and immutable)
        new_revision = SpatialUnitRevision(
            unit_id=predecessor.unit_id,
            revision_number=predecessor.revision_number + 1,
            prototype_vuid=vuid_res.prototype_vuid,
            parent_ulpin=predecessor.parent_ulpin,
            semantic_type=semantic,
            level_code=predecessor.level_code,
            z_min=z_min,
            z_max=z_max,
            footprint_area_sqm=metrics.footprint_area_sqm,
            volume_cbm=metrics.volume_cbm,
            centroid_x=metrics.centroid_x,
            centroid_y=metrics.centroid_y,
            centroid_z=metrics.centroid_z,
            footprint_geom=footprint_poly,
            polyhedron_wkt=metrics.polyhedron_wkt,
            vuid_full_hash=vuid_res.vuid_full_hash,
            predecessor_revision_id=predecessor.id,
            status=UnitStatus.CORRECTED,
            created_by=request.reviewer_id
        )
        saved_new_rev = self.revision_repo.save(new_revision)

        # 4. Update the active revision pointer on the unit
        self.unit_repo.update_from_revision(
            unit_id=predecessor.unit_id,
            revision_id=saved_new_rev.id,
            vuid=saved_new_rev.prototype_vuid,
            vuid_hash=saved_new_rev.vuid_full_hash,
            footprint=saved_new_rev.footprint_geom,
            z_min=saved_new_rev.z_min,
            z_max=saved_new_rev.z_max,
            status=UnitStatus.CORRECTED,
            area_sqm=saved_new_rev.footprint_area_sqm,
            volume_cbm=saved_new_rev.volume_cbm,
            centroid=(saved_new_rev.centroid_x, saved_new_rev.centroid_y, saved_new_rev.centroid_z)
        )

        # 5. Attach provenance record linking predecessor VUID
        prev_prov = self.prov_service.get_provenance_for_revision(predecessor.id)
        evidence_ids = [e["id"] for e in prev_prov.evidence_sources] if prev_prov else []
        self.prov_service.create_provenance(
            revision=saved_new_rev,
            evidence_ids=evidence_ids,
            generation_method="HUMAN_REVIEW_CORRECTION",
            generation_method_version="1.0.0",
            vuid_algorithm_version=vuid_res.vuid_algorithm_version,
            predecessor_vuid=predecessor.prototype_vuid
        )

        # 6. Audit event for correction submission and revision creation
        self.audit_service.log_event(
            action=AuditAction.CORRECTION_SUBMITTED,
            entity_type="SPATIAL_UNIT_REVISION",
            entity_id=str(predecessor.id),
            actor_id=request.reviewer_id,
            authorization_mode=request.actor_context,
            revision_id=predecessor.id,
            previous_state=predecessor.status.value,
            new_state=UnitStatus.CORRECTED.value,
            reason=f"Correction applied by officer. Reason: {request.reason}",
            metadata={"new_revision_id": str(saved_new_rev.id), "new_vuid": saved_new_rev.prototype_vuid}
        )
        self.audit_service.log_event(
            action=AuditAction.REVISION_CREATED,
            entity_type="SPATIAL_UNIT_REVISION",
            entity_id=str(saved_new_rev.id),
            actor_id=request.reviewer_id,
            authorization_mode=request.actor_context,
            revision_id=saved_new_rev.id,
            new_state=UnitStatus.CORRECTED.value,
            reason=f"Revision {saved_new_rev.revision_number} generated from predecessor {predecessor.prototype_vuid}."
        )

        # 7. Revalidation: run validation on updated units for this parcel
        parcel = self.parcel_repo.find_by_ulpin(predecessor.parent_ulpin)
        all_units = self.unit_repo.find_by_parent_ulpin(predecessor.parent_ulpin)
        now = datetime.now(timezone.utc)
        from uuid import uuid4
        new_run_id = uuid4()

        issues = self.runner.execute(parcel=parcel, units=all_units, run_id=new_run_id)

        passed_rules = sum(1 for i in issues if i.passed)
        blocker_count = sum(1 for i in issues if not i.passed and i.severity.value == "BLOCKER")
        error_count = sum(1 for i in issues if not i.passed and i.severity.value == "ERROR")
        warning_count = sum(1 for i in issues if not i.passed and i.severity.value == "WARN")
        can_approve = (blocker_count == 0)

        val_run = ValidationRun(
            id=new_run_id,
            parent_ulpin=predecessor.parent_ulpin,
            unit_id=predecessor.unit_id,
            revision_id=saved_new_rev.id,
            gate=GateType.GATE_A,
            validator_version="1.0.0",
            rules_evaluated=len(issues),
            passed_rules=passed_rules,
            failed_rules=len(issues) - passed_rules,
            blocker_count=blocker_count,
            error_count=error_count,
            warning_count=warning_count,
            can_approve=can_approve,
            created_at=now
        )
        self.val_run_repo.save(val_run)
        self.issue_repo.save_issues(issues)

        # Update revision status to REVALIDATED
        final_status = UnitStatus.REVALIDATED if can_approve else UnitStatus.CORRECTED
        self.revision_repo.update_status(saved_new_rev.id, final_status)
        self.unit_repo.set_active_revision(predecessor.unit_id, saved_new_rev.id)

        # Audit revalidation
        self.audit_service.log_event(
            action=AuditAction.REVALIDATION_EXECUTED,
            entity_type="SPATIAL_UNIT_REVISION",
            entity_id=str(saved_new_rev.id),
            actor_id=request.reviewer_id,
            authorization_mode=request.actor_context,
            revision_id=saved_new_rev.id,
            new_state=final_status.value,
            correlation_id=str(new_run_id),
            reason=f"Revalidation executed after correction: {blocker_count} blockers.",
            metadata={"run_id": str(new_run_id), "blocker_count": blocker_count, "can_approve": can_approve}
        )

        return CorrectionResponse(
            new_revision_id=str(saved_new_rev.id),
            predecessor_revision_id=str(predecessor.id),
            prototype_vuid=saved_new_rev.prototype_vuid,
            vuid_full_hash=saved_new_rev.vuid_full_hash,
            validation_run_id=str(new_run_id),
            blocker_count=blocker_count,
            can_approve=can_approve,
            status=final_status.value,
            created_at=saved_new_rev.created_at
        )
