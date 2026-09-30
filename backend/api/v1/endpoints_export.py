from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas.governance_contracts import StructuredExportResponse
from backend.services.export_service import ExportService
from backend.exceptions import RevisionNotFoundError

router = APIRouter(tags=["Structured Export"])


@router.get("/units/{vuid}/revisions/{revision_id}/export", response_model=StructuredExportResponse)
@router.get("/governance/export/revision/{revision_id}", response_model=StructuredExportResponse)
def export_revision(
    revision_id: UUID,
    vuid: str = "",
    exported_by: str = "SIM-OFFICER-001",
    db: Session = Depends(get_db)
):
    service = ExportService(db)
    try:
        return service.generate_export_for_revision(revision_id=revision_id, exported_by=exported_by)
    except RevisionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
