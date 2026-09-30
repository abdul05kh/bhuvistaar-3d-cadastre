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


@router.get("/export/geojson/{ulpin}")
def export_geojson(ulpin: str, db: Session = Depends(get_db)):
    from backend.services.interoperability_service import InteroperabilityService
    service = InteroperabilityService(db)
    return service.export_geojson(ulpin)


@router.get("/export/3d/{revision_id}")
def export_3d_obj(revision_id: UUID, db: Session = Depends(get_db)):
    from fastapi.responses import PlainTextResponse
    from backend.services.interoperability_service import InteroperabilityService
    service = InteroperabilityService(db)
    obj_content = service.export_3d_obj(revision_id)
    return PlainTextResponse(
        content=obj_content,
        media_type="text/plain",
        headers={"Content-Disposition": f"attachment; filename=cadastral_unit_{revision_id}.obj"}
    )


@router.post("/export/roundtrip/verify")
def verify_export_roundtrip(payload: dict, db: Session = Depends(get_db)):
    from backend.services.interoperability_service import InteroperabilityService
    service = InteroperabilityService(db)
    return service.verify_round_trip(payload)

