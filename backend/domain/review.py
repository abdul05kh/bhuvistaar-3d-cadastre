from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from backend.domain.enums import ReviewDecisionType


@dataclass
class ReviewDecision:
    revision_id: UUID
    reviewer_id: str
    decision: ReviewDecisionType
    reason: str
    actor_context: str = "SIMULATED_PROTOTYPE"
    referenced_validation_run_id: Optional[UUID] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
