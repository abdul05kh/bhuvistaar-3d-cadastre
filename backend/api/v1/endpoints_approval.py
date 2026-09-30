from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas.governance_contracts import (
    ApprovalSubmitRequest,
    ApprovalDecisionResponse,
    RejectionSubmitRequest,
    RejectionResponse
)
from backend.services.approval_service import ApprovalService
from backend.exceptions import RevisionNotFoundError, ApprovalBlockedError

router = APIRouter(tags=["Approval & Gate C"])


@router.get("/units/{vuid}/revisions/{revision_id}/eligibility")
def check_approval_eligibility(
    vuid: str,
    revision_id: UUID,
    db: Session = Depends(get_db)
):
    service = ApprovalService(db)
    is_eligible, blockers = service.evaluate_gate_c_eligibility(revision_id)
    return {
        "revision_id": str(revision_id),
        "prototype_vuid": vuid,
        "is_eligible": is_eligible,
        "blockers": blockers
    }


@router.post("/units/{vuid}/revisions/{revision_id}/approve", response_model=ApprovalDecisionResponse, status_code=status.HTTP_201_CREATED)
def approve_revision(
    vuid: str,
    revision_id: UUID,
    request: ApprovalSubmitRequest,
    db: Session = Depends(get_db)
):
    service = ApprovalService(db)
    try:
        decision = service.approve_revision(revision_id=revision_id, request=request)
        return ApprovalDecisionResponse(
            id=str(decision.id),
            revision_id=str(decision.revision_id),
            approver_id=decision.approver_id,
            status=decision.status.value,
            reason=decision.reason,
            referenced_validation_run_id=str(decision.referenced_validation_run_id),
            referenced_review_id=str(decision.referenced_review_id),
            actor_context=decision.actor_context,
            created_at=decision.created_at
        )
    except RevisionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ApprovalBlockedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.post("/units/{vuid}/revisions/{revision_id}/reject", response_model=RejectionResponse)
def reject_revision(
    vuid: str,
    revision_id: UUID,
    request: RejectionSubmitRequest,
    db: Session = Depends(get_db)
):
    service = ApprovalService(db)
    try:
        return service.reject_revision(revision_id=revision_id, request=request)
    except RevisionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ApprovalBlockedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
