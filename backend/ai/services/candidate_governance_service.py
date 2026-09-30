"""Candidate Governance Service (Slice 3).

Coordinates the human-in-the-loop transition from untrusted AI candidate proposal
into governed spatial unit revision, deterministic validation, and end-to-end lineage tracing.

CRITICAL PRINCIPLES:
1. Candidate acceptance generates deterministic Prototype VUID via the authoritative algorithm.
2. Candidate rejection is permanently preserved with justification in audit logs.
3. End-to-end data lineage is fully traversable across all lifecycle stages.
"""
import uuid
from datetime import datetime, timezone
from typing import Any
from sqlalchemy.orm import Session
from shapely.geometry import shape

from backend.domain.enums import (
    AuditAction,
    SemanticType,
    ConfidenceLevel,
    UnitStatus,
    GateType
)
from backend.domain.spatial_unit import SpatialUnit3D
from backend.domain.revision import SpatialUnitRevision
from backend.exceptions import (
    AICandidateNotFoundError,
    ParcelNotFoundError
)
from backend.db.models import (
    AICandidateModel,
    ParentParcelModel,
    SpatialUnitModel,
    SpatialUnitRevisionModel,
    ProvenanceRecordModel,
    EvidenceSourceModel,
    EvidenceObservationModel,
    ValidationRunModel,
    ValidationIssueModel,
    ReviewDecisionModel,
    ApprovalDecisionModel,
    ExportRecordModel,
    AuditEventModel
)
from backend.geometry.extrusion import compute_volumetric_extrusion
from backend.vuid.generator import generate_prototype_vuid
from backend.repository.unit_repository import SpatialUnitRepository
from backend.repository.revision_repository import RevisionRepository
from backend.repository.evidence_repository import EvidenceRepository
from backend.services.provenance_service import ProvenanceService
from backend.services.validation_service import ValidationService
from backend.services.audit_service import AuditService
from backend.ai.schemas.lineage import TraceOriginNode, TraceOriginResponse


