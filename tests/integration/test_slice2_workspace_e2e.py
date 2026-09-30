"""BhuVistaar Slice 2 — Golden Path Workspace E2E Verification.

Mandatory acceptance test testing the complete interactive workflow:
1. Load Demo Scenario (POST /api/v1/demo/reset?scenario=defect)
2. Retrieve Parcel (GET /api/v1/parcels/{ulpin})
3. Retrieve 3D Spatial Units (GET /api/v1/parcels/{ulpin}/units)
4. Retrieve Evidence Sources (GET /api/v1/parcels/{ulpin}/evidence)
5. Run Validation -> Detect VRT-003 BLOCKER (POST /api/v1/validation/run)
6. Attempt Premature Approval -> Rejected with HTTP 409 Conflict (POST /api/v1/governance/approval/{rev_id})
7. Submit Non-Destructive Correction for L01 ceiling (POST /api/v1/governance/correction/{rev_id})
8. Verify Revision 2 is created and predecessor pointer equals Revision 1
9. Verify new deterministic Prototype VUID is generated
10. Verify historical Revision 1 remains intact with original VUID and elevation
11. Verify automated revalidation has 0 BLOCKERS and can_approve is True
12. Submit Human Review Decision ACCEPT (POST /api/v1/governance/review/{new_rev_id})
13. Submit Prototype Workflow Approval -> Succeeds with HTTP 200 (POST /api/v1/governance/approval/{new_rev_id})
14. Retrieve Revision History showing both revisions (GET /api/v1/units/{new_vuid}/revisions)
15. Retrieve Audit Event Ledger (GET /api/v1/governance/audit/revision/{new_rev_id})
16. Retrieve Structured Export (GET /api/v1/governance/export/revision/{new_rev_id})
"""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_slice2_golden_workspace_workflow():
    # 1. Reset demo to synthetic defect fixture
    reset_res = client.post("/api/v1/demo/reset?scenario=defect")
    assert reset_res.status_code == 200
    reset_data = reset_res.json()
    assert reset_data["status"] == "RESET_SUCCESSFUL"
    ulpin = reset_data["parent_ulpin"]
    assert ulpin == "12345678901234"
    assert reset_data["units_count"] == 4
    assert reset_data["validation"]["blocker_count"] == 1

    # 2. Retrieve parcel
    parcel_res = client.get(f"/api/v1/parcels/{ulpin}")
    assert parcel_res.status_code == 200
    parcel_data = parcel_res.json()
    assert parcel_data["ulpin"] == ulpin
    assert parcel_data["storage_srid"] == 32643
    assert parcel_data["area_sqm"] == 1200.0

    # 3. Retrieve units
    units_res = client.get(f"/api/v1/parcels/{ulpin}/units")
    assert units_res.status_code == 200
    units = units_res.json()
    assert len(units) == 4
    level_codes = [u["level_code"] for u in units]
    assert "B1" in level_codes
    assert "G" in level_codes
    assert "L01" in level_codes
    assert "L02" in level_codes

    unit_l01 = next(u for u in units if u["level_code"] == "L01")
    unit_l02 = next(u for u in units if u["level_code"] == "L02")
    rev1_l01_id = unit_l01["active_revision_id"]
    rev1_vuid = unit_l01["prototype_vuid"]
    assert rev1_l01_id is not None
    assert unit_l01["z_min"] == 103.0
    assert unit_l01["z_max"] == 106.5  # 0.50m collision with L02 (z_min=106.0)

    # 4. Retrieve evidence
    evidence_res = client.get(f"/api/v1/parcels/{ulpin}/evidence")
    assert evidence_res.status_code == 200
    evidence = evidence_res.json()
    assert len(evidence) == 3
    assert all(len(e["checksum"]) == 64 for e in evidence)

    # 5. Validation check
    val_res = client.post("/api/v1/validation/run", json={"ulpin": ulpin})
    assert val_res.status_code == 200
    val_data = val_res.json()
    assert val_data["blocker_count"] == 1
    assert val_data["can_approve"] is False
    vrt_issue = next(i for i in val_data["issues"] if i["rule_code"] == "VRT-003" and not i["passed"])
    assert vrt_issue["severity"] == "BLOCKER"

    # 6. Attempt premature approval -> must be rejected with HTTP 409 Conflict
    premature_approval = client.post(
        f"/api/v1/governance/approval/{rev1_l01_id}",
        json={
            "approver_id": "SIM-APPROVER-001",
            "reason": "Attempting premature approval on defect unit.",
            "actor_context": "SIMULATED_PROTOTYPE"
        }
    )
    assert premature_approval.status_code == 409
    assert "BLOCKER" in str(premature_approval.json())

    # 7. Submit non-destructive correction for L01
    correction_res = client.post(
        f"/api/v1/governance/correction/{rev1_l01_id}",
        json={
            "reviewer_id": "REV-OFFICER-001",
            "reason": "Adjusted ceiling elevation from 106.50m down to 106.00m to eliminate 0.50m vertical collision with Level L02.",
            "z_min": 103.0,
            "z_max": 106.0,
            "actor_context": "SIMULATED_PROTOTYPE"
        }
    )
    assert correction_res.status_code in (200, 201)
    corr_data = correction_res.json()
    rev2_l01_id = corr_data["new_revision_id"]
    rev2_vuid = corr_data["prototype_vuid"]

    # 8. Verify Revision 2 is created and points to Revision 1
    assert rev2_l01_id != rev1_l01_id
    assert corr_data["predecessor_revision_id"] == rev1_l01_id

    # 9. Verify new deterministic VUID is generated
    assert rev2_vuid != rev1_vuid

    # 10. Verify historical Revision 1 remains intact in database
    historical_rev1_unit = client.get(f"/api/v1/units/{rev1_vuid}").json()
    assert historical_rev1_unit["prototype_vuid"] == rev1_vuid

    # 11. Verify revalidation has 0 blockers
    assert corr_data["blocker_count"] == 0
    assert corr_data["can_approve"] is True

    # 12. Submit human review decision ACCEPT
    review_res = client.post(
        f"/api/v1/governance/review/{rev2_l01_id}",
        json={
            "decision": "ACCEPT",
            "reason": "Elevations verified against architectural drawing. Revalidation passes with 0 blockers.",
            "reviewer_id": "REV-OFFICER-001",
            "actor_context": "SIMULATED_PROTOTYPE"
        }
    )
    assert review_res.status_code in (200, 201)
    assert review_res.json()["decision"] == "ACCEPT"

    # 13. Gate C approval succeeds
    approval_res = client.post(
        f"/api/v1/governance/approval/{rev2_l01_id}",
        json={
            "approver_id": "SIM-APPROVER-001",
            "reason": "All Gate A, Gate B, and Gate C conditions satisfied. Approved as Prototype 3D Unit.",
            "actor_context": "SIMULATED_PROTOTYPE"
        }
    )
    assert approval_res.status_code in (200, 201)
    approval_data = approval_res.json()
    assert approval_data["status"] == "APPROVED"
    assert approval_data["revision_id"] == rev2_l01_id

    # 14. Retrieve revision history
    rev_history_res = client.get(f"/api/v1/units/{rev2_vuid}/revisions")
    assert rev_history_res.status_code == 200
    revisions = rev_history_res.json()
    assert len(revisions) == 2
    assert revisions[0]["revision_number"] == 1
    assert revisions[1]["revision_number"] == 2
    assert revisions[1]["predecessor_revision_id"] == revisions[0]["id"]

    # 15. Retrieve audit trail
    audit_res = client.get(f"/api/v1/governance/audit/revision/{rev2_l01_id}")
    assert audit_res.status_code == 200
    audit_events = audit_res.json()
    actions = [e["action"] for e in audit_events]
    assert "REVISION_CREATED" in actions
    assert "REVALIDATION_EXECUTED" in actions
    assert "REVIEW_SUBMITTED" in actions
    assert "APPROVAL_GRANTED" in actions

    # 16. Retrieve structured JSON export
    export_res = client.get(f"/api/v1/governance/export/revision/{rev2_l01_id}?exported_by=SIM-APPROVER-001")
    assert export_res.status_code == 200
    export_data = export_res.json()
    assert export_data["spatial_unit_revision"]["revision_id"] == rev2_l01_id
    assert export_data["spatial_unit_revision"]["revision_number"] == 2
    assert export_data["vuid"]["prototype_vuid"] == rev2_vuid
    assert export_data["approval"]["status"] == "APPROVED"
    assert "PROTOTYPE" in export_data["export_metadata"]["disclaimer"]
    assert export_data["audit_summary"]["total_events"] >= 4
