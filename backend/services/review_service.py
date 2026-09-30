from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.domain.review import ReviewDecision
from backend.domain.enums import ReviewDecisionType, UnitStatus, AuditAction
from backend.repository.review_repository import ReviewRepository
from backend.repository.revision_repository import RevisionRepository
from backend.repository.validation_run_repository import ValidationRunRepository
from backend.services.audit_service import AuditService
from backend.schemas.governance_contracts import ReviewSubmitRequest
from backend.exceptions import RevisionNotFoundError, ApprovalBlockedError


class ReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.review_repo = ReviewRepository(db)
        self.revision_repo = RevisionRepository(db)
        self.val_run_repo = ValidationRunRepository(db)
        self.audit_service = AuditService(db)

    def submit_review(self, revision_id: UUID, request: ReviewSubmitRequest) -> ReviewDecision:
        revision = self.revision_repo.find_by_id(revision_id)
        if not revision:
            raise RevisionNotFoundError(str(revision_id))

        if revision.status == UnitStatus.APPROVED:
            raise ApprovalBlockedError(
                "Cannot submit review on an already approved revision. Revisions are immutable.",
                details={"revision_id": str(revision_id), "status": revision.status.value}
            )

        # Look up latest validation run for this revision (or parcel)
        latest_val = self.val_run_repo.find_latest_for_revision(revision_id)
        if not latest_val:
            latest_val = self.val_run_repo.find_latest_for_parcel(revision.parent_ulpin)

        decision = ReviewDecision(
            revision_id=revision.id,
            reviewer_id=request.reviewer_id,
            decision=request.decision,
            reason=request.reason,
            actor_context=request.actor_context,
            referenced_validation_run_id=latest_val.id if latest_val else None
        )
        saved_decision = self.review_repo.save(decision)

        # Update revision status according to decision
        prev_status = revision.status.value
        if request.decision == ReviewDecisionType.REJECT:
            new_status = UnitStatus.REJECTED
        else:
            new_status = UnitStatus.UNDER_REVIEW

        self.revision_repo.update_status(revision_id, new_status)

        # Log audit event
        self.audit_service.log_event(
            action=AuditAction.REVIEW_SUBMITTED,
            entity_type="SPATIAL_UNIT_REVISION",
            entity_id=str(revision_id),
            actor_id=request.reviewer_id,
            authorization_mode=request.actor_context,
            revision_id=revision_id,
            previous_state=prev_status,
            new_state=new_status.value,
            reason=f"Review decision: {request.decision.value}. Justification: {request.reason}",
            metadata={"decision": request.decision.value, "review_id": str(saved_decision.id)}
        )

        return saved_decision

    def get_latest_review(self, revision_id: UUID):
        return self.review_repo.find_latest_for_revision(revision_id)
