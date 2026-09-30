from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from backend.domain.enums import GateType


@dataclass
class ValidationRun:
    parent_ulpin: str
    gate: GateType
    validator_version: str = "1.0.0"
    revision_id: Optional[UUID] = None
    unit_id: Optional[UUID] = None
    rules_evaluated: int = 0
    passed_rules: int = 0
    failed_rules: int = 0
    blocker_count: int = 0
    error_count: int = 0
    warning_count: int = 0
    can_approve: bool = False
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
