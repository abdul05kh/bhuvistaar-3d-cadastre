import json
import hashlib
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from shapely.geometry import mapping
from backend.domain.export import ExportRecord
from backend.domain.enums import AuditAction
from backend.repository.revision_repository import RevisionRepository
from backend.repository.unit_repository import SpatialUnitRepository
from backend.repository.parcel_repository import ParcelRepository
from backend.repository.provenance_repository import ProvenanceRepository
from backend.repository.validation_run_repository import ValidationRunRepository
from backend.repository.issue_repository import IssueRepository
from backend.repository.review_repository import ReviewRepository
from backend.repository.approval_repository import ApprovalRepository
from backend.repository.audit_repository import AuditRepository
from backend.repository.export_repository import ExportRepository
from backend.services.audit_service import AuditService
from backend.schemas.governance_contracts import StructuredExportResponse
from backend.exceptions import RevisionNotFoundError


class ExportService:
    def __init__(self, db: Session):
        self.db = db
        self.revision_repo = RevisionRepository(db)
        self.unit_repo = SpatialUnitRepository(db)
        self.parcel_repo = ParcelRepository(db)
        self.prov_repo = ProvenanceRepository(db)
        self.val_run_repo = ValidationRunRepository(db)
        self.issue_repo = IssueRepository(db)
        self.review_repo = ReviewRepository(db)
        self.approval_repo = ApprovalRepository(db)
        self.audit_repo = AuditRepository(db)
        self.export_repo = ExportRepository(db)
        self.audit_service = AuditService(db)

    def generate_export_for_revision(self, revision_id: UUID, exported_by: str = "OFFICER-001") -> StructuredExportResponse:
        revision = self.revision_repo.find_by_id(revision_id)
        if not revision:
            raise RevisionNotFoundError(str(revision_id))

        parcel = self.parcel_repo.find_by_ulpin(revision.parent_ulpin)
        prov = self.prov_repo.find_by_revision_id(revision_id)
        val_run = self.val_run_repo.find_latest_for_revision(revision_id)
        if not val_run:
            val_run = self.val_run_repo.find_latest_for_parcel(revision.parent_ulpin)
        review = self.review_repo.find_latest_for_revision(revision_id)
        approval = self.approval_repo.find_latest_for_revision(revision_id)
        audit_events = self.audit_repo.find_by_revision(revision_id)

        now = datetime.now(timezone.utc)

        # 1. Export Metadata
        export_metadata = {
            "schema_version": "1.0.0",
            "exported_at": now.isoformat(),
            "exported_by": exported_by,
            "authorization_mode": "SIMULATED_PROTOTYPE",
            "disclaimer": (
                "PROTOTYPE EXPORT ONLY. This document contains machine-assisted candidate 3D cadastral units. "
                "Identifiers (VUID) are prototype data-layer keys and are NOT official 3D ULPINs. "
                "This does NOT represent legal title adjudication or official government certification."
            )
        }

        # 2. Parcel
        parcel_data = {
            "ulpin": parcel.ulpin if parcel else revision.parent_ulpin,
            "crs": parcel.crs if parcel else "EPSG:32643",
            "storage_srid": parcel.storage_srid if parcel else 32643,
            "area_sqm": float(parcel.area_sqm) if parcel else None,
            "geometry": mapping(parcel.geometry) if parcel else None
        }

        # 3. Spatial Unit & Revision
        unit_data = {
            "unit_id": str(revision.unit_id),
            "level_code": revision.level_code,
            "semantic_type": revision.semantic_type.value
        }

        revision_data = {
            "revision_id": str(revision.id),
            "revision_number": revision.revision_number,
            "predecessor_revision_id": str(revision.predecessor_revision_id) if revision.predecessor_revision_id else None,
            "status": revision.status.value,
            "created_by": revision.created_by,
            "created_at": revision.created_at.isoformat()
        }

        # 4. Prototype VUID
        vuid_data = {
            "prototype_vuid": revision.prototype_vuid,
            "vuid_full_hash": revision.vuid_full_hash,
            "vuid_display_token": revision.prototype_vuid.split("-")[-1],
            "vuid_algorithm_version": "v1",
            "prototype_disclaimer": "PROTOTYPE IDENTIFIER - NOT AN OFFICIAL 3D ULPIN"
        }

        # 5. Geometry & Elevation
        geometry_data = {
            "footprint": mapping(revision.footprint_geom),
            "polyhedron_wkt": revision.polyhedron_wkt
        }

        elevation_data = {
            "z_min": revision.z_min,
            "z_max": revision.z_max,
            "height_m": revision.height_m,
            "footprint_area_sqm": revision.footprint_area_sqm,
            "volume_cbm": revision.volume_cbm,
            "centroid": {
                "x": revision.centroid_x,
                "y": revision.centroid_y,
                "z": revision.centroid_z
            }
        }

        # 6. Evidence Sources (sorted deterministically by ID)
        evidence_list = sorted(
            prov.evidence_sources if prov else [],
            key=lambda e: e.get("id", "")
        )

        # 7. Provenance Record
        provenance_data = {
            "id": str(prov.id) if prov else None,
            "generation_method": prov.generation_method if prov else "PRISMATIC_EXTRUSION",
            "generation_method_version": prov.generation_method_version if prov else "1.0.0",
            "vuid_algorithm_version": prov.vuid_algorithm_version if prov else "v1",
            "predecessor_vuid": prov.predecessor_vuid if prov else None,
            "is_verified": prov.is_verified if prov else False,
            "verified_at": prov.verified_at.isoformat() if (prov and prov.verified_at) else None
        }

        # 8. Validation Run Details
        val_data = {
            "run_id": str(val_run.id) if val_run else None,
            "gate": val_run.gate.value if val_run else None,
            "validator_version": val_run.validator_version if val_run else "1.0.0",
            "rules_evaluated": val_run.rules_evaluated if val_run else 0,
            "passed_rules": val_run.passed_rules if val_run else 0,
            "failed_rules": val_run.failed_rules if val_run else 0,
            "blocker_count": val_run.blocker_count if val_run else 0,
            "error_count": val_run.error_count if val_run else 0,
            "warning_count": val_run.warning_count if val_run else 0,
            "can_approve": val_run.can_approve if val_run else False,
            "created_at": val_run.created_at.isoformat() if val_run else None
        }

        # 9. Review Decision
        review_data = {
            "id": str(review.id),
            "reviewer_id": review.reviewer_id,
            "decision": review.decision.value,
            "reason": review.reason,
            "actor_context": review.actor_context,
            "created_at": review.created_at.isoformat()
        } if review else None

        # 10. Approval Decision
        approval_data = {
            "id": str(approval.id),
            "approver_id": approval.approver_id,
            "status": approval.status.value,
            "reason": approval.reason,
            "actor_context": approval.actor_context,
            "created_at": approval.created_at.isoformat()
        } if approval else None

        # 11. Audit Summary (sorted deterministically by timestamp)
        audit_list = sorted(
            [
                {
                    "id": str(a.id),
                    "action": a.action.value,
                    "actor_id": a.actor_id,
                    "timestamp": a.timestamp.isoformat(),
                    "reason": a.reason,
                    "previous_state": a.previous_state,
                    "new_state": a.new_state
                }
                for a in audit_events
            ],
            key=lambda a: a["timestamp"]
        )
        audit_summary = {
            "total_events": len(audit_list),
            "events": audit_list
        }

        payload = {
            "export_metadata": export_metadata,
            "parcel": parcel_data,
            "parent_ulpin": revision.parent_ulpin,
            "spatial_unit": unit_data,
            "spatial_unit_revision": revision_data,
            "vuid": vuid_data,
            "geometry": geometry_data,
            "elevation": elevation_data,
            "evidence": evidence_list,
            "provenance": provenance_data,
            "validation": val_data,
            "review": review_data,
            "approval": approval_data,
            "audit_summary": audit_summary
        }

        # Compute deterministic checksum of the payload
        canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        checksum = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

        # Save ExportRecord
        record = ExportRecord(
            revision_id=revision.id,
            checksum=checksum,
            exported_by=exported_by,
            content=payload
        )
        self.export_repo.save(record)

        # Audit event
        self.audit_service.log_event(
            action=AuditAction.EXPORT_GENERATED,
            entity_type="SPATIAL_UNIT_REVISION",
            entity_id=str(revision.id),
            actor_id=exported_by,
            revision_id=revision.id,
            reason=f"Structured JSON export generated for revision {revision.revision_number} (checksum: {checksum[:8]}).",
            metadata={"checksum": checksum, "vuid": revision.prototype_vuid}
        )

        return StructuredExportResponse(**payload)
