from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from backend.domain.enums import ApprovalStatus


@dataclass
class ApprovalDecision:
    revision_id: UUID
    approver_id: str
    status: ApprovalStatus
    reason: str
    referenced_validation_run_id: UUID
    referenced_review_id: UUID
    actor_context: str = "SIMULATED_PROTOTYPE"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
