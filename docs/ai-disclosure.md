# BhuVistaar — Machine Intelligence & AI Disclosure

This disclosure defines the operational boundaries, non-authoritative constraints, and evaluation methodology of machine intelligence within the BhuVistaar platform.

---

## 1. Absolute Architectural Principle
```
      EVIDENCE
         ↓
   AI / ML MODEL
         ↓
 CANDIDATE PROPOSAL (Non-Authoritative)
         ↓
DETERMINISTIC GEOMETRY ENGINE
         ↓
  GATE A / B VALIDATION
         ↓
   HUMAN OFFICER REVIEW
         ↓
   GATE C APPROVAL
```

> [!IMPORTANT]
> **AI IS NOT THE AUTHORITY.**
> Machine intelligence models in BhuVistaar are strictly assistive. They propose candidate geometries and flag potential anomalies. They have zero statutory authority to alter legal records, bypass spatial validation rules, or grant approvals.

---

## 2. Implemented Models & Capabilities

### 2.1 Prismatic Extrusion Candidate Model (`prismatic-candidate-001`)
- **Type:** Heuristic-statistical geometry generator.
- **Function:** Ingests 2D parcel/building footprints and architectural elevation annotations; synthesizes extruded 3D candidate prisms $[z_{\text{min}}, z_{\text{max}}]$ for standard floor heights.
- **Output:** `AI_CANDIDATE` records tagged with confidence scores [0.0 - 1.0] and structured reason codes (`REASON_EXTRUDED_FROM_FOOTPRINT`, `REASON_ELEVATION_INFERRED`).

### 2.2 Cadastral Anomaly Detector (`cadastral-anomaly-001`)
- **Type:** Rule-assisted statistical anomaly scanner.
- **Function:** Analyzes inter-floor elevation transitions and flags potential vertical collisions before official Gate A validation.
- **Output:** `AI_ANOMALY` records classified by type (`ELEVATION_COLLISION`, `UNUSUAL_FLOOR_HEIGHT`, `SUSPECT_BOUNDARY`).

### 2.3 AI vs Validation Disagreement Engine
Tracks operational friction between machine proposals and deterministic spatial reality across four explicit cases:
- **Case A (`AI_VALIDATION_DISAGREEMENT`):** Model assigned high confidence ($\ge 0.80$), but deterministic spatial validation detected a physical defect (e.g. VRT-003 overlap). **Approval remains strictly blocked.**
- **Case B (`LOW_AI_CONFIDENCE_GEOMETRICALLY_VALID`):** Model expressed uncertainty due to noisy evidence, but mathematical validation passed cleanly. The candidate is flagged for human review.
- **Case C (`CONSISTENT`):** Model and deterministic validator agree.
- **Case D (`HUMAN_OVERRIDE_OF_AI_PROPOSAL`):** A human reviewing officer rejects a machine proposal. The override is permanently recorded in the audit trail.

---

## 3. Synthetic Benchmark Evaluation Disclosure

> [!WARNING]
> **SYNTHETIC PROTOTYPE EVALUATION DISCLOSURE**  
> All benchmark metrics (Precision, Recall, F1-Score) reported in the Model Evaluation Modal and specifications are evaluated against **10 controlled synthetic cadastral scenarios**. They demonstrate that the evaluation harness functions correctly; they do **NOT** represent measured field accuracy on real-world national datasets.

The 10 synthetic benchmark scenarios include:
1. `clean`: Flawless 4-floor stacked configuration.
2. `vertical_overlap`: Controlled 0.50m collision between L01 and L02.
3. `out_of_parcel`: Unit footprint breaching parent parcel perimeter.
4. `invalid_geometry`: Self-intersecting polygon bowtie defect.
5. `missing_evidence`: Missing architectural floorplan plan.
6. `conflicting_evidence`: 0.50m discrepancy between survey elevation and CAD drawing.
7. `low_confidence`: Weak or noisy input signals.
8. `high_conf_invalid`: High-confidence machine hallucination (Disagreement Case A).
9. `low_conf_valid`: Low-confidence valid geometry (Disagreement Case B).
10. `human_rejection`: Human officer override of machine candidate (Disagreement Case D).
