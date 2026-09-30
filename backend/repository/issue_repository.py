from typing import Sequence
from sqlalchemy.orm import Session
from backend.db.models import ValidationIssueModel
from backend.domain.validation import ValidationIssue


class IssueRepository:
    def __init__(self, db: Session):
        self.db = db

    def delete_for_objects(self, object_ids: Sequence[str]) -> None:
        if not object_ids:
            return
        if hasattr(self.db, "query"):
            self.db.query(ValidationIssueModel).filter(
                ValidationIssueModel.object_id.in_(object_ids)
            ).delete(synchronize_session=False)
            self.db.commit()

    def save_issues(self, issues: Sequence[ValidationIssue]) -> None:
        if not hasattr(self.db, "add"):
            return
        for issue in issues:
            model = ValidationIssueModel(
                id=issue.id,
                run_id=issue.run_id,
                rule_code=issue.rule_code,
                severity=issue.severity.value,
                object_type=issue.object_type,
                object_id=issue.object_id,
                passed=issue.passed,
                message=issue.message,
                measured_value=issue.measured_value,
                threshold=issue.threshold,
                suggested_action=issue.suggested_action,
                created_at=issue.created_at
            )
            self.db.add(model)
        self.db.commit()
