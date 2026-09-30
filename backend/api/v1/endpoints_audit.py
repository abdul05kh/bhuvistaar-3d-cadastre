from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas.governance_contracts import AuditEventResponse
from backend.services.audit_service import AuditService

router = APIRouter(tags=["Audit Trail"])


@router.get("/audit/events", response_model=list[AuditEventResponse])
def get_audit_events(
    revision_id: Optional[UUID] = Query(None, description="Filter by spatial unit revision ID"),
    entity_type: Optional[str] = Query(None, description="Filter by entity type (e.g. SPATIAL_UNIT, PARCEL)"),
    entity_id: Optional[str] = Query(None, description="Filter by entity ID"),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    service = AuditService(db)
    if revision_id:
        events = service.get_events_for_revision(revision_id)
    elif entity_type and entity_id:
        events = service.get_events_for_entity(entity_type, entity_id)
    else:
        events = service.get_recent_events(limit=limit)

    return [
        AuditEventResponse(
            id=str(e.id),
            timestamp=e.timestamp,
            actor_id=e.actor_id,
            authorization_mode=e.authorization_mode,
            action=e.action.value,
            entity_type=e.entity_type,
            entity_id=e.entity_id,
            revision_id=str(e.revision_id) if e.revision_id else None,
            previous_state=e.previous_state,
            new_state=e.new_state,
            reason=e.reason,
            correlation_id=e.correlation_id,
            metadata=e.metadata
        )
        for e in events
    ]


@router.get("/governance/audit/revision/{revision_id}", response_model=list[AuditEventResponse])
def get_revision_audit_trail(
    revision_id: UUID,
    db: Session = Depends(get_db)
):
    service = AuditService(db)
    events = service.get_events_for_revision(revision_id)
    return [
        AuditEventResponse(
            id=str(e.id),
            timestamp=e.timestamp,
            actor_id=e.actor_id,
            authorization_mode=e.authorization_mode,
            action=e.action.value,
            entity_type=e.entity_type,
            entity_id=e.entity_id,
            revision_id=str(e.revision_id) if e.revision_id else None,
            previous_state=e.previous_state,
            new_state=e.new_state,
            reason=e.reason,
            correlation_id=e.correlation_id,
            metadata=e.metadata
        )
        for e in events
    ]


@router.get("/governance/audit/recent", response_model=list[AuditEventResponse])
def get_recent_audit_trail(
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    service = AuditService(db)
    events = service.get_recent_events(limit=limit)
    return [
        AuditEventResponse(
            id=str(e.id),
            timestamp=e.timestamp,
            actor_id=e.actor_id,
            authorization_mode=e.authorization_mode,
            action=e.action.value,
            entity_type=e.entity_type,
            entity_id=e.entity_id,
            revision_id=str(e.revision_id) if e.revision_id else None,
            previous_state=e.previous_state,
            new_state=e.new_state,
            reason=e.reason,
            correlation_id=e.correlation_id,
            metadata=e.metadata
        )
        for e in events
    ]
