"""
Slice 5 Operational, Interoperability, and Reliability Unit Tests.
Co-authored-by: Abdul Khader <abdulkhader.work@gmail.com>
Co-authored-by: S S Shriram <ssshriram06@gmail.com>
Co-authored-by: Varun H <varunh.contact@gmail.com>
Co-authored-by: Rohan G <rohan.g.contact@gmail.com>
Co-authored-by: Rithvik Shenoy <rithvikshenoy@gmail.com>
Co-authored-by: Samarth H Naik <samarthhnaik@gmail.com>
"""

import pytest
import hashlib
from datetime import datetime, timezone, timedelta
from uuid import uuid4
from backend.config import settings
from backend.domain.enums import EvidenceQuality, OperationalRole, SyncStatus, ApprovalStatus
from backend.schemas.evidence_contracts import EvidenceRegisterRequest
from backend.services.evidence_service import EvidenceService
from backend.services.approval_service import ApprovalService
from backend.services.interoperability_service import InteroperabilityService
from backend.db.bootstrap import verify_data_integrity
from backend.exceptions import DuplicateEvidenceError, EvidenceConflictError, StaleEvidenceError, StaleValidationError
from backend.db.session import SessionLocal
from backend.db.models import ParentParcelModel, SpatialUnitModel, SpatialUnitRevisionModel, EvidenceSourceModel, ValidationRunModel


def test_config_safe_defaults():
    """Verify configuration safe defaults for operational deployment."""
    assert settings.AUTH_MODE == "SIMULATED_PROTOTYPE"
    assert settings.AUTHORIZATION_MODE == "SIMULATED_PROTOTYPE"
    assert settings.DEMO_MODE is True
    assert settings.AI_MODE in ("LOCAL", "DETERMINISTIC", "DISABLED")
    assert settings.LOG_LEVEL in ("DEBUG", "INFO", "WARNING", "ERROR")
    assert settings.RULESET_VERSION == "1.0.0"
    assert settings.VALIDATOR_VERSION == "1.0.0"
    assert settings.MAX_UPLOAD_SIZE_BYTES > 0
    assert settings.STALE_THRESHOLD_SECONDS > 0


def test_evidence_quality_gate_checks():
    """Verify evidence quality evaluation for valid, invalid, and missing payloads."""
    service = EvidenceService()

    # 1. Invalid checksum (64 chars but non-hex) and empty provider
    req_blocked = EvidenceRegisterRequest(
        id="EVID-BLOCKED-01",
        parent_ulpin="12345678901234",
        evidence_type="FLOOR_PLAN",
        provider="   ",  # whitespace only
        source_reference="plan.dwg",
        checksum="Z" * 64,  # invalid hex
        crs="EPSG:32643"
    )
    res_blocked = service.evaluate_quality(req_blocked)
    assert res_blocked.status == EvidenceQuality.BLOCKED.value
    assert len(res_blocked.blockers) > 0

    # 2. Unprojected geographic CRS
    req_unprojected = EvidenceRegisterRequest(
        id="EVID-TEST-WGS84",
        parent_ulpin="12345678901234",
        evidence_type="SURVEY_MEASUREMENT",
        provider="Survey Team",
        source_reference="survey.dxf",
        checksum=hashlib.sha256(b"dummy").hexdigest(),
        crs="EPSG:4326"
    )
    res_unprojected = service.evaluate_quality(req_unprojected)
    assert res_unprojected.status == EvidenceQuality.WARNING.value
    assert any("geographic" in w.lower() for w in res_unprojected.warnings)

    # 3. Valid projected survey evidence
    req_valid = EvidenceRegisterRequest(
        id="EVID-TEST-VALID-01",
        parent_ulpin="12345678901234",
        evidence_type="SURVEY_MEASUREMENT",
        provider="Survey Department",
        source_reference="survey_clean.dxf",
        checksum=hashlib.sha256(b"valid_payload_bytes").hexdigest(),
        crs="EPSG:32643"
    )
    res_valid = service.evaluate_quality(req_valid)
    assert res_valid.status == EvidenceQuality.ACCEPTED.value
    assert len(res_valid.blockers) == 0


def test_duplicate_evidence_detection():
    """Verify that uploading duplicate evidence with the same SHA-256 is detected."""
    db = SessionLocal()
    service = EvidenceService(db=db)
    ulpin = "12345678901234"
    dummy_checksum = hashlib.sha256(f"UNIQUE_SURVEY_PAYLOAD_{uuid4()}".encode()).hexdigest()

    try:
        # Ingest first time
        req1 = EvidenceRegisterRequest(
            id=f"EVID-DUP-ORIG-{uuid4().hex[:6]}",
            parent_ulpin=ulpin,
            evidence_type="SURVEY_MEASUREMENT",
            provider="Survey Team A",
            source_reference="survey_alpha.dxf",
            checksum=dummy_checksum,
            crs="EPSG:32643"
        )
        ev1 = service.register_evidence(req1)
        assert ev1.id == req1.id

        # Attempt to ingest duplicate with different ID
        req2 = EvidenceRegisterRequest(
            id=f"EVID-DUP-COPY-{uuid4().hex[:6]}",
            parent_ulpin=ulpin,
            evidence_type="SURVEY_MEASUREMENT",
            provider="Survey Team B",
            source_reference="survey_alpha_copy.dxf",
            checksum=dummy_checksum,
            crs="EPSG:32643"
        )
        with pytest.raises(DuplicateEvidenceError) as exc_info:
            service.register_evidence(req2)
        assert exc_info.value.original_id == ev1.id
        assert "Duplicate evidence detected" in str(exc_info.value)
    finally:
        db.rollback()
        db.close()


