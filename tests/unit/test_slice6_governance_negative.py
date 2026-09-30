"""
Slice 6 Governance Negative Tests and Data Integrity Verification.
Proves that under no circumstances can an invalid, unreviewed, or unauthorized
state bypass the BhuVistaar trust chain.

Co-authored-by: Mohammad Abdul Kalam Hussain <abdul05kh.college@gmail.com>
Co-authored-by: Siri Chandana <kotagirisirichandana73@gmail.com>
Co-authored-by: Mohammad Zakiruddin <zakirmd.1805@gmail.com>
Co-authored-by: Mohammed Numan <mohammednumaan901@gmail.com>
Co-authored-by: Manivarun Chintala <manivarunchintala2005.2728@gmail.com>
Co-authored-by: Thaniska <ramatenkithanishka@gmail.com>
"""

import pytest
from uuid import uuid4
from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

from backend.domain.enums import UnitStatus, ApprovalStatus, ReviewDecisionType
from backend.services.approval_service import ApprovalService
from backend.schemas.governance_contracts import ApprovalSubmitRequest
from backend.exceptions import ApprovalBlockedError
from backend.db.bootstrap import verify_data_integrity


def test_ai_autonomous_approval_blocked():
    """Verify Section 34: Autonomous AI cannot grant Gate C approval."""
    db = MagicMock()
    service = ApprovalService(db)
    
    rev_id = uuid4()
    req = ApprovalSubmitRequest(
        approver_id="AI-AGENT-001",
        reason="Autonomous approval attempted by machine model",
        actor_context="AI_AUTONOMOUS",
    )
    
    with pytest.raises(ApprovalBlockedError) as exc_info:
        service.approve_revision(rev_id, req)
    
    assert "AI IS NOT THE AUTHORITY" in str(exc_info.value)


def test_viewer_role_approval_blocked():
    """Verify Section 34: Viewer role cannot grant Gate C approval."""
    db = MagicMock()
    service = ApprovalService(db)
    
    rev_id = uuid4()
    req = ApprovalSubmitRequest(
        approver_id="USER-VIEWER",
        reason="Viewer attempting to approve",
        role="VIEWER"
    )
    
    with pytest.raises(ApprovalBlockedError) as exc_info:
        service.approve_revision(rev_id, req)
    
    assert "Unauthorized role" in str(exc_info.value)
    assert "VIEWER" in str(exc_info.value)


def test_unreviewed_revision_approval_blocked():
    """Verify Section 34: Revision with no recorded human review cannot be approved."""
    db = MagicMock()
    service = ApprovalService(db)
    
    rev_id = uuid4()
    mock_rev = MagicMock()
    mock_rev.id = rev_id
    mock_rev.status = UnitStatus.VALIDATED
    mock_rev.created_at = datetime.now(timezone.utc)
    mock_rev.parent_ulpin = "12345678901234"
    service.revision_repo.find_by_id = MagicMock(return_value=mock_rev)
    
    # Valid validation
    mock_val = MagicMock()
    mock_val.blocker_count = 0
    mock_val.can_approve = True
    mock_val.created_at = datetime.now(timezone.utc) + timedelta(seconds=10)
    service.val_run_repo.find_latest_for_revision = MagicMock(return_value=mock_val)
    
    # Valid provenance
    mock_prov = MagicMock()
    mock_prov.evidence_sources = [{"id": "ev-1", "checksum": "abc12345"}]
    mock_prov.is_verified = True
    service.prov_repo.find_by_revision_id = MagicMock(return_value=mock_prov)
    
    # NO review
    service.review_repo.find_latest_for_revision = MagicMock(return_value=None)
    
    req = ApprovalSubmitRequest(approver_id="OFFICER-001", reason="Pre-review attempt")
    with pytest.raises(ApprovalBlockedError) as exc_info:
        service.approve_revision(rev_id, req)
    
    assert "No human review decision has been recorded" in str(exc_info.value)


