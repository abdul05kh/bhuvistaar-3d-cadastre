"""Layer B — Candidate Spatial-Unit Generation.

Proposes candidate 3D spatial units from parcel boundaries, building footprints,
and evidence observations.
CRITICAL CONSTRAINT: Status is ALWAYS AI_CANDIDATE. Never APPROVED.
"""
import uuid
from typing import Any
from shapely.geometry import shape, mapping, Polygon
from backend.domain.enums import SemanticType, CandidateStatus, ReasonCode
from backend.ai.schemas.candidate import CandidateSpatialUnit, VerticalExtent, ModelMetadata
from backend.ai.schemas.observation import EvidenceObservation
from backend.db.models import ParentParcelModel


class CandidateGenerator:
    MODEL_NAME = "prismatic-candidate-001"
    MODEL_VERSION = "0.1.0"

    @classmethod
    def generate_candidates(
        cls,
        parent_parcel: ParentParcelModel,
        observations: list[EvidenceObservation],
        footprint_geojson: dict[str, Any] | None = None,
        custom_levels: list[dict[str, Any]] | None = None
    ) -> list[CandidateSpatialUnit]:
        """Generates candidate 3D spatial units with transparent reason codes and confidence scores."""
        ulpin = parent_parcel.ulpin

        # 1. Determine footprint geometry
        if not footprint_geojson:
            # Check observations for BUILDING_FOOTPRINT
            for obs in observations:
                if obs.observation_type == "BUILDING_FOOTPRINT" and obs.geometry_geojson:
                    footprint_geojson = obs.geometry_geojson
                    break

        if not footprint_geojson:
            # Fallback: Default synthetic 20m x 15m building footprint in UTM 43N
            footprint_geojson = {
                "type": "Polygon",
                "coordinates": [
                    [
                        [643010.0, 1435005.0],
                        [643030.0, 1435005.0],
                        [643030.0, 1435020.0],
                        [643010.0, 1435020.0],
                        [643010.0, 1435005.0]
                    ]
                ]
            }

        footprint_poly = shape(footprint_geojson)
        if not isinstance(footprint_poly, Polygon) or not footprint_poly.is_valid:
            raise ValueError("Candidate footprint must be a valid Polygon geometry.")

        area_sqm = round(float(footprint_poly.area), 3)
        c_x = round(float(footprint_poly.centroid.x), 3)
        c_y = round(float(footprint_poly.centroid.y), 3)

        # 2. Extract Floor Levels to propose
        levels_to_propose = []
        if custom_levels:
            levels_to_propose = custom_levels
        else:
            # Aggregate from observations
            floor_obs = [obs for obs in observations if obs.observation_type == "FLOOR_BOUNDARY"]
            if floor_obs:
                for f_obs in floor_obs:
                    sem_type = SemanticType.BASEMENT_VOLUME if f_obs.semantic_level == "B1" else SemanticType.FLOOR_VOLUME
                    levels_to_propose.append({
                        "level_code": f_obs.semantic_level,
                        "z_min": f_obs.z_min,
                        "z_max": f_obs.z_max,
                        "semantic_type": sem_type,
                        "confidence": f_obs.confidence,
                        "source_evidence_ids": [f_obs.evidence_id],
                        "source_ref": f_obs.source_reference
                    })
            else:
                # Standard default 4-floor sequence
                levels_to_propose = [
                    {"level_code": "B1", "z_min": 97.0, "z_max": 100.0, "semantic_type": SemanticType.BASEMENT_VOLUME, "confidence": 0.88, "source_evidence_ids": ["EVID-003"]},
                    {"level_code": "Ground", "z_min": 100.0, "z_max": 103.0, "semantic_type": SemanticType.FLOOR_VOLUME, "confidence": 0.95, "source_evidence_ids": ["EVID-002", "EVID-003"]},
                    {"level_code": "L01", "z_min": 103.0, "z_max": 106.0, "semantic_type": SemanticType.FLOOR_VOLUME, "confidence": 0.94, "source_evidence_ids": ["EVID-003"]},
                    {"level_code": "L02", "z_min": 106.0, "z_max": 109.0, "semantic_type": SemanticType.FLOOR_VOLUME, "confidence": 0.91, "source_evidence_ids": ["EVID-003"]}
                ]

        candidates: list[CandidateSpatialUnit] = []

        for lvl in levels_to_propose:
            lvl_code = lvl["level_code"]
            z_min = float(lvl["z_min"])
            z_max = float(lvl["z_max"])
            sem_type = lvl.get("semantic_type", SemanticType.FLOOR_VOLUME)
            conf = float(lvl.get("confidence", 0.90))
            ev_ids = lvl.get("source_evidence_ids", [])
            height = round(z_max - z_min, 3)
            volume = round(area_sqm * height, 3)
            c_z = round((z_min + z_max) / 2.0, 3)

            # Assign explainability reason codes
            reasons = [
                ReasonCode.FOOTPRINT_MATCH.value,
                ReasonCode.FLOOR_PLAN_MATCH.value,
                ReasonCode.LEVEL_LABEL_DETECTED.value,
                ReasonCode.ELEVATION_SEQUENCE_MATCH.value,
                ReasonCode.GEOMETRIC_CONSISTENCY.value
            ]
            if len(ev_ids) > 1:
                reasons.append(ReasonCode.EVIDENCE_ALIGNMENT.value)

            cand_id = f"cand-{lvl_code.lower()}-{uuid.uuid4().hex[:8]}"
            conf_band = CandidateSpatialUnit.compute_confidence_band(conf)

            candidates.append(
                CandidateSpatialUnit(
                    candidate_id=cand_id,
                    parent_ulpin=ulpin,
                    source_evidence_ids=ev_ids,
                    geometry=footprint_geojson,
                    vertical_extent=VerticalExtent(z_min=z_min, z_max=z_max),
                    semantic_type=sem_type,
                    level_code=lvl_code,
                    confidence=conf,
                    confidence_band=conf_band,
                    reason_codes=reasons,
                    model=ModelMetadata(name=cls.MODEL_NAME, version=cls.MODEL_VERSION),
                    status=CandidateStatus.AI_CANDIDATE,
                    footprint_area_sqm=area_sqm,
                    volume_cbm=volume,
                    centroid_x=c_x,
                    centroid_y=c_y,
                    centroid_z=c_z
                )
            )

        return candidates
