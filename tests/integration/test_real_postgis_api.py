import json
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from backend.main import app
from backend.db.session import SessionLocal, Base, engine
from backend.db.models import ParentParcelModel, SpatialUnitModel, EvidenceSourceModel, ValidationIssueModel


@pytest.fixture(scope="module")
def live_client():
    # Ensure tables exist
    Base.metadata.create_all(bind=engine)
    client = TestClient(app)
    yield client


def test_audit7_real_fastapi_endpoints_against_postgis(live_client):
    # 0. Clean prior state in real database
    with SessionLocal() as db:
        db.query(ValidationIssueModel).delete()
        db.query(SpatialUnitModel).delete()
        db.query(EvidenceSourceModel).delete()
        db.query(ParentParcelModel).delete()
        db.commit()

    with open("fixtures/synthetic_parcel_clean.json", "r", encoding="utf-8") as f:
        clean_data = json.load(f)

    # 1. POST /api/v1/parcels
    res = live_client.post("/api/v1/parcels", json=clean_data["parent_parcel"])
    assert res.status_code == 201, res.text
    p_data = res.json()
    assert p_data["ulpin"] == "12345678901234"
    assert p_data["storage_srid"] == 32643

    # Verify parcel actually stored in PostGIS
    with SessionLocal() as db:
        srid = db.execute(
            text("SELECT ST_SRID(geometry) FROM parent_parcels WHERE ulpin = '12345678901234';")
        ).scalar()
        assert srid == 32643

    # 2. POST /api/v1/evidence
    for ev in clean_data["evidence"]:
        ev_payload = dict(ev, parent_ulpin="12345678901234")
        res = live_client.post("/api/v1/evidence", json=ev_payload)
        assert res.status_code == 201, res.text

    # 3. POST /api/v1/parcels/{ulpin}/generate
    res = live_client.post("/api/v1/parcels/12345678901234/generate", json=clean_data["building"])
    assert res.status_code == 201, res.text
    units = res.json()
    assert len(units) == 4
    first_vuid = units[0]["prototype_vuid"]
    assert first_vuid.startswith("BV-12345678901234-BLDG-")

    # Verify unit stored in PostGIS
    with SessionLocal() as db:
        u_count = db.execute(
            text("SELECT COUNT(*) FROM spatial_units WHERE parent_ulpin = '12345678901234';")
        ).scalar()
        assert u_count == 4

    # 4. POST /api/v1/validation/run
    res = live_client.post("/api/v1/validation/run", json={"ulpin": "12345678901234"})
    assert res.status_code == 200, res.text
    val_data = res.json()
    assert val_data["blocker_count"] == 0
    assert val_data["can_approve"] is True

    # 5. GET /api/v1/validation/issues?ulpin=12345678901234
    res = live_client.get("/api/v1/validation/issues?ulpin=12345678901234")
    assert res.status_code == 200, res.text
    issues = res.json()
    assert len(issues) > 0

    # 6. GET /api/v1/units/{vuid}
    res = live_client.get(f"/api/v1/units/{first_vuid}")
    assert res.status_code == 200, res.text
    unit_data = res.json()
    assert unit_data["prototype_vuid"] == first_vuid
    assert unit_data["parent_ulpin"] == "12345678901234"
