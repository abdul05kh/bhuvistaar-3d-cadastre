"""AI Orchestration Service (Slice 3).

Coordinates Layers A, B, C, and D:
Evidence -> Observations -> Candidates -> Output Validation -> Anomalies -> Persistence -> Audit.
CRITICAL CONSTRAINT: AI failure never crashes the application; if disabled, raises AIServiceDisabledError.
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.config import settings
from backend.exceptions import (
    ParcelNotFoundError,
    AIServiceDisabledError,
    AIOutputValidationError
)
from backend.domain.enums import AuditAction, IssueSeverity
from backend.db.models import (
    ParentParcelModel,
    EvidenceSourceModel,
    EvidenceObservationModel,
    AICandidateModel,
    AIAnomalyModel,
    SpatialUnitModel
)
from backend.ai.models.evidence_extractor import EvidenceExtractor
from backend.ai.models.candidate_generator import CandidateGenerator
from backend.ai.models.anomaly_detector import AnomalyDetector
from backend.ai.schemas.candidate import CandidateSpatialUnit
from backend.ai.schemas.anomaly import AIAnomaly
from backend.ai.schemas.observation import EvidenceObservation
from backend.ai.schemas.summary import (
    AIAssistanceSummary,
    ReviewerQueueItem,
    ReviewerQueueResponse
)
from backend.services.audit_service import AuditService


class AIOrchestrator:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    def run_inference_pipeline(
        self,
        parent_ulpin: str,
        actor_id: str = "ai_inference_pipeline",
        custom_levels: list[dict] | None = None
    ) -> tuple[list[CandidateSpatialUnit], list[AIAnomaly], AIAssistanceSummary]:
        """Executes full AI inference pipeline for a given parcel."""
        if not settings.AI_ASSISTANCE_ENABLED:
            raise AIServiceDisabledError()

        parcel = self.db.query(ParentParcelModel).filter(ParentParcelModel.ulpin == parent_ulpin).first()
        if not parcel:
            raise ParcelNotFoundError(parent_ulpin)

        evidence_sources = self.db.query(EvidenceSourceModel).filter(EvidenceSourceModel.parent_ulpin == parent_ulpin).all()
        existing_units = self.db.query(SpatialUnitModel).filter(SpatialUnitModel.parent_ulpin == parent_ulpin).all()

        # Audit: AI_INFERENCE_STARTED
        correlation_id = f"ai-run-{uuid.uuid4().hex[:12]}"
        self.audit_service.record_event(
            actor_id=actor_id,
            action=AuditAction.AI_INFERENCE_STARTED,
            entity_type="PARENT_PARCEL",
            entity_id=parent_ulpin,
            reason="Triggered AI cadastral intelligence inference",
            correlation_id=correlation_id,
            metadata={"evidence_count": len(evidence_sources)}
        )

        # 1. Layer A: Evidence Extraction
        observations = EvidenceExtractor.extract_observations(evidence_sources, parcel)

        # Persist observations
        for obs in observations:
            obs_model = EvidenceObservationModel(
                evidence_id=obs.evidence_id,
                parent_ulpin=obs.parent_ulpin,
                observation_type=obs.observation_type.value,
                semantic_level=obs.semantic_level,
                z_min=obs.z_min,
                z_max=obs.z_max,
                confidence=obs.confidence,
                source_reference=obs.source_reference,
                extraction_method=obs.extraction_method.value,
                extraction_version=obs.extraction_version,
                model_name=obs.model_name,
                model_version=obs.model_version,
                geometry_geojson=obs.geometry_geojson,
                input_checksum=obs.input_checksum,
                metadata_json=obs.metadata
            )
            self.db.add(obs_model)

        # 2. Layer B: Candidate Generation
        candidates = CandidateGenerator.generate_candidates(
            parent_parcel=parcel,
            observations=observations,
            custom_levels=custom_levels
        )

        # Output schema validation
        for cand in candidates:
            if cand.status.value == "APPROVED":
                raise AIOutputValidationError("AI candidate output illegally claimed APPROVED status.")
            if cand.vertical_extent.z_max <= cand.vertical_extent.z_min:
                raise AIOutputValidationError(f"Invalid vertical bounds for {cand.level_code}")

            # Persist candidate
            cand_model = AICandidateModel(
                candidate_id=cand.candidate_id,
                parent_ulpin=cand.parent_ulpin,
                level_code=cand.level_code,
                semantic_type=cand.semantic_type.value,
                z_min=cand.vertical_extent.z_min,
                z_max=cand.vertical_extent.z_max,
                confidence=cand.confidence,
                confidence_band=cand.confidence_band,
                status=cand.status.value,
                source_evidence_ids=cand.source_evidence_ids,
                reason_codes=cand.reason_codes,
                footprint_geojson=cand.geometry,
                footprint_area_sqm=cand.footprint_area_sqm,
                volume_cbm=cand.volume_cbm,
                centroid_x=cand.centroid_x,
                centroid_y=cand.centroid_y,
                centroid_z=cand.centroid_z,
                model_name=cand.model.name,
                model_version=cand.model.version
            )
            self.db.add(cand_model)

            # Audit: AI_CANDIDATE_CREATED
            self.audit_service.record_event(
                actor_id=actor_id,
                action=AuditAction.AI_CANDIDATE_CREATED,
                entity_type="AI_CANDIDATE",
                entity_id=cand.candidate_id,
                reason=f"Generated candidate for level {cand.level_code} with confidence {cand.confidence:.2f}",
                correlation_id=correlation_id,
                metadata={
                    "level_code": cand.level_code,
                    "confidence": cand.confidence,
                    "reasons": cand.reason_codes
                }
            )

        # 3. Layer C: Anomaly Detection
        anomalies = AnomalyDetector.detect_anomalies(
            parent_parcel=parcel,
            candidates=candidates,
            existing_units=existing_units,
            observations=observations
        )

        # Persist anomalies
        for anom in anomalies:
            anom_model = AIAnomalyModel(
                anomaly_id=anom.anomaly_id,
                parent_ulpin=anom.parent_ulpin,
                anomaly_type=anom.anomaly_type.value,
                severity=anom.severity.value,
                affected_units=anom.affected_units,
                evidence_ids=anom.evidence_ids,
                confidence=anom.confidence,
                reason_codes=anom.reason_codes,
                recommended_action=anom.recommended_action,
                model_name=anom.model.name,
                model_version=anom.model.version
            )
            self.db.add(anom_model)

            # Audit: AI_ANOMALY_DETECTED
            self.audit_service.record_event(
                actor_id=actor_id,
                action=AuditAction.AI_ANOMALY_DETECTED,
                entity_type="AI_ANOMALY",
                entity_id=anom.anomaly_id,
                reason=anom.recommended_action,
                correlation_id=correlation_id,
                metadata={
                    "anomaly_type": anom.anomaly_type.value,
                    "severity": anom.severity.value,
                    "affected_units": anom.affected_units
                }
            )

        # Audit: AI_INFERENCE_COMPLETED
        self.audit_service.record_event(
            actor_id=actor_id,
            action=AuditAction.AI_INFERENCE_COMPLETED,
            entity_type="PARENT_PARCEL",
            entity_id=parent_ulpin,
            reason="Completed AI inference pipeline",
            correlation_id=correlation_id,
            metadata={
                "candidates_count": len(candidates),
                "anomalies_count": len(anomalies)
            }
        )

        self.db.commit()

        # 4. Layer D: Summary
        summary = self.get_summary(parent_ulpin, candidates, anomalies)

        return candidates, anomalies, summary

    def get_summary(
        self,
        parent_ulpin: str,
        candidates: list[CandidateSpatialUnit] | None = None,
        anomalies: list[AIAnomaly] | None = None
    ) -> AIAssistanceSummary:
        if candidates is None:
            cand_models = self.db.query(AICandidateModel).filter(AICandidateModel.parent_ulpin == parent_ulpin).all()
            # Convert models to schemas
            candidates = []
            for cm in cand_models:
                candidates.append(
                    CandidateSpatialUnit(
                        candidate_id=cm.candidate_id,
                        parent_ulpin=cm.parent_ulpin,
                        source_evidence_ids=cm.source_evidence_ids or [],
                        geometry=cm.footprint_geojson,
                        vertical_extent={"z_min": float(cm.z_min), "z_max": float(cm.z_max)},
                        semantic_type=cm.semantic_type,
                        level_code=cm.level_code,
                        confidence=float(cm.confidence),
                        confidence_band=cm.confidence_band,
                        reason_codes=cm.reason_codes or [],
                        model={"name": cm.model_name, "version": cm.model_version},
                        status=cm.status,
                        footprint_area_sqm=float(cm.footprint_area_sqm),
                        volume_cbm=float(cm.volume_cbm),
                        centroid_x=float(cm.centroid_x),
                        centroid_y=float(cm.centroid_y),
                        centroid_z=float(cm.centroid_z),
                        governed_unit_id=str(cm.governed_unit_id) if cm.governed_unit_id else None,
                        governed_revision_id=str(cm.governed_revision_id) if cm.governed_revision_id else None,
                        rejection_reason=cm.rejection_reason,
                        reviewed_by=cm.reviewed_by,
                        reviewed_at=cm.reviewed_at,
                        created_at=cm.created_at
                    )
                )

        if anomalies is None:
            anom_models = self.db.query(AIAnomalyModel).filter(AIAnomalyModel.parent_ulpin == parent_ulpin, AIAnomalyModel.resolved == False).all()
            anomalies = []
            for am in anom_models:
                anomalies.append(
                    AIAnomaly(
                        anomaly_id=am.anomaly_id,
                        parent_ulpin=am.parent_ulpin,
                        anomaly_type=am.anomaly_type,
                        severity=am.severity,
                        affected_units=am.affected_units or [],
                        evidence_ids=am.evidence_ids or [],
                        confidence=float(am.confidence),
                        reason_codes=am.reason_codes or [],
                        recommended_action=am.recommended_action,
                        model={"name": am.model_name, "version": am.model_version},
                        resolved=am.resolved,
                        resolution_notes=am.resolution_notes,
                        created_at=am.created_at
                    )
                )

        high_count = sum(1 for c in candidates if c.confidence >= settings.AI_CONFIDENCE_THRESHOLD_HIGH)
        med_count = sum(1 for c in candidates if settings.AI_CONFIDENCE_THRESHOLD_MEDIUM <= c.confidence < settings.AI_CONFIDENCE_THRESHOLD_HIGH)
        low_count = sum(1 for c in candidates if c.confidence < settings.AI_CONFIDENCE_THRESHOLD_MEDIUM)
        blocker_count = sum(1 for a in anomalies if a.severity == IssueSeverity.BLOCKER)
        evid_conflicts = sum(1 for a in anomalies if a.anomaly_type == "EVIDENCE_CONFLICT")
        review_req = sum(1 for c in candidates if c.status.value == "AI_CANDIDATE")

        return AIAssistanceSummary(
            parent_ulpin=parent_ulpin,
            total_candidates=len(candidates),
            high_confidence_count=high_count,
            medium_confidence_count=med_count,
            low_confidence_count=low_count,
            anomalies_count=len(anomalies),
            blocker_count=blocker_count,
            evidence_conflicts_count=evid_conflicts,
            review_required_count=review_req,
            model_name="prismatic-candidate-001",
            model_version="0.1.0"
        )

    def get_reviewer_queue(self, parent_ulpin: str) -> ReviewerQueueResponse:
        cand_models = self.db.query(AICandidateModel).filter(AICandidateModel.parent_ulpin == parent_ulpin).all()
        anom_models = self.db.query(AIAnomalyModel).filter(AIAnomalyModel.parent_ulpin == parent_ulpin, AIAnomalyModel.resolved == False).all()

        queue_items: list[ReviewerQueueItem] = []

        # 1. Blockers (Priority 1)
        for a in anom_models:
            if a.severity == IssueSeverity.BLOCKER.value:
                queue_items.append(
                    ReviewerQueueItem(
                        priority=1,
                        item_type="BLOCKER",
                        identifier=a.anomaly_id,
                        title=f"Blocker: {a.anomaly_type}",
                        severity=IssueSeverity.BLOCKER,
                        confidence=float(a.confidence),
                        reason=a.recommended_action,
                        recommended_action="Reconcile vertical elevation conflict before Gate C approval.",
                        affected_level=", ".join(a.affected_units or [])
                    )
                )

        # 2. Anomalies / Warnings (Priority 2)
        for a in anom_models:
            if a.severity != IssueSeverity.BLOCKER.value:
                queue_items.append(
                    ReviewerQueueItem(
                        priority=2,
                        item_type="ANOMALY",
                        identifier=a.anomaly_id,
                        title=f"Anomaly: {a.anomaly_type}",
                        severity=IssueSeverity(a.severity),
                        confidence=float(a.confidence),
                        reason=a.recommended_action,
                        recommended_action="Inspect drawing annotations against spatial bounds.",
                        affected_level=", ".join(a.affected_units or [])
                    )
                )

        # 3. Low Confidence Candidates (Priority 3)
        for c in cand_models:
            if float(c.confidence) < settings.AI_CONFIDENCE_THRESHOLD_MEDIUM and c.status == "AI_CANDIDATE":
                queue_items.append(
                    ReviewerQueueItem(
                        priority=3,
                        item_type="CANDIDATE_REVIEW",
                        identifier=c.candidate_id,
                        title=f"Low Confidence Proposal: Level {c.level_code}",
                        severity=IssueSeverity.WARN,
                        confidence=float(c.confidence),
                        reason=f"Candidate confidence ({float(c.confidence):.2f}) below threshold.",
                        recommended_action="Manual survey transcription or evidence attachment required.",
                        affected_level=c.level_code
                    )
                )

        # 4. Standard Unreviewed Candidates (Priority 4)
        for c in cand_models:
            if float(c.confidence) >= settings.AI_CONFIDENCE_THRESHOLD_MEDIUM and c.status == "AI_CANDIDATE":
                queue_items.append(
                    ReviewerQueueItem(
                        priority=4,
                        item_type="CANDIDATE_REVIEW",
                        identifier=c.candidate_id,
                        title=f"Unreviewed Candidate: Level {c.level_code}",
                        severity=IssueSeverity.INFO,
                        confidence=float(c.confidence),
                        reason=f"Proposed with {float(c.confidence):.2f} confidence from {len(c.source_evidence_ids or [])} evidence records.",
                        recommended_action="Review geometry and accept into governed workflow.",
                        affected_level=c.level_code
                    )
                )

        # Sort by priority ascending
        queue_items.sort(key=lambda x: x.priority)

        return ReviewerQueueResponse(
            parent_ulpin=parent_ulpin,
            total_items=len(queue_items),
            items=queue_items
        )
