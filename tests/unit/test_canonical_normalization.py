from shapely.geometry import Polygon
from backend.geometry.normalization import canonicalize_polygon, canonical_wkb_hex
from backend.vuid.generator import generate_prototype_vuid


def test_shifted_starting_vertex_produces_identical_vuid():
    # A rectangle defined with 4 different starting vertices
    ring1 = [(200008.0, 1900006.0), (200032.0, 1900006.0), (200032.0, 1900024.0), (200008.0, 1900024.0), (200008.0, 1900006.0)]
    ring2 = [(200032.0, 1900006.0), (200032.0, 1900024.0), (200008.0, 1900024.0), (200008.0, 1900006.0), (200032.0, 1900006.0)]
    ring3 = [(200032.0, 1900024.0), (200008.0, 1900024.0), (200008.0, 1900006.0), (200032.0, 1900006.0), (200032.0, 1900024.0)]
    ring4 = [(200008.0, 1900024.0), (200008.0, 1900006.0), (200032.0, 1900006.0), (200032.0, 1900024.0), (200008.0, 1900024.0)]

    poly1 = Polygon(ring1)
    poly2 = Polygon(ring2)
    poly3 = Polygon(ring3)
    poly4 = Polygon(ring4)

    wkb1 = canonical_wkb_hex(poly1)
    wkb2 = canonical_wkb_hex(poly2)
    wkb3 = canonical_wkb_hex(poly3)
    wkb4 = canonical_wkb_hex(poly4)

    assert wkb1 == wkb2 == wkb3 == wkb4

    vuid1 = generate_prototype_vuid("12345678901234", "BLDG", "L01", poly1, 103.0, 106.0)
    vuid2 = generate_prototype_vuid("12345678901234", "BLDG", "L01", poly2, 103.0, 106.0)
    vuid3 = generate_prototype_vuid("12345678901234", "BLDG", "L01", poly3, 103.0, 106.0)
    vuid4 = generate_prototype_vuid("12345678901234", "BLDG", "L01", poly4, 103.0, 106.0)

    assert vuid1.prototype_vuid == vuid2.prototype_vuid == vuid3.prototype_vuid == vuid4.prototype_vuid
    assert vuid1.vuid_full_hash == vuid2.vuid_full_hash == vuid3.vuid_full_hash == vuid4.vuid_full_hash


def test_reversed_exterior_winding_produces_identical_vuid():
    ccw_ring = [(200008.0, 1900006.0), (200032.0, 1900006.0), (200032.0, 1900024.0), (200008.0, 1900024.0), (200008.0, 1900006.0)]
    cw_ring = list(reversed(ccw_ring))

    poly_ccw = Polygon(ccw_ring)
    poly_cw = Polygon(cw_ring)

    vuid_ccw = generate_prototype_vuid("12345678901234", "BLDG", "L01", poly_ccw, 103.0, 106.0)
    vuid_cw = generate_prototype_vuid("12345678901234", "BLDG", "L01", poly_cw, 103.0, 106.0)

    assert vuid_ccw.prototype_vuid == vuid_cw.prototype_vuid
    assert vuid_ccw.vuid_full_hash == vuid_cw.vuid_full_hash


def test_reordered_holes_produce_identical_vuid():
    ext = [(0.0, 0.0), (50.0, 0.0), (50.0, 50.0), (0.0, 50.0), (0.0, 0.0)]
    # Hole A at (10, 10), Hole B at (30, 30)
    hole_a = [(10.0, 10.0), (15.0, 10.0), (15.0, 15.0), (10.0, 15.0), (10.0, 10.0)]
    hole_b = [(30.0, 30.0), (35.0, 30.0), (35.0, 35.0), (30.0, 35.0), (30.0, 30.0)]

    poly_order1 = Polygon(ext, [hole_a, hole_b])
    poly_order2 = Polygon(ext, [hole_b, hole_a])

    vuid1 = generate_prototype_vuid("12345678901234", "BLDG", "L02", poly_order1, 106.0, 109.0)
    vuid2 = generate_prototype_vuid("12345678901234", "BLDG", "L02", poly_order2, 106.0, 109.0)

    assert vuid1.prototype_vuid == vuid2.prototype_vuid
    assert vuid1.vuid_full_hash == vuid2.vuid_full_hash
