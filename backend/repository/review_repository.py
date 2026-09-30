from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from backend.db.models import ReviewDecisionModel
from backend.domain.review import ReviewDecision
from backend.domain.enums import ReviewDecisionType


class ReviewRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, decision: ReviewDecision) -> ReviewDecision:
        model = ReviewDecisionModel(
            id=decision.id,
            revision_id=decision.revision_id,
            reviewer_id=decision.reviewer_id,
            actor_context=decision.actor_context,
            decision=decision.decision.value,
            reason=decision.reason,
            referenced_validation_run_id=decision.referenced_validation_run_id,
            created_at=decision.created_at
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def find_latest_for_revision(self, revision_id: UUID) -> Optional[ReviewDecision]:
        model = (
            self.db.query(ReviewDecisionModel)
            .filter_by(revision_id=revision_id)
            .order_by(ReviewDecisionModel.created_at.desc())
            .first()
        )
        if not model:
            return None
        return self._to_domain(model)

    def find_by_id(self, review_id: UUID) -> Optional[ReviewDecision]:
        model = self.db.query(ReviewDecisionModel).filter_by(id=review_id).first()
        if not model:
            return None
        return self._to_domain(model)

    def _to_domain(self, model: ReviewDecisionModel) -> ReviewDecision:
        return ReviewDecision(
            id=model.id,
            revision_id=model.revision_id,
            reviewer_id=model.reviewer_id,
            actor_context=model.actor_context,
            decision=ReviewDecisionType(model.decision),
            reason=model.reason,
            referenced_validation_run_id=model.referenced_validation_run_id,
            created_at=model.created_at
        )
