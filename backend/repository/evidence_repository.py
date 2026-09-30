from typing import Optional
from sqlalchemy.orm import Session
from backend.db.models import EvidenceSourceModel
from backend.domain.evidence import EvidenceSource
from backend.domain.enums import EvidenceType


class EvidenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, evidence: EvidenceSource) -> EvidenceSource:
        model = self.db.query(EvidenceSourceModel).filter_by(id=evidence.id).first()
        if model:
            model.provider = evidence.provider
            model.source_reference = evidence.source_reference
            model.checksum = evidence.checksum
            model.crs = evidence.crs
            model.acquisition_time = evidence.acquisition_time
            model.processing_version = evidence.processing_version
            model.metadata_json = evidence.metadata
        else:
            model = EvidenceSourceModel(
                id=evidence.id,
                parent_ulpin=evidence.parent_ulpin,
                evidence_type=evidence.evidence_type.value,
                provider=evidence.provider,
                source_reference=evidence.source_reference,
                checksum=evidence.checksum,
                crs=evidence.crs,
                acquisition_time=evidence.acquisition_time,
                processing_version=evidence.processing_version,
                metadata_json=evidence.metadata,
                created_at=evidence.created_at
            )
            self.db.add(model)
            
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def find_by_id(self, evidence_id: str) -> Optional[EvidenceSource]:
        model = self.db.query(EvidenceSourceModel).filter_by(id=evidence_id).first()
        if not model:
            return None
        return self._to_domain(model)

    def find_by_parent_ulpin(self, ulpin: str) -> list[EvidenceSource]:
        models = self.db.query(EvidenceSourceModel).filter_by(parent_ulpin=ulpin).all()
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: EvidenceSourceModel) -> EvidenceSource:
        return EvidenceSource(
            id=model.id,
            parent_ulpin=model.parent_ulpin,
            evidence_type=EvidenceType(model.evidence_type),
            provider=model.provider,
            source_reference=model.source_reference,
            checksum=model.checksum,
            crs=model.crs,
            acquisition_time=model.acquisition_time,
            processing_version=model.processing_version,
            metadata=model.metadata_json or {},
            created_at=model.created_at
        )
