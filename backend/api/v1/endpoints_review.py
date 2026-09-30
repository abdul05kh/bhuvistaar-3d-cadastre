from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas.governance_contracts import ReviewSubmitRequest, ReviewDecisionResponse
from backend.services.review_service import ReviewService
from backend.exceptions import RevisionNotFoundError, ApprovalBlockedError

router = APIRouter(tags=["Human Review"])


@router.post("/units/{vuid}/revisions/{revision_id}/review", response_model=ReviewDecisionResponse, status_code=status.HTTP_201_CREATED)
@router.post("/governance/review/{revision_id}", response_model=ReviewDecisionResponse, status_code=status.HTTP_201_CREATED)
def submit_review(
    revision_id: UUID,
    request: ReviewSubmitRequest,
    vuid: str = "",
    db: Session = Depends(get_db)
):
    service = ReviewService(db)
    try:
        decision = service.submit_review(revision_id=revision_id, request=request)
        return ReviewDecisionResponse(
            id=str(decision.id),
            revision_id=str(decision.revision_id),
            reviewer_id=decision.reviewer_id,
            decision=decision.decision.value,
            reason=decision.reason,
            actor_context=decision.actor_context,
            referenced_validation_run_id=str(decision.referenced_validation_run_id) if decision.referenced_validation_run_id else None,
            created_at=decision.created_at
        )
    except RevisionNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ApprovalBlockedError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))


@router.get("/units/{vuid}/revisions/{revision_id}/review", response_model=ReviewDecisionResponse)
@router.get("/governance/review/{revision_id}", response_model=ReviewDecisionResponse)
def get_review(
    revision_id: UUID,
    vuid: str = "",
    db: Session = Depends(get_db)
):
    service = ReviewService(db)
    decision = service.get_latest_review(revision_id=revision_id)
    if not decision:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No review found for revision '{revision_id}'.")
    return ReviewDecisionResponse(
        id=str(decision.id),
        revision_id=str(decision.revision_id),
        reviewer_id=decision.reviewer_id,
        decision=decision.decision.value,
        reason=decision.reason,
        actor_context=decision.actor_context,
        referenced_validation_run_id=str(decision.referenced_validation_run_id) if decision.referenced_validation_run_id else None,
        created_at=decision.created_at
    )
