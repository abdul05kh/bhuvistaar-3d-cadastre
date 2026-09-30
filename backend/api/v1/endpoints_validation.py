from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.session import get_db
from backend.schemas.validation_contracts import ValidationRunRequest, ValidationSummaryResponse, ValidationIssueResponse
from backend.services.validation_service import ValidationService
from backend.db.models import ValidationIssueModel


router = APIRouter(tags=["Validation"])


@router.post("/validation/run", response_model=ValidationSummaryResponse)
def run_validation(request: ValidationRunRequest, db: Session = Depends(get_db)):
    service = ValidationService(db)
    return service.run_validation(ulpin=request.ulpin)


@router.get("/validation/issues", response_model=list[ValidationIssueResponse])
def get_validation_issues(ulpin: str, db: Session = Depends(get_db)):
    issues = db.query(ValidationIssueModel).filter(
        ValidationIssueModel.object_id.like(f"%{ulpin}%")
    ).all()
    return [
        ValidationIssueResponse(
            id=str(i.id),
            run_id=str(i.run_id),
            rule_code=i.rule_code,
            severity=i.severity,
            object_type=i.object_type,
            object_id=i.object_id,
            passed=i.passed,
            message=i.message,
            measured_value=i.measured_value,
            threshold=i.threshold,
            suggested_action=i.suggested_action,
            created_at=i.created_at
        )
        for i in issues
    ]
