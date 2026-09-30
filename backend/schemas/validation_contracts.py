from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field


class ValidationRunRequest(BaseModel):
    ulpin: str = Field(..., pattern=r"^[0-9]{14}$", description="Parent ULPIN to validate")


class ValidationIssueResponse(BaseModel):
    id: str
    run_id: str
    rule_code: str
    severity: str
    object_type: str
    object_id: str
    passed: bool
    message: str
    measured_value: Optional[dict[str, Any]] = None
    threshold: Optional[dict[str, Any]] = None
    suggested_action: Optional[str] = None
    created_at: datetime


class ValidationSummaryResponse(BaseModel):
    run_id: str
    ulpin: str
    timestamp: datetime
    rules_evaluated: int
    passed_rules: int
    failed_rules: int
    blocker_count: int
    error_count: int
    warning_count: int
    can_approve: bool
    issues: list[ValidationIssueResponse]