def test_blocker_validation_approval_blocked():
    """Verify Section 34: Unresolved BLOCKER issues block Gate C approval."""
    db = MagicMock()
    service = ApprovalService(db)
    
    rev_id = uuid4()
    mock_rev = MagicMock()
    mock_rev.id = rev_id
    mock_rev.status = UnitStatus.UNDER_REVIEW
    mock_rev.created_at = datetime.now(timezone.utc)
    mock_rev.parent_ulpin = "12345678901234"
    service.revision_repo.find_by_id = MagicMock(return_value=mock_rev)
    
    # Validation with blockers
    mock_val = MagicMock()
    mock_val.blocker_count = 1
    mock_val.can_approve = False
    mock_val.created_at = datetime.now(timezone.utc)
    service.val_run_repo.find_latest_for_revision = MagicMock(return_value=mock_val)
    
    mock_prov = MagicMock()
    mock_prov.evidence_sources = [{"id": "ev-1", "checksum": "abc12345"}]
    mock_prov.is_verified = True
    service.prov_repo.find_by_revision_id = MagicMock(return_value=mock_prov)
    
    mock_review = MagicMock()
    mock_review.decision = ReviewDecisionType.ACCEPT
    service.review_repo.find_latest_for_revision = MagicMock(return_value=mock_review)
    
    req = ApprovalSubmitRequest(approver_id="OFFICER-001", reason="Attempt with blockers")
    with pytest.raises(ApprovalBlockedError) as exc_info:
        service.approve_revision(rev_id, req)
    
    assert "Unresolved BLOCKER validation issues exist" in str(exc_info.value)


def test_stale_validation_approval_blocked():
    """Verify Section 34: Validation predating revision modification is marked stale."""
    db = MagicMock()
    service = ApprovalService(db)
    
    rev_id = uuid4()
    mock_rev = MagicMock()
    mock_rev.id = rev_id
    mock_rev.status = UnitStatus.UNDER_REVIEW
    mock_rev.created_at = datetime.now(timezone.utc)  # Revision created NOW
    mock_rev.parent_ulpin = "12345678901234"
    service.revision_repo.find_by_id = MagicMock(return_value=mock_rev)
    
    # Validation was run 10 minutes BEFORE the revision was updated
    mock_val = MagicMock()
    mock_val.id = uuid4()
    mock_val.blocker_count = 0
    mock_val.can_approve = True
    mock_val.created_at = datetime.now(timezone.utc) - timedelta(minutes=10)
    service.val_run_repo.find_latest_for_revision = MagicMock(return_value=mock_val)
    
    mock_prov = MagicMock()
    mock_prov.evidence_sources = [{"id": "ev-1", "checksum": "abc12345"}]
    mock_prov.is_verified = True
    service.prov_repo.find_by_revision_id = MagicMock(return_value=mock_prov)
    
    mock_review = MagicMock()
    mock_review.decision = ReviewDecisionType.ACCEPT
    service.review_repo.find_latest_for_revision = MagicMock(return_value=mock_review)
    
    req = ApprovalSubmitRequest(approver_id="OFFICER-001", reason="Stale val attempt")
    with pytest.raises(ApprovalBlockedError) as exc_info:
        service.approve_revision(rev_id, req)
    
    assert "VALIDATION_OUTDATED" in str(exc_info.value)


def test_immutable_approved_revision_cannot_be_reapproved():
    """Verify Section 34: Approved revisions are immutable and cannot be re-approved."""
    db = MagicMock()
    service = ApprovalService(db)
    
    rev_id = uuid4()
    mock_rev = MagicMock()
    mock_rev.id = rev_id
    mock_rev.status = UnitStatus.APPROVED  # Already APPROVED
    mock_rev.created_at = datetime.now(timezone.utc)
    mock_rev.parent_ulpin = "12345678901234"
    service.revision_repo.find_by_id = MagicMock(return_value=mock_rev)
    service.val_run_repo.find_latest_for_revision = MagicMock(return_value=None)
    service.val_run_repo.find_latest_for_parcel = MagicMock(return_value=None)
    service.prov_repo.find_by_revision_id = MagicMock(return_value=None)
    service.review_repo.find_latest_for_revision = MagicMock(return_value=None)
    
    is_eligible, blockers = service.evaluate_gate_c_eligibility(rev_id)
    assert not is_eligible
    assert any("already approved" in b for b in blockers)


def test_data_integrity_negative_checks():
    """Verify Section 35: verify_data_integrity non-destructively identifies defects."""
    from backend.db.session import SessionLocal
    db = SessionLocal()
    try:
        report = verify_data_integrity(db)
        assert report["status"] in ("PASS", "WARNING", "BLOCKER")
        assert "summary" in report
        assert "total_issues" in report["summary"]
        assert "blockers" in report["summary"]
        assert "warnings" in report["summary"]
        assert isinstance(report["issues"], list)
    finally:
        db.close()
