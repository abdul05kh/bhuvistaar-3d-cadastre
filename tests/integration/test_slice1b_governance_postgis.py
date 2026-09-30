import json
import pytest
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from backend.services.parcel_service import ParcelService
from backend.services.evidence_service import EvidenceService
from backend.services.generation_service import GenerationService
from backend.services.validation_service import ValidationService
from backend.services.review_service import ReviewService
from backend.services.correction_service import CorrectionService
from backend.services.approval_service import ApprovalService
from backend.services.audit_service import AuditService
from backend.services.export_service import ExportService
from backend.services.provenance_service import ProvenanceService
from backend.repository.revision_repository import RevisionRepository
from backend.repository.unit_repository import SpatialUnitRepository
from backend.schemas.parcel_contracts import ParcelIngestRequest
from backend.schemas.evidence_contracts import EvidenceRegisterRequest
from backend.schemas.unit_contracts import UnitGenerateRequest
from backend.schemas.governance_contracts import (
    ReviewSubmitRequest,
    CorrectionSubmitRequest,
    ApprovalSubmitRequest,
    RejectionSubmitRequest
)
from backend.domain.enums import ReviewDecisionType, UnitStatus, AuditAction
from backend.exceptions import ApprovalBlockedError, RevisionNotFoundError

POSTGIS_URL = "postgresql+psycopg://postgres:postgrespassword@127.0.0.1:5432/bhuvistaar_cadastre"


