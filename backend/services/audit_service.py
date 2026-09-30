from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from backend.domain.audit import AuditEvent
from backend.domain.enums import AuditAction
from backend.repository.audit_repository import AuditRepository


class AuditService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = AuditRepository(db)

    def log_event(
        self,
        action: AuditAction,
        entity_type: str,
        entity_id: str,
        actor_id: str = "OFFICER-001",
        authorization_mode: str = "SIMULATED_PROTOTYPE",
        revision_id: Optional[UUID] = None,
        previous_state: Optional[str] = None,
        new_state: Optional[str] = None,
        reason: Optional[str] = None,
        correlation_id: Optional[str] = None,
        metadata: Optional[dict] = None
    ) -> AuditEvent:
        event = AuditEvent(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            authorization_mode=authorization_mode,
            revision_id=revision_id,
            previous_state=previous_state,
            new_state=new_state,
            reason=reason,
            correlation_id=correlation_id,
            metadata=metadata or {}
        )
        return self.repo.append(event)

    def get_events_for_revision(self, revision_id: UUID) -> list[AuditEvent]:
        return self.repo.find_by_revision(revision_id)

    def get_events_for_entity(self, entity_type: str, entity_id: str) -> list[AuditEvent]:
        return self.repo.find_by_entity(entity_type, entity_id)

    def get_recent_events(self, limit: int = 100) -> list[AuditEvent]:
        return self.repo.find_all(limit=limit)
