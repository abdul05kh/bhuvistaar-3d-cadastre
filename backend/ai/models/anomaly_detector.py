"""Layer C — Anomaly & Inconsistency Detection.

Independent detection of vertical overlaps, inter-floor gaps, missing levels,
boundary breaches, and evidence discrepancies.
CRITICAL CONSTRAINT: Does NOT mutate underlying geometry.
"""
import uuid
from typing import Any
from shapely.geometry import shape, Polygon
from backend.domain.enums import AnomalyType, IssueSeverity, ReasonCode
from backend.ai.schemas.anomaly import AIAnomaly
from backend.ai.schemas.candidate import CandidateSpatialUnit, ModelMetadata
from backend.ai.schemas.observation import EvidenceObservation
from backend.db.models import ParentParcelModel, SpatialUnitModel


class AnomalyDetector:
    MODEL_NAME = "cadastral-anomaly-001"
    MODEL_VERSION = "0.1.0"

    @classmethod
    def detect_anomalies(
        cls,
        parent_parcel: ParentParcelModel,
        candidates: list[CandidateSpatialUnit],
        existing_units: list[SpatialUnitModel] | None = None,
        observations: list[EvidenceObservation] | None = None
    ) -> list[AIAnomaly]:
        anomalies: list[AIAnomaly] = []
        ulpin = parent_parcel.ulpin
        model_meta = ModelMetadata(name=cls.MODEL_NAME, version=cls.MODEL_VERSION)

        # 1. Parcel Extent Containment Check
        parcel_poly = None
        if parent_parcel and getattr(parent_parcel, "metadata_json", None):
            geom_json = parent_parcel.metadata_json.get("geometry")
            if geom_json and isinstance(geom_json, dict) and geom_json.get("type"):
                try:
                    parcel_poly = shape(geom_json)
                except Exception:
                    parcel_poly = None
            elif "coordinates" in parent_parcel.metadata_json:
                try:
                    coords = parent_parcel.metadata_json["coordinates"]
                    if coords and len(coords[0]) >= 4:
                        parcel_poly = Polygon(coords[0])
                except Exception:
                    parcel_poly = None

        if not parcel_poly and hasattr(parent_parcel, "geometry") and parent_parcel.geometry is not None:
            try:
                from geoalchemy2.shape import to_shape
                parcel_poly = to_shape(parent_parcel.geometry)
            except Exception:
                parcel_poly = None

        for cand in candidates:
            cand_poly = shape(cand.geometry)
            if parcel_poly and parcel_poly.is_valid:
                # Tolerance check
                if not parcel_poly.buffer(0.001).contains(cand_poly):
                    anomalies.append(
                        AIAnomaly(
                            anomaly_id=f"anom-extent-{uuid.uuid4().hex[:8]}",
                            parent_ulpin=ulpin,
                            anomaly_type=AnomalyType.PARCEL_EXTENT_VIOLATION,
                            severity=IssueSeverity.BLOCKER,
                            affected_units=[cand.level_code],
                            evidence_ids=cand.source_evidence_ids,
                            confidence=0.99,
                            reason_codes=["PARCEL_BOUNDARY_BREACH"],
                            recommended_action=f"BLOCKER: Unit {cand.level_code} footprint extends beyond parent parcel boundary. Inspect boundary alignment.",
                            model=model_meta
                        )
                    )

        # 2. Vertical Topology (Overlap & Gap Detection)
        # Combine candidates and existing units
        all_vertical_units = []
        for c in candidates:
            all_vertical_units.append({
                "id": c.candidate_id,
                "level": c.level_code,
                "z_min": c.vertical_extent.z_min,
                "z_max": c.vertical_extent.z_max,
                "evidence_ids": c.source_evidence_ids
            })

        if existing_units and not candidates:
            for u in existing_units:
                all_vertical_units.append({
                    "id": str(u.id),
                    "level": u.level_code,
                    "z_min": float(u.z_min),
                    "z_max": float(u.z_max),
                    "evidence_ids": []
                })

        # Sort by z_min
        all_vertical_units.sort(key=lambda u: u["z_min"])

        for i in range(len(all_vertical_units) - 1):
            curr = all_vertical_units[i]
            nxt = all_vertical_units[i + 1]

            # Overlap check: curr.z_max > nxt.z_min
            overlap_m = round(curr["z_max"] - nxt["z_min"], 3)
            if overlap_m > 0.001:
                anomalies.append(
                    AIAnomaly(
                        anomaly_id=f"anom-overlap-{uuid.uuid4().hex[:8]}",
                        parent_ulpin=ulpin,
                        anomaly_type=AnomalyType.OVERLAPPING_LEVELS,
                        severity=IssueSeverity.BLOCKER,
                        affected_units=[curr["level"], nxt["level"]],
                        evidence_ids=list(set(curr["evidence_ids"] + nxt["evidence_ids"])),
                        confidence=0.98,
                        reason_codes=[ReasonCode.VERTICAL_EXTENT_OVERLAP.value],
                        recommended_action=(
                            f"BLOCKER: Vertical overlap of {overlap_m:.2f}m detected between {curr['level']} "
                            f"(ceiling {curr['z_max']}m) and {nxt['level']} (floor {nxt['z_min']}m). "
                            f"Deterministic rule VRT-003 will block approval. Reconcile stratum boundary to {nxt['z_min']}m."
                        ),
                        model=model_meta
                    )
                )
            # Gap check: nxt.z_min - curr.z_max > 0.05m
            elif nxt["z_min"] - curr["z_max"] > 0.05:
                gap_m = round(nxt["z_min"] - curr["z_max"], 3)
                anomalies.append(
                    AIAnomaly(
                        anomaly_id=f"anom-gap-{uuid.uuid4().hex[:8]}",
                        parent_ulpin=ulpin,
                        anomaly_type=AnomalyType.VERTICAL_GAP,
                        severity=IssueSeverity.WARN,
                        affected_units=[curr["level"], nxt["level"]],
                        evidence_ids=list(set(curr["evidence_ids"] + nxt["evidence_ids"])),
                        confidence=0.92,
                        reason_codes=[ReasonCode.UNEXPLAINED_FLOOR_GAP.value],
                        recommended_action=(
                            f"WARNING: Unexplained vertical gap of {gap_m:.2f}m between {curr['level']} "
                            f"(ceiling {curr['z_max']}m) and {nxt['level']} (floor {nxt['z_min']}m). "
                            "Verify if structural slab or interstitial plenum exists."
                        ),
                        model=model_meta
                    )
                )

        # 3. Missing Level Sequence Check
        expected_sequence = ["B1", "Ground", "L01", "L02"]
        present_levels = {u["level"] for u in all_vertical_units}
        if "Ground" in present_levels and "L02" in present_levels and "L01" not in present_levels:
            anomalies.append(
                AIAnomaly(
                    anomaly_id=f"anom-missing-{uuid.uuid4().hex[:8]}",
                    parent_ulpin=ulpin,
                    anomaly_type=AnomalyType.MISSING_LEVEL,
                    severity=IssueSeverity.WARN,
                    affected_units=["Ground", "L02"],
                    evidence_ids=[],
                    confidence=0.89,
                    reason_codes=["LEVEL_SEQUENCE_GAP"],
                    recommended_action="WARNING: Level L01 is missing between Ground and L02 in proposed sequence. Verify floor plan completeness.",
                    model=model_meta
                )
            )

        # 4. Evidence Conflict Check
        if observations:
            floor_obs = [obs for obs in observations if obs.observation_type == "FLOOR_BOUNDARY"]
            by_level: dict[str, list[EvidenceObservation]] = {}
            for obs in floor_obs:
                if obs.semantic_level:
                    by_level.setdefault(obs.semantic_level, []).append(obs)

            for lvl, obs_list in by_level.items():
                if len(obs_list) > 1:
                    z_mins = {o.z_min for o in obs_list if o.z_min is not None}
                    z_maxs = {o.z_max for o in obs_list if o.z_max is not None}
                    if len(z_mins) > 1 or len(z_maxs) > 1:
                        anomalies.append(
                            AIAnomaly(
                                anomaly_id=f"anom-evid-conflict-{uuid.uuid4().hex[:8]}",
                                parent_ulpin=ulpin,
                                anomaly_type=AnomalyType.EVIDENCE_CONFLICT,
                                severity=IssueSeverity.WARN,
                                affected_units=[lvl],
                                evidence_ids=[o.evidence_id for o in obs_list],
                                confidence=0.88,
                                reason_codes=[ReasonCode.DISCORDANT_BOUNDARIES.value],
                                recommended_action=(
                                    f"WARNING: Evidence sources disagree on vertical extent for level {lvl}. "
                                    f"Sources specify discordant bounds: {z_mins} to {z_maxs}. Officer inspection required."
                                ),
                                model=model_meta
                            )
                        )

        # 5. Low Confidence Check
        for c in candidates:
            if c.confidence < 0.60:
                anomalies.append(
                    AIAnomaly(
                        anomaly_id=f"anom-lowconf-{uuid.uuid4().hex[:8]}",
                        parent_ulpin=ulpin,
                        anomaly_type=AnomalyType.SUSPICIOUS_GEOMETRY,
                        severity=IssueSeverity.WARN,
                        affected_units=[c.level_code],
                        evidence_ids=c.source_evidence_ids,
                        confidence=c.confidence,
                        reason_codes=[ReasonCode.CONFIDENCE_BELOW_THRESHOLD.value],
                        recommended_action=(
                            f"WARNING: Candidate {c.level_code} has low model confidence ({c.confidence:.2f} < 0.60). "
                            "Evidence support is weak or ambiguous; manual verification mandatory."
                        ),
                        model=model_meta
                    )
                )

        return anomalies
