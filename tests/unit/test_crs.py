import pytest
from shapely.geometry import Polygon
from backend.geometry.crs import parse_and_validate_crs, assert_projected_metric_crs, transform_polygon_to_srid
from backend.exceptions import InvalidCRSError


def test_parse_valid_projected_crs():
    crs = assert_projected_metric_crs("EPSG:32643")
    assert crs.is_projected is True
    assert crs.to_epsg() == 32643


def test_reject_unprojected_geographic_crs():
    with pytest.raises(InvalidCRSError) as exc_info:
        assert_projected_metric_crs("EPSG:4326")
    assert "geographic (angular degrees)" in str(exc_info.value)


def test_reject_malformed_crs():
    with pytest.raises(InvalidCRSError):
        assert_projected_metric_crs("NOT_A_VALID_CRS_99999")


def test_transform_polygon_preserves_shape():
    # Polygon in UTM 43N
    poly = Polygon([(200000.0, 1900000.0), (200040.0, 1900000.0), (200040.0, 1900030.0), (200000.0, 1900030.0), (200000.0, 1900000.0)])
    transformed = transform_polygon_to_srid(poly, "EPSG:32643", 32643)
    assert transformed.equals(poly)
    assert round(transformed.area, 1) == 1200.0
