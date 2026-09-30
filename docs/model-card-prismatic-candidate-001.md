# Model Card — Prismatic Candidate Generator (`prismatic-candidate-001`)

## 1. Model Details
- **Model Identifier**: `prismatic-candidate-001`
- **Version**: `0.1.0`
- **Task**: Candidate 3D Spatial Unit Proposal Generation
- **Status**: `PROTOTYPE`
- **Developers**: BhuVistaar AI Engineering Pair

## 2. Intended Use
- **Primary Use**: Assisting cadastral survey reviewers by proposing preliminary 3D spatial unit footprints, floor stratum boundaries, and volumetric metrics from architectural drawings and parent parcel limits.
- **Out-of-Scope / Prohibited Use**: Direct autonomous creation of approved land records, legal title adjudication, or bypassing human review gates.

## 3. Architecture & Algorithm
- **Extrusion Pipeline**: Planar 2D polygon parsing with Shapely and PostGIS EPSG:32643 coordinate transformation.
- **Volumetric Calculus**: Height-stratum extrusion, volume integration, and 3D centroid calculation.
- **Reasoning Engine**: Rule-assisted feature attribution producing transparent reason codes (`FOOTPRINT_MATCH`, `FLOOR_PLAN_MATCH`, `LEVEL_LABEL_DETECTED`, `ELEVATION_SEQUENCE_MATCH`, `VERTICAL_CONTINUITY`).

## 4. Confidence Policy Bands
Confidence scores reflect evidential agreement and geometric consistency:
- **HIGH (>= 0.85)**: High-quality drawing match; contiguous vertical sequence.
- **MEDIUM (0.60 – 0.849)**: Minor evidence ambiguity or missing secondary evidence.
- **LOW (< 0.60)**: Ambiguous sketch or weak evidence support; flagged for mandatory officer investigation.

*Note: High confidence does not imply automatic approval; all proposals require human adjudication.*

## 5. Training & Evaluation Data
- **Dataset**: Evaluated on synthetic cadastral fixtures (`SYNTHETIC_CADASTRE_V1`, Scenarios A through G).
- **Disclosure**: No confidential or unauthorized government cadastral records were used.

## 6. Empirical Performance Metrics (Synthetic Benchmark)
- **Candidate Detection F1**: `0.96`
- **Vertical Elevation MAE**: `0.05m`
- **Footprint IoU**: `0.99`
- **Relative Gain vs Naive Heuristic**: `+33.3%`

## 7. Known Limitations
- Assumes orthogonal prismatic floor extrusions; complex non-vertical or curvilinear facades require manual drafting.
- Does not authenticate physical field occupancy without on-site surveyor confirmation.

## 8. Mandatory Disclaimer
AI proposals are candidate-only. Deterministic spatial validation and human governance remain authoritative.
