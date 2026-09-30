from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from backend.domain.enums import AuditAction


@dataclass
class AuditEvent:
    actor_id: str
    action: AuditAction
    entity_type: str
    entity_id: str
    authorization_mode: str = "SIMULATED_PROTOTYPE"
    revision_id: Optional[UUID] = None
    previous_state: Optional[str] = None
    new_state: Optional[str] = None
    reason: Optional[str] = None
    correlation_id: Optional[str] = None
    metadata: dict = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
