import hashlib
import json
from uuid import uuid4
from shapely.geometry import Polygon
from backend.domain.enums import (
    SemanticType,
    UnitStatus,
    ReviewDecisionType,
    ApprovalStatus,
    AuditAction,
    GateType,
    IssueSeverity
)
from backend.domain.parcel import ParentParcel
from backend.domain.spatial_unit import SpatialUnit3D
from backend.domain.revision import SpatialUnitRevision
from backend.domain.provenance import ProvenanceRecord
from backend.domain.review import ReviewDecision
from backend.domain.approval import ApprovalDecision
from backend.domain.audit import AuditEvent
from backend.domain.export import ExportRecord
from backend.validation.rules.gate_b_provenance import (
    RuleProv001ParentLinkage,
    RuleProv002EvidenceAttached,
    RuleProv003EvidenceIntegrity,
    RuleProv004GenerationProvenance
)
from backend.vuid.generator import generate_prototype_vuid


def make_test_parcel():
    poly = Polygon([(0.0, 0.0), (40.0, 0.0), (40.0, 30.0), (0.0, 30.0), (0.0, 0.0)])
    return ParentParcel(ulpin="12345678901234", crs="EPSG:32643", geometry=poly, area_sqm=1200.0)


def make_test_unit(parcel, level="L01", z_min=103.0, z_max=106.0, source_ids=None):
    poly = Polygon([(8.0, 6.0), (32.0, 6.0), (32.0, 24.0), (8.0, 24.0), (8.0, 6.0)])
    vuid_res = generate_prototype_vuid(parcel.ulpin, "BLDG", level, poly, z_min, z_max)
    return SpatialUnit3D(
        parent_parcel_id=parcel.id,
        parent_ulpin=parcel.ulpin,
        prototype_vuid=vuid_res.prototype_vuid,
        semantic_type=SemanticType.FLOOR_VOLUME,
        level_code=level,
        z_min=z_min,
        z_max=z_max,
        footprint_area_sqm=432.0,
        volume_cbm=432.0 * (z_max - z_min),
        centroid_x=20.0,
        centroid_y=15.0,
        centroid_z=(z_min + z_max) / 2.0,
        footprint_geom=poly,
        vuid_full_hash=vuid_res.vuid_full_hash,
        source_ids=source_ids if source_ids is not None else ["EVID-001"],
        generation_method="PRISMATIC_EXTRUSION",
        vuid_algorithm_version="v1"
    )


def test_gate_b_rule_prov_001_parent_linkage():
    parcel = make_test_parcel()
    unit = make_test_unit(parcel)
    rule = RuleProv001ParentLinkage()
    issues = rule.evaluate(uuid4(), parcel, [unit])
    assert len(issues) == 1
    assert issues[0].passed is True
    assert issues[0].rule_code == "PROV-001"

    # Test mismatched parent ULPIN
    unlinked_unit = make_test_unit(parcel)
    unlinked_unit.parent_ulpin = "99999999999999"
    issues_fail = rule.evaluate(uuid4(), parcel, [unlinked_unit])
    assert len(issues_fail) == 1
    assert issues_fail[0].passed is False
    assert issues_fail[0].severity == IssueSeverity.BLOCKER


def test_gate_b_rule_prov_002_evidence_attached():
    parcel = make_test_parcel()
    rule = RuleProv002EvidenceAttached()

    # Unit with evidence passes
    unit_with_ev = make_test_unit(parcel, source_ids=["EVID-001"])
    issues = rule.evaluate(uuid4(), parcel, [unit_with_ev])
    assert len(issues) == 1
    assert issues[0].passed is True

    # Unit without evidence produces BLOCKER
    unit_no_ev = make_test_unit(parcel, source_ids=[])
    issues_no_ev = rule.evaluate(uuid4(), parcel, [unit_no_ev])
    assert len(issues_no_ev) == 1
    assert issues_no_ev[0].passed is False
    assert issues_no_ev[0].severity == IssueSeverity.BLOCKER


def test_gate_b_rule_prov_003_evidence_integrity():
    parcel = make_test_parcel()
    valid_hash = hashlib.sha256(b"survey_measurement_data").hexdigest()

    # Valid evidence source
    evidence_map_valid = {
        "EVID-001": {
            "checksum": valid_hash,
            "integrity_failed": False
        }
    }
    rule_valid = RuleProv003EvidenceIntegrity(evidence_sources=evidence_map_valid)
    unit = make_test_unit(parcel, source_ids=["EVID-001"])
    issues_ok = rule_valid.evaluate(uuid4(), parcel, [unit])
    assert len(issues_ok) == 1
    assert issues_ok[0].passed is True

    # Corrupted / mismatched evidence triggers BLOCKER
    evidence_map_corrupt = {
        "EVID-001": {
            "checksum": "invalid_short_hash",
            "integrity_failed": True
        }
    }
    rule_corrupt = RuleProv003EvidenceIntegrity(evidence_sources=evidence_map_corrupt)
    issues_corrupt = rule_corrupt.evaluate(uuid4(), parcel, [unit])
    assert len(issues_corrupt) == 1
    assert issues_corrupt[0].passed is False
    assert issues_corrupt[0].severity == IssueSeverity.BLOCKER


def test_gate_b_rule_prov_004_generation_provenance():
    parcel = make_test_parcel()
    rule = RuleProv004GenerationProvenance()
    unit = make_test_unit(parcel)
    issues = rule.evaluate(uuid4(), parcel, [unit])
    assert len(issues) == 1
    assert issues[0].passed is True

    # Missing method triggers BLOCKER
    unit.generation_method = ""
    issues_fail = rule.evaluate(uuid4(), parcel, [unit])
    assert len(issues_fail) == 1
    assert issues_fail[0].passed is False
    assert issues_fail[0].severity == IssueSeverity.BLOCKER


def test_revision_immutability_and_lineage():
    unit_id = uuid4()
    poly = Polygon([(0, 0), (10, 0), (10, 10), (0, 10), (0, 0)])

    rev1 = SpatialUnitRevision(
        unit_id=unit_id,
        revision_number=1,
        prototype_vuid="BV-12345678901234-BLDG-L01-111111",
        parent_ulpin="12345678901234",
        semantic_type=SemanticType.FLOOR_VOLUME,
        level_code="L01",
        z_min=100.0,
        z_max=103.0,
        footprint_area_sqm=100.0,
        volume_cbm=300.0,
        centroid_x=5.0,
        centroid_y=5.0,
        centroid_z=101.5,
        footprint_geom=poly,
        vuid_full_hash="a" * 64,
        status=UnitStatus.GENERATED
    )

    rev2 = SpatialUnitRevision(
        unit_id=unit_id,
        revision_number=2,
        prototype_vuid="BV-12345678901234-BLDG-L01-222222",
        parent_ulpin="12345678901234",
        semantic_type=SemanticType.FLOOR_VOLUME,
        level_code="L01",
        z_min=100.0,
        z_max=103.5,
        footprint_area_sqm=100.0,
        volume_cbm=350.0,
        centroid_x=5.0,
        centroid_y=5.0,
        centroid_z=101.75,
        footprint_geom=poly,
        vuid_full_hash="b" * 64,
        predecessor_revision_id=rev1.id,
        status=UnitStatus.CORRECTED
    )

    assert rev1.revision_number == 1
    assert rev2.revision_number == 2
    assert rev2.predecessor_revision_id == rev1.id
    assert rev1.prototype_vuid != rev2.prototype_vuid
    assert rev1.height_m == 3.0
    assert rev2.height_m == 3.5
