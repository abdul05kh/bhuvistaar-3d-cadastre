import pytest
from shapely.geometry import Polygon
from backend.vuid.generator import generate_prototype_vuid


def test_vuid_format_and_stability():
    poly = Polygon([(0.0, 0.0), (20.0, 0.0), (20.0, 10.0), (0.0, 10.0), (0.0, 0.0)])
    res1 = generate_prototype_vuid("12345678901234", "BLDG", "L01", poly, 103.0, 106.0)
    res2 = generate_prototype_vuid("12345678901234", "BLDG", "L01", poly, 103.0, 106.0)

    assert res1.prototype_vuid == res2.prototype_vuid
    assert res1.vuid_full_hash == res2.vuid_full_hash
    assert res1.prototype_vuid.startswith("BV-12345678901234-BLDG-L01-")
    assert len(res1.vuid_full_hash) == 64
    assert len(res1.prototype_vuid.split("-")[-1]) == 6


def test_vuid_changes_on_elevation_modification():
    poly = Polygon([(0.0, 0.0), (20.0, 0.0), (20.0, 10.0), (0.0, 10.0), (0.0, 0.0)])
    res_base = generate_prototype_vuid("12345678901234", "BLDG", "L01", poly, 103.0, 106.0)
    res_diff_z = generate_prototype_vuid("12345678901234", "BLDG", "L01", poly, 103.0, 106.5)

    assert res_base.prototype_vuid != res_diff_z.prototype_vuid
    assert res_base.vuid_full_hash != res_diff_z.vuid_full_hash


def test_vuid_changes_on_geometry_modification():
    poly1 = Polygon([(0.0, 0.0), (20.0, 0.0), (20.0, 10.0), (0.0, 10.0), (0.0, 0.0)])
    poly2 = Polygon([(0.0, 0.0), (25.0, 0.0), (25.0, 10.0), (0.0, 10.0), (0.0, 0.0)])
    
    res1 = generate_prototype_vuid("12345678901234", "BLDG", "L01", poly1, 103.0, 106.0)
    res2 = generate_prototype_vuid("12345678901234", "BLDG", "L01", poly2, 103.0, 106.0)

    assert res1.prototype_vuid != res2.prototype_vuid
    assert res1.vuid_full_hash != res2.vuid_full_hash
