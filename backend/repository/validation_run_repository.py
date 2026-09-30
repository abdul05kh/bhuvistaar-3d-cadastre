from typing import Optional
from uuid import UUID
from sqlalchemy.orm import Session
from backend.db.models import ValidationRunModel
from backend.domain.validation_run import ValidationRun
from backend.domain.enums import GateType


class ValidationRunRepository:
    def __init__(self, db: Session):
        self.db = db

    def save(self, run: ValidationRun) -> ValidationRun:
        if not hasattr(self.db, "add"):
            return run
        model = ValidationRunModel(
            id=run.id,
            parent_ulpin=run.parent_ulpin,
            unit_id=run.unit_id,
            revision_id=run.revision_id,
            gate=run.gate.value,
            validator_version=run.validator_version,
            rules_evaluated=run.rules_evaluated,
            passed_rules=run.passed_rules,
            failed_rules=run.failed_rules,
            blocker_count=run.blocker_count,
            error_count=run.error_count,
            warning_count=run.warning_count,
            can_approve=run.can_approve,
            created_at=run.created_at
        )
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._to_domain(model)

    def find_by_id(self, run_id: UUID) -> Optional[ValidationRun]:
        model = self.db.query(ValidationRunModel).filter_by(id=run_id).first()
        if not model:
            return None
        return self._to_domain(model)

    def find_latest_for_revision(self, revision_id: UUID, gate: Optional[GateType] = None) -> Optional[ValidationRun]:
        query = self.db.query(ValidationRunModel).filter_by(revision_id=revision_id)
        if gate:
            query = query.filter_by(gate=gate.value)
        model = query.order_by(ValidationRunModel.created_at.desc()).first()
        if not model:
            return None
        return self._to_domain(model)

    def find_latest_for_parcel(self, ulpin: str, gate: Optional[GateType] = None) -> Optional[ValidationRun]:
        query = self.db.query(ValidationRunModel).filter_by(parent_ulpin=ulpin)
        if gate:
            query = query.filter_by(gate=gate.value)
        model = query.order_by(ValidationRunModel.created_at.desc()).first()
        if not model:
            return None
        return self._to_domain(model)

    def _to_domain(self, model: ValidationRunModel) -> ValidationRun:
        return ValidationRun(
            id=model.id,
            parent_ulpin=model.parent_ulpin,
            unit_id=model.unit_id,
            revision_id=model.revision_id,
            gate=GateType(model.gate),
            validator_version=model.validator_version,
            rules_evaluated=model.rules_evaluated,
            passed_rules=model.passed_rules,
            failed_rules=model.failed_rules,
            blocker_count=model.blocker_count,
            error_count=model.error_count,
            warning_count=model.warning_count,
            can_approve=model.can_approve,
            created_at=model.created_at
        )
