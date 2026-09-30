"""Unit tests for AI Models (Layers A, B, C, D) and Model Registry."""
from backend.ai.models.evidence_extractor import EvidenceExtractor
from backend.ai.models.candidate_generator import CandidateGenerator
from backend.ai.models.anomaly_detector import AnomalyDetector
from backend.ai.models.explainer import CadastralExplainer
from backend.ai.registry.model_registry import get_registered_models, get_model_by_id
from backend.ai.schemas.candidate import CandidateSpatialUnit, VerticalExtent, ModelMetadata
from backend.domain.enums import ObservationType, AnomalyType, IssueSeverity, SemanticType, CandidateStatus


class MockParcel:
    ulpin = "12345678901234"
    metadata_json = {
        "coordinates": [
            [
                [643000.0, 1435000.0],
                [643040.0, 1435000.0],
                [643040.0, 1435030.0],
                [643000.0, 1435030.0],
                [643000.0, 1435000.0]
            ]
        ]
    }


def test_model_registry_entries():
    models = get_registered_models()
    assert len(models) >= 3
    model_ids = {m.model_id for m in models}
    assert "prismatic-candidate-001" in model_ids
    assert "cadastral-anomaly-001" in model_ids
    assert "evidence-extractor-001" in model_ids

    pc = get_model_by_id("prismatic-candidate-001")
    assert pc is not None
    assert pc.task == "CANDIDATE_SPATIAL_UNIT_GENERATION"
    assert pc.status == "PROTOTYPE"
    assert len(pc.known_limitations) > 0


def test_candidate_generator_deterministic():
    parcel = MockParcel()
    candidates = CandidateGenerator.generate_candidates(parent_parcel=parcel, observations=[])
    assert len(candidates) == 4
    levels = [c.level_code for c in candidates]
    assert levels == ["B1", "Ground", "L01", "L02"]

    for c in candidates:
        assert c.status == CandidateStatus.AI_CANDIDATE
        assert c.footprint_area_sqm > 0
        assert c.volume_cbm > 0
        assert len(c.reason_codes) >= 4
        assert 0.0 <= c.confidence <= 1.0


def test_anomaly_detector_vertical_overlap():
    parcel = MockParcel()
    meta = ModelMetadata(name="prismatic-candidate-001", version="0.1.0")
    footprint = {
        "type": "Polygon",
        "coordinates": [
            [[643010.0, 1435005.0], [643030.0, 1435005.0], [643030.0, 1435020.0], [643010.0, 1435020.0], [643010.0, 1435005.0]]
        ]
    }

    # Deliberate 0.50m overlap: L01 ceiling 106.5m overlaps L02 floor 106.0m
    c1 = CandidateSpatialUnit(
        candidate_id="c1",
        parent_ulpin=parcel.ulpin,
        geometry=footprint,
        vertical_extent=VerticalExtent(z_min=103.0, z_max=106.5),
        semantic_type=SemanticType.FLOOR_VOLUME,
        level_code="L01",
        confidence=0.94,
        confidence_band="HIGH",
        reason_codes=["FOOTPRINT_MATCH"],
        model=meta,
        status=CandidateStatus.AI_CANDIDATE,
        footprint_area_sqm=300.0,
        volume_cbm=1050.0,
        centroid_x=643020.0,
        centroid_y=643012.5,
        centroid_z=104.75
    )
    c2 = CandidateSpatialUnit(
        candidate_id="c2",
        parent_ulpin=parcel.ulpin,
        geometry=footprint,
        vertical_extent=VerticalExtent(z_min=106.0, z_max=109.0),
        semantic_type=SemanticType.FLOOR_VOLUME,
        level_code="L02",
        confidence=0.91,
        confidence_band="HIGH",
        reason_codes=["FOOTPRINT_MATCH"],
        model=meta,
        status=CandidateStatus.AI_CANDIDATE,
        footprint_area_sqm=300.0,
        volume_cbm=900.0,
        centroid_x=643020.0,
        centroid_y=643012.5,
        centroid_z=107.5
    )

    anomalies = AnomalyDetector.detect_anomalies(parcel, [c1, c2])
    overlap_anoms = [a for a in anomalies if a.anomaly_type == AnomalyType.OVERLAPPING_LEVELS]
    assert len(overlap_anoms) == 1
    assert overlap_anoms[0].severity == IssueSeverity.BLOCKER
    assert "0.50m" in overlap_anoms[0].recommended_action


def test_explainer_grounded_output():
    meta = ModelMetadata(name="prismatic-candidate-001", version="0.1.0")
    footprint = {
        "type": "Polygon",
        "coordinates": [
            [[643010.0, 1435005.0], [643030.0, 1435005.0], [643030.0, 1435020.0], [643010.0, 1435020.0], [643010.0, 1435005.0]]
        ]
    }
    c = CandidateSpatialUnit(
        candidate_id="cand-001",
        parent_ulpin="12345678901234",
        source_evidence_ids=["EVID-003"],
        geometry=footprint,
        vertical_extent=VerticalExtent(z_min=103.0, z_max=106.0),
        semantic_type=SemanticType.FLOOR_VOLUME,
        level_code="L01",
        confidence=0.94,
        confidence_band="HIGH",
        reason_codes=["FOOTPRINT_MATCH", "LEVEL_LABEL_DETECTED"],
        model=meta,
        status=CandidateStatus.AI_CANDIDATE,
        footprint_area_sqm=300.0,
        volume_cbm=900.0,
        centroid_x=643020.0,
        centroid_y=643012.5,
        centroid_z=104.5
    )

    explanation = CadastralExplainer.explain_candidate(c)
    assert explanation.target_id == "cand-001"
    assert "Candidate L01 was proposed with 0.94 (HIGH) confidence" in explanation.summary
    assert len(explanation.geometric_facts) >= 3
    assert len(explanation.evidence_basis) >= 2
    assert "No generative hallucination" in explanation.disclaimer