class CandidateGovernanceService:
    def __init__(self, db: Session):
        self.db = db
        self.unit_repo = SpatialUnitRepository(db)
        self.revision_repo = RevisionRepository(db)
        self.evidence_repo = EvidenceRepository(db)
        self.prov_service = ProvenanceService(db)
        self.validation_service = ValidationService(db)
        self.audit_service = AuditService(db)

    def accept_candidate(
        self,
        candidate_id: str,
        reviewer_id: str = "surveyor_officer_01",
        justification: str = "Candidate boundary and elevation verified against architectural drawings"
    ) -> tuple[SpatialUnit3D, SpatialUnitRevision, dict[str, Any]]:
        """Transitions an AI proposal into an authoritative governed spatial unit revision."""
        cand = self.db.query(AICandidateModel).filter(AICandidateModel.candidate_id == candidate_id).first()
        if not cand:
            raise AICandidateNotFoundError(candidate_id)

        if cand.status == "ACCEPTED":
            raise ValueError(f"Candidate '{candidate_id}' has already been accepted as a governed spatial unit.")

        parcel = self.db.query(ParentParcelModel).filter(ParentParcelModel.ulpin == cand.parent_ulpin).first()
        if not parcel:
            raise ParcelNotFoundError(cand.parent_ulpin)

        footprint_poly = shape(cand.footprint_geojson)
        z_min = float(cand.z_min)
        z_max = float(cand.z_max)

        # 1. Compute volumetric metrics
        metrics = compute_volumetric_extrusion(
            polygon=footprint_poly,
            z_min=z_min,
            z_max=z_max
        )

        # 2. Authoritative deterministic Prototype VUID generation
        vuid_res = generate_prototype_vuid(
            parent_ulpin=cand.parent_ulpin,
            unit_class="BLDG",
            level_code=cand.level_code,
            footprint_geom=footprint_poly,
            z_min=z_min,
            z_max=z_max
        )

        # 3. Create SpatialUnit3D
        unit_domain = SpatialUnit3D(
            parent_parcel_id=parcel.id,
            parent_ulpin=cand.parent_ulpin,
            prototype_vuid=vuid_res.prototype_vuid,
            semantic_type=SemanticType(cand.semantic_type),
            level_code=cand.level_code,
            z_min=z_min,
            z_max=z_max,
            footprint_area_sqm=metrics.footprint_area_sqm,
            volume_cbm=metrics.volume_cbm,
            centroid_x=metrics.centroid_x,
            centroid_y=metrics.centroid_y,
            centroid_z=metrics.centroid_z,
            footprint_geom=footprint_poly,
            polyhedron_wkt=metrics.polyhedron_wkt,
            confidence=ConfidenceLevel.VERIFIED,
            generation_method="AI_ASSISTED_CANDIDATE_GENERATION",
            vuid_algorithm_version=vuid_res.vuid_algorithm_version,
            vuid_full_hash=vuid_res.vuid_full_hash,
            source_ids=cand.source_evidence_ids or [],
            status=UnitStatus.GENERATED
        )

        saved_unit = self.unit_repo.save(unit_domain)

        # 4. Create Revision 1
        revision_1 = SpatialUnitRevision(
            unit_id=saved_unit.id,
            revision_number=1,
            prototype_vuid=saved_unit.prototype_vuid,
            parent_ulpin=cand.parent_ulpin,
            semantic_type=saved_unit.semantic_type,
            level_code=saved_unit.level_code,
            z_min=saved_unit.z_min,
            z_max=saved_unit.z_max,
            footprint_area_sqm=saved_unit.footprint_area_sqm,
            volume_cbm=saved_unit.volume_cbm,
            centroid_x=saved_unit.centroid_x,
            centroid_y=saved_unit.centroid_y,
            centroid_z=saved_unit.centroid_z,
            footprint_geom=saved_unit.footprint_geom,
            polyhedron_wkt=saved_unit.polyhedron_wkt,
            vuid_full_hash=saved_unit.vuid_full_hash,
            status=UnitStatus.GENERATED,
            created_by=reviewer_id
        )
        saved_rev = self.revision_repo.save(revision_1)
        self.unit_repo.set_active_revision(saved_unit.id, saved_rev.id)

        # 5. Create Provenance Record
        self.prov_service.ev_repo = self.evidence_repo
        self.prov_service.create_provenance(
            revision=saved_rev,
            evidence_ids=cand.source_evidence_ids or [],
            generation_method="AI_ASSISTED_CANDIDATE_GENERATION",
            generation_method_version=f"{cand.model_name}:{cand.model_version}",
            vuid_algorithm_version=vuid_res.vuid_algorithm_version
        )

        # 6. Execute Gate A & Gate B deterministic validation
        val_summary = self.validation_service.run_validation(
            ulpin=cand.parent_ulpin
        )

        # 7. Update Candidate Model with governance linkages
        cand.status = "ACCEPTED"
        cand.governed_unit_id = saved_unit.id
        cand.governed_revision_id = saved_rev.id
        cand.reviewed_by = reviewer_id
        cand.reviewed_at = datetime.now(timezone.utc)
        self.db.commit()

        # 8. Append-only Audit Log
        correlation_id = f"ai-accept-{uuid.uuid4().hex[:8]}"
        self.audit_service.record_event(
            actor_id=reviewer_id,
            action=AuditAction.AI_REVIEWED,
            entity_type="AI_CANDIDATE",
            entity_id=cand.candidate_id,
            revision_id=saved_rev.id,
            previous_state="AI_CANDIDATE",
            new_state="ACCEPTED",
            reason=justification,
            correlation_id=correlation_id,
            metadata={
                "decision": "ACCEPT",
                "prototype_vuid": saved_unit.prototype_vuid,
                "confidence": float(cand.confidence)
            }
        )

        self.audit_service.record_event(
            actor_id=reviewer_id,
            action=AuditAction.CANDIDATE_CREATED,
            entity_type="SPATIAL_UNIT",
            entity_id=saved_unit.prototype_vuid,
            revision_id=saved_rev.id,
            previous_state=None,
            new_state=UnitStatus.GENERATED.value,
            reason=f"Accepted AI candidate {cand.candidate_id} into governed spatial unit",
            correlation_id=correlation_id,
            metadata={"origin_candidate_id": cand.candidate_id}
        )

        return saved_unit, saved_rev, val_summary.model_dump()

    def reject_candidate(
        self,
        candidate_id: str,
        reviewer_id: str = "surveyor_officer_01",
        justification: str = "Evidence does not support independent 3D unit"
    ) -> AICandidateModel:
        """Records reviewer rejection while permanently preserving candidate and rationale."""
        cand = self.db.query(AICandidateModel).filter(AICandidateModel.candidate_id == candidate_id).first()
        if not cand:
            raise AICandidateNotFoundError(candidate_id)

        cand.status = "REJECTED"
        cand.rejection_reason = justification
        cand.reviewed_by = reviewer_id
        cand.reviewed_at = datetime.now(timezone.utc)
        self.db.commit()

        # Audit: AI_CANDIDATE_REJECTED
        self.audit_service.record_event(
            actor_id=reviewer_id,
            action=AuditAction.AI_CANDIDATE_REJECTED,
            entity_type="AI_CANDIDATE",
            entity_id=cand.candidate_id,
            previous_state="AI_CANDIDATE",
            new_state="REJECTED",
            reason=justification,
            correlation_id=f"ai-reject-{uuid.uuid4().hex[:8]}",
            metadata={
                "level_code": cand.level_code,
                "confidence": float(cand.confidence)
            }
        )

        return cand

    def trace_origin(self, identifier: str) -> TraceOriginResponse:
        """Traverses the complete provenance and governance lifecycle for a candidate or spatial unit."""
        nodes: list[TraceOriginNode] = []
        step_idx = 1
        is_approved = False
        prov_hash = None
        ulpin = "12345678901234"

        # Check if identifier is an AI candidate
        cand = self.db.query(AICandidateModel).filter(AICandidateModel.candidate_id == identifier).first()
        unit = None
        rev = None

        if cand:
            ulpin = cand.parent_ulpin
            # Stage 1: Evidence Sources
            ev_sources = self.db.query(EvidenceSourceModel).filter(
                EvidenceSourceModel.parent_ulpin == cand.parent_ulpin
            ).all()
            for ev in ev_sources:
                if not cand.source_evidence_ids or ev.id in cand.source_evidence_ids:
                    nodes.append(
                        TraceOriginNode(
                            step=step_idx,
                            stage="EVIDENCE",
                            title=f"Source Evidence: {ev.evidence_type}",
                            identifier=ev.id,
                            status="VERIFIED" if ev.checksum else "REGISTERED",
                            timestamp=ev.created_at.isoformat() if ev.created_at else None,
                            actor=ev.provider,
                            details={
                                "source_reference": ev.source_reference,
                                "checksum": ev.checksum,
                                "algorithm": ev.checksum_algorithm
                            }
                        )
                    )
                    step_idx += 1

            # Stage 2: AI Observations
            obs_list = self.db.query(EvidenceObservationModel).filter(
                EvidenceObservationModel.parent_ulpin == cand.parent_ulpin,
                EvidenceObservationModel.semantic_level == cand.level_code
            ).all()
            for o in obs_list:
                nodes.append(
                    TraceOriginNode(
                        step=step_idx,
                        stage="AI_OBSERVATION",
                        title=f"Observation: {o.observation_type}",
                        identifier=str(o.id),
                        status="EXTRACTED",
                        timestamp=o.created_at.isoformat() if o.created_at else None,
                        actor=f"{o.model_name}:{o.model_version}",
                        details={
                            "level": o.semantic_level,
                            "elevation_range": [float(o.z_min) if o.z_min else 0, float(o.z_max) if o.z_max else 0],
                            "confidence": float(o.confidence),
                            "extraction_method": o.extraction_method
                        }
                    )
                )
                step_idx += 1

            # Stage 3: Inference Run / Candidate Proposal
            nodes.append(
                TraceOriginNode(
                    step=step_idx,
                    stage="AI_CANDIDATE",
                    title=f"Proposal: Level {cand.level_code}",
                    identifier=cand.candidate_id,
                    status=cand.status,
                    timestamp=cand.created_at.isoformat() if cand.created_at else None,
                    actor=f"{cand.model_name}:{cand.model_version}",
                    details={
                        "confidence": float(cand.confidence),
                        "confidence_band": cand.confidence_band,
                        "elevation_stratum": [float(cand.z_min), float(cand.z_max)],
                        "volume_cbm": float(cand.volume_cbm),
                        "reasons": cand.reason_codes
                    }
                )
            )
            step_idx += 1

            if cand.governed_unit_id:
                unit = self.db.query(SpatialUnitModel).filter(SpatialUnitModel.id == cand.governed_unit_id).first()
                if cand.governed_revision_id:
                    rev = self.db.query(SpatialUnitRevisionModel).filter(SpatialUnitRevisionModel.id == cand.governed_revision_id).first()

        else:
            # Identifier might be a Prototype VUID or Unit ID
            unit = self.db.query(SpatialUnitModel).filter(
                (SpatialUnitModel.prototype_vuid == identifier) | (SpatialUnitModel.id.cast(str) == identifier)
            ).first()
            if unit:
                ulpin = unit.parent_ulpin
                prov_hash = unit.vuid_full_hash
                if unit.active_revision_id:
                    rev = self.db.query(SpatialUnitRevisionModel).filter(SpatialUnitRevisionModel.id == unit.active_revision_id).first()

        # If we have a governed unit / revision
        if unit and rev:
            prov_hash = rev.vuid_full_hash

            # Stage 4: Validation Run
            val_run = self.db.query(ValidationRunModel).filter(ValidationRunModel.revision_id == rev.id).order_by(ValidationRunModel.created_at.desc()).first()
            if val_run:
                nodes.append(
                    TraceOriginNode(
                        step=step_idx,
                        stage="DETERMINISTIC_VALIDATION",
                        title=f"Validation {val_run.gate}",
                        identifier=str(val_run.id),
                        status="PASSED" if val_run.blocker_count == 0 else "BLOCKED",
                        timestamp=val_run.created_at.isoformat() if val_run.created_at else None,
                        actor="SYSTEM_VALIDATOR_ENGINE",
                        details={
                            "rules_evaluated": val_run.rules_evaluated,
                            "blockers": val_run.blocker_count,
                            "can_approve": val_run.can_approve
                        }
                    )
                )
                step_idx += 1

            # Stage 5: Human Review
            review = self.db.query(ReviewDecisionModel).filter(ReviewDecisionModel.revision_id == rev.id).first()
            if review:
                nodes.append(
                    TraceOriginNode(
                        step=step_idx,
                        stage="HUMAN_REVIEW",
                        title=f"Review: {review.decision}",
                        identifier=str(review.id),
                        status=review.decision,
                        timestamp=review.created_at.isoformat() if review.created_at else None,
                        actor=review.reviewer_id,
                        details={
                            "reason": review.reason,
                            "actor_context": review.actor_context
                        }
                    )
                )
                step_idx += 1

            # Stage 6: Governed Revision
            nodes.append(
                TraceOriginNode(
                    step=step_idx,
                    stage="GOVERNED_REVISION",
                    title=f"Revision {rev.revision_number}: {rev.prototype_vuid}",
                    identifier=str(rev.id),
                    status=rev.status,
                    timestamp=rev.created_at.isoformat() if rev.created_at else None,
                    actor=rev.created_by,
                    details={
                        "prototype_vuid": rev.prototype_vuid,
                        "vuid_full_hash": rev.vuid_full_hash,
                        "elevation_bounds": [float(rev.z_min), float(rev.z_max)],
                        "volume_cbm": float(rev.volume_cbm)
                    }
                )
            )
            step_idx += 1

            # Stage 7: Gate C Approval
            approval = self.db.query(ApprovalDecisionModel).filter(ApprovalDecisionModel.revision_id == rev.id).first()
            if approval:
                is_approved = True
                nodes.append(
                    TraceOriginNode(
                        step=step_idx,
                        stage="GATE_C_APPROVAL",
                        title=f"Adjudication: {approval.status}",
                        identifier=str(approval.id),
                        status=approval.status,
                        timestamp=approval.created_at.isoformat() if approval.created_at else None,
                        actor=approval.approver_id,
                        details={
                            "reason": approval.reason,
                            "actor_context": approval.actor_context
                        }
                    )
                )
                step_idx += 1

            # Stage 8: Export
            export_rec = self.db.query(ExportRecordModel).filter(ExportRecordModel.revision_id == rev.id).first()
            if export_rec:
                nodes.append(
                    TraceOriginNode(
                        step=step_idx,
                        stage="EXPORT",
                        title=f"Export: {export_rec.export_format}",
                        identifier=str(export_rec.id),
                        status="EXPORTED",
                        timestamp=export_rec.created_at.isoformat() if export_rec.created_at else None,
                        actor=export_rec.exported_by,
                        details={
                            "checksum": export_rec.checksum,
                            "format": export_rec.export_format
                        }
                    )
                )

        return TraceOriginResponse(
            target_identifier=identifier,
            parent_ulpin=ulpin,
            lineage_path=nodes,
            is_authoritative=is_approved,
            provenance_hash=prov_hash
        )
