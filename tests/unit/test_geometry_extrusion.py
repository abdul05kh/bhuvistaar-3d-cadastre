import pytest
from shapely.geometry import Polygon
from backend.geometry.extrusion import compute_volumetric_extrusion, generate_polyhedral_surface_wkt


def test_volumetric_extrusion_metrics():
    # 24m x 18m building footprint
    poly = Polygon([(0.0, 0.0), (24.0, 0.0), (24.0, 18.0), (0.0, 18.0), (0.0, 0.0)])
    z_min = 100.0
    z_max = 103.0

    metrics = compute_volumetric_extrusion(poly, z_min, z_max)
    assert metrics.footprint_area_sqm == 432.0
    assert metrics.height_m == 3.0
    assert metrics.volume_cbm == 1296.0
    assert metrics.centroid_x == 12.0
    assert metrics.centroid_y == 9.0
    assert metrics.centroid_z == 101.5
    assert metrics.polyhedron_wkt.startswith("POLYHEDRALSURFACE Z (")


def test_reject_inverted_vertical_bounds():
    poly = Polygon([(0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0), (0.0, 0.0)])
    with pytest.raises(ValueError) as exc_info:
        compute_volumetric_extrusion(poly, 105.0, 102.0)
    assert "must be strictly less than" in str(exc_info.value)
