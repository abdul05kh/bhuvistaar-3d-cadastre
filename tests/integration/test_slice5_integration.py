"""
Slice 5 Full Operational, Deployment, and Field Simulation Integration Tests.
Co-authored-by: Mohammad Abdul Kalam Hussain <abdul05kh.college@gmail.com>
Co-authored-by: Siri Chandana <kotagirisirichandana73@gmail.com>
Co-authored-by: Mohammad Zakiruddin <zakirmd.1805@gmail.com>
Co-authored-by: Mohammed Numan <mohammednumaan901@gmail.com>
Co-authored-by: Manivarun Chintala <manivarunchintala2005.2728@gmail.com>
Co-authored-by: Thaniska <ramatenkithanishka@gmail.com>
"""

import json
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.db.session import SessionLocal, Base, engine


@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    test_client = TestClient(app)
    yield test_client


def test_health_endpoints(client):
    """Verify operational health probes (/health, /health/ready, /health/live)."""
    # 1. Base health check
    res_base = client.get("/health")
    assert res_base.status_code == 200
    base_data = res_base.json()
    assert base_data["status"] in ("ok", "ready")
    assert "database" in base_data
    assert "postgis" in base_data

    # 2. Readiness check
    res_ready = client.get("/health/ready")
    assert res_ready.status_code == 200
    ready_data = res_ready.json()
    assert ready_data["status"] == "ready"
    assert ready_data["database"] == "ok"
    assert "ok" in ready_data["postgis"]
    assert "current" in ready_data["migrations"] or ready_data["migrations"] == "pending"
    assert "ai" in ready_data

    # 3. Liveness check
    res_live = client.get("/health/live")
    assert res_live.status_code == 200
    assert res_live.json()["status"].lower() == "alive"


def test_system_readiness_and_integrity_endpoints(client):
    """Verify system readiness category matrix and non-destructive integrity audit."""
    # 1. System Readiness Category Matrix
    res_readiness = client.get("/api/v1/system/readiness")
    assert res_readiness.status_code == 200
    readiness = res_readiness.json()
    assert "categories" in readiness
    cats = readiness["categories"]
    assert cats["database"]["status"] in ("READY", "DEGRADED", "ERROR")
    assert cats["postgis"]["status"] in ("READY", "DEGRADED", "ERROR")
    assert cats["validation_engine"]["status"] in ("READY", "DEGRADED", "ERROR")
    assert cats["governance_engine"]["status"] in ("READY", "DEGRADED", "ERROR")
    assert cats["interoperability"]["status"] == "PROTOTYPE"
    assert "role_context" in readiness
    assert readiness["role_context"]["authorization_mode"] == "SIMULATED_PROTOTYPE"

    # 2. Non-destructive Data Integrity Endpoint
    res_integrity = client.get("/api/v1/system/integrity")
    assert res_integrity.status_code == 200
    integrity = res_integrity.json()
    assert integrity["status"] in ("PASS", "WARNING", "BLOCKER")
    assert "summary" in integrity
    assert "issues" in integrity

    # 3. Observability Metrics Endpoint
    res_obs = client.get("/api/v1/system/observability")
    assert res_obs.status_code == 200
    obs = res_obs.json()
    assert "total_requests" in obs
    assert "validations_executed" in obs
    assert "exports_generated" in obs


