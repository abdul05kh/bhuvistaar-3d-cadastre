"""
BhuVistaar API & Governance Red-Team Adversarial Fuzzing Test Suite.
Adversarially tests boundary conditions, malformed payloads, security injections,
unauthorized operations, state-machine violations, and data integrity.

Co-authored-by: Mohammad Abdul Kalam Hussain <abdul05kh.college@gmail.com>
Co-authored-by: Siri Chandana <kotagirisirichandana73@gmail.com>
Co-authored-by: Mohammad Zakiruddin <zakirmd.1805@gmail.com>
Co-authored-by: Mohammed Numan <mohammednumaan901@gmail.com>
Co-authored-by: Manivarun Chintala <manivarunchintala2005.2728@gmail.com>
Co-authored-by: Thaniska <ramatenkithanishka@gmail.com>
"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)
DEFAULT_ULPIN = "12345678901234"


# ============================================================================
# 1. System Health & Readiness Verification
# ============================================================================

def test_system_health_and_readiness_endpoints():
    """Verify /health, /health/live, /health/ready, and /api/v1/system/readiness."""
    resp_health = client.get("/health")
    assert resp_health.status_code == 200
    data = resp_health.json()
    assert data["status"] in ("ready", "degraded")
    assert data["application"] == "ok"
    assert "postgis" in data

    resp_live = client.get("/health/live")
    assert resp_live.status_code == 200
    assert resp_live.json()["status"] == "ALIVE"

    resp_ready = client.get("/health/ready")
    assert resp_ready.status_code in (200, 503)

    resp_system_readiness = client.get("/api/v1/system/readiness")
    assert resp_system_readiness.status_code == 200
    sys_data = resp_system_readiness.json()
    assert "categories" in sys_data
    assert "database" in sys_data["categories"]
    assert "governance_engine" in sys_data["categories"]


# ============================================================================
# 2. Security Fuzzing: SQL Injection & Path Traversal Protections
# ============================================================================

@pytest.mark.parametrize("malicious_ulpin", [
    "' OR '1'='1",
    "1234'; DROP TABLE spatial_units; --",
    "../../etc/passwd",
    "..\\..\\windows\\win.ini",
    "<script>alert(1)</script>",
    "null",
    " ",
    "A" * 500,  # Buffer/length overflow
])
def test_security_fuzzing_parcel_ulpin_parameters(malicious_ulpin):
    """Ensure malicious injection strings in URL paths are safely handled (404/422/400) without crashing the server."""
    resp = client.get(f"/api/v1/parcels/{malicious_ulpin}")
    # Must never return 500 or expose SQL errors
    assert resp.status_code in (400, 404, 422)
    data = resp.json()
    assert "error" in data or "detail" in data
    assert "syntax error" not in resp.text.lower()
    assert "pg_catalog" not in resp.text.lower()


# ============================================================================
# 3. Boundary & Malformed Inputs on Creation & Correction Endpoints
# ============================================================================

def test_correction_inverted_elevation_boundary_rejection():
    """Submit correction where z_min > z_max; must be deterministically rejected."""
    # Reset demo to ensure fresh state
    client.post("/api/v1/demo/reset?scenario=defect")
    units = client.get(f"/api/v1/parcels/{DEFAULT_ULPIN}/units").json()
    l01 = next(u for u in units if u["level_code"] == "L01")
    rev_id = l01["active_revision_id"]

    # Fuzz: inverted elevation (z_min 110 > z_max 100)
    payload = {
        "z_min": 110.0,
        "z_max": 100.0,
        "reason": "Adversarial test: inverted elevations",
        "actor_id": "TEST-OFFICER-001",
        "role": "ADMIN"
    }
    resp = client.post(f"/api/v1/governance/correction/{rev_id}", json=payload)
    # Elevation inversion should fail validation or return 400/422
    assert resp.status_code in (400, 422)


def test_correction_extreme_elevation_boundary_rejection():
    """Submit correction with extreme impossible elevations."""
    units = client.get(f"/api/v1/parcels/{DEFAULT_ULPIN}/units").json()
    l01 = next(u for u in units if u["level_code"] == "L01")
    rev_id = l01["active_revision_id"]

    # Impossible negative elevation: -5000m
    payload = {
        "z_min": -5000.0,
        "z_max": 106.0,
        "reason": "Deep subsurface anomaly",
        "actor_id": "TEST-OFFICER-001",
        "role": "ADMIN"
    }
    resp = client.post(f"/api/v1/governance/correction/{rev_id}", json=payload)
    assert resp.status_code in (400, 422)


def test_malformed_json_body_rejection():
    """Ensure malformed JSON payloads return standard 422 Unprocessable Entity."""
    resp = client.post(
        f"/api/v1/governance/correction/{uuid4()}",
        content="NOT_A_JSON_STRING",
        headers={"Content-Type": "application/json"}
    )
    assert resp.status_code == 422


# ============================================================================
# 4. Negative Governance & Role Escalation Checks
# ============================================================================

def test_viewer_role_cannot_submit_review():
    """VIEWER role cannot record human review decisions (HTTP 403 or 409)."""
    units = client.get(f"/api/v1/parcels/{DEFAULT_ULPIN}/units").json()
    l01 = next(u for u in units if u["level_code"] == "L01")
    rev_id = l01["active_revision_id"]

    payload = {
        "decision": "ACCEPT",
        "reviewer_id": "SIM-VIEWER-001",
        "reason": "Viewer attempting unauthorized review acceptance",
        "role": "VIEWER"
    }
    resp = client.post(f"/api/v1/governance/review/{rev_id}", json=payload)
    assert resp.status_code in (400, 403, 409)


def test_viewer_role_cannot_submit_approval():
    """VIEWER role cannot grant Gate C approval (HTTP 403, 400 or 409)."""
    units = client.get(f"/api/v1/parcels/{DEFAULT_ULPIN}/units").json()
    l01 = next(u for u in units if u["level_code"] == "L01")
    rev_id = l01["active_revision_id"]

    payload = {
        "approver_id": "SIM-VIEWER-001",
        "reason": "Viewer attempting unauthorized approval",
        "role": "VIEWER"
    }
    resp = client.post(f"/api/v1/governance/approval/{rev_id}", json=payload)
    assert resp.status_code in (400, 403, 409)
    assert "unauthorized" in resp.text.lower() or "blocked" in resp.text.lower()


def test_field_operator_cannot_submit_approval():
    """FIELD_OPERATOR role cannot grant Gate C approval."""
    units = client.get(f"/api/v1/parcels/{DEFAULT_ULPIN}/units").json()
    l01 = next(u for u in units if u["level_code"] == "L01")
    rev_id = l01["active_revision_id"]

    payload = {
        "approver_id": "SIM-OPERATOR-001",
        "reason": "Field operator attempting approval",
        "role": "FIELD_OPERATOR"
    }
    resp = client.post(f"/api/v1/governance/approval/{rev_id}", json=payload)
    assert resp.status_code in (400, 403, 409)


# ============================================================================
# 5. State Machine Violations: Blocker, Unreviewed & Autonomous Approvals
# ============================================================================

def test_autonomous_ai_approval_blocked():
    """API-level check: AI actor attempting autonomous Gate C approval is blocked."""
    units = client.get(f"/api/v1/parcels/{DEFAULT_ULPIN}/units").json()
    l01 = next(u for u in units if u["level_code"] == "L01")
    rev_id = l01["active_revision_id"]

    payload = {
        "approver_id": "AI-AGENT-AUTONOMOUS",
        "reason": "Automated pipeline bypass",
        "actor_context": "AI_AUTONOMOUS",
        "role": "ADMIN"
    }
    resp = client.post(f"/api/v1/governance/approval/{rev_id}", json=payload)
    assert resp.status_code in (400, 403, 409)
    assert "AI IS NOT THE AUTHORITY" in resp.text


def test_approval_with_unresolved_blockers_rejected():
    """Attempting Gate C approval on a revision with active validation blockers fails."""
    client.post("/api/v1/demo/reset?scenario=defect")
    units = client.get(f"/api/v1/parcels/{DEFAULT_ULPIN}/units").json()
    l01 = next(u for u in units if u["level_code"] == "L01")
    rev_id = l01["active_revision_id"]

    payload = {
        "approver_id": "SENIOR-OFFICER-001",
        "reason": "Bypassing validation blockers intentionally",
        "role": "ADMIN"
    }
    resp = client.post(f"/api/v1/governance/approval/{rev_id}", json=payload)
    assert resp.status_code in (400, 409)
    assert "blocker" in resp.text.lower() or "blocked" in resp.text.lower()


# ============================================================================
# 6. Interoperability & Export Round-Trip Verification
# ============================================================================

def test_export_geojson_success():
    """Verify GeoJSON export includes FeatureCollection, CRS, and disclaimer."""
    resp = client.get(f"/api/v1/export/geojson/{DEFAULT_ULPIN}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["type"] == "FeatureCollection"
    assert "features" in data
    assert len(data["features"]) >= 1
    assert "PROTOTYPE" in data["disclaimer"]


def test_export_3d_obj_success():
    """Verify Wavefront OBJ export includes vertices, faces, and prototype disclaimer."""
    units = client.get(f"/api/v1/parcels/{DEFAULT_ULPIN}/units").json()
    rev_id = units[0]["active_revision_id"]

    resp = client.get(f"/api/v1/export/3d/{rev_id}")
    assert resp.status_code == 200
    text = resp.text
    assert "v " in text  # Vertices
    assert "f " in text  # Faces
    assert "Prototype VUID" in text


def test_export_roundtrip_verification_valid():
    """Fetch structured export and verify roundtrip determinism passes."""
    units = client.get(f"/api/v1/parcels/{DEFAULT_ULPIN}/units").json()
    rev_id = units[0]["active_revision_id"]

    # 1. Fetch export
    exp_resp = client.get(f"/api/v1/governance/export/revision/{rev_id}")
    assert exp_resp.status_code == 200
    export_payload = exp_resp.json()

    # 2. Verify roundtrip
    rt_resp = client.post("/api/v1/export/roundtrip/verify", json=export_payload)
    assert rt_resp.status_code == 200
    rt_data = rt_resp.json()
    assert rt_data["status"] == "VERIFIED"
    assert rt_data["verified"] is True
    assert rt_data["vuid_match"] is True


def test_export_roundtrip_verification_tampered_payload():
    """Adversarially tamper with geometry/vuid in export payload and verify roundtrip fails."""
    units = client.get(f"/api/v1/parcels/{DEFAULT_ULPIN}/units").json()
    rev_id = units[0]["active_revision_id"]

    exp_resp = client.get(f"/api/v1/governance/export/revision/{rev_id}")
    export_payload = exp_resp.json()

    # Tamper with elevation to alter recalculated VUID
    export_payload["elevation"]["z_max"] = float(export_payload["elevation"]["z_max"]) + 5.0

    rt_resp = client.post("/api/v1/export/roundtrip/verify", json=export_payload)
    assert rt_resp.status_code == 200
    rt_data = rt_resp.json()
    assert rt_data["status"] == "FAILED"
    assert rt_data["verified"] is False
    assert len(rt_data["discrepancies"]) > 0


# ============================================================================
# 7. Non-Existent Entities: 404 Verification
# ============================================================================

def test_nonexistent_entity_404_responses():
    """Verify 404 responses for nonexistent IDs without server 500 error."""
    random_uuid = str(uuid4())
    assert client.get(f"/api/v1/parcels/99999999999999").status_code == 404
    assert client.get(f"/api/v1/governance/export/revision/{random_uuid}").status_code == 404
    assert client.get(f"/api/v1/export/3d/{random_uuid}").status_code == 404


# ============================================================================
# 8. Observability & Database Integrity Verification
# ============================================================================

def test_observability_metrics():
    """Verify observability endpoint reports system metrics and counts."""
    resp = client.get("/api/v1/system/observability")
    assert resp.status_code == 200
    metrics = resp.json()
    assert "metrics" in metrics
    assert metrics["metrics"]["parent_parcels"] > 0
    assert metrics["metrics"]["spatial_units"] > 0


def test_database_integrity_audit():
    """Verify database integrity check reports zero blockers in baseline state."""
    resp = client.get("/api/v1/system/integrity")
    assert resp.status_code == 200
    integrity = resp.json()
    assert integrity["status"] in ("PASS", "WARNING")
    assert integrity["summary"]["blockers"] == 0
