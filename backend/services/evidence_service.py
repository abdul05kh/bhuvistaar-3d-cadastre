from sqlalchemy.orm import Session
from backend.domain.evidence import EvidenceSource
from backend.schemas.evidence_contracts import EvidenceRegisterRequest
from backend.repository.evidence_repository import EvidenceRepository
from backend.repository.parcel_repository import ParcelRepository
from backend.exceptions import ParcelNotFoundError


class EvidenceService:
    def __init__(self, db: Session):
        self.db = db
        self.evidence_repo = EvidenceRepository(db)
        self.parcel_repo = ParcelRepository(db)

    def register_evidence(self, request: EvidenceRegisterRequest) -> EvidenceSource:
        # Verify parent parcel exists
        parcel = self.parcel_repo.find_by_ulpin(request.parent_ulpin)
        if not parcel:
            raise ParcelNotFoundError(request.parent_ulpin)

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
            metadata=request.metadata
        )

        return self.evidence_repo.save(evidence)

    def get_evidence(self, evidence_id: str) -> EvidenceSource:
        evidence = self.evidence_repo.find_by_id(evidence_id)
        if not evidence:
            from backend.exceptions import EvidenceNotFoundError
            raise EvidenceNotFoundError(evidence_id)
        return evidence
