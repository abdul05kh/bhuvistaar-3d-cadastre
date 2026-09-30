from uuid import uuid4
from shapely.geometry import Polygon
from backend.domain.parcel import ParentParcel
from backend.domain.spatial_unit import SpatialUnit3D
from backend.domain.enums import SemanticType, ConfidenceLevel, UnitStatus, IssueSeverity
from backend.validation.rules.gate_a_geometry import (
    RuleGeo001NonEmpty,
    RuleGeo002ValidPolygon,
    RuleGeo003ExplicitCRS,
    RuleGeo004FiniteCoordinates
)
from backend.validation.rules.gate_a_vertical import (
    RuleVrt001ZOrder,
    RuleVrt003FloorOverlap
)
from backend.validation.rules.gate_a_topology import (
    RuleTop001ParentContainment
)
from backend.validation.rules.gate_a_identity import (
    RuleId001ParentUlpinIntegrity,
    RuleId002VuidUniqueness,
    RuleId003VuidDeterminism
)
from backend.vuid.generator import generate_prototype_vuid


def make_test_parcel(ulpin="12345678901234", crs="EPSG:32643", poly=None):
    if poly is None:
        poly = Polygon([(0.0, 0.0), (40.0, 0.0), (40.0, 30.0), (0.0, 30.0), (0.0, 0.0)])
    return ParentParcel(
        ulpin=ulpin,
        crs=crs,
        geometry=poly,
        area_sqm=float(poly.area)
    )


def make_test_unit(parcel_id, ulpin, level, z_min, z_max, poly=None):
    if poly is None:
        poly = Polygon([(8.0, 6.0), (32.0, 6.0), (32.0, 24.0), (8.0, 24.0), (8.0, 6.0)])
    vuid_res = generate_prototype_vuid(ulpin, "BLDG", level, poly, z_min, z_max)
    return SpatialUnit3D(
        parent_parcel_id=parcel_id,
        parent_ulpin=ulpin,
        prototype_vuid=vuid_res.prototype_vuid,
        semantic_type=SemanticType.FLOOR_VOLUME,
        level_code=level,
        z_min=z_min,
        z_max=z_max,
        footprint_area_sqm=float(poly.area),
        volume_cbm=float(poly.area * (z_max - z_min)),
        centroid_x=float(poly.centroid.x),
        centroid_y=float(poly.centroid.y),
        centroid_z=float((z_min + z_max) / 2.0),
        footprint_geom=poly,
        vuid_full_hash=vuid_res.vuid_full_hash,
        source_ids=["EVID-001"]
    )


def test_rule_geo_002_bowtie_polygon_rejected():
    rule = RuleGeo002ValidPolygon()
    run_id = uuid4()
    # Self-intersecting bowtie polygon
    bowtie = Polygon([(0, 0), (10, 10), (0, 10), (10, 0), (0, 0)])
    parcel = make_test_parcel(poly=bowtie)
    
    issues = rule.evaluate(run_id, parcel, [])
    assert len(issues) == 1
    assert issues[0].passed is False
    assert issues[0].severity == IssueSeverity.BLOCKER
    assert "Self-intersection" in issues[0].message


def test_rule_geo_003_geographic_crs_rejected():
    rule = RuleGeo003ExplicitCRS()
    run_id = uuid4()
    parcel = make_test_parcel(crs="EPSG:4326")
    
    issues = rule.evaluate(run_id, parcel, [])
    assert len(issues) == 1
    assert issues[0].passed is False
    assert issues[0].severity == IssueSeverity.BLOCKER
    assert "angular degrees" in issues[0].message


def test_rule_vrt_003_overlap_detected():
    rule = RuleVrt003FloorOverlap()
    run_id = uuid4()
    parcel = make_test_parcel()
    # L01 ends at 106.5, L02 starts at 106.0 -> 0.50m overlap defect
    u1 = make_test_unit(parcel.id, parcel.ulpin, "L01", 103.0, 106.5)
    u2 = make_test_unit(parcel.id, parcel.ulpin, "L02", 106.0, 109.0)
    
    issues = rule.evaluate(run_id, parcel, [u1, u2])
    assert len(issues) == 1
    issue = issues[0]
    assert issue.passed is False
    assert issue.severity == IssueSeverity.BLOCKER
    assert issue.measured_value["overlap_m"] == 0.5
    assert issue.measured_value["gap_m"] == -0.5
    assert "Vertical overlap conflict" in issue.message


def test_rule_vrt_003_adjacent_floors_pass():
    rule = RuleVrt003FloorOverlap()
    run_id = uuid4()
    parcel = make_test_parcel()
    # L01 ends at 106.0, L02 starts at 106.0 -> exact adjacency
    u1 = make_test_unit(parcel.id, parcel.ulpin, "L01", 103.0, 106.0)
    u2 = make_test_unit(parcel.id, parcel.ulpin, "L02", 106.0, 109.0)
    
    issues = rule.evaluate(run_id, parcel, [u1, u2])
    assert len(issues) == 1
    assert issues[0].passed is True
    assert issues[0].severity == IssueSeverity.INFO


def test_rule_top_001_out_of_parcel_detected():
    rule = RuleTop001ParentContainment()
    run_id = uuid4()
    # Parcel is 40x30 (0..40, 0..30)
    parcel = make_test_parcel()
    # Unit extends to 50 on X axis (encroachment of 10m x 18m)
    encroaching_poly = Polygon([(8.0, 6.0), (50.0, 6.0), (50.0, 24.0), (8.0, 24.0), (8.0, 6.0)])
    unit = make_test_unit(parcel.id, parcel.ulpin, "L01", 103.0, 106.0, poly=encroaching_poly)
    
    issues = rule.evaluate(run_id, parcel, [unit])
    assert len(issues) == 1
    issue = issues[0]
    assert issue.passed is False
    assert issue.severity == IssueSeverity.BLOCKER
    assert issue.measured_value["exterior_area_sqm"] > 0
    assert "extends beyond parent parcel" in issue.message
    # Critical invariant: candidate geometry was NOT modified
    assert unit.footprint_geom.equals(encroaching_poly)
