from uuid import uuid4
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from backend.domain.enums import IssueSeverity
from backend.repository.parcel_repository import ParcelRepository
from backend.repository.unit_repository import SpatialUnitRepository
from backend.repository.issue_repository import IssueRepository
from backend.validation.runner import ValidationRunner
from backend.schemas.validation_contracts import ValidationSummaryResponse, ValidationIssueResponse
from backend.exceptions import ParcelNotFoundError


class ValidationService:
    def __init__(self, db: Session):
        self.db = db
        self.parcel_repo = ParcelRepository(db)
        self.unit_repo = SpatialUnitRepository(db)
        self.issue_repo = IssueRepository(db)
        self.runner = ValidationRunner()

    def run_validation(self, ulpin: str) -> ValidationSummaryResponse:
        parcel = self.parcel_repo.find_by_ulpin(ulpin)
        if not parcel:
            raise ParcelNotFoundError(ulpin)

        units = self.unit_repo.find_by_parent_ulpin(ulpin)
        run_id = uuid4()
        now = datetime.now(timezone.utc)

        # Execute Gate A validation rules
        issues = self.runner.execute(parcel=parcel, units=units, run_id=run_id)

        # Clear prior issues for this parcel
        object_ids = [parcel.ulpin] + [u.prototype_vuid for u in units]
        self.issue_repo.delete_for_objects(object_ids)

        issue_responses: list[ValidationIssueResponse] = []
        blocker_count = 0
        error_count = 0
        warning_count = 0
        passed_rules = 0

        for issue in issues:
            if issue.passed:
                passed_rules += 1
            else:
                if issue.severity == IssueSeverity.BLOCKER:
                    blocker_count += 1
                elif issue.severity == IssueSeverity.ERROR:
                    error_count += 1
                elif issue.severity == IssueSeverity.WARN:
                    warning_count += 1

            issue_responses.append(
                ValidationIssueResponse(
                    id=str(issue.id),
                    run_id=str(issue.run_id),
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
            )

        # Persist issues
        self.issue_repo.save_issues(issues)

        can_approve = (blocker_count == 0)

        return ValidationSummaryResponse(
            run_id=str(run_id),
            ulpin=ulpin,
            timestamp=now,
            rules_evaluated=len(issues),
            passed_rules=passed_rules,
            failed_rules=len(issues) - passed_rules,
            blocker_count=blocker_count,
            error_count=error_count,
            warning_count=warning_count,
            can_approve=can_approve,
            issues=issue_responses
        )
