from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas.evidence_contracts import EvidenceRegisterRequest, EvidenceResponse
from backend.services.evidence_service import EvidenceService


router = APIRouter(prefix="/evidence", tags=["Evidence"])


@router.post("", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
def register_evidence(request: EvidenceRegisterRequest, db: Session = Depends(get_db)):
    service = EvidenceService(db)
    evidence = service.register_evidence(request)
    return EvidenceResponse(
        id=evidence.id,
        parent_ulpin=evidence.parent_ulpin,
        evidence_type=evidence.evidence_type.value,
        provider=evidence.provider,
        source_reference=evidence.source_reference,
        checksum=evidence.checksum,
        crs=evidence.crs,
        acquisition_time=evidence.acquisition_time,
        processing_version=evidence.processing_version,
        metadata=evidence.metadata,
        created_at=evidence.created_at
    )


@router.get("/conflicts/{ulpin}", response_model=list[dict])
def get_evidence_conflicts(ulpin: str, db: Session = Depends(get_db)):
    service = EvidenceService(db)
    conflicts = service.detect_evidence_conflicts(ulpin)
    return [c.model_dump() for c in conflicts]


@router.post("/quality/check")
def check_evidence_quality(request: EvidenceRegisterRequest, db: Session = Depends(get_db)):
    service = EvidenceService(db)
    report = service.evaluate_quality(request)
    return report.model_dump()


@router.get("/{evidence_id}", response_model=EvidenceResponse)
def get_evidence(evidence_id: str, db: Session = Depends(get_db)):
    service = EvidenceService(db)
    evidence = service.get_evidence(evidence_id)
    return EvidenceResponse(
        id=evidence.id,
        parent_ulpin=evidence.parent_ulpin,
        evidence_type=evidence.evidence_type.value,
        provider=evidence.provider,
        source_reference=evidence.source_reference,
        checksum=evidence.checksum,
        crs=evidence.crs,
        acquisition_time=evidence.acquisition_time,
        processing_version=evidence.processing_version,
        metadata=evidence.metadata,
        created_at=evidence.created_at
    )


