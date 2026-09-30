import json
import pytest
from pathlib import Path
from shapely.geometry import Polygon
from backend.services.parcel_service import ParcelService
from backend.services.evidence_service import EvidenceService
from backend.services.generation_service import GenerationService
from backend.services.validation_service import ValidationService
from backend.schemas.parcel_contracts import ParcelIngestRequest
from backend.schemas.evidence_contracts import EvidenceRegisterRequest
from backend.schemas.unit_contracts import UnitGenerateRequest
from backend.exceptions import InvalidCRSError
from backend.domain.enums import IssueSeverity


class InMemoryDB:
    """Pure in-memory repository store for isolated unit/integration verification."""
    def __init__(self):
        self.parcels = {}
        self.evidence = {}
        self.units = {}
        self.unit_evidence = []
        self.issues = []

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass


class MockParcelRepo:
    def __init__(self, db: InMemoryDB):
        self.db = db

    def save(self, parcel):
        self.db.parcels[parcel.ulpin] = parcel
        return parcel

    def find_by_ulpin(self, ulpin: str):
        return self.db.parcels.get(ulpin)


class MockEvidenceRepo:
    def __init__(self, db: InMemoryDB):
        self.db = db

    def save(self, evidence):
        self.db.evidence[evidence.id] = evidence
        return evidence

    def find_by_id(self, evidence_id: str):
        return self.db.evidence.get(evidence_id)

    def find_by_parent_ulpin(self, ulpin: str):
        return [e for e in self.db.evidence.values() if e.parent_ulpin == ulpin]


class MockSpatialUnitRepo:
    def __init__(self, db: InMemoryDB):
        self.db = db

    def save(self, unit):
        existing = self.db.units.get(unit.prototype_vuid)
        if existing:
            if existing.vuid_full_hash != unit.vuid_full_hash:
                from backend.exceptions import VUIDCollisionError
                raise VUIDCollisionError(f"Collision on {unit.prototype_vuid}")
            return existing
        self.db.units[unit.prototype_vuid] = unit
        return unit

    def find_by_vuid(self, vuid: str):
        return self.db.units.get(vuid)

    def find_by_parent_ulpin(self, ulpin: str):
        units = [u for u in self.db.units.values() if u.parent_ulpin == ulpin]
        return sorted(units, key=lambda u: u.z_min)


class MockIssueRepo:
    def __init__(self, db: InMemoryDB):
        self.db = db

    def delete_for_objects(self, object_ids):
        self.db.issues = [i for i in self.db.issues if i.object_id not in object_ids]

    def save_issues(self, issues):
        self.db.issues.extend(issues)


def setup_mock_services():
    db = InMemoryDB()
    p_service = ParcelService(db)
    p_service.repo = MockParcelRepo(db)

    e_service = EvidenceService(db)
    e_service.evidence_repo = MockEvidenceRepo(db)
    e_service.parcel_repo = p_service.repo

    g_service = GenerationService(db)
    g_service.parcel_repo = p_service.repo
    g_service.evidence_repo = e_service.evidence_repo
    g_service.unit_repo = MockSpatialUnitRepo(db)

    v_service = ValidationService(db)
    v_service.parcel_repo = p_service.repo
    v_service.unit_repo = g_service.unit_repo
    v_service.issue_repo = MockIssueRepo(db)
    
    return p_service, e_service, g_service, v_service


def test_clean_fixture_pipeline_generates_four_units_and_passes():
    fixture_path = Path("fixtures/synthetic_parcel_clean.json")
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    p_service, e_service, g_service, v_service = setup_mock_services()

    # 1. Ingest parcel
    parcel_req = ParcelIngestRequest(**data["parent_parcel"])
    parcel = p_service.ingest_parcel(parcel_req)
    assert parcel.ulpin == "12345678901234"
    assert parcel.storage_srid == 32643
    assert parcel.area_sqm == 1200.0

    # 2. Register evidence
    for ev_data in data["evidence"]:
        ev_req = EvidenceRegisterRequest(parent_ulpin=parcel.ulpin, **ev_data)
        evidence = e_service.register_evidence(ev_req)
        assert evidence.id == ev_data["id"]

    # 3. Generate 3D units
    gen_req = UnitGenerateRequest(**data["building"])
    units = g_service.generate_3d_units(ulpin=parcel.ulpin, request=gen_req)
    assert len(units) == 4
    levels = [u.level_code for u in units]
    assert levels == ["B1", "G", "L01", "L02"]

    # Check prototype VUIDs and volumes
    for u in units:
        assert u.parent_ulpin == "12345678901234"
        assert u.prototype_vuid.startswith(f"BV-12345678901234-BLDG-{u.level_code}-")
        assert len(u.vuid_full_hash) == 64
        assert u.volume_cbm == 1296.0  # 432 sqm * 3m height

    # 4. Run Gate A validation
    summary = v_service.run_validation(ulpin=parcel.ulpin)
    assert summary.blocker_count == 0
    assert summary.can_approve is True
    assert summary.failed_rules == 0
    assert summary.passed_rules > 0