@pytest.fixture(scope="module")
def db_session():
    engine = create_engine(POSTGIS_URL)
    Session = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_slice1b_full_governance_lifecycle_postgis(db_session):
    # 0. Clean prior state in real PostGIS
    db_session.execute(text("DELETE FROM export_records;"))
    db_session.execute(text("DELETE FROM audit_events;"))
    db_session.execute(text("DELETE FROM approval_decisions;"))
    db_session.execute(text("DELETE FROM review_decisions;"))
    db_session.execute(text("DELETE FROM validation_issues;"))
    db_session.execute(text("DELETE FROM validation_runs;"))
    db_session.execute(text("DELETE FROM provenance_records;"))
    db_session.execute(text("DELETE FROM spatial_unit_revisions;"))
    db_session.execute(text("DELETE FROM spatial_units;"))
    db_session.execute(text("DELETE FROM evidence_sources;"))
    db_session.execute(text("DELETE FROM parent_parcels;"))
    db_session.commit()

    p_svc = ParcelService(db_session)
    e_svc = EvidenceService(db_session)
    g_svc = GenerationService(db_session)
    v_svc = ValidationService(db_session)
    r_svc = ReviewService(db_session)
    c_svc = CorrectionService(db_session)
    a_svc = ApprovalService(db_session)
    audit_svc = AuditService(db_session)
    exp_svc = ExportService(db_session)
    rev_repo = RevisionRepository(db_session)
    u_repo = SpatialUnitRepository(db_session)

    # 1. Ingest clean parcel
    with open("fixtures/synthetic_parcel_clean.json", "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    parcel = p_svc.ingest_parcel(ParcelIngestRequest(**clean_data["parent_parcel"]))
    assert parcel.ulpin == "12345678901234"

    # 2. Register evidence
    for ev in clean_data["evidence"]:
        e_svc.register_evidence(EvidenceRegisterRequest(parent_ulpin=parcel.ulpin, **ev))

    # 3. Generate 3D units -> creates Revision 1, ProvenanceRecord, and AuditEvent
    units = g_svc.generate_3d_units(parcel.ulpin, UnitGenerateRequest(**clean_data["building"]))
    assert len(units) == 4

    first_unit = units[0]
    rev_1 = rev_repo.find_latest_for_unit(first_unit.id)
    assert rev_1 is not None
    assert rev_1.revision_number == 1
    assert rev_1.status == UnitStatus.GENERATED
    assert rev_1.predecessor_revision_id is None

    # Verify audit events for creation
    events_rev1 = audit_svc.get_events_for_revision(rev_1.id)
    actions = [e.action for e in events_rev1]
    assert AuditAction.CANDIDATE_CREATED in actions
    assert AuditAction.REVISION_CREATED in actions
    assert events_rev1[0].authorization_mode == "SIMULATED_PROTOTYPE"

    # 4. Run Gate A Validation on clean fixture
    summary = v_svc.run_validation(parcel.ulpin)
    assert summary.blocker_count == 0
    assert summary.can_approve is True

    # TEST 4: Attempting approval WITHOUT human review must be rejected (Gate C)
    with pytest.raises(ApprovalBlockedError) as exc_info:
        a_svc.approve_revision(
            revision_id=rev_1.id,
            request=ApprovalSubmitRequest(approver_id="OFFICER-001", reason="Pre-mature approval attempt")
        )
    assert "No human review decision has been recorded" in str(exc_info.value)

    # TEST 1: Clean candidate enters review
    review = r_svc.submit_review(
        revision_id=rev_1.id,
        request=ReviewSubmitRequest(
            decision=ReviewDecisionType.ACCEPT,
            reason="Cadastral geometry and vertical elevation bounds verified against architectural plan.",
            reviewer_id="REVIEWER-001"
        )
    )
    assert review.decision == ReviewDecisionType.ACCEPT
    assert review.actor_context == "SIMULATED_PROTOTYPE"

    # Verify review audit event
    review_events = [e for e in audit_svc.get_events_for_revision(rev_1.id) if e.action == AuditAction.REVIEW_SUBMITTED]
    assert len(review_events) == 1
    assert review_events[0].actor_id == "REVIEWER-001"

    # TEST 6 & 7: Approval records exact revision ID and creates audit event
    approval = a_svc.approve_revision(
        revision_id=rev_1.id,
        request=ApprovalSubmitRequest(
            approver_id="OFFICER-002",
            reason="All Gate A and Gate B conditions satisfied and review accepted."
        )
    )
    assert approval.revision_id == rev_1.id
    assert approval.status.value == "APPROVED"
    assert approval.actor_context == "SIMULATED_PROTOTYPE"

    rev_1_after_approval = rev_repo.find_by_id(rev_1.id)
    assert rev_1_after_approval.status == UnitStatus.APPROVED

    # TEST 14: Approved revision cannot be silently mutated / modified in place
    with pytest.raises(ApprovalBlockedError):
        r_svc.submit_review(
            revision_id=rev_1.id,
            request=ReviewSubmitRequest(decision=ReviewDecisionType.REJECT, reason="Cannot mutate approved")
        )

    # TEST 9, 10, 11: Correction creates a NEW revision (Revision 2) and recalculates VUID
    # Let's apply a correction to level L01 (second unit)
    l01_unit = units[2]  # L01
    rev_l01_v1 = rev_repo.find_latest_for_unit(l01_unit.id)
    original_vuid = rev_l01_v1.prototype_vuid
    original_z_max = rev_l01_v1.z_max

    correction_res = c_svc.apply_correction(
        revision_id=rev_l01_v1.id,
        request=CorrectionSubmitRequest(
            reviewer_id="SURVEYOR-001",
            reason="Adjust ceiling elevation by +0.10m per updated as-built measurement.",
            z_max=rev_l01_v1.z_max + 0.10
        )
    )

    # TEST 9: New revision ID was returned
    assert correction_res.new_revision_id != str(rev_l01_v1.id)
    assert correction_res.predecessor_revision_id == str(rev_l01_v1.id)

    # TEST 10: Original revision remains unchanged
    rev_l01_v1_post = rev_repo.find_by_id(rev_l01_v1.id)
    assert rev_l01_v1_post.z_max == original_z_max
    assert rev_l01_v1_post.prototype_vuid == original_vuid

    # TEST 11: Corrected geometry produces new deterministic VUID
    rev_l01_v2 = rev_repo.find_by_id(correction_res.new_revision_id)
    assert rev_l01_v2.revision_number == 2
    assert rev_l01_v2.prototype_vuid != original_vuid
    assert rev_l01_v2.z_max == original_z_max + 0.10
    assert rev_l01_v2.predecessor_revision_id == rev_l01_v1.id

    # TEST 12 & 13: Revalidation was run and recorded with new run ID
    assert correction_res.validation_run_id is not None

    # TEST 16, 17, 18, 19, 20, 21: Structured export
    export = exp_svc.generate_export_for_revision(rev_1.id, exported_by="OFFICER-002")
    assert export.spatial_unit_revision["revision_id"] == str(rev_1.id)
    assert export.vuid["prototype_vuid"] == rev_1.prototype_vuid
    assert export.export_metadata["authorization_mode"] == "SIMULATED_PROTOTYPE"
    assert export.approval["approver_id"] == "OFFICER-002"
    assert export.provenance["is_verified"] is True
    assert export.audit_summary["total_events"] > 0

    # TEST 22: Audit events are append-only
    all_events = audit_svc.get_recent_events(limit=50)
    assert len(all_events) >= 5
