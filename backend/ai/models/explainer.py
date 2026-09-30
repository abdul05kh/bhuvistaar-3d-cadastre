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

    @classmethod
    def explain_validation_issue(cls, issue: dict[str, Any]) -> dict[str, Any]:
        """Provides a deep, transparent breakdown of why a validation rule failed or passed."""
        code = issue.get("rule_code", "UNKNOWN")
        sev = issue.get("severity", "INFO")
        meas = issue.get("measured_value") or {}
        thresh = issue.get("threshold") or {}
        msg = issue.get("message", "")
        action = issue.get("suggested_action") or "Review and correct based on authoritative survey records."

        if code == "VRT-003":
            gap = meas.get("gap_m", 0.0)
            overlap = meas.get("overlap_m", abs(gap) if gap < 0 else 0.0)
            low_lvl = meas.get("lower_level", "Lower Unit")
            up_lvl = meas.get("upper_level", "Upper Unit")
            min_gap = thresh.get("min_gap_m", -0.001)

            if gap < min_gap:
                detailed_explanation = (
                    f"Vertical collision detected: Level '{low_lvl}' extends {overlap:.2f}m into the vertical "
                    f"stratum of level '{up_lvl}'. The computed gap is {gap:.3f}m, which violates the minimum "
                    f"permissible threshold of {min_gap:.3f}m."
                )
            else:
                detailed_explanation = f"Vertical gap of {gap:.3f}m detected between '{low_lvl}' and '{up_lvl}'."

            return {
                "rule_code": code,
                "rule_family": "GATE_A_VERTICAL",
                "rule_version": "1.0.0",
                "ruleset_version": "1.0.0",
                "severity": sev,
                "lower_unit": low_lvl,
                "upper_unit": up_lvl,
                "measured_values": meas,
                "thresholds": thresh,
                "detailed_explanation": detailed_explanation,
                "suggested_action": action,
                "governance_implication": "BLOCKER: Approval strictly prohibited while physical collision persists." if sev == "BLOCKER" else "Advisory warning."
            }

        elif code == "TOP-001":
            return {
                "rule_code": code,
                "rule_family": "GATE_A_TOPOLOGY",
                "rule_version": "1.0.0",
                "ruleset_version": "1.0.0",
                "severity": sev,
                "measured_values": meas,
                "thresholds": thresh,
                "detailed_explanation": (
                    f"Cadastral boundary breach: Unit footprint extends outside the parent parcel polygon. "
                    f"3D spatial units must be strictly contained within the registered 2D parcel boundary."
                ),
                "suggested_action": "Clip or adjust candidate polygon to fit strictly within parent parcel bounds.",
                "governance_implication": "BLOCKER: Approval strictly prohibited for candidates breaching parcel boundary."
            }

        elif code == "GEO-002":
            return {
                "rule_code": code,
                "rule_family": "GATE_A_GEOMETRY",
                "rule_version": "1.0.0",
                "ruleset_version": "1.0.0",
                "severity": sev,
                "measured_values": meas,
                "thresholds": thresh,
                "detailed_explanation": (
                    "Geometric invalidity: The footprint polygon contains self-intersecting segments, "
                    "duplicate rings, or an invalid interior ring structure."
                ),
                "suggested_action": "Repair self-intersections or re-digitize boundary polygon.",
                "governance_implication": "BLOCKER: Malformed geometry cannot enter spatial registry."
            }

        else:
            return {
                "rule_code": code,
                "rule_family": "VALIDATION_RULE",
                "rule_version": "1.0.0",
                "ruleset_version": "1.0.0",
                "severity": sev,
                "measured_values": meas,
                "thresholds": thresh,
                "detailed_explanation": msg or f"Evaluation of rule {code} completed with outcome {sev}.",
                "suggested_action": action,
                "governance_implication": "BLOCKER: Must be resolved before Gate C." if sev == "BLOCKER" else "Advisory."
            }