def test_defect_fixture_detects_vrt_003_overlap_blocker():
    fixture_path = Path("fixtures/synthetic_parcel_defect.json")
    with open(fixture_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    p_service, e_service, g_service, v_service = setup_mock_services()

    # 1. Ingest parcel
    parcel_req = ParcelIngestRequest(**data["parent_parcel"])
    parcel = p_service.ingest_parcel(parcel_req)

    # 2. Register evidence
    for ev_data in data["evidence"]:
        ev_req = EvidenceRegisterRequest(parent_ulpin=parcel.ulpin, **ev_data)
        e_service.register_evidence(ev_req)

    # 3. Generate 3D units
    gen_req = UnitGenerateRequest(**data["building"])
    units = g_service.generate_3d_units(ulpin=parcel.ulpin, request=gen_req)
    assert len(units) == 4

    # 4. Run Gate A validation
    summary = v_service.run_validation(ulpin=parcel.ulpin)
    assert summary.blocker_count == 1
    assert summary.can_approve is False

    # Find VRT-003 blocker issue
    vrt_issues = [i for i in summary.issues if i.rule_code == "VRT-003" and not i.passed]
    assert len(vrt_issues) == 1
    defect_issue = vrt_issues[0]
    assert defect_issue.severity == "BLOCKER"
    assert defect_issue.measured_value["overlap_m"] == 0.5
    assert defect_issue.measured_value["gap_m"] == -0.5
    assert defect_issue.measured_value["lower_level"] == "L01"
    assert defect_issue.measured_value["upper_level"] == "L02"
    assert "Adjust floor boundary interval based on survey evidence." in defect_issue.suggested_action


def test_top_001_blocker_does_not_modify_candidate_geometry():
    p_service, e_service, g_service, v_service = setup_mock_services()

    # Ingest 40x30m parcel
    parcel_req = ParcelIngestRequest(
        ulpin="12345678901234",
        crs="EPSG:32643",
        geometry={"type": "Polygon", "coordinates": [[[200000.0, 1900000.0], [200040.0, 1900000.0], [200040.0, 1900030.0], [200000.0, 1900030.0], [200000.0, 1900000.0]]]}
    )
    parcel = p_service.ingest_parcel(parcel_req)

    e_req = EvidenceRegisterRequest(
        id="EVID-001",
        parent_ulpin=parcel.ulpin,
        evidence_type="PARCEL_BOUNDARY",
        provider="Survey Dept",
        source_reference="REF-001",
        checksum="12345678abcdef00"
    )
    e_service.register_evidence(e_req)

    # Footprint extending beyond parcel (Easting reaches 200050, 10m beyond East edge)
    out_of_bounds_footprint = {
        "type": "Polygon",
        "coordinates": [[[200008.0, 1900006.0], [200050.0, 1900006.0], [200050.0, 1900024.0], [200008.0, 1900024.0], [200008.0, 1900006.0]]]
    }

    gen_req = UnitGenerateRequest(
        building_id="BLDG-002",
        footprint=out_of_bounds_footprint,
        floors=[{"level": "G", "z_min": 100.0, "z_max": 103.0}],
        evidence_ids=["EVID-001"]
    )
    units = g_service.generate_3d_units(ulpin=parcel.ulpin, request=gen_req)
    assert len(units) == 1

    summary = v_service.run_validation(ulpin=parcel.ulpin)
    assert summary.blocker_count >= 1
    assert summary.can_approve is False

    top_issues = [i for i in summary.issues if i.rule_code == "TOP-001" and not i.passed]
    assert len(top_issues) == 1
    assert top_issues[0].severity == "BLOCKER"
    assert top_issues[0].measured_value["exterior_area_sqm"] > 0

    # Ensure geometry was NOT clipped
    unit = units[0]
    expected_poly = Polygon(out_of_bounds_footprint["coordinates"][0])
    assert unit.footprint_geom.equals(expected_poly)


def test_reject_epsg_4326_at_ingestion():
    p_service, _, _, _ = setup_mock_services()
    with pytest.raises(InvalidCRSError) as exc_info:
        p_service.ingest_parcel(
            ParcelIngestRequest(
                ulpin="12345678901234",
                crs="EPSG:4326",
                geometry={"type": "Polygon", "coordinates": [[[78.0, 17.0], [78.1, 17.0], [78.1, 17.1], [78.0, 17.1], [78.0, 17.0]]]}
            )
        )
    assert "geographic (angular degrees)" in str(exc_info.value)
