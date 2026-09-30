"""Unit tests for Slice 3 AI Schemas and Safety Gates."""
import pytest
from backend.ai.schemas.candidate import CandidateSpatialUnit, VerticalExtent, ModelMetadata
from backend.ai.schemas.anomaly import AIAnomaly
from backend.ai.schemas.observation import EvidenceObservation
from backend.domain.enums import (
    SemanticType,
    CandidateStatus,
    AnomalyType,
    IssueSeverity,
    ObservationType,
    ExtractionMethod
)


def test_vertical_extent_validation():
    # Valid vertical extent
    ve = VerticalExtent(z_min=100.0, z_max=103.0)
    assert ve.z_min == 100.0
    assert ve.z_max == 103.0

    # Inverted vertical bounds should raise ValueError
    with pytest.raises(ValueError, match="z_max .* must be strictly greater than z_min"):
        VerticalExtent(z_min=105.0, z_max=102.0)

    # Equal vertical bounds should raise ValueError
    with pytest.raises(ValueError, match="z_max .* must be strictly greater than z_min"):
        VerticalExtent(z_min=100.0, z_max=100.0)


def test_candidate_cannot_be_approved_by_ai():
    """Safety Gate: AI candidate can NEVER have status APPROVED."""
    poly_geom = {
        "type": "Polygon",
        "coordinates": [[[0, 0], [10, 0], [10, 10], [0, 10], [0, 0]]]
    }
    model_meta = ModelMetadata(name="prismatic-candidate-001", version="0.1.0")

    # Creating candidate with APPROVED status must fail validation
    with pytest.raises(ValueError):
        CandidateSpatialUnit(
            candidate_id="cand-001",
            parent_ulpin="12345678901234",
            geometry=poly_geom,
            vertical_extent=VerticalExtent(z_min=100.0, z_max=103.0),
            semantic_type=SemanticType.FLOOR_VOLUME,
            level_code="L01",
            confidence=0.95,
            confidence_band="HIGH",
            reason_codes=["FOOTPRINT_MATCH"],
            model=model_meta,
            status="APPROVED",  # ILLEGAL
            footprint_area_sqm=100.0,
            volume_cbm=300.0,
            centroid_x=5.0,
            centroid_y=5.0,
            centroid_z=101.5
        )


def test_candidate_confidence_bands():
    assert CandidateSpatialUnit.compute_confidence_band(0.92) == "HIGH"
    assert CandidateSpatialUnit.compute_confidence_band(0.85) == "HIGH"
    assert CandidateSpatialUnit.compute_confidence_band(0.75) == "MEDIUM"
    assert CandidateSpatialUnit.compute_confidence_band(0.60) == "MEDIUM"
    assert CandidateSpatialUnit.compute_confidence_band(0.59) == "LOW"
    assert CandidateSpatialUnit.compute_confidence_band(0.40) == "LOW"


def test_candidate_invalid_geometry():
    model_meta = ModelMetadata(name="prismatic-candidate-001", version="0.1.0")

    # Non-polygon geometry
    with pytest.raises(ValueError, match="Geometry must be a GeoJSON Polygon"):
        CandidateSpatialUnit(
            candidate_id="cand-002",
            parent_ulpin="12345678901234",
            geometry={"type": "Point", "coordinates": [0, 0]},
            vertical_extent=VerticalExtent(z_min=100.0, z_max=103.0),
            semantic_type=SemanticType.FLOOR_VOLUME,
            level_code="L01",
            confidence=0.90,
            confidence_band="HIGH",
            reason_codes=["FOOTPRINT_MATCH"],
            model=model_meta,
            status=CandidateStatus.AI_CANDIDATE,
            footprint_area_sqm=100.0,
            volume_cbm=300.0,
            centroid_x=5.0,
            centroid_y=5.0,
            centroid_z=101.5
        )


def test_anomaly_schema():
    model_meta = ModelMetadata(name="cadastral-anomaly-001", version="0.1.0")
    anom = AIAnomaly(
        anomaly_id="anom-001",
        parent_ulpin="12345678901234",
        anomaly_type=AnomalyType.OVERLAPPING_LEVELS,
        severity=IssueSeverity.BLOCKER,
        affected_units=["L01", "L02"],
        evidence_ids=["EVID-003"],
        confidence=0.98,
        reason_codes=["VERTICAL_EXTENT_OVERLAP"],
        recommended_action="INSPECT: Reconcile vertical stratum boundary",
        model=model_meta
    )
    assert anom.severity == IssueSeverity.BLOCKER
    assert anom.anomaly_type == AnomalyType.OVERLAPPING_LEVELS
    assert not anom.resolved
