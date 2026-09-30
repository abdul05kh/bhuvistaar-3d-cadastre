"""Comprehensive End-to-End Integration Test for Slice 3 AI Pipeline.

Tests:
1. Real PostGIS database state reset.
2. AI Inference pipeline execution (Layer A, B, C, D).
3. Candidate proposal inspection, confidence scoring, reason codes.
4. Anomaly detection (VRT-003 vertical overlap blocker).
5. Reviewer queue prioritization (Blocker -> Anomaly -> Candidate).
6. Fact-based explanation synthesis from structured facts.
7. Human officer acceptance: generates deterministic Prototype VUID, Revision 1, Gate A validation, audit logs.
8. Human officer rejection: preserves candidate, records justification and audit event.
9. Trace Origin lineage traversal across all lifecycle stages.
10. Model registry and synthetic evaluation benchmarking.
11. Feature toggle fallback: when AI_ASSISTANCE_ENABLED is false, core deterministic workflow remains 100% operational.
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.config import settings
from backend.db.session import SessionLocal
from backend.db.models import (
    AICandidateModel,
    AIAnomalyModel,
    EvidenceObservationModel,
    AuditEventModel
)

client = TestClient(app)


def test_ai_pipeline_end_to_end_real_postgis():
    # Step 1: Reset database to defect scenario (L01 ceiling 106.50m vs L02 floor 106.00m)
    reset_res = client.post("/api/v1/demo/reset?scenario=defect")
    assert reset_res.status_code == 200
    ulpin = reset_res.json()["parent_ulpin"]
    assert ulpin == "12345678901234"

    # Step 2: Trigger AI Inference Pipeline
    infer_res = client.post(f"/api/v1/ai/infer/{ulpin}")
    assert infer_res.status_code == 200
    infer_data = infer_res.json()
    assert infer_data["status"] == "INFERENCE_COMPLETED"
    assert infer_data["parent_ulpin"] == ulpin

    candidates = infer_data["candidates"]
    assert len(candidates) == 4
    level_codes = [c["level_code"] for c in candidates]
    assert "B1" in level_codes
    assert "Ground" in level_codes
    assert "L01" in level_codes
    assert "L02" in level_codes

    # Verify candidate properties
    for c in candidates:
        assert c["status"] == "AI_CANDIDATE"  # AI never approves
        assert c["confidence"] >= 0.0
        assert c["confidence_band"] in ("HIGH", "MEDIUM", "LOW")
        assert len(c["reason_codes"]) >= 3
        assert c["model"]["name"] == "prismatic-candidate-001"
        assert c["footprint_area_sqm"] > 0
        assert c["volume_cbm"] > 0

    # Step 3: Verify Anomaly Detection (Layer C)
    anomalies = infer_data["anomalies"]
    assert len(anomalies) >= 1
    overlap_anom = next((a for a in anomalies if a["anomaly_type"] == "OVERLAPPING_LEVELS"), None)
    assert overlap_anom is not None
    assert overlap_anom["severity"] == "BLOCKER"
    assert "L01" in overlap_anom["affected_units"]
    assert "L02" in overlap_anom["affected_units"]
    assert "VRT-003" in overlap_anom["recommended_action"]

    # Step 4: Verify Reviewer Queue Prioritization (Layer D)
    queue_res = client.get(f"/api/v1/ai/queue/{ulpin}")
    assert queue_res.status_code == 200
    queue_data = queue_res.json()
    assert queue_data["total_items"] >= 4
    # Highest priority (priority 1) must be the blocker anomaly
    first_item = queue_data["items"][0]
    assert first_item["priority"] == 1
    assert first_item["severity"] == "BLOCKER"

    # Step 5: Verify Fact-Based Explanation
    l01_cand = next(c for c in candidates if c["level_code"] == "L01")
    explain_res = client.get(f"/api/v1/ai/explain/{l01_cand['candidate_id']}")
    assert explain_res.status_code == 200
    explain_data = explain_res.json()
    assert explain_data["target_id"] == l01_cand["candidate_id"]
    assert explain_data["validation_status"] == "BLOCKER"
    assert "VRT-003" in explain_data["summary"]
    assert len(explain_data["geometric_facts"]) >= 3

    # Step 6: Human Officer Accepts Candidate (Ground floor)
    ground_cand = next(c for c in candidates if c["level_code"] == "Ground")
    accept_res = client.post(
        f"/api/v1/ai/candidates/{ground_cand['candidate_id']}/accept",
        json={
            "reviewer_id": "test_officer_sih",
            "justification": "Ground floor dimensions verified against structural blueprint."
        }
    )
    assert accept_res.status_code == 200
    accept_data = accept_res.json()
    assert accept_data["status"] == "ACCEPTED_INTO_GOVERNANCE"
    assert accept_data["prototype_vuid"].startswith(f"BV-{ulpin}-")
    assert accept_data["revision_number"] == 1

    # Verify candidate status in DB
    db = SessionLocal()
    try:
        updated_cand = db.query(AICandidateModel).filter(AICandidateModel.candidate_id == ground_cand["candidate_id"]).first()
        assert updated_cand.status == "ACCEPTED"
        assert updated_cand.reviewed_by == "test_officer_sih"
        assert updated_cand.governed_unit_id is not None
    finally:
        db.close()

    # Step 7: Human Officer Rejects Candidate (B1 basement)
    b1_cand = next(c for c in candidates if c["level_code"] == "B1")
    reject_res = client.post(
        f"/api/v1/ai/candidates/{b1_cand['candidate_id']}/reject",
        json={
            "reviewer_id": "test_officer_sih",
            "justification": "Basement parking not registered in primary cadastral parcel deed."
        }
    )
    assert reject_res.status_code == 200
    reject_data = reject_res.json()
    assert reject_data["status"] == "REJECTED"
    assert "Basement parking not registered" in reject_data["rejection_reason"]

    # Verify B1 is preserved in DB (never deleted)
    db = SessionLocal()
    try:
        preserved_cand = db.query(AICandidateModel).filter(AICandidateModel.candidate_id == b1_cand["candidate_id"]).first()
        assert preserved_cand is not None
        assert preserved_cand.status == "REJECTED"
        assert preserved_cand.rejection_reason is not None

        # Verify audit event for rejection
        reject_audit = db.query(AuditEventModel).filter(
            AuditEventModel.action == "AI_CANDIDATE_REJECTED",
            AuditEventModel.entity_id == b1_cand["candidate_id"]
        ).first()
        assert reject_audit is not None
        assert reject_audit.actor_id == "test_officer_sih"
    finally:
        db.close()

    # Step 8: Trace Origin Lineage Traversal
    trace_res = client.get(f"/api/v1/ai/trace-origin/{ground_cand['candidate_id']}")
    assert trace_res.status_code == 200
    trace_data = trace_res.json()
    assert trace_data["target_identifier"] == ground_cand["candidate_id"]
    stages = [n["stage"] for n in trace_data["lineage_path"]]
    assert "EVIDENCE" in stages
    assert "AI_CANDIDATE" in stages
    assert "GOVERNED_REVISION" in stages

    # Step 9: Model Registry and Evaluation Benchmark
    models_res = client.get("/api/v1/ai/models")
    assert models_res.status_code == 200
    assert models_res.json()["total_models"] >= 3

    eval_res = client.post("/api/v1/ai/evaluate")
    assert eval_res.status_code == 200
    eval_data = eval_res.json()
    assert eval_data["total_scenarios_evaluated"] >= 7
    assert eval_data["metrics"]["candidate_detection"]["f1_score"] > 0.80

    # Step 10: Demo Scenario Loader
    scenario_res = client.post("/api/v1/ai/scenarios/evidence-conflict")
    assert scenario_res.status_code == 200
    assert scenario_res.json()["scenario"] == "evidence-conflict"

    # Step 11: Feature Toggle Test (AI disabled -> core workflow unaffected)
    settings.AI_ASSISTANCE_ENABLED = False
    try:
        # AI inference should now fail gracefully with 503
        disabled_res = client.post(f"/api/v1/ai/infer/{ulpin}")
        assert disabled_res.status_code == 503
        assert "AI_SERVICE_DISABLED" in disabled_res.text

        # Core deterministic API remains 100% operational
        parcel_res = client.get(f"/api/v1/parcels/{ulpin}")
        assert parcel_res.status_code == 200
        assert parcel_res.json()["ulpin"] == ulpin
    finally:
        # Restore feature toggle
        settings.AI_ASSISTANCE_ENABLED = True
