"""Synthetic Cadastral Benchmark Dataset for Slice 4 AI Evaluation.

Explicitly labeled: SYNTHETIC PROTOTYPE EVALUATION.
Contains the 10 mandated controlled, reproducible test scenarios.
"""
from typing import Any

SYNTHETIC_BENCHMARK_SCENARIOS: dict[str, dict[str, Any]] = {
    "1_CLEAN": {
        "scenario_id": 1,
        "title": "Clean Multi-Level Prismatic Sequence",
        "category": "SYNTHETIC_PROTOTYPE_EVALUATION",
        "description": "Standard 4-level building (B1, Ground, L01, L02) with perfectly contiguous vertical strata.",
        "ground_truth_levels": ["B1", "Ground", "L01", "L02"],
        "ground_truth_elevations": {
            "B1": (97.0, 100.0),
            "Ground": (100.0, 103.0),
            "L01": (103.0, 106.0),
            "L02": (106.0, 109.0)
        },
        "ai_confidence": 0.94,
        "expected_validation": "PASS",
        "expected_disagreement": "CONSISTENT",
        "human_decision": "ACCEPTED",
        "final_state": "GOVERNED_APPROVED",
        "expected_anomalies": []
    },
    "2_VRT_003_OVERLAP": {
        "scenario_id": 2,
        "title": "VRT-003 Vertical Stratum Overlap (Defect Fixture)",
        "category": "SYNTHETIC_PROTOTYPE_EVALUATION",
        "description": "L01 ceiling at 106.50m overlaps L02 floor at 106.00m by 0.50m, triggering VRT-003 blocker.",
        "ground_truth_levels": ["B1", "Ground", "L01", "L02"],
        "ground_truth_elevations": {
            "B1": (97.0, 100.0),
            "Ground": (100.0, 103.0),
            "L01": (103.0, 106.5),
            "L02": (106.0, 109.0)
        },
        "ai_confidence": 0.91,
        "expected_validation": "BLOCKER",
        "expected_disagreement": "AI_VALIDATION_DISAGREEMENT",
        "human_decision": "CORRECTION_REQUESTED",
        "final_state": "BLOCKED_PENDING_CORRECTION",
        "expected_anomalies": ["OVERLAPPING_LEVELS"]
    },
    "3_OUT_OF_PARCEL": {
        "scenario_id": 3,
        "title": "TOP-001 Footprint Extends Beyond Parent Parcel",
        "category": "SYNTHETIC_PROTOTYPE_EVALUATION",
        "description": "Candidate footprint extends 2.5m past the northern cadastral parcel boundary.",
        "ground_truth_levels": ["Ground"],
        "ground_truth_elevations": {
            "Ground": (100.0, 103.0)
        },
        "ai_confidence": 0.88,
        "expected_validation": "BLOCKER",
        "expected_disagreement": "AI_VALIDATION_DISAGREEMENT",
        "human_decision": "REJECTED",
        "final_state": "REJECTED_PRESERVED",
        "expected_anomalies": ["PARCEL_EXTENT_VIOLATION"]
    },
    "4_INVALID_GEOMETRY": {
        "scenario_id": 4,
        "title": "GEO-002 Self-Intersecting Bowtie Polygon",
        "category": "SYNTHETIC_PROTOTYPE_EVALUATION",
        "description": "Candidate polygon contains self-intersecting edges forming an invalid figure-8 ring.",
        "ground_truth_levels": ["Ground"],
        "ground_truth_elevations": {
            "Ground": (100.0, 103.0)
        },
        "ai_confidence": 0.75,
        "expected_validation": "BLOCKER",
        "expected_disagreement": "AI_VALIDATION_DISAGREEMENT",
        "human_decision": "REJECTED",
        "final_state": "REJECTED_PRESERVED",
        "expected_anomalies": ["SUSPICIOUS_GEOMETRY"]
    },
    "5_MISSING_EVIDENCE": {
        "scenario_id": 5,
        "title": "PROV-002 Missing Primary Evidence Linkage",
        "category": "SYNTHETIC_PROTOTYPE_EVALUATION",
        "description": "Candidate spatial unit submitted without any registered source evidence document IDs.",
        "ground_truth_levels": ["L01"],
        "ground_truth_elevations": {
            "L01": (103.0, 106.0)
        },
        "ai_confidence": 0.60,
        "expected_validation": "BLOCKER",
        "expected_disagreement": "AI_VALIDATION_DISAGREEMENT",
        "human_decision": "REJECTED",
        "final_state": "REJECTED_PRESERVED",
        "expected_anomalies": ["EVIDENCE_CONFLICT"]
    },
    "6_CONFLICTING_EVIDENCE": {
        "scenario_id": 6,
        "title": "Conflicting Multi-Source Evidence",
        "category": "SYNTHETIC_PROTOTYPE_EVALUATION",
        "description": "Architectural drawing indicates Level 2 at 106.00m while survey metadata specifies 107.00m.",
        "ground_truth_levels": ["Ground", "L01", "L02"],
        "ground_truth_elevations": {
            "Ground": (100.0, 103.0),
            "L01": (103.0, 106.0),
            "L02": (106.0, 109.0)
        },
        "ai_confidence": 0.70,
        "expected_validation": "WARN",
        "expected_disagreement": "CONSISTENT",
        "human_decision": "REVIEW_REQUIRED",
        "final_state": "UNDER_REVIEW",
        "expected_anomalies": ["EVIDENCE_CONFLICT"]
    },
    "7_LOW_CONFIDENCE_OBSERVATION": {
        "scenario_id": 7,
        "title": "Weak Hand-Drawn Sketch Observation",
        "category": "SYNTHETIC_PROTOTYPE_EVALUATION",
        "description": "Partial rooftop terrace proposal derived from an ambiguous sketch with 0.45 confidence.",
        "ground_truth_levels": ["Roof"],
        "ground_truth_elevations": {
            "Roof": (109.0, 112.0)
        },
        "ai_confidence": 0.45,
        "expected_validation": "PASS",
        "expected_disagreement": "LOW_AI_CONFIDENCE_GEOMETRICALLY_VALID",
        "human_decision": "PENDING_VERIFICATION",
        "final_state": "UNDER_REVIEW",
        "expected_anomalies": ["SUSPICIOUS_GEOMETRY"]
    },
    "8_AI_HIGH_CONF_BUT_INVALID": {
        "scenario_id": 8,
        "title": "AI High Confidence Proposal with Hidden Geometric Overlap",
        "category": "SYNTHETIC_PROTOTYPE_EVALUATION",
        "description": "Model outputs 0.93 high confidence based on clear floor plan text, but deterministic 3D extrusion overlaps lower floor by 0.5m.",
        "ground_truth_levels": ["L01", "L02"],
        "ground_truth_elevations": {
            "L01": (103.0, 106.5),
            "L02": (106.0, 109.0)
        },
        "ai_confidence": 0.93,
        "expected_validation": "BLOCKER",
        "expected_disagreement": "AI_VALIDATION_DISAGREEMENT",
        "human_decision": "CORRECTION_REQUESTED",
        "final_state": "BLOCKED_PENDING_CORRECTION",
        "expected_anomalies": ["OVERLAPPING_LEVELS"]
    },
    "9_AI_LOW_CONF_BUT_VALID": {
        "scenario_id": 9,
        "title": "AI Low Confidence Proposal that is Geometrically Clean",
        "category": "SYNTHETIC_PROTOTYPE_EVALUATION",
        "description": "Model outputs 0.52 confidence due to faded blueprint scan, but deterministic geometry checks completely pass Gate A and B.",
        "ground_truth_levels": ["Basement"],
        "ground_truth_elevations": {
            "Basement": (97.0, 100.0)
        },
        "ai_confidence": 0.52,
        "expected_validation": "PASS",
        "expected_disagreement": "LOW_AI_CONFIDENCE_GEOMETRICALLY_VALID",
        "human_decision": "ACCEPTED",
        "final_state": "GOVERNED_APPROVED",
        "expected_anomalies": []
    },
    "10_HUMAN_REJECTED_CANDIDATE": {
        "scenario_id": 10,
        "title": "Human Reviewer Overrides High-Confidence AI Proposal",
        "category": "SYNTHETIC_PROTOTYPE_EVALUATION",
        "description": "Human officer rejects AI proposal for secondary mezzanine after verifying field deed excludes interior partition.",
        "ground_truth_levels": ["Mezzanine"],
        "ground_truth_elevations": {
            "Mezzanine": (104.5, 106.0)
        },
        "ai_confidence": 0.89,
        "expected_validation": "PASS",
        "expected_disagreement": "HUMAN_OVERRIDE_OF_AI_PROPOSAL",
        "human_decision": "REJECTED",
        "final_state": "REJECTED_PRESERVED",
        "expected_anomalies": []
    }
}
