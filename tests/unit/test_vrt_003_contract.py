from uuid import uuid4
from shapely.geometry import Polygon
from backend.domain.parcel import ParentParcel
from backend.domain.spatial_unit import SpatialUnit3D
from backend.domain.enums import SemanticType, ConfidenceLevel, UnitStatus, IssueSeverity
from backend.validation.rules.gate_a_vertical import RuleVrt003FloorOverlap
from backend.vuid.generator import generate_prototype_vuid


def make_parcel():
    poly = Polygon([(0.0, 0.0), (40.0, 0.0), (40.0, 30.0), (0.0, 30.0), (0.0, 0.0)])
    return ParentParcel(ulpin="12345678901234", crs="EPSG:32643", geometry=poly, area_sqm=1200.0)


def make_floor(parcel_id, level, z_min, z_max):
    poly = Polygon([(8.0, 6.0), (32.0, 6.0), (32.0, 24.0), (8.0, 24.0), (8.0, 6.0)])
    vuid_res = generate_prototype_vuid("12345678901234", "BLDG", level, poly, z_min, z_max)
    return SpatialUnit3D(
        parent_parcel_id=parcel_id,
        parent_ulpin="12345678901234",
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
        source_ids=["EVID-001"]
    )


def test_vrt_003_gap_negative_0_500():
    rule = RuleVrt003FloorOverlap()
    p = make_parcel()
    # gap = 106.0 - 106.5 = -0.500m (< -0.001m -> BLOCKER)
    f1 = make_floor(p.id, "L01", 103.0, 106.5)
    f2 = make_floor(p.id, "L02", 106.0, 109.0)
    issues = rule.evaluate(uuid4(), p, [f1, f2])
    assert len(issues) == 1
    assert issues[0].passed is False
    assert issues[0].severity == IssueSeverity.BLOCKER
    assert issues[0].measured_value["gap_m"] == -0.5
    assert issues[0].measured_value["overlap_m"] == 0.5


def test_vrt_003_gap_negative_0_001():
    rule = RuleVrt003FloorOverlap()
    p = make_parcel()
    # gap = 106.0 - 106.001 = -0.001m (>= -0.001m -> acceptable adjacency INFO)
    f1 = make_floor(p.id, "L01", 103.0, 106.001)
    f2 = make_floor(p.id, "L02", 106.0, 109.0)
    issues = rule.evaluate(uuid4(), p, [f1, f2])
    assert len(issues) == 1
    assert issues[0].passed is True
    assert issues[0].severity == IssueSeverity.INFO
    assert issues[0].measured_value["gap_m"] == -0.001


def test_vrt_003_gap_exact_zero():
    rule = RuleVrt003FloorOverlap()
    p = make_parcel()
    # gap = 106.0 - 106.0 = 0.0m (acceptable adjacency INFO)
    f1 = make_floor(p.id, "L01", 103.0, 106.0)
    f2 = make_floor(p.id, "L02", 106.0, 109.0)
    issues = rule.evaluate(uuid4(), p, [f1, f2])
    assert len(issues) == 1
    assert issues[0].passed is True
    assert issues[0].severity == IssueSeverity.INFO
    assert issues[0].measured_value["gap_m"] == 0.0


def test_vrt_003_gap_positive_0_001():
    rule = RuleVrt003FloorOverlap()
    p = make_parcel()
    # gap = 106.0 - 105.999 = +0.001m (<= +0.001m -> acceptable adjacency INFO)
    f1 = make_floor(p.id, "L01", 103.0, 105.999)
    f2 = make_floor(p.id, "L02", 106.0, 109.0)
    issues = rule.evaluate(uuid4(), p, [f1, f2])
    assert len(issues) == 1
    assert issues[0].passed is True
    assert issues[0].severity == IssueSeverity.INFO
    assert issues[0].measured_value["gap_m"] == 0.001


def test_vrt_003_gap_positive_0_002():
    rule = RuleVrt003FloorOverlap()
    p = make_parcel()
    # gap = 106.0 - 105.998 = +0.002m (> +0.001m -> WARN reported explicitly)
    f1 = make_floor(p.id, "L01", 103.0, 105.998)
    f2 = make_floor(p.id, "L02", 106.0, 109.0)
    issues = rule.evaluate(uuid4(), p, [f1, f2])
    assert len(issues) == 1
    assert issues[0].passed is True
    assert issues[0].severity == IssueSeverity.WARN
    assert issues[0].measured_value["gap_m"] == 0.002
    assert "Vertical gap of 0.002m detected" in issues[0].message
