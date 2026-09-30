import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from backend.main import app
from backend.db.session import SessionLocal, Base, engine


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    test_client = TestClient(app)
    yield test_client


def test_slice1b_fastapi_governance_workflow(client):
    # 0. Clean database
    with SessionLocal() as db:
        db.execute(text("DELETE FROM export_records;"))
        db.execute(text("DELETE FROM audit_events;"))
        db.execute(text("DELETE FROM approval_decisions;"))
        db.execute(text("DELETE FROM review_decisions;"))
        db.execute(text("DELETE FROM validation_issues;"))
        db.execute(text("DELETE FROM validation_runs;"))
        db.execute(text("DELETE FROM provenance_records;"))
        db.execute(text("DELETE FROM spatial_unit_revisions;"))
        db.execute(text("DELETE FROM spatial_units;"))
        db.execute(text("DELETE FROM evidence_sources;"))
        db.execute(text("DELETE FROM parent_parcels;"))
        db.commit()

    with open("fixtures/synthetic_parcel_clean.json", "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    # 1. Ingest parcel
    p_res = client.post("/api/v1/parcels", json=clean_data["parent_parcel"])
    assert p_res.status_code == 201
    ulpin = p_res.json()["ulpin"]

    # 2. Register evidence
    for ev in clean_data["evidence"]:
        ev_payload = dict(ev, parent_ulpin=ulpin)
        e_res = client.post("/api/v1/evidence", json=ev_payload)
        assert e_res.status_code == 201

    # 3. Generate 3D units
    g_res = client.post(f"/api/v1/parcels/{ulpin}/generate", json=clean_data["building"])
    assert g_res.status_code == 201
    units = g_res.json()
    assert len(units) == 4
    first_vuid = units[0]["prototype_vuid"]

    # 4. List revisions for the first unit
    revs_res = client.get(f"/api/v1/units/{first_vuid}/revisions")
    assert revs_res.status_code == 200
    revs = revs_res.json()
    assert len(revs) == 1
    rev1_id = revs[0]["id"]
    assert revs[0]["revision_number"] == 1

    # 5. Run validation
    v_res = client.post("/api/v1/validation/run", json={"ulpin": ulpin})
    assert v_res.status_code == 200

    # 6. Check eligibility before review -> should report blocked
    elig_res = client.get(f"/api/v1/units/{first_vuid}/revisions/{rev1_id}/eligibility")
    assert elig_res.status_code == 200
    assert elig_res.json()["is_eligible"] is False

    # Attempt approval without review -> HTTP 409 Conflict
    appr_fail = client.post(
        f"/api/v1/units/{first_vuid}/revisions/{rev1_id}/approve",
        json={"approver_id": "OFFICER-001", "reason": "Attempt without review"}
    )
    assert appr_fail.status_code == 409

    # 7. Submit human review (ACCEPT)
    rev_submit = client.post(
        f"/api/v1/units/{first_vuid}/revisions/{rev1_id}/review",
        json={
            "decision": "ACCEPT",
            "reason": "Geometry and elevation boundaries conform to architectural survey plan.",
            "reviewer_id": "REVIEWER-101"
        }
    )
    assert rev_submit.status_code == 201
    rev_data = rev_submit.json()
    assert rev_data["decision"] == "ACCEPT"

    # View review
    rev_view = client.get(f"/api/v1/units/{first_vuid}/revisions/{rev1_id}/review")
    assert rev_view.status_code == 200
    assert rev_view.json()["decision"] == "ACCEPT"

    # 8. Check eligibility after review -> should now be True
    elig_res2 = client.get(f"/api/v1/units/{first_vuid}/revisions/{rev1_id}/eligibility")
    assert elig_res2.status_code == 200
    assert elig_res2.json()["is_eligible"] is True

    # 9. Approve revision -> HTTP 201 Created
    appr_res = client.post(
        f"/api/v1/units/{first_vuid}/revisions/{rev1_id}/approve",
        json={"approver_id": "OFFICER-001", "reason": "Officer approval granted based on verified survey evidence."}
    )
    assert appr_res.status_code == 201
    appr_data = appr_res.json()
    assert appr_data["status"] == "APPROVED"
    assert appr_data["revision_id"] == rev1_id

    # 10. Attempting correction on a non-approved revision (e.g. unit 1)
    second_vuid = units[1]["prototype_vuid"]
    u2_revs = client.get(f"/api/v1/units/{second_vuid}/revisions").json()
    u2_rev1_id = u2_revs[0]["id"]

    corr_res = client.post(
        f"/api/v1/units/{second_vuid}/revisions/{u2_rev1_id}/correct",
        json={
            "reviewer_id": "OFFICER-002",
            "reason": "Adjust ground floor foundation offset by +0.05m per site measurement.",
            "z_min": 100.05
        }
    )
    assert corr_res.status_code == 201
    corr_data = corr_res.json()
    assert corr_data["new_revision_id"] != u2_rev1_id
    assert corr_data["predecessor_revision_id"] == u2_rev1_id
    assert corr_data["status"] == "REVALIDATED"

    # Verify unit 2 now has 2 revisions
    u2_all_revs = client.get(f"/api/v1/units/{second_vuid}/revisions").json()
    assert len(u2_all_revs) == 2

    # 11. Structured export
    exp_res = client.get(f"/api/v1/units/{first_vuid}/revisions/{rev1_id}/export")
    assert exp_res.status_code == 200
    exp_data = exp_res.json()
    assert exp_data["spatial_unit_revision"]["revision_id"] == rev1_id
    assert exp_data["approval"]["status"] == "APPROVED"
    assert exp_data["export_metadata"]["authorization_mode"] == "SIMULATED_PROTOTYPE"

    # 12. Query audit events
    audit_res = client.get(f"/api/v1/audit/events?revision_id={rev1_id}")
    assert audit_res.status_code == 200
    events = audit_res.json()
    assert len(events) >= 3
    event_actions = [e["action"] for e in events]
    assert "APPROVAL_GRANTED" in event_actions
    assert "REVIEW_SUBMITTED" in event_actions
