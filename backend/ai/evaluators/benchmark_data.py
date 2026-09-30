"""Synthetic Cadastral Benchmark Dataset for Slice 3 AI Evaluation.

Explicitly labeled: SYNTHETIC DEMO BENCHMARK DATA.
Contains controlled, reproducible test scenarios (Scenarios A through G).
"""
from typing import Any

SYNTHETIC_BENCHMARK_SCENARIOS: dict[str, dict[str, Any]] = {
    "SCENARIO_A_CLEAN_SEQUENCE": {
        "title": "Clean Multi-Level Prismatic Sequence",
        "category": "SYNTHETIC_DEMO_DATA",
        "description": "Standard 4-level building (B1, Ground, L01, L02) with perfectly contiguous vertical strata.",
        "ground_truth_levels": ["B1", "Ground", "L01", "L02"],
        "ground_truth_elevations": {
            "B1": (97.0, 100.0),
            "Ground": (100.0, 103.0),
            "L01": (103.0, 106.0),
            "L02": (106.0, 109.0)
        },
        "expected_anomalies": []
    },
    "SCENARIO_B_VERTICAL_OVERLAP": {
        "title": "Vertical Stratum Overlap (Defect Fixture)",
        "category": "SYNTHETIC_DEMO_DATA",
        "description": "L01 ceiling at 106.50m overlaps L02 floor at 106.00m by 0.50m, triggering VRT-003 blocker.",
        "ground_truth_levels": ["B1", "Ground", "L01", "L02"],
        "ground_truth_elevations": {
            "B1": (97.0, 100.0),
            "Ground": (100.0, 103.0),
            "L01": (103.0, 106.5),
            "L02": (106.0, 109.0)
        },
        "expected_anomalies": ["OVERLAPPING_LEVELS"]
    },
    "SCENARIO_C_VERTICAL_GAP": {
        "title": "Unexplained Inter-Floor Vertical Gap",
        "category": "SYNTHETIC_DEMO_DATA",
        "description": "Unexplained 1.00m gap between Ground ceiling (103.00m) and L01 floor (104.00m).",
        "ground_truth_levels": ["Ground", "L01"],
        "ground_truth_elevations": {
            "Ground": (100.0, 103.0),
            "L01": (104.0, 107.0)
        },
        "expected_anomalies": ["VERTICAL_GAP"]
    },
    "SCENARIO_D_EVIDENCE_MISMATCH": {
        "title": "Conflicting Multi-Source Evidence",
        "category": "SYNTHETIC_DEMO_DATA",
        "description": "Architectural drawing indicates Level 2 at 106.00m while survey metadata specifies 107.00m.",
        "ground_truth_levels": ["Ground", "L01", "L02"],
        "ground_truth_elevations": {
            "Ground": (100.0, 103.0),
            "L01": (103.0, 106.0),
            "L02": (106.0, 109.0)
        },
        "expected_anomalies": ["EVIDENCE_CONFLICT"]
    },
    "SCENARIO_E_PARCEL_BOUNDARY_BREACH": {
        "title": "Footprint Extends Beyond Parent Parcel",
        "category": "SYNTHETIC_DEMO_DATA",
        "description": "Candidate footprint extends 2.5m past the northern cadastral parcel boundary.",
        "ground_truth_levels": ["Ground"],
        "ground_truth_elevations": {
            "Ground": (100.0, 103.0)
        },
        "expected_anomalies": ["PARCEL_EXTENT_VIOLATION"]
    },
    "SCENARIO_F_MISSING_LEVEL": {
        "title": "Incomplete Architectural Sequence",
        "category": "SYNTHETIC_DEMO_DATA",
        "description": "Proposals contain Ground and L02, with L01 completely omitted.",
        "ground_truth_levels": ["Ground", "L02"],
        "ground_truth_elevations": {
            "Ground": (100.0, 103.0),
            "L02": (106.0, 109.0)
        },
        "expected_anomalies": ["MISSING_LEVEL"]
    },
    "SCENARIO_G_LOW_CONFIDENCE": {
        "title": "Ambiguous Hand-Drawn Sketch Candidate",
        "category": "SYNTHETIC_DEMO_DATA",
        "description": "Partial rooftop terrace proposal derived from an ambiguous sketch with 0.45 confidence.",
        "ground_truth_levels": ["Roof"],
        "ground_truth_elevations": {
            "Roof": (109.0, 112.0)
        },
        "expected_anomalies": ["SUSPICIOUS_GEOMETRY"]
    }
}
