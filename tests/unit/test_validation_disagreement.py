"""Unit tests for Validation Disagreement Engine (Slice 4)."""
import pytest
from unittest.mock import MagicMock
from backend.domain.enums import DisagreementType
from backend.ai.services.disagreement_engine import ValidationDisagreementEngine
from backend.ai.schemas.disagreement import DisagreementRecord


def test_disagreement_detection_case_a_blocker():
    """CASE A: AI proposes with high confidence, but deterministic validation detects BLOCKER."""
    mock_db = MagicMock()

    # Mock candidate L02 with 0.91 confidence
    cand = MagicMock()
    cand.candidate_id = "CAND-L02-001"
    cand.parent_ulpin = "12345678901234"
    cand.level_code = "L02"
    cand.confidence = 0.91
    cand.confidence_band = "HIGH"
    cand.status = "AI_CANDIDATE"
    cand.source_evidence_ids = ["EVID-003"]
    cand.reason_codes = ["FOOTPRINT_MATCH"]
    cand.model_name = "prismatic-candidate-001"
    cand.model_version = "0.1.0"
    cand.rejection_reason = None

    # Mock validation run and VRT-003 blocker issue
    val_run = MagicMock()
    val_run.id = "RUN-001"

    issue = MagicMock()
    issue.rule_code = "VRT-003"
    issue.severity = "BLOCKER"
    issue.object_id = "BV-12345678901234-SPATIAL_UNIT-L02-123"
    issue.passed = False
    issue.message = "Vertical overlap conflict between level 'L01' and level 'L02'"
    issue.measured_value = {"gap_m": -0.50, "overlap_m": 0.50, "lower_level": "L01", "upper_level": "L02"}
    issue.threshold = {"min_gap_m": -0.001}

    unit = MagicMock()
    unit.level_code = "L02"
    unit.prototype_vuid = "BV-12345678901234-SPATIAL_UNIT-L02-123"

    mock_db.query.return_value.filter.return_value.all.side_effect = [
        [cand],       # candidates
        [issue],      # issues
        [unit]        # units
    ]
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = val_run

    engine = ValidationDisagreementEngine(mock_db)
    result = engine.analyze_disagreements("12345678901234")

    assert result.total_disagreements == 1
    assert result.blocker_count == 1
    dis = result.disagreements[0]
    assert dis.disagreement_type == DisagreementType.AI_VALIDATION_DISAGREEMENT
    assert dis.severity == "BLOCKER"
    assert "VRT-003" in dis.rule_codes
    assert "cannot enter governed approval" in dis.explanation


def test_disagreement_detection_case_d_human_override():
    """CASE D: Human reviewer rejects a high-confidence proposal."""
    mock_db = MagicMock()

    cand = MagicMock()
    cand.candidate_id = "CAND-L02-002"
    cand.parent_ulpin = "12345678901234"
    cand.level_code = "L02"
    cand.confidence = 0.94
    cand.confidence_band = "HIGH"
    cand.status = "REJECTED"
    cand.source_evidence_ids = ["EVID-003"]
    cand.reason_codes = ["FOOTPRINT_MATCH"]
    cand.model_name = "prismatic-candidate-001"
    cand.model_version = "0.1.0"
    cand.rejection_reason = "Field deed indicates attic void, not independent floor boundary."

    mock_db.query.return_value.filter.return_value.all.side_effect = [
        [cand],
        [],
        []
    ]
    mock_db.query.return_value.filter.return_value.order_by.return_value.first.return_value = None

    engine = ValidationDisagreementEngine(mock_db)
    result = engine.analyze_disagreements("12345678901234")

    assert result.total_disagreements == 1
    assert result.warning_count == 1
    dis = result.disagreements[0]
    assert dis.disagreement_type == DisagreementType.HUMAN_OVERRIDE_OF_AI_PROPOSAL
    assert dis.human_decision == "REJECTED"
    assert "rejected proposal" in dis.explanation
