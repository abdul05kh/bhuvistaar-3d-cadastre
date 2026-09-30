from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas.governance_contracts import CorrectionSubmitRequest, CorrectionResponse
from backend.services.correction_service import CorrectionService
from backend.exceptions import RevisionNotFoundError, InvalidGeometryError, ApprovalBlockedError

router = APIRouter(tags=["Correction Workflow"])


@router.post("/units/{vuid}/revisions/{revision_id}/correct", response_model=CorrectionResponse, status_code=status.HTTP_201_CREATED)
def apply_correction(
    vuid: str,
    revision_id: UUID,
    request: CorrectionSubmitRequest,
    db: Session = Depends(get_db)
):
    service = CorrectionService(db)
    try:
        return service.apply_correction(revision_id=revision_id, request=request)
    except RevisionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except (InvalidGeometryError, ValueError) as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
    except ApprovalBlockedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
