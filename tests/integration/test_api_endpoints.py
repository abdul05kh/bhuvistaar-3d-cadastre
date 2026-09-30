import json
from fastapi.testclient import TestClient
from backend.main import app
from backend.db.session import get_db
from tests.integration.test_slice1a_pipeline import setup_mock_services
from backend.api.v1 import endpoints_parcels, endpoints_evidence, endpoints_generation, endpoints_validation, endpoints_units


def test_api_clean_fixture_end_to_end():
    p_service, e_service, g_service, v_service = setup_mock_services()

    # Mock get_db dependency
    app.dependency_overrides[get_db] = lambda: None
    client = TestClient(app)

    # Patch route service constructors
    orig_parcel_service = endpoints_parcels.ParcelService
    orig_evidence_service = endpoints_evidence.EvidenceService
    orig_generation_service = endpoints_generation.GenerationService
    orig_validation_service = endpoints_validation.ValidationService
    orig_unit_repo = endpoints_units.SpatialUnitRepository

    endpoints_parcels.ParcelService = lambda db: p_service
    endpoints_evidence.EvidenceService = lambda db: e_service
    endpoints_generation.GenerationService = lambda db: g_service
    endpoints_validation.ValidationService = lambda db: v_service
    endpoints_units.SpatialUnitRepository = lambda db: g_service.unit_repo

    try:
        # Load clean fixture
        with open("fixtures/synthetic_parcel_clean.json", "r", encoding="utf-8") as f:
            fixture_data = json.load(f)

        # 1. Health check
        res = client.get("/health/ready")
        assert res.status_code == 200
        assert res.json()["authorization_mode"] == "SIMULATED_PROTOTYPE"

        # 2. POST /api/v1/parcels
        res = client.post("/api/v1/parcels", json=fixture_data["parent_parcel"])
        assert res.status_code == 201
        p_json = res.json()
        assert p_json["ulpin"] == "12345678901234"
        assert p_json["storage_srid"] == 32643

        # 3. POST /api/v1/evidence
        for ev in fixture_data["evidence"]:
            ev_payload = dict(ev, parent_ulpin="12345678901234")
            res = client.post("/api/v1/evidence", json=ev_payload)
            assert res.status_code == 201

        # 4. POST /api/v1/parcels/{ulpin}/generate
        res = client.post("/api/v1/parcels/12345678901234/generate", json=fixture_data["building"])
        assert res.status_code == 201
        units_json = res.json()
        assert len(units_json) == 4
        first_vuid = units_json[0]["prototype_vuid"]
        assert first_vuid.startswith("BV-12345678901234-BLDG-")

        # 5. POST /api/v1/validation/run
        res = client.post("/api/v1/validation/run", json={"ulpin": "12345678901234"})
        assert res.status_code == 200
        val_json = res.json()
        assert val_json["blocker_count"] == 0
        assert val_json["can_approve"] is True

        # 6. GET /api/v1/units/{vuid}
        res = client.get(f"/api/v1/units/{first_vuid}")
        assert res.status_code == 200
        u_data = res.json()
        assert u_data["prototype_vuid"] == first_vuid
        assert u_data["parent_ulpin"] == "12345678901234"

    finally:
        endpoints_parcels.ParcelService = orig_parcel_service
        endpoints_evidence.EvidenceService = orig_evidence_service
        endpoints_generation.GenerationService = orig_generation_service
        endpoints_validation.ValidationService = orig_validation_service
        endpoints_units.SpatialUnitRepository = orig_unit_repo
        app.dependency_overrides.clear()