def test_field_simulation_catalog_and_scenarios(client):
    """Verify field simulation scenario catalog and deterministic execution."""
    # 1. List scenarios
    res_catalog = client.get("/api/v1/demo/scenarios")
    assert res_catalog.status_code == 200
    scenarios = res_catalog.json()
    assert len(scenarios) >= 8
    scenario_ids = [s["scenario_id"] for s in scenarios]
    assert "clean" in scenario_ids
    assert "conflicting_evidence" in scenario_ids
    assert "ai_unavailable" in scenario_ids
    assert "failure_recovery" in scenario_ids
    assert "golden_workflow" in scenario_ids

    # 2. Execute clean scenario
    res_clean = client.post("/api/v1/demo/scenarios/clean/execute")
    assert res_clean.status_code == 200
    clean_out = res_clean.json()
    assert clean_out["status"] in ("SUCCESS", "COMPLETED", "CLEAN_BASELINE_READY")
    assert clean_out["scenario_id"] == "clean"

    # 3. Execute conflicting evidence scenario
    res_conf = client.post("/api/v1/demo/scenarios/conflicting_evidence/execute")
    assert res_conf.status_code == 200
    conf_out = res_conf.json()
    assert conf_out["scenario_id"] == "conflicting_evidence"
    assert "conflicts" in conf_out
    assert len(conf_out["conflicts"]) >= 1

    # 4. Execute AI unavailable scenario (fallback mode verification)
    res_ai_unavail = client.post("/api/v1/demo/scenarios/ai_unavailable/execute")
    assert res_ai_unavail.status_code == 200
    ai_out = res_ai_unavail.json()
    assert ai_out["scenario_id"] == "ai_unavailable"
    assert ai_out["ai_status"] == "UNAVAILABLE"
    assert ai_out["core_pipeline"] == "OPERATIONAL"


def test_failure_recovery_workflow(client):
    """Verify partial ingestion failure recovery workflow."""
    res_rec = client.post("/api/v1/demo/scenarios/failure_recovery/execute")
    assert res_rec.status_code == 200
    rec_out = res_rec.json()
    assert rec_out["scenario_id"] == "failure_recovery"
    assert rec_out["initial_failure_state"] == "PARTIAL_INGESTION"
    assert rec_out["recovery_state"] == "RECOVERED"
    assert rec_out["checksum_verified"] is True
    assert rec_out["duplicate_prevented"] is True


def test_golden_operational_workflow(client):
    """Verify full end-to-end golden operational workflow simulation."""
    res_golden = client.post("/api/v1/demo/scenarios/golden_workflow/execute")
    assert res_golden.status_code == 200
    golden_out = res_golden.json()
    assert golden_out["scenario_id"] == "golden_workflow"
    assert golden_out["status"] == "GOLDEN_WORKFLOW_COMPLETE"
    assert golden_out["roundtrip_verified"] is True
    assert golden_out["revalidation_blockers"] == 0


def test_interoperability_export_endpoints(client):
    """Verify 2D GeoJSON, 3D OBJ, and Round-Trip API endpoints."""
    # Ensure clean data is loaded
    client.post("/api/v1/demo/scenarios/clean/execute")

    # 1. GeoJSON export
    res_geojson = client.get("/api/v1/export/geojson/12345678901234")
    assert res_geojson.status_code == 200
    geojson_data = res_geojson.json()
    assert geojson_data["type"] == "FeatureCollection"
    assert "disclaimer" in geojson_data
    assert "features" in geojson_data
    assert len(geojson_data["features"]) > 0

    # 2. Get a valid unit revision ID to test 3D OBJ export
    units_res = client.get("/api/v1/units?parent_ulpin=12345678901234")
    if units_res.status_code == 200 and len(units_res.json()) > 0:
        vuid = units_res.json()[0]["prototype_vuid"]
        revs_res = client.get(f"/api/v1/units/{vuid}/revisions")
        if revs_res.status_code == 200 and len(revs_res.json()) > 0:
            rev_id = revs_res.json()[0]["id"]
            
            # Test 3D OBJ export
            res_obj = client.get(f"/api/v1/export/3d/{rev_id}")
            assert res_obj.status_code == 200
            assert "text/plain" in res_obj.headers["content-type"]
            assert len(res_obj.text) > 0

            # Test Round-Trip Verification API
            export_pkg_res = client.get(f"/api/v1/export/units/{rev_id}")
            if export_pkg_res.status_code == 200:
                pkg_data = export_pkg_res.json()
                res_verify = client.post("/api/v1/export/roundtrip/verify", json=pkg_data)
                assert res_verify.status_code == 200
                verify_out = res_verify.json()
                assert verify_out["verified"] is True
                assert verify_out["vuid_match"] is True
