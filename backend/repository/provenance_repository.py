from typing import Optional
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.db.models import ProvenanceRecordModel
from backend.domain.provenance import ProvenanceRecord


class ProvenanceRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, record: ProvenanceRecord) -> ProvenanceRecord:
        if not hasattr(self.db, "add"):
            return record
        model = ProvenanceRecordModel(
            id=record.id,
            revision_id=record.revision_id,
            parent_ulpin=record.parent_ulpin,
            generation_method=record.generation_method,
            generation_method_version=record.generation_method_version,
            vuid_algorithm_version=record.vuid_algorithm_version,
            predecessor_vuid=record.predecessor_vuid,
            evidence_sources_json=record.evidence_sources,
            is_verified=record.is_verified,
            verified_at=record.verified_at,
            created_at=record.created_at
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def find_by_revision_id(self, revision_id: UUID) -> Optional[ProvenanceRecord]:
        model = self.db.query(ProvenanceRecordModel).filter_by(revision_id=revision_id).first()
        if not model:
            return None
        return self._to_domain(model)

    def mark_verified(self, record_id: UUID, is_verified: bool) -> Optional[ProvenanceRecord]:
        model = self.db.query(ProvenanceRecordModel).filter_by(id=record_id).first()
        if not model:
            return None
        model.is_verified = is_verified
        model.verified_at = datetime.now(timezone.utc) if is_verified else None
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def _to_domain(self, model: ProvenanceRecordModel) -> ProvenanceRecord:
        return ProvenanceRecord(
            id=model.id,
            revision_id=model.revision_id,
            parent_ulpin=model.parent_ulpin,
            generation_method=model.generation_method,
            generation_method_version=model.generation_method_version,
            vuid_algorithm_version=model.vuid_algorithm_version,
            predecessor_vuid=model.predecessor_vuid,
            evidence_sources=model.evidence_sources_json,
            is_verified=model.is_verified,
            verified_at=model.verified_at,
            created_at=model.created_at
        )
