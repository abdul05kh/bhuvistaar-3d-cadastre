import logging
from typing import Optional
from sqlalchemy.orm import Session
from backend.domain.evidence import EvidenceSource
from backend.domain.enums import AuditAction, EvidenceQuality
from backend.schemas.evidence_contracts import (
    EvidenceRegisterRequest,
    EvidenceQualityReport,
    EvidenceConflict
)
from backend.repository.evidence_repository import EvidenceRepository
from backend.repository.parcel_repository import ParcelRepository
from backend.services.audit_service import AuditService
from backend.exceptions import (
    ParcelNotFoundError,
    EvidenceNotFoundError,
    DuplicateEvidenceError,
    EvidenceQualityError
)

logger = logging.getLogger("bhuvistaar.evidence")


class EvidenceService:
    def __init__(self, db: Session = None, db_session: Session = None):
        self.db = db if db is not None else db_session
        self.evidence_repo = EvidenceRepository(self.db) if self.db is not None else None
        self.parcel_repo = ParcelRepository(self.db) if self.db is not None else None
        self.audit_service = AuditService(self.db) if self.db is not None else None

    def evaluate_quality(self, request: EvidenceRegisterRequest) -> EvidenceQualityReport:
        passed = []
        warnings = []
        blockers = []

        # Check 1: ID format
        if len(request.id) < 2 or not request.id.replace("-", "").isalnum():
            blockers.append("Invalid evidence identifier format.")
        else:
            passed.append("Identifier schema valid.")

        # Check 2: Checksum format (SHA-256 hex or min 8 chars)
        if len(request.checksum) < 8:
            blockers.append("Evidence checksum too short (minimum 8 characters).")
        elif len(request.checksum) == 64 and not all(c in "0123456789abcdefABCDEF" for c in request.checksum):
            blockers.append("Checksum is not a valid hexadecimal SHA-256 hash.")
        else:
            passed.append("Checksum schema valid.")

        # Check 3: Provider & Reference
        if not request.provider.strip():
            blockers.append("Evidence provider is empty.")
        else:
            passed.append("Provider metadata present.")

        if not request.source_reference.strip():
            blockers.append("Evidence source reference is empty.")
        else:
            passed.append("Source reference present.")

        # Check 4: CRS Check
        if request.crs:
            if "4326" in request.crs:
                warnings.append("Unprojected geographic CRS (EPSG:4326) supplied; projected CRS recommended.")
            elif not request.crs.startswith("EPSG:"):
                warnings.append(f"Non-standard CRS representation '{request.crs}'.")
            else:
                passed.append("Projected coordinate reference system verified.")

        status = EvidenceQuality.BLOCKED if blockers else (EvidenceQuality.WARNING if warnings else EvidenceQuality.ACCEPTED)

        return EvidenceQualityReport(
            evidence_id=request.id,
            parent_ulpin=request.parent_ulpin,
            status=status.value,
            checks_evaluated=len(passed) + len(warnings) + len(blockers),
            passed_checks=passed,
            warnings=warnings,
            blockers=blockers
        )

    def register_evidence(self, request: EvidenceRegisterRequest) -> EvidenceSource:
        # 1. Verify parent parcel exists
        parcel = self.parcel_repo.find_by_ulpin(request.parent_ulpin)
        if not parcel:
            raise ParcelNotFoundError(request.parent_ulpin)

        # 2. Run Evidence Quality Gate
        quality = self.evaluate_quality(request)
        if quality.status == EvidenceQuality.BLOCKED.value:
            self.audit_service.log_event(
                action=AuditAction.EVIDENCE_REJECTED,
                entity_type="EVIDENCE",
                entity_id=request.id,
                reason=f"Evidence quality gate rejected: {'; '.join(quality.blockers)}",
                metadata={"blockers": quality.blockers, "parent_ulpin": request.parent_ulpin}
            )
            raise EvidenceQualityError(
                message=f"Evidence quality gate rejected registration for '{request.id}': {'; '.join(quality.blockers)}",
                issues=quality.blockers
            )

        # 3. Duplicate Detection
        existing_sources = self.evidence_repo.find_by_parent_ulpin(request.parent_ulpin)
        for existing in existing_sources:
            if existing.checksum == request.checksum:
                if existing.id == request.id:
                    # Idempotent re-registration of the exact same evidence
                    return existing
                else:
                    # Duplicate checksum under a different ID -> report duplicate
                    self.audit_service.log_event(
                        action=AuditAction.EVIDENCE_DUPLICATE_DETECTED,
                        entity_type="EVIDENCE",
                        entity_id=request.id,
                        reason=f"Duplicate evidence content matches existing record '{existing.id}' (checksum: {request.checksum[:8]}).",
                        metadata={"duplicate_of": existing.id, "checksum": request.checksum}
                    )
                    raise DuplicateEvidenceError(
                        evidence_id=request.id,
                        checksum=request.checksum,
                        original_id=existing.id
                    )

        # 4. Check for conflicting evidence
        metadata = dict(request.metadata)
        metadata["quality_status"] = quality.status
        metadata["quality_notes"] = quality.warnings

        evidence = EvidenceSource(
            id=request.id,
            parent_ulpin=request.parent_ulpin,
            evidence_type=request.evidence_type,
            provider=request.provider,
            source_reference=request.source_reference,
            checksum=request.checksum,
            crs=request.crs,
            acquisition_time=request.acquisition_time,
            processing_version=request.processing_version,
            metadata=metadata
        )

        saved = self.evidence_repo.save(evidence)

        # Log Ingestion Audit Event
        self.audit_service.log_event(
            action=AuditAction.EVIDENCE_INGESTED,
            entity_type="EVIDENCE",
            entity_id=saved.id,
            reason=f"Evidence '{saved.id}' successfully ingested (quality: {quality.status}).",
            metadata={"checksum": saved.checksum, "evidence_type": saved.evidence_type.value, "parent_ulpin": saved.parent_ulpin}
        )

        return saved

    def get_evidence(self, evidence_id: str) -> EvidenceSource:
        evidence = self.evidence_repo.find_by_id(evidence_id)
        if not evidence:
            raise EvidenceNotFoundError(evidence_id)
        return evidence

    def list_evidence_for_parcel(self, ulpin: str) -> list[EvidenceSource]:
        return self.evidence_repo.find_by_parent_ulpin(ulpin)

    def detect_evidence_conflicts(self, ulpin: str) -> list[EvidenceConflict]:
        """Detect conflicting elevation or geometric evidence registered for the same parcel."""
        sources = self.list_evidence_for_parcel(ulpin)
        conflicts = []

        elevation_map: dict[str, tuple[str, float]] = {}

        for src in sources:
            level_elevations = dict(src.metadata.get("level_elevations", {}))
            if "level_code" in src.metadata and "elevation" in src.metadata:
                level_elevations[src.metadata["level_code"]] = src.metadata["elevation"]

            for level, elev in level_elevations.items():
                elev_val = float(elev)
                if level in elevation_map:
                    prev_src_id, prev_elev = elevation_map[level]
                    if abs(prev_elev - elev_val) > 0.05:  # > 5cm discrepancy
                        conflict = EvidenceConflict(
                            source_a_id=prev_src_id,
                            source_b_id=src.id,
                            parameter="level_elevation",
                            level_code=level,
                            source_a_value=prev_elev,
                            source_b_value=elev_val,
                            discrepancy=f"{level} elevation discrepancy: {prev_src_id} recorded {prev_elev}m, whereas {src.id} recorded {elev_val}m (delta: {abs(prev_elev - elev_val):.2f}m).",
                            resolution_status="PENDING_HUMAN_RESOLUTION"
                        )
                        conflicts.append(conflict)
                        self.audit_service.log_event(
                            action=AuditAction.EVIDENCE_CONFLICT_DETECTED,
                            entity_type="EVIDENCE_CONFLICT",
                            entity_id=f"{prev_src_id}_{src.id}_{level}",
                            reason=conflict.discrepancy,
                            metadata={"level": level, "source_a": prev_src_id, "source_b": src.id}
                        )
                else:
                    elevation_map[level] = (src.id, elev_val)

        return conflicts