def test_conflicting_evidence_detection():
    """Verify detection of conflicting vertical measurements for the same level."""
    db = SessionLocal()
    service = EvidenceService(db=db)
    ulpin = "12345678901234"

    try:
        # Register Evidence A: Elevation = 106.0m
        req_a = EvidenceRegisterRequest(
            id=f"EVID-CONF-A-{uuid4().hex[:6]}",
            parent_ulpin=ulpin,
            evidence_type="FLOOR_PLAN",
            provider="Architectural Bureau",
            source_reference="arch_plan_106_0.dwg",
            checksum=hashlib.sha256(f"PAYLOAD_A_{uuid4()}".encode()).hexdigest(),
            crs="EPSG:32643",
            metadata={"level_code": "L01", "elevation": 106.0}
        )
        service.register_evidence(req_a)

        # Register Evidence B: Elevation = 106.5m (conflicting)
        req_b = EvidenceRegisterRequest(
            id=f"EVID-CONF-B-{uuid4().hex[:6]}",
            parent_ulpin=ulpin,
            evidence_type="SURVEY_MEASUREMENT",
            provider="Field Survey Team",
            source_reference="field_elev_106_5.txt",
            checksum=hashlib.sha256(f"PAYLOAD_B_{uuid4()}".encode()).hexdigest(),
            crs="EPSG:32643",
            metadata={"level_code": "L01", "elevation": 106.5}
        )
        service.register_evidence(req_b)

        conflicts = service.detect_evidence_conflicts(ulpin)
        assert len(conflicts) >= 1
        l01_conflicts = [c for c in conflicts if c.level_code == "L01"]
        assert len(l01_conflicts) >= 1
        delta = abs(float(l01_conflicts[0].source_a_value) - float(l01_conflicts[0].source_b_value))
        assert delta == 0.5
        assert "PENDING" in l01_conflicts[0].resolution_status
    finally:
        db.rollback()
        db.close()


def test_stale_validation_detection():
    """Verify that an outdated validation result prevents Gate C approval."""
    db = SessionLocal()
    approval_service = ApprovalService(db=db)

    try:
        rev = db.query(SpatialUnitRevisionModel).first()
        if rev:
            # Create a validation run older than the revision
            val = ValidationRunModel(
                id=uuid4(),
                parent_ulpin=rev.parent_ulpin,
                revision_id=rev.id,
                gate="GATE_A",
                validator_version="1.0.0",
                rules_evaluated=5,
                passed_rules=5,
                failed_rules=0,
                blocker_count=0,
                error_count=0,
                warning_count=0,
                can_approve=True,
                created_at=rev.created_at - timedelta(hours=2)
            )
            db.add(val)
            db.commit()

            is_eligible, reasons = approval_service.evaluate_gate_c_eligibility(rev.id)
            assert is_eligible is False
            assert any("VALIDATION_OUTDATED" in r for r in reasons)
    finally:
        db.rollback()
        db.close()


def test_non_destructive_data_integrity_check():
    """Verify that verify_data_integrity performs audit checks without altering data."""
    db = SessionLocal()
    try:
        report = verify_data_integrity(db)
        assert report["status"] in ("PASS", "WARNING", "BLOCKER")
        assert "summary" in report
        assert "checks_performed" in report["summary"]
        assert "ORPHAN_SPATIAL_UNIT" in report["summary"]["checks_performed"]
        assert "MISSING_PROVENANCE" in report["summary"]["checks_performed"]
        assert "STALE_VALIDATION" in report["summary"]["checks_performed"]
    finally:
        db.close()


def test_interoperability_geojson_export():
    """Verify standard 2D/3D GeoJSON export preserving volumetric metadata."""
    db = SessionLocal()
    interop_service = InteroperabilityService(db=db)
    try:
        parcel = db.query(ParentParcelModel).first()
        if parcel:
            geojson_data = interop_service.export_geojson(parcel.ulpin)
            assert geojson_data["type"] == "FeatureCollection"
            assert "crs" in geojson_data
            assert "Prototype VUID is NOT an official 3D ULPIN" in geojson_data["disclaimer"]
            assert "features" in geojson_data
    finally:
        db.close()


def test_interoperability_obj_export():
    """Verify 3D Wavefront OBJ export format."""
    db = SessionLocal()
    interop_service = InteroperabilityService(db=db)
    try:
        rev = db.query(SpatialUnitRevisionModel).first()
        if rev:
            obj_text = interop_service.export_3d_obj(rev.id)
            assert "# OBJ Export" in obj_text or "o " in obj_text
            assert "v " in obj_text
            assert "f " in obj_text
    finally:
        db.close()


def test_interoperability_round_trip_verification():
    """Verify complete import-export round trip verification."""
    db = SessionLocal()
    interop_service = InteroperabilityService(db=db)
    try:
        rev = db.query(SpatialUnitRevisionModel).first()
        if rev:
            resp = interop_service.export_service.generate_export_for_revision(rev.id)
            pkg = resp.model_dump()
            result = interop_service.verify_round_trip(pkg)
            assert "verified" in result
            assert result["verified"] is True
            assert result["vuid_match"] is True
            assert result["checksum_match"] is True
    finally:
        db.close()
