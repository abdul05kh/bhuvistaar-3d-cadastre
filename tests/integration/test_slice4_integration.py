"""Slice 4 Integration Test against Real PostgreSQL 16 + PostGIS 3.4.

Validates:
1. AI inference + deterministic validation handoff
2. Validation Disagreement Engine (Case A blocker detection)
3. Cryptographic Reproducibility Snapshot generation and verification
4. Human rejection preservation (Case D human override audit)
5. AI Service Failure resilience (Core deterministic workflow continues uninterrupted)
"""
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.config import settings
from backend.domain.enums import DisagreementType, ReproducibilityStatus


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def test_slice4_full_lifecycle_real_postgis(client):
    ulpin = "12345678901234"

    # 1. Reset demo to defect scenario (L01/L02 0.50m overlap)
    reset_resp = client.post("/api/v1/demo/reset?scenario=defect")
    assert reset_resp.status_code == 200
    assert reset_resp.json()["status"] == "RESET_SUCCESSFUL"

    # 2. Run AI Inference
    infer_resp = client.post(f"/api/v1/ai/infer/{ulpin}")
    assert infer_resp.status_code == 200
    infer_data = infer_resp.json()
    assert infer_data["status"] == "INFERENCE_COMPLETED"
    candidates = infer_data["candidates"]
    assert len(candidates) >= 3

    # Find candidate L02
    l02_cand = next((c for c in candidates if c["level_code"] == "L02"), candidates[0])
    l02_cand_id = l02_cand["candidate_id"]

    # 3. Analyze Disagreements (AI said high conf, but deterministic validator flagged VRT-003)
    disagree_resp = client.get(f"/api/v1/ai/disagreements/{ulpin}")
    assert disagree_resp.status_code == 200
    disagree_data = disagree_resp.json()
    assert disagree_data["total_disagreements"] >= 1
    assert disagree_data["blocker_count"] >= 1

    # Check for CASE A
    case_a = next(
        (d for d in disagree_data["disagreements"] if d["disagreement_type"] == DisagreementType.AI_VALIDATION_DISAGREEMENT.value),
        None
    )
    assert case_a is not None
    assert case_a["severity"] == "BLOCKER"
    assert "VRT-003" in case_a["rule_codes"]

    # 4. Generate Reproducibility Snapshot
    snap_resp = client.get(f"/api/v1/ai/reproducibility/{l02_cand_id}")
    assert snap_resp.status_code == 200
    snap_data = snap_resp.json()
    assert snap_data["reproducibility_status"] == ReproducibilityStatus.REPRODUCIBLE.value
    assert snap_data["can_reproduce"] is True
    assert snap_data["snapshot_hash"] is not None
    assert len(snap_data["snapshot_hash"]) == 64
    assert snap_data["software_commit"] is not None

    # Verify Reproducibility endpoint
    verify_resp = client.post(
        "/api/v1/ai/reproducibility/verify",
        json={"target_id": l02_cand_id, "recompute_hash": True}
    )
    assert verify_resp.status_code == 200
    assert verify_resp.json()["is_valid"] is True

    # 5. Model Comparison
    compare_resp = client.post(
        "/api/v1/ai/models/compare",
        json={
            "model_a_id": "prismatic-candidate-001",
            "model_b_id": "cadastral-heuristic-baseline-001",
            "parent_ulpin": ulpin
        }
    )
    assert compare_resp.status_code == 200
    compare_data = compare_resp.json()
    assert len(compare_data["metrics"]) >= 4
    assert "Difference observed" in compare_data["metrics"][0]["observation"]

    # 6. Human Reviewer Rejects Proposal -> Case D recorded, proposal preserved
    reject_resp = client.post(
        f"/api/v1/ai/candidates/{l02_cand_id}/reject",
        json={
            "reviewer_id": "senior_reviewer_01",
            "justification": "Evidence does not support separate strata boundary for L02 mezzanine."
        }
    )
    assert reject_resp.status_code == 200
    assert reject_resp.json()["status"] == "REJECTED"

    # Re-check disagreements: Case D must now be cataloged
    disagree_resp_after = client.get(f"/api/v1/ai/disagreements/{ulpin}")
    assert disagree_resp_after.status_code == 200
    case_d = next(
        (d for d in disagree_resp_after.json()["disagreements"] if d["disagreement_type"] == DisagreementType.HUMAN_OVERRIDE_OF_AI_PROPOSAL.value),
        None
    )
    assert case_d is not None
    assert case_d["human_decision"] == "REJECTED"

    # 7. AI Service Failure Fallback Test:
    # Disable AI assistance and verify core deterministic spatial validation and review continue 100%
    original_flag = settings.AI_ASSISTANCE_ENABLED
    try:
        settings.AI_ASSISTANCE_ENABLED = False

        # Core validation continues
        val_resp = client.post("/api/v1/validation/run", json={"ulpin": ulpin})
        assert val_resp.status_code == 200
        assert val_resp.json()["blocker_count"] >= 1

        # Audit events continue
        audit_resp = client.get("/api/v1/governance/audit/recent")
        assert audit_resp.status_code == 200
        assert len(audit_resp.json()) > 0
    finally:
        settings.AI_ASSISTANCE_ENABLED = original_flag
