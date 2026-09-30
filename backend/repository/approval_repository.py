from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from backend.db.models import ApprovalDecisionModel
from backend.domain.approval import ApprovalDecision
from backend.domain.enums import ApprovalStatus


class ApprovalRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, decision: ApprovalDecision) -> ApprovalDecision:
        model = ApprovalDecisionModel(
            id=decision.id,
            revision_id=decision.revision_id,
            approver_id=decision.approver_id,
            actor_context=decision.actor_context,
            status=decision.status.value,
            reason=decision.reason,
            referenced_validation_run_id=decision.referenced_validation_run_id,
            referenced_review_id=decision.referenced_review_id,
            created_at=decision.created_at
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def find_latest_for_revision(self, revision_id: UUID) -> Optional[ApprovalDecision]:
        model = (
            self.db.query(ApprovalDecisionModel)
            .filter_by(revision_id=revision_id)
            .order_by(ApprovalDecisionModel.created_at.desc())
            .first()
        )
        if not model:
            return None
        return self._to_domain(model)

    def _to_domain(self, model: ApprovalDecisionModel) -> ApprovalDecision:
        return ApprovalDecision(
            id=model.id,
            revision_id=model.revision_id,
            approver_id=model.approver_id,
            actor_context=model.actor_context,
            status=ApprovalStatus(model.status),
            reason=model.reason,
            referenced_validation_run_id=model.referenced_validation_run_id,
            referenced_review_id=model.referenced_review_id,
            created_at=model.created_at
        )
