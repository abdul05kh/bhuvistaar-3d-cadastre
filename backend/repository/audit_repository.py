from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from backend.db.models import AuditEventModel
from backend.domain.audit import AuditEvent
from backend.domain.enums import AuditAction


class AuditRepository:
    def __init__(self, db: Session):
        self.db = db

    def append(self, event: AuditEvent) -> AuditEvent:
        if not hasattr(self.db, "add"):
            return event
        model = AuditEventModel(
            id=event.id,
            timestamp=event.timestamp,
            actor_id=event.actor_id,
            authorization_mode=event.authorization_mode,
            action=event.action.value,
            entity_type=event.entity_type,
            entity_id=event.entity_id,
            revision_id=event.revision_id,
            previous_state=event.previous_state,
            new_state=event.new_state,
            reason=event.reason,
            correlation_id=event.correlation_id,
            metadata_json=event.metadata
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def find_by_entity(self, entity_type: str, entity_id: str) -> list[AuditEvent]:
        models = (
            self.db.query(AuditEventModel)
            .filter_by(entity_type=entity_type, entity_id=entity_id)
            .order_by(AuditEventModel.timestamp.asc())
            .all()
        )
        return [self._to_domain(m) for m in models]

    def find_by_revision(self, revision_id: UUID) -> list[AuditEvent]:
        models = (
            self.db.query(AuditEventModel)
            .filter_by(revision_id=revision_id)
            .order_by(AuditEventModel.timestamp.asc())
            .all()
        )
        return [self._to_domain(m) for m in models]

    def find_all(self, limit: int = 100) -> list[AuditEvent]:
        models = (
            self.db.query(AuditEventModel)
            .order_by(AuditEventModel.timestamp.desc())
            .limit(limit)
            .all()
        )
        return [self._to_domain(m) for m in models]

    def _to_domain(self, model: AuditEventModel) -> AuditEvent:
        return AuditEvent(
            id=model.id,
            timestamp=model.timestamp,
            actor_id=model.actor_id,
            authorization_mode=model.authorization_mode,
            action=AuditAction(model.action),
            entity_type=model.entity_type,
            entity_id=model.entity_id,
            revision_id=model.revision_id,
            previous_state=model.previous_state,
            new_state=model.new_state,
            reason=model.reason,
            correlation_id=model.correlation_id,
            metadata=model.metadata_json
        )
