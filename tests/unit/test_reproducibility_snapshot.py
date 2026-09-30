"""Unit tests for Reproducibility Service (Slice 4)."""
import pytest
from unittest.mock import MagicMock
from backend.domain.enums import ReproducibilityStatus
from backend.ai.services.reproducibility_service import ReproducibilityService


def test_reproducibility_snapshot_generation():
    """Verifies cryptographic reproducibility snapshot calculation and status."""
    mock_db = MagicMock()

    cand = MagicMock()
    cand.candidate_id = "CAND-001"
    cand.parent_ulpin = "12345678901234"
    cand.level_code = "L01"
    cand.footprint_geojson = {"type": "Polygon", "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]}
    cand.model_name = "prismatic-candidate-001"
    cand.model_version = "0.1.0"
    cand.governed_revision_id = None
    cand.source_evidence_ids = ["EVID-001"]

    ev = MagicMock()
    ev.id = "EVID-001"
    ev.checksum = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    mock_db.query.return_value.filter.return_value.first.side_effect = [
        cand,  # candidate
        None   # existing snapshot
    ]
    mock_db.query.return_value.filter.return_value.all.return_value = [ev]

    service = ReproducibilityService(mock_db)
    snap = service.generate_snapshot(target_id="CAND-001")

    assert snap.reproducibility_status == ReproducibilityStatus.REPRODUCIBLE
    assert snap.can_reproduce is True
    assert snap.snapshot_hash is not None
    assert len(snap.snapshot_hash) == 64
    assert snap.software_commit == "ab35dd2"
    assert snap.validation_ruleset_version == "1.0.0"
    assert snap.verification_report["evidence_checksums_pinned"] is True
