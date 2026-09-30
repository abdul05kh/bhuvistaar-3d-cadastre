"""Validation Disagreement Schemas (Slice 4)."""
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field
from backend.domain.enums import DisagreementType


class DisagreementRecord(BaseModel):
    disagreement_id: str
    parent_ulpin: str
    candidate_id: Optional[str] = None
    level_code: Optional[str] = None
    disagreement_type: DisagreementType
    severity: str
    ai_confidence: float
    validation_status: str
    human_decision: Optional[str] = None
    rule_codes: list[str] = Field(default_factory=list)
    explanation: str
    measured_values: Optional[dict[str, Any]] = None
    thresholds: Optional[dict[str, Any]] = None
    model: dict[str, str] = Field(default_factory=dict)
    ruleset_version: str = "1.0.0"
    created_at: Optional[datetime] = None


class DisagreementListResponse(BaseModel):
    parent_ulpin: str
    total_disagreements: int
    blocker_count: int
    warning_count: int
    consistent_count: int
    disagreements: list[DisagreementRecord]
