"""Validation Disagreement Engine (Slice 4).

Explicitly detects and categorizes tensions between:
- AI confidence and proposals
- Deterministic geometric/topological validation rules
- Human review decisions
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy.orm import Session

from backend.db.models import (
    AICandidateModel,
    ValidationRunModel,
    ValidationIssueModel,
    ValidationDisagreementModel,
    SpatialUnitModel,
    ParentParcelModel
)
from backend.domain.enums import DisagreementType, AuditAction
from backend.ai.schemas.disagreement import DisagreementRecord, DisagreementListResponse
from backend.services.audit_service import AuditService


class ValidationDisagreementEngine:
    def __init__(self, db: Session):
        self.db = db
        self.audit_service = AuditService(db)

    def analyze_disagreements(self, parent_ulpin: str, actor_id: str = "system") -> DisagreementListResponse:
        """Analyzes all candidates and validation issues for a parcel and catalogs disagreements."""
        candidates = self.db.query(AICandidateModel).filter(
            AICandidateModel.parent_ulpin == parent_ulpin
        ).all()

        # Get latest validation run for the parcel
        val_run = self.db.query(ValidationRunModel).filter(
            ValidationRunModel.parent_ulpin == parent_ulpin
        ).order_by(ValidationRunModel.created_at.desc()).first()

        issues = []
        if val_run:
            issues = self.db.query(ValidationIssueModel).filter(
                ValidationIssueModel.run_id == val_run.id
            ).all()

        units = self.db.query(SpatialUnitModel).filter(
            SpatialUnitModel.parent_ulpin == parent_ulpin
        ).all()
        unit_map = {u.level_code: u for u in units}

        # Clear previous disagreements for this parcel to keep fresh
        self.db.query(ValidationDisagreementModel).filter(
            ValidationDisagreementModel.parent_ulpin == parent_ulpin
        ).delete()
        self.db.commit()

        disagreements: list[DisagreementRecord] = []
        blocker_count = 0
        warning_count = 0
        consistent_count = 0

        for cand in candidates:
            # Match spatial unit
            unit = unit_map.get(cand.level_code)
            unit_vuid = unit.prototype_vuid if unit else None

            # Collect issues relevant to this candidate / unit
            cand_issues = [
                iss for iss in issues
                if (iss.object_id == cand.candidate_id or
                    (unit_vuid and iss.object_id == unit_vuid) or
                    cand.level_code in (iss.message or "") or
                    (iss.measured_value and isinstance(iss.measured_value, dict) and
                     cand.level_code in (iss.measured_value.get("lower_level", ""), iss.measured_value.get("upper_level", ""))))
            ]

            blockers = [iss for iss in cand_issues if iss.severity == "BLOCKER" and not iss.passed]
            ai_conf = float(cand.confidence)

            # 1. Check CASE D: Human Override
            if cand.status == "REJECTED" or cand.rejection_reason:
                d_id = f"DISAGREE-HUMAN-{cand.candidate_id}"
                expl = (
                    f"Human reviewer rejected proposal for '{cand.level_code}' "
                    f"despite {ai_conf:.2f} ({cand.confidence_band}) AI confidence. "
                    f"Rationale: {cand.rejection_reason or 'Reviewer discretion'}."
                )
                rec = DisagreementRecord(
                    disagreement_id=d_id,
                    parent_ulpin=parent_ulpin,
                    candidate_id=cand.candidate_id,
                    level_code=cand.level_code,
                    disagreement_type=DisagreementType.HUMAN_OVERRIDE_OF_AI_PROPOSAL,
                    severity="WARNING",
                    ai_confidence=ai_conf,
                    validation_status="BLOCKER" if blockers else "PASS",
                    human_decision="REJECTED",
                    rule_codes=[b.rule_code for b in blockers],
                    explanation=expl,
                    measured_values={"confidence": ai_conf, "rejection_reason": cand.rejection_reason},
                    thresholds={"confidence_band": cand.confidence_band},
                    model={"name": cand.model_name, "version": cand.model_version},
                    ruleset_version="1.0.0",
                    created_at=datetime.now(timezone.utc)
                )
                disagreements.append(rec)
                warning_count += 1
                self._persist_disagreement(rec)
                continue

            # 2. Check CASE A: AI / Validation Disagreement (AI proposed with confidence >= 0.60, but validation blocked)
            if len(blockers) > 0 and ai_conf >= 0.60:
                d_id = f"DISAGREE-VAL-{cand.candidate_id}"
                rule_names = ", ".join(sorted(list({b.rule_code for b in blockers})))
                blocker_details = blockers[0].message if blockers else "Validation failed"
                expl = (
                    f"AI proposed '{cand.level_code}' with {ai_conf:.2f} ({cand.confidence_band}) confidence "
                    f"as likely valid, but deterministic validation identified blocker(s) [{rule_names}]: {blocker_details}. "
                    f"The proposal cannot enter governed approval without human correction."
                )
                rec = DisagreementRecord(
                    disagreement_id=d_id,
                    parent_ulpin=parent_ulpin,
                    candidate_id=cand.candidate_id,
                    level_code=cand.level_code,
                    disagreement_type=DisagreementType.AI_VALIDATION_DISAGREEMENT,
                    severity="BLOCKER",
                    ai_confidence=ai_conf,
                    validation_status="BLOCKER",
                    human_decision="PENDING",
                    rule_codes=[b.rule_code for b in blockers],
                    explanation=expl,
                    measured_values=blockers[0].measured_value if blockers else None,
                    thresholds=blockers[0].threshold if blockers else None,
                    model={"name": cand.model_name, "version": cand.model_version},
                    ruleset_version="1.0.0",
                    created_at=datetime.now(timezone.utc)
                )
                disagreements.append(rec)
                blocker_count += 1
                self._persist_disagreement(rec)

                # Log audit event
                self.audit_service.log_event(
                    action=AuditAction.AI_VALIDATION_DISAGREEMENT,
                    entity_type="AI_CANDIDATE",
                    entity_id=cand.candidate_id,
                    actor_id=actor_id,
                    reason=expl,
                    metadata={
                        "candidate_id": cand.candidate_id,
                        "level_code": cand.level_code,
                        "ai_confidence": ai_conf,
                        "rule_codes": [b.rule_code for b in blockers]
                    }
                )
                continue

            # 3. Check CASE B: Low AI Confidence / Geometrically Valid
            if ai_conf < 0.60 and len(blockers) == 0:
                d_id = f"DISAGREE-LOWCONF-{cand.candidate_id}"
                expl = (
                    f"AI assigned low confidence ({ai_conf:.2f}) to '{cand.level_code}' due to weak "
                    f"or incomplete evidence, but deterministic spatial validation verified geometry "
                    f"and vertical topology with 0 blockers."
                )
                rec = DisagreementRecord(
                    disagreement_id=d_id,
                    parent_ulpin=parent_ulpin,
                    candidate_id=cand.candidate_id,
                    level_code=cand.level_code,
                    disagreement_type=DisagreementType.LOW_AI_CONFIDENCE_GEOMETRICALLY_VALID,
                    severity="WARNING",
                    ai_confidence=ai_conf,
                    validation_status="PASS",
                    human_decision="PENDING",
                    rule_codes=[],
                    explanation=expl,
                    measured_values={"confidence": ai_conf},
                    thresholds={"low_threshold": 0.60},
                    model={"name": cand.model_name, "version": cand.model_version},
                    ruleset_version="1.0.0",
                    created_at=datetime.now(timezone.utc)
                )
                disagreements.append(rec)
                warning_count += 1
                self._persist_disagreement(rec)
                continue

            # 4. Check CASE C: Consistent
            d_id = f"AGREE-{cand.candidate_id}"
            expl = (
                f"AI proposal for '{cand.level_code}' ({ai_conf:.2f} confidence) is "
                f"geometrically and topologically consistent with deterministic validation rules."
            )
            rec = DisagreementRecord(
                disagreement_id=d_id,
                parent_ulpin=parent_ulpin,
                candidate_id=cand.candidate_id,
                level_code=cand.level_code,
                disagreement_type=DisagreementType.CONSISTENT,
                severity="INFO",
                ai_confidence=ai_conf,
                validation_status="PASS",
                human_decision="PENDING" if cand.status == "AI_CANDIDATE" else cand.status,
                rule_codes=[],
                explanation=expl,
                measured_values={"confidence": ai_conf},
                thresholds=None,
                model={"name": cand.model_name, "version": cand.model_version},
                ruleset_version="1.0.0",
                created_at=datetime.now(timezone.utc)
            )
            disagreements.append(rec)
            consistent_count += 1
            self._persist_disagreement(rec)

        return DisagreementListResponse(
            parent_ulpin=parent_ulpin,
            total_disagreements=len(disagreements),
            blocker_count=blocker_count,
            warning_count=warning_count,
            consistent_count=consistent_count,
            disagreements=disagreements
        )

    def _persist_disagreement(self, rec: DisagreementRecord) -> None:
        db_model = ValidationDisagreementModel(
            disagreement_id=rec.disagreement_id,
            parent_ulpin=rec.parent_ulpin,
            candidate_id=rec.candidate_id,
            disagreement_type=rec.disagreement_type.value,
            severity=rec.severity,
            ai_confidence=rec.ai_confidence,
            validation_status=rec.validation_status,
            human_decision=rec.human_decision,
            rule_codes=rec.rule_codes,
            explanation=rec.explanation,
            measured_values=rec.measured_values,
            thresholds=rec.thresholds,
            model_name=rec.model.get("name", "unknown"),
            model_version=rec.model.get("version", "1.0.0"),
            ruleset_version=rec.ruleset_version,
            created_at=rec.created_at or datetime.now(timezone.utc)
        )
        self.db.add(db_model)
        self.db.commit()
