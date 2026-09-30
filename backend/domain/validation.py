from dataclasses import dataclass, field
from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional, Any
from backend.domain.enums import IssueSeverity


@dataclass
class ValidationIssue:
    rule_code: str
    severity: IssueSeverity
    object_type: str
    object_id: str
    passed: bool
    message: str
    run_id: UUID = field(default_factory=uuid4)
    measured_value: Optional[dict[str, Any]] = None
    threshold: Optional[dict[str, Any]] = None
    suggested_action: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": str(self.id),
            "run_id": str(self.run_id),
            "rule_code": self.rule_code,
            "severity": self.severity.value,
            "object_type": self.object_type,
            "object_id": self.object_id,
            "passed": self.passed,
            "message": self.message,
            "measured_value": self.measured_value,
            "threshold": self.threshold,
            "suggested_action": self.suggested_action,
            "created_at": self.created_at.isoformat()
        }
