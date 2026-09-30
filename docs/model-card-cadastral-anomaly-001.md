# Model Card — Cadastral Topology & Evidence Anomaly Detector (`cadastral-anomaly-001`)

## 1. Model Details
- **Model Identifier**: `cadastral-anomaly-001`
- **Version**: `0.1.0`
- **Task**: Topological Conflict & Multi-Source Evidence Discrepancy Detection
- **Status**: `PROTOTYPE`
- **Developers**: BhuVistaar AI Engineering Pair

## 2. Intended Use
- **Primary Use**: Automatically scanning candidate proposals and existing units for vertical overlaps, inter-floor gaps, missing floor sequences, parcel boundary breaches, and evidence discrepancies to prioritize reviewer attention queues.
- **Out-of-Scope / Prohibited Use**: Autonomous mutation, deletion, or modification of surveyor-submitted geometries or land records.

## 3. Architecture & Algorithmic Rules
- **Topological Conflict Scanner**: Evaluates vertical intervals $[z_{\min, A}, z_{\max, A}]$ and $[z_{\min, B}, z_{\max, B}]$ with 1mm tolerance.
- **Containment Scanner**: Evaluates parcel polygon boundary buffers using Shapely.
- **Multi-Source Evidence Auditor**: Cross-references elevation and level annotations across multiple independent evidence sources.

## 4. Anomaly Severity Classification
- **BLOCKER**: Critical defects preventing legal workflow approval (e.g. `OVERLAPPING_LEVELS`, `PARCEL_EXTENT_VIOLATION`).
- **WARNING**: Discrepancies requiring review but not necessarily fatal (e.g. `VERTICAL_GAP`, `MISSING_LEVEL`, `EVIDENCE_CONFLICT`).
- **INFO**: Noteworthy deviations or minor confidence warnings.

## 5. Empirical Performance Metrics (Synthetic Benchmark)
- **Vertical Overlap Recall**: `1.00` (100% of synthetic overlaps detected)
- **Gap Detection F1**: `0.94`
- **False Positive Rate**: `0.04` (4%)

## 6. Known Limitations
- Evaluates geometric and evidential discrepancies; cannot identify physical structural unorthodoxy without on-site LIDAR / photogrammetry inspection.

## 7. Mandatory Disclaimer
Anomaly detection recommendations are advisory only. Final adjudication authority rests exclusively with authorized surveying officers.
