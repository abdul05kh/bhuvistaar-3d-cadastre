"""Layer D — Fact-Based Explainability Engine.

Produces human-readable cadastral explanations synthesized strictly from
deterministic validation outcomes, geometric measurements, and evidence provenance.
CRITICAL CONSTRAINT: No ungrounded LLM hallucination.
"""
from typing import Any
from backend.ai.schemas.candidate import CandidateSpatialUnit
from backend.ai.schemas.anomaly import AIAnomaly
from backend.ai.schemas.summary import FactBasedExplanationResponse
from backend.domain.enums import IssueSeverity


class CadastralExplainer:
    MODEL_NAME = "fact-based-explainer-001"
    MODEL_VERSION = "0.1.0"

    @classmethod
    def explain_candidate(
        cls,
        candidate: CandidateSpatialUnit,
        associated_anomalies: list[AIAnomaly] | None = None,
        validation_blockers: list[dict[str, Any]] | None = None
    ) -> FactBasedExplanationResponse:
        lvl = candidate.level_code
        z_min = candidate.vertical_extent.z_min
        z_max = candidate.vertical_extent.z_max
        height = round(z_max - z_min, 3)
        conf = candidate.confidence
        band = candidate.confidence_band
        ev_list = candidate.source_evidence_ids or ["Unspecified"]
        reasons = candidate.reason_codes

        geometric_facts = [
            f"Vertical extent: {z_min:.2f}m to {z_max:.2f}m (Height: {height:.2f}m)",
            f"Planar footprint area: {candidate.footprint_area_sqm:.2f} m²",
            f"Extruded 3D volume: {candidate.volume_cbm:.2f} m³",
            f"Centroid: ({candidate.centroid_x:.2f}E, {candidate.centroid_y:.2f}N, {candidate.centroid_z:.2f}m Z)"
        ]

        evidence_basis = [
            f"Supported by evidence records: {', '.join(ev_list)}",
            f"Model {candidate.model.name} (v{candidate.model.version}) evaluated confidence: {conf:.2f} ({band})",
            f"Extracted reason codes: {', '.join(reasons)}"
        ]

        # Check for blockers / anomalies
        blockers = validation_blockers or []
        anoms = associated_anomalies or []
        has_blocker = any(b.get("severity") == "BLOCKER" for b in blockers) or any(a.severity == IssueSeverity.BLOCKER for a in anoms)

        val_status = "BLOCKER" if has_blocker else "PASS"

        if has_blocker:
            overlap_anom = next((a for a in anoms if a.anomaly_type == "OVERLAPPING_LEVELS"), None)
            if overlap_anom:
                summary = (
                    f"Candidate {lvl} was proposed by model {candidate.model.name} with {conf:.2f} confidence "
                    f"based on {', '.join(ev_list)}. However, deterministic validation flagged a critical vertical overlap blocker "
                    f"(Rule VRT-003). {overlap_anom.recommended_action} Human reviewer must reconcile elevation before Gate C approval."
                )
            else:
                summary = (
                    f"Candidate {lvl} was proposed with {conf:.2f} confidence. "
                    "However, deterministic validation identified blockers preventing approval. Human review and correction required."
                )
        else:
            summary = (
                f"Candidate {lvl} was proposed with {conf:.2f} ({band}) confidence from evidence {', '.join(ev_list)}. "
                "Deterministic geometry and vertical topology checks have passed with zero blockers. "
                "Awaiting human officer adjudication."
            )

        return FactBasedExplanationResponse(
            target_id=candidate.candidate_id,
            target_type="CANDIDATE",
            summary=summary,
            evidence_basis=evidence_basis,
            geometric_facts=geometric_facts,
            validation_status=val_status,
            governance_status=candidate.status.value
        )
