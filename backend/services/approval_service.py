from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.domain.approval import ApprovalDecision
from backend.domain.enums import ApprovalStatus, UnitStatus, AuditAction, ReviewDecisionType
from backend.repository.approval_repository import ApprovalRepository
from backend.repository.revision_repository import RevisionRepository
from backend.repository.review_repository import ReviewRepository
from backend.repository.validation_run_repository import ValidationRunRepository
from backend.repository.provenance_repository import ProvenanceRepository
from backend.repository.unit_repository import SpatialUnitRepository
from backend.services.audit_service import AuditService
from backend.schemas.governance_contracts import ApprovalSubmitRequest, RejectionSubmitRequest, RejectionResponse
from backend.exceptions import RevisionNotFoundError, ApprovalBlockedError


class ApprovalService:
    def __init__(self, db: Session):
        self.db = db
        self.approval_repo = ApprovalRepository(db)
        self.revision_repo = RevisionRepository(db)
        self.review_repo = ReviewRepository(db)
        self.val_run_repo = ValidationRunRepository(db)
        self.prov_repo = ProvenanceRepository(db)
        self.unit_repo = SpatialUnitRepository(db)
        self.audit_service = AuditService(db)

    def evaluate_gate_c_eligibility(self, revision_id: UUID) -> tuple[bool, list[str]]:
        reasons = []

        revision = self.revision_repo.find_by_id(revision_id)
        if not revision:
            return False, [f"Spatial unit revision '{revision_id}' does not exist."]

        # 1. Revision must not be already approved
        if revision.status == UnitStatus.APPROVED:
            reasons.append("Revision is already approved (approved revisions are immutable).")

        # 2. Latest validation run check
        latest_val = self.val_run_repo.find_latest_for_revision(revision_id)
        if not latest_val:
            # Fall back to parent parcel validation
            latest_val = self.val_run_repo.find_latest_for_parcel(revision.parent_ulpin)

        if not latest_val:
            reasons.append("No validation run found for this candidate revision.")
        else:
            if latest_val.blocker_count > 0 or not latest_val.can_approve:
                reasons.append(f"Unresolved BLOCKER validation issues exist ({latest_val.blocker_count} blockers).")
            # Validation must have run on or after revision creation
            if latest_val.created_at < revision.created_at:
                reasons.append("Revision was created/corrected after the latest validation run. Revalidation is required.")

        # 3. Provenance and evidence integrity
        prov = self.prov_repo.find_by_revision_id(revision_id)
        if not prov:
            reasons.append("Mandatory provenance record is missing for this revision.")
        else:
            if not prov.evidence_sources or len(prov.evidence_sources) == 0:
                reasons.append("No evidence records attached to this revision.")
            if not prov.is_verified:
                reasons.append("Attached evidence integrity has not been verified.")

        # 4. Human review decision check
        latest_review = self.review_repo.find_latest_for_revision(revision_id)
        if not latest_review:
            reasons.append("No human review decision has been recorded for this revision.")
        else:
            if latest_review.decision != ReviewDecisionType.ACCEPT:
                reasons.append(f"Latest review decision is '{latest_review.decision.value}', not 'ACCEPT'.")

        is_eligible = (len(reasons) == 0)
        return is_eligible, reasons

    def approve_revision(self, revision_id: UUID, request: ApprovalSubmitRequest) -> ApprovalDecision:
        is_eligible, blockers = self.evaluate_gate_c_eligibility(revision_id)
        if not is_eligible:
            raise ApprovalBlockedError(
                f"Gate C approval rejected: {'; '.join(blockers)}",
                details={"revision_id": str(revision_id), "blockers": blockers}
            )

        revision = self.revision_repo.find_by_id(revision_id)
        latest_val = self.val_run_repo.find_latest_for_revision(revision_id)
        if not latest_val:
            latest_val = self.val_run_repo.find_latest_for_parcel(revision.parent_ulpin)
        latest_review = self.review_repo.find_latest_for_revision(revision_id)

        decision = ApprovalDecision(
            revision_id=revision.id,
            approver_id=request.approver_id,
            status=ApprovalStatus.APPROVED,
            reason=request.reason,
            referenced_validation_run_id=latest_val.id,
            referenced_review_id=latest_review.id,
            actor_context=request.actor_context
        )
        saved_decision = self.approval_repo.save(decision)

        # Transition revision and unit status to APPROVED
        prev_status = revision.status.value
        self.revision_repo.update_status(revision_id, UnitStatus.APPROVED)
        self.unit_repo.set_active_revision(revision.unit_id, revision_id)

        # Audit event
        self.audit_service.log_event(
            action=AuditAction.APPROVAL_GRANTED,
            entity_type="SPATIAL_UNIT_REVISION",
            entity_id=str(revision_id),
            actor_id=request.approver_id,
            authorization_mode=request.actor_context,
            revision_id=revision_id,
            previous_state=prev_status,
            new_state=UnitStatus.APPROVED.value,
            reason=f"Candidate approved by officer. Reason: {request.reason}",
            metadata={"approval_id": str(saved_decision.id), "vuid": revision.prototype_vuid}
        )

        return saved_decision

    def reject_revision(self, revision_id: UUID, request: RejectionSubmitRequest) -> RejectionResponse:
        revision = self.revision_repo.find_by_id(revision_id)
        if not revision:
            raise RevisionNotFoundError(str(revision_id))

        if revision.status == UnitStatus.APPROVED:
            raise ApprovalBlockedError(
                "Cannot reject an already approved revision. Approved revisions are immutable.",
                details={"revision_id": str(revision_id)}
            )

        prev_status = revision.status.value
        self.revision_repo.update_status(revision_id, UnitStatus.REJECTED)

        # Audit event
        self.audit_service.log_event(
            action=AuditAction.APPROVAL_REJECTED,
            entity_type="SPATIAL_UNIT_REVISION",
            entity_id=str(revision_id),
            actor_id=request.actor_id,
            authorization_mode=request.actor_context,
            revision_id=revision_id,
            previous_state=prev_status,
            new_state=UnitStatus.REJECTED.value,
            reason=f"Candidate rejected: {request.reason}",
            metadata={"rejection_reason": request.reason}
        )

        return RejectionResponse(
            revision_id=str(revision_id),
            status=UnitStatus.REJECTED.value,
            reason=request.reason,
            created_at=datetime.now(timezone.utc)
        )
